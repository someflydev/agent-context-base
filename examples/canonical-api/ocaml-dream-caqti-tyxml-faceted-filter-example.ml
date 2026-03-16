(* ocaml-dream-caqti-tyxml-faceted-filter-example.ml

   Demonstrates the full split include/exclude filter panel pattern with OCaml + Dream + TyXML.
   Uses inline data; Caqti DB queries are not required for this example.

   Multi-value params: Dream.queries request "status_out" returns string list.

   TyXML data-* attributes: use Tyxml.Html.Unsafe.string_attrib "data-filter-dimension" "team".
*)

open Lwt.Syntax

(* ---------------------------------------------------------------------------
   Dataset
   --------------------------------------------------------------------------- *)

type report_row = {
  report_id : string;
  team      : string;
  status    : string;
  region    : string;
  events    : int;
}

let report_rows = [
  { report_id = "daily-signups";     team = "growth";   status = "active";   region = "us";   events = 12 };
  { report_id = "trial-conversions"; team = "growth";   status = "active";   region = "us";   events = 7  };
  { report_id = "api-latency";       team = "platform"; status = "paused";   region = "eu";   events = 5  };
  { report_id = "checkout-failures"; team = "growth";   status = "active";   region = "eu";   events = 9  };
  { report_id = "queue-depth";       team = "platform"; status = "active";   region = "apac"; events = 11 };
  { report_id = "legacy-import";     team = "platform"; status = "archived"; region = "us";   events = 4  };
]

let facet_options = [
  ("team",   ["growth"; "platform"]);
  ("status", ["active"; "paused"; "archived"]);
  ("region", ["us"; "eu"; "apac"]);
]

let quick_excludes = [("status", "archived"); ("status", "paused")]

(* ---------------------------------------------------------------------------
   Query state
   --------------------------------------------------------------------------- *)

type query_state = {
  team_in    : string list;
  team_out   : string list;
  status_in  : string list;
  status_out : string list;
  region_in  : string list;
  region_out : string list;
}

let normalize values =
  values
  |> List.map (fun s -> String.trim s |> String.lowercase_ascii)
  |> List.filter (fun s -> s <> "")
  |> List.sort_uniq String.compare

let build_query_state request =
  {
    team_in    = normalize (Dream.queries request "team_in");
    team_out   = normalize (Dream.queries request "team_out");
    status_in  = normalize (Dream.queries request "status_in");
    status_out = normalize (Dream.queries request "status_out");
    region_in  = normalize (Dream.queries request "region_in");
    region_out = normalize (Dream.queries request "region_out");
  }

let fingerprint state =
  String.concat "|" [
    "team_in="    ^ String.concat "," state.team_in;
    "team_out="   ^ String.concat "," state.team_out;
    "status_in="  ^ String.concat "," state.status_in;
    "status_out=" ^ String.concat "," state.status_out;
    "region_in="  ^ String.concat "," state.region_in;
    "region_out=" ^ String.concat "," state.region_out;
  ]

(* ---------------------------------------------------------------------------
   Filter helpers
   --------------------------------------------------------------------------- *)

let matches_dim value includes excludes =
  (includes = [] || List.mem value includes) &&
  not (excludes <> [] && List.mem value excludes)

let row_dim_value row dim = match dim with
  | "team"   -> row.team
  | "status" -> row.status
  | "region" -> row.region
  | _        -> ""

let filter_rows state =
  List.filter (fun row ->
    matches_dim row.team   state.team_in   state.team_out   &&
    matches_dim row.status state.status_in state.status_out &&
    matches_dim row.region state.region_in state.region_out
  ) report_rows

let facet_counts state dimension =
  let options = List.assoc_opt dimension facet_options |> Option.value ~default:[] in
  let init    = List.map (fun o -> (o, 0)) options in
  let filtered = match dimension with
    | "team" ->
        List.filter (fun r ->
          matches_dim r.status state.status_in state.status_out &&
          matches_dim r.region state.region_in state.region_out &&
          matches_dim r.team   []              state.team_out
        ) report_rows
    | "status" ->
        List.filter (fun r ->
          matches_dim r.team   state.team_in   state.team_out   &&
          matches_dim r.region state.region_in state.region_out &&
          matches_dim r.status []              state.status_out
        ) report_rows
    | _ ->
        List.filter (fun r ->
          matches_dim r.team   state.team_in   state.team_out   &&
          matches_dim r.status state.status_in state.status_out &&
          matches_dim r.region []              state.region_out
        ) report_rows
  in
  List.fold_left (fun acc row ->
    let v = row_dim_value row dimension in
    List.map (fun (o, c) -> if o = v then (o, c + 1) else (o, c)) acc
  ) init filtered

let exclude_impact_counts state dimension =
  let options = List.assoc_opt dimension facet_options |> Option.value ~default:[] in
  let dim_out = match dimension with
    | "team"   -> state.team_out
    | "status" -> state.status_out
    | _        -> state.region_out
  in
  List.map (fun option ->
    let other_excludes = List.filter (fun v -> v <> option) dim_out in
    let count = List.length (List.filter (fun row ->
      let other_pass = match dimension with
        | "team" ->
            matches_dim row.status state.status_in state.status_out &&
            matches_dim row.region state.region_in state.region_out
        | "status" ->
            matches_dim row.team   state.team_in   state.team_out   &&
            matches_dim row.region state.region_in state.region_out
        | _ ->
            matches_dim row.team   state.team_in   state.team_out   &&
            matches_dim row.status state.status_in state.status_out
      in
      let v = row_dim_value row dimension in
      other_pass &&
      (other_excludes = [] || not (List.mem v other_excludes)) &&
      v = option
    ) report_rows)
    in (option, count)
  ) options

(* ---------------------------------------------------------------------------
   HTML rendering with TyXML
   --------------------------------------------------------------------------- *)

let str_attrib name value = Tyxml.Html.Unsafe.string_attrib name value

let pp_elt elt = Format.asprintf "%a" (Tyxml.Html.pp_elt ()) elt

let capitalize s =
  if String.length s = 0 then s
  else String.make 1 (Char.uppercase_ascii s.[0]) ^ String.sub s 1 (String.length s - 1)

let render_quick_exclude_toggle state dim v =
  let open Tyxml.Html in
  let impact    = exclude_impact_counts state dim in
  let dim_out   = match dim with
    | "team"   -> state.team_out
    | "status" -> state.status_out
    | _        -> state.region_out
  in
  let is_active = List.mem v dim_out in
  let active_str = if is_active then "true" else "false" in
  let impact_n  = List.assoc_opt v impact |> Option.value ~default:0 in
  let cls = if is_active
    then "flex items-center gap-1 rounded border border-red-300 bg-red-50 px-2 py-1 text-xs font-medium text-red-700 cursor-pointer"
    else "flex items-center gap-1 rounded border border-slate-200 px-2 py-1 text-xs text-slate-600 cursor-pointer"
  in
  let input_attrs = [a_input_type `Checkbox; a_name (dim ^ "_out"); a_value v; a_class ["sr-only"]] in
  let input_attrs = if is_active then input_attrs @ [a_checked ()] else input_attrs in
  label ~a:[
    str_attrib "data-role" "quick-exclude";
    str_attrib "data-quick-exclude-dimension" dim;
    str_attrib "data-quick-exclude-value" v;
    str_attrib "data-active" active_str;
    a_class [cls];
  ] [
    input ~a:input_attrs ();
    txt (" " ^ capitalize v ^ " ");
    span ~a:[a_class ["rounded bg-slate-100 px-1 ml-1"]] [txt (string_of_int impact_n)];
  ]

let render_include_option state dimension option inc_counts =
  let open Tyxml.Html in
  let dim_out    = match dimension with
    | "team"   -> state.team_out   | "status" -> state.status_out | _ -> state.region_out in
  let dim_in     = match dimension with
    | "team"   -> state.team_in    | "status" -> state.status_in  | _ -> state.region_in  in
  let is_excluded = List.mem option dim_out in
  let is_checked  = List.mem option dim_in  in
  let opt_count   = if is_excluded then 0 else (List.assoc_opt option inc_counts |> Option.value ~default:0) in
  let label_extra = if is_excluded then " opacity-50 cursor-not-allowed" else "" in
  let base_attrs  = [
    str_attrib "data-filter-dimension" dimension;
    str_attrib "data-filter-option"    option;
    str_attrib "data-filter-mode"      "include";
    str_attrib "data-option-count"     (string_of_int opt_count);
    a_class ["flex items-center justify-between rounded border border-slate-200 px-3 py-2 text-sm" ^ label_extra];
  ] in
  let label_attrs = if is_excluded then base_attrs @ [str_attrib "data-excluded" "true"] else base_attrs in
  let input_attrs = [a_input_type `Checkbox; a_name (dimension ^ "_in"); a_value option] in
  let input_attrs = if is_checked  then input_attrs @ [a_checked ()] else input_attrs in
  let input_attrs = if is_excluded then input_attrs @ [a_disabled ()] else input_attrs in
  label ~a:label_attrs [
    span ~a:[a_class ["flex items-center gap-2"]] [
      input ~a:input_attrs ();
      span ~a:[a_class ["font-medium text-slate-800"]] [txt (capitalize option)];
    ];
    span ~a:[str_attrib "data-role" "option-count"; a_class ["rounded bg-slate-100 px-2 py-1 text-slate-600"]]
         [txt (string_of_int opt_count)];
  ]

let render_exclude_option state dimension option exc_counts =
  let open Tyxml.Html in
  let dim_out   = match dimension with
    | "team"   -> state.team_out | "status" -> state.status_out | _ -> state.region_out in
  let is_active = List.mem option dim_out in
  let impact    = List.assoc_opt option exc_counts |> Option.value ~default:0 in
  let border_cls = if is_active then "border-red-200 bg-red-50" else "border-slate-200" in
  let base_attrs = [
    str_attrib "data-filter-dimension" dimension;
    str_attrib "data-filter-option"    option;
    str_attrib "data-filter-mode"      "exclude";
    str_attrib "data-option-count"     (string_of_int impact);
    a_class ["flex items-center justify-between rounded border " ^ border_cls ^ " px-3 py-2 text-sm"];
  ] in
  let label_attrs = if is_active then base_attrs @ [str_attrib "data-active" "true"] else base_attrs in
  let input_attrs = [a_input_type `Checkbox; a_name (dimension ^ "_out"); a_value option] in
  let input_attrs = if is_active then input_attrs @ [a_checked ()] else input_attrs in
  label ~a:label_attrs [
    span ~a:[a_class ["flex items-center gap-2"]] [
      input ~a:input_attrs ();
      span ~a:[a_class ["font-medium text-slate-800"]] [txt (capitalize option)];
    ];
    span ~a:[str_attrib "data-role" "option-count"; a_class ["rounded bg-slate-100 px-2 py-1 text-slate-600"]]
         [txt (string_of_int impact)];
  ]

let render_filter_panel state =
  let open Tyxml.Html in
  let quick_toggles = List.map (fun (dim, v) -> render_quick_exclude_toggle state dim v) quick_excludes in
  let dim_groups = List.map (fun dimension ->
    let options    = List.assoc_opt dimension facet_options |> Option.value ~default:[] in
    let inc_counts = facet_counts state dimension in
    let exc_counts = exclude_impact_counts state dimension in
    section ~a:[str_attrib "data-filter-dimension" dimension; a_class ["space-y-2"]] [
      h3 ~a:[a_class ["text-xs font-semibold uppercase tracking-wide text-slate-500"]] [txt (capitalize dimension)];
      div ~a:[str_attrib "data-role" "include-options"; a_class ["space-y-1"]] (
        p ~a:[a_class ["text-xs text-slate-400 uppercase tracking-wide"]] [txt "Include"] ::
        List.map (fun opt -> render_include_option state dimension opt inc_counts) options
      );
      div ~a:[str_attrib "data-role" "exclude-options"; a_class ["mt-2 space-y-1"]] (
        p ~a:[a_class ["text-xs text-slate-400 uppercase tracking-wide"]] [txt "Exclude"] ::
        List.map (fun opt -> render_exclude_option state dimension opt exc_counts) options
      );
    ]
  ) ["team"; "status"; "region"] in
  let panel = div ~a:[a_id "filter-panel"; a_class ["space-y-4"]] (
    div ~a:[a_class ["rounded bg-slate-50 px-3 py-2 text-xs text-slate-600"];
            str_attrib "data-role" "count-discipline"]
        [txt "Counts reflect the active backend query semantics."] ::
    div ~a:[a_class ["flex flex-wrap items-center gap-2 border-b border-slate-100 pb-3"];
            str_attrib "data-role" "quick-excludes-strip"] (
      span ~a:[a_class ["text-xs font-semibold uppercase tracking-wide text-slate-400 self-center"]]
           [txt "Quick excludes"] ::
      quick_toggles
    ) ::
    dim_groups
  ) in
  pp_elt panel

let render_results_fragment state =
  let open Tyxml.Html in
  let rows = filter_rows state in
  let n    = List.length rows in
  let fp   = fingerprint state in
  let badge = div ~a:[
    a_id "result-count";
    str_attrib "hx-swap-oob" "true";
    str_attrib "data-role" "result-count";
    str_attrib "data-result-count" (string_of_int n);
    a_class ["rounded bg-blue-50 px-3 py-1 text-sm font-medium text-blue-700"];
  ] [txt (Printf.sprintf "%d results" n)] in
  let cards = List.map (fun row ->
    div ~a:[a_class ["rounded border border-slate-200 px-4 py-3 text-sm"];
            str_attrib "data-report-id" row.report_id]
        [strong [txt row.report_id]; txt (" " ^ row.team ^ " / " ^ row.status ^ " / " ^ row.region)]
  ) rows in
  let results_sec = section ~a:[
    a_id "report-results";
    str_attrib "data-query-fingerprint" fp;
    str_attrib "data-result-count" (string_of_int n);
    a_class ["space-y-2"];
  ] (div ~a:[str_attrib "data-role" "active-filters"; a_class ["text-xs text-slate-500"]] [txt fp] :: cards) in
  pp_elt badge ^ pp_elt results_sec

let render_full_page state =
  let panel = render_filter_panel state in
  let rows  = filter_rows state in
  let n     = List.length rows in
  let fp    = fingerprint state in
  let cards = List.map (fun row ->
    Printf.sprintf {|<div class="rounded border border-slate-200 px-4 py-3 text-sm" data-report-id="%s"><strong>%s</strong></div>|}
      row.report_id row.report_id
  ) rows |> String.concat "\n" in
  Printf.sprintf {|<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Reports</title>
<script src="https://unpkg.com/htmx.org@1.9.10"></script>
<script src="https://cdn.tailwindcss.com"></script></head>
<body class="p-6 font-sans"><h1 class="text-xl font-bold mb-4">Reports</h1>
<form id="report-filters" hx-get="/ui/reports/results" hx-target="#report-results" hx-trigger="change, submit">
<div class="flex gap-6"><aside class="w-64 shrink-0">%s</aside><main class="flex-1">
<div id="result-count" data-role="result-count" data-result-count="%d" class="rounded bg-blue-50 px-3 py-1 text-sm font-medium text-blue-700 mb-3">%d results</div>
<section id="report-results" data-query-fingerprint="%s" data-result-count="%d" class="space-y-2">%s</section>
</main></div></form></body></html>|}
    panel n n fp n cards

(* ---------------------------------------------------------------------------
   Routes
   --------------------------------------------------------------------------- *)

let routes = [
  Dream.get "/ui/reports" (fun request ->
    let state = build_query_state request in
    Dream.html (render_full_page state));

  Dream.get "/ui/reports/results" (fun request ->
    let state = build_query_state request in
    Dream.html (render_results_fragment state));

  Dream.get "/ui/reports/filter-panel" (fun request ->
    let state = build_query_state request in
    Dream.html (render_filter_panel state));

  Dream.get "/healthz" (fun _ ->
    Dream.json {|{"status":"ok"}|});
]
