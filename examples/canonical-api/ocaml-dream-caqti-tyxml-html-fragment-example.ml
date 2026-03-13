open Lwt.Syntax

type report_summary = {
  total_events : int;
  status : string;
}

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

let fragment_handler report_lookup request =
  let tenant_id = Dream.param request "tenant_id" in
  let* report = report_lookup tenant_id in
  Dream.html (render_report_card tenant_id report)

let routes report_lookup =
  [ Dream.get "/fragments/report-card/:tenant_id" (fragment_handler report_lookup) ]
