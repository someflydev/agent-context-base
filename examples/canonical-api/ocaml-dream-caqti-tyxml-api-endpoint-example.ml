open Lwt.Syntax
open Caqti_request.Infix

type db = (module Caqti_lwt.CONNECTION)

type report_summary = {
  report_id : string;
  total_events : int;
  status : string;
}

let select_reports =
  (Caqti_type.(t2 string int) ->* Caqti_type.(t3 string int string))
    {|
      SELECT report_id, total_events, status
      FROM reports
      WHERE tenant_id = ?
      ORDER BY report_id
      LIMIT ?
    |}

let report_to_yojson { report_id; total_events; status } =
  `Assoc
    [
      ("report_id", `String report_id);
      ("total_events", `Int total_events);
      ("status", `String status);
    ]

let reports_handler (db : db) request =
  let module Db = (val db : Caqti_lwt.CONNECTION) in
  let tenant_id = Dream.param request "tenant_id" in
  let limit =
    Option.bind (Dream.query request "limit") int_of_string_opt
    |> Option.value ~default:5
  in
  let* rows = Db.collect_list select_reports (tenant_id, limit) >>= Caqti_lwt.or_fail in
  let reports =
    List.map
      (fun (report_id, total_events, status) -> { report_id; total_events; status })
      rows
  in
  Dream.json
    (Yojson.Safe.to_string
       (`Assoc
          [
            ("service", `String "ocaml-dream-caqti-tyxml");
            ("tenant_id", `String tenant_id);
            ("reports", `List (List.map report_to_yojson reports));
          ]))

let routes db =
  [ Dream.get "/api/reports/:tenant_id" (reports_handler db) ]
