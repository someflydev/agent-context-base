open Lwt.Syntax
open Caqti_request.Infix

type db = (module Caqti_lwt.CONNECTION)

type series_point = {
  x : string;
  y : int;
}

let select_points =
  (Caqti_type.string ->* Caqti_type.(t2 string int))
    {|
      SELECT bucket, value
      FROM metric_points
      WHERE metric = ?
      ORDER BY bucket
    |}

let point_to_yojson { x; y } =
  `Assoc [ ("x", `String x); ("y", `Int y) ]

let data_handler (db : db) request =
  let module Db = (val db : Caqti_lwt.CONNECTION) in
  let metric = Dream.param request "metric" in
  let* rows = Db.collect_list select_points metric >>= Caqti_lwt.or_fail in
  let points = List.map (fun (x, y) -> { x; y }) rows in
  Dream.json
    (Yojson.Safe.to_string
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
          ]))

let routes db =
  [ Dream.get "/data/chart/:metric" (data_handler db) ]
