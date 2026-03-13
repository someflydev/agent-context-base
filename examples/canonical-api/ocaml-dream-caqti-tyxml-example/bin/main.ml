open Lwt.Infix
open Lwt.Syntax
open Caqti_request.Infix

type db = (module Caqti_lwt.CONNECTION)

type report_summary = {
  report_id : string;
  total_events : int;
  status : string;
}

type series_point = {
  x : string;
  y : int;
}

let database_uri = Uri.of_string "sqlite3:///tmp/ocaml-dream-caqti-tyxml-example.db"

let create_reports =
  (Caqti_type.unit ->. Caqti_type.unit)
    {|
      CREATE TABLE IF NOT EXISTS reports (
        tenant_id TEXT NOT NULL,
        report_id TEXT NOT NULL,
        total_events INTEGER NOT NULL,
        status TEXT NOT NULL
      )
    |}

let create_metric_points =
  (Caqti_type.unit ->. Caqti_type.unit)
    {|
      CREATE TABLE IF NOT EXISTS metric_points (
        metric TEXT NOT NULL,
        bucket TEXT NOT NULL,
        value INTEGER NOT NULL
      )
    |}

let seed_report =
  (Caqti_type.(t4 string string int string) ->. Caqti_type.unit)
    {|
      INSERT INTO reports (tenant_id, report_id, total_events, status)
      VALUES (?, ?, ?, ?)
    |}

let seed_metric_point =
  (Caqti_type.(t3 string string int) ->. Caqti_type.unit)
    {|
      INSERT INTO metric_points (metric, bucket, value)
      VALUES (?, ?, ?)
    |}

let clear_reports =
  (Caqti_type.unit ->. Caqti_type.unit) "DELETE FROM reports"

let clear_metric_points =
  (Caqti_type.unit ->. Caqti_type.unit) "DELETE FROM metric_points"

let select_reports =
  (Caqti_type.(t2 string int) ->* Caqti_type.(t3 string int string))
    {|
      SELECT report_id, total_events, status
      FROM reports
      WHERE tenant_id = ?
      ORDER BY report_id
      LIMIT ?
    |}

let select_metric_points =
  (Caqti_type.string ->* Caqti_type.(t2 string int))
    {|
      SELECT bucket, value
      FROM metric_points
      WHERE metric = ?
      ORDER BY bucket
    |}

let json_response payload =
  Dream.json (Yojson.Safe.to_string payload)

let report_to_yojson { report_id; total_events; status } =
  `Assoc
    [
      ("report_id", `String report_id);
      ("total_events", `Int total_events);
      ("status", `String status);
    ]

let point_to_yojson { x; y } =
  `Assoc [ ("x", `String x); ("y", `Int y) ]

let render_report_card tenant_id report =
  let open Tyxml.Html in
  section
    ~a:
      [
        a_id ("report-card-" ^ tenant_id);
        a_class [ "report-card" ];
        Unsafe.string_attrib "hx-swap-oob" "true";
      ]
    [
      strong [ txt ("Tenant " ^ tenant_id) ];
      span [ txt (Printf.sprintf "%d events in the last hour" report.total_events) ];
      p ~a:[ a_class [ "status" ] ] [ txt report.status ];
    ]
  |> Format.asprintf "%a" (Tyxml.Html.pp_elt ())

let with_db (db : db) f =
  let module Db = (val db : Caqti_lwt.CONNECTION) in
  f (module Db : Caqti_lwt.CONNECTION)

let list_reports (db : db) tenant_id limit =
  with_db db (fun (module Db : Caqti_lwt.CONNECTION) ->
      Db.collect_list select_reports (tenant_id, limit) >>= Caqti_lwt.or_fail)
  >|= List.map (fun (report_id, total_events, status) -> { report_id; total_events; status })

let list_metric_points (db : db) metric =
  with_db db (fun (module Db : Caqti_lwt.CONNECTION) ->
      Db.collect_list select_metric_points metric >>= Caqti_lwt.or_fail)
  >|= List.map (fun (x, y) -> { x; y })

let initialize_db (db : db) =
  with_db db (fun (module Db : Caqti_lwt.CONNECTION) ->
      let* () = Db.exec create_reports () >>= Caqti_lwt.or_fail in
      let* () = Db.exec create_metric_points () >>= Caqti_lwt.or_fail in
      let* () = Db.exec clear_reports () >>= Caqti_lwt.or_fail in
      let* () = Db.exec clear_metric_points () >>= Caqti_lwt.or_fail in
      let* () =
        Db.exec seed_report ("acme", "daily-signups", 42, "ready") >>= Caqti_lwt.or_fail
      in
      let* () =
        Db.exec seed_metric_point ("signups", "2026-03-01", 18) >>= Caqti_lwt.or_fail
      in
      let* () =
        Db.exec seed_metric_point ("signups", "2026-03-02", 24) >>= Caqti_lwt.or_fail
      in
      Db.exec seed_metric_point ("signups", "2026-03-03", 31) >>= Caqti_lwt.or_fail)

let health_handler _request =
  json_response
    (`Assoc
       [
         ("status", `String "ok");
         ("service", `String "ocaml-dream-caqti-tyxml-example");
       ])

let reports_handler db request =
  let tenant_id = Dream.param request "tenant_id" in
  let limit =
    Option.bind (Dream.query request "limit") int_of_string_opt
    |> Option.value ~default:5
  in
  let* reports = list_reports db tenant_id limit in
  json_response
    (`Assoc
       [
         ("service", `String "ocaml-dream-caqti-tyxml-example");
         ("tenant_id", `String tenant_id);
         ("reports", `List (List.map report_to_yojson reports));
       ])

let fragment_handler db request =
  let tenant_id = Dream.param request "tenant_id" in
  let* reports = list_reports db tenant_id 1 in
  match reports with
  | report :: _ -> Dream.html (render_report_card tenant_id report)
  | [] -> Dream.empty `Not_Found

let data_handler db request =
  let metric = Dream.param request "metric" in
  let* points = list_metric_points db metric in
  json_response
    (`Assoc
       [
         ("metric", `String metric);
         ( "series",
           `List
             [
               `Assoc
                 [
                   ("name", `String metric);
                   ("points", `List (List.map point_to_yojson points));
                 ];
             ] );
       ])

let connect_db () =
  Caqti_lwt_unix.connect database_uri >>= Caqti_lwt.or_fail

let () =
  let db =
    Lwt_main.run
      (let* db = connect_db () in
       let* () = initialize_db db in
       Lwt.return db)
  in
  Dream.run ~interface:"0.0.0.0" ~port:8080
  @@ Dream.logger
  @@ Dream.router
       [
         Dream.get "/healthz" health_handler;
         Dream.get "/api/reports/:tenant_id" (reports_handler db);
         Dream.get "/fragments/report-card/:tenant_id" (fragment_handler db);
         Dream.get "/data/chart/:metric" (data_handler db);
       ]
