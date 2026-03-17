defmodule PhoenixFacetedFilterExample do
  @moduledoc """
  phoenix-faceted-filter-example.ex

  Demonstrates the full split include/exclude filter panel pattern with Elixir Phoenix.
  - QueryState with all eight fields (team_in, team_out, status_in, status_out, region_in,
    region_out, query, sort)
  - apply_text_search, sort_rows, filter_rows, facet_counts, exclude_impact_counts
  - render_filter_panel building complete HTML with all data-* attributes
  - render_results_fragment with OOB result-count badge, sort select, independent scroll layout
  - All four endpoints wired in the router

  Multi-value params: Phoenix parses ?status_out[]=archived&status_out[]=paused into
  params["status_out"] as a list automatically. Use Map.get(params, "status_out", []).
  """

  # ---------------------------------------------------------------------------
  # Dataset
  # ---------------------------------------------------------------------------

  @report_rows [
    %{report_id: "daily-signups",     team: "growth",   status: "active",   region: "us",   events: 12},
    %{report_id: "trial-conversions", team: "growth",   status: "active",   region: "us",   events: 7},
    %{report_id: "api-latency",       team: "platform", status: "paused",   region: "eu",   events: 5},
    %{report_id: "checkout-failures", team: "growth",   status: "active",   region: "eu",   events: 9},
    %{report_id: "queue-depth",       team: "platform", status: "active",   region: "apac", events: 11},
    %{report_id: "legacy-import",     team: "platform", status: "archived", region: "us",   events: 4},
  ]

  @facet_options %{
    "team"   => ["growth", "platform"],
    "status" => ["active", "paused", "archived"],
    "region" => ["us", "eu", "apac"],
  }

  @quick_excludes [{"status", "archived"}, {"status", "paused"}]

  # ---------------------------------------------------------------------------
  # Query state
  # ---------------------------------------------------------------------------

  defp normalize(nil), do: []
  defp normalize(values) when is_list(values) do
    values
    |> Enum.map(&(String.trim(String.downcase(to_string(&1)))))
    |> Enum.reject(&(&1 == ""))
    |> Enum.sort()
    |> Enum.uniq()
  end
  defp normalize(value), do: normalize([value])

  defp normalize_query(q) do
    String.trim(String.downcase(q || ""))
  end

  defp normalize_sort(s) when s in ["events_desc", "events_asc", "name_asc"], do: s
  defp normalize_sort(_), do: "events_desc"

  defp build_query_state(params) do
    %{
      team_in:    normalize(Map.get(params, "team_in",    [])),
      team_out:   normalize(Map.get(params, "team_out",   [])),
      status_in:  normalize(Map.get(params, "status_in",  [])),
      status_out: normalize(Map.get(params, "status_out", [])),
      region_in:  normalize(Map.get(params, "region_in",  [])),
      region_out: normalize(Map.get(params, "region_out", [])),
      query:      normalize_query(Map.get(params, "query", "")),
      sort:       normalize_sort(Map.get(params, "sort", "events_desc")),
    }
  end

  defp fingerprint(state) do
    [
      "team_in=#{Enum.join(state.team_in, ",")}",
      "team_out=#{Enum.join(state.team_out, ",")}",
      "status_in=#{Enum.join(state.status_in, ",")}",
      "status_out=#{Enum.join(state.status_out, ",")}",
      "region_in=#{Enum.join(state.region_in, ",")}",
      "region_out=#{Enum.join(state.region_out, "")}",
    ]
    |> Enum.join("|")
    |> Kernel.<>("|query=#{state.query}|sort=#{state.sort}")
  end

  # ---------------------------------------------------------------------------
  # Filter helpers
  # ---------------------------------------------------------------------------

  defp matches_dim?(value, includes, excludes) do
    (Enum.empty?(includes) or value in includes) and
    (Enum.empty?(excludes) or value not in excludes)
  end

  defp apply_text_search(rows, ""), do: rows
  defp apply_text_search(rows, query) do
    Enum.filter(rows, fn row ->
      String.contains?(String.downcase(row.report_id), query)
    end)
  end

  defp sort_rows(rows, sort) do
    case sort do
      "events_asc" ->
        Enum.sort_by(rows, fn row -> {row.events, row.report_id} end, :asc)
      "name_asc" ->
        Enum.sort_by(rows, fn row -> row.report_id end, :asc)
      _ ->
        Enum.sort_by(rows, fn row -> {-row.events, row.report_id} end, :asc)
    end
  end

  defp filter_rows(state) do
    @report_rows
    |> apply_text_search(state.query)
    |> Enum.filter(fn row ->
      matches_dim?(row.team,   state.team_in,   state.team_out)   and
      matches_dim?(row.status, state.status_in, state.status_out) and
      matches_dim?(row.region, state.region_in, state.region_out)
    end)
  end

  defp facet_counts(state, dimension) do
    options  = Map.get(@facet_options, dimension, [])
    zero_map = Map.new(options, &{&1, 0})

    rows =
      @report_rows
      |> apply_text_search(state.query)
      |> (fn base ->
        case dimension do
          "team" ->
            Enum.filter(base, fn row ->
              matches_dim?(row.status, state.status_in, state.status_out) and
              matches_dim?(row.region, state.region_in, state.region_out) and
              matches_dim?(row.team,   [],              state.team_out)
            end)

          "status" ->
            Enum.filter(base, fn row ->
              matches_dim?(row.team,   state.team_in,   state.team_out)   and
              matches_dim?(row.region, state.region_in, state.region_out) and
              matches_dim?(row.status, [],              state.status_out)
            end)

          "region" ->
            Enum.filter(base, fn row ->
              matches_dim?(row.team,   state.team_in,   state.team_out)   and
              matches_dim?(row.status, state.status_in, state.status_out) and
              matches_dim?(row.region, [],              state.region_out)
            end)
        end
      end).()

    Enum.reduce(rows, zero_map, fn row, acc ->
      val = Map.get(row, String.to_atom(dimension))
      if Map.has_key?(acc, val), do: Map.update!(acc, val, &(&1 + 1)), else: acc
    end)
  end

  defp exclude_impact_counts(state, dimension) do
    options = Map.get(@facet_options, dimension, [])
    dim_out = Map.get(state, String.to_atom("#{dimension}_out"), [])
    base    = apply_text_search(@report_rows, state.query)

    Map.new(options, fn option ->
      other_excludes = Enum.reject(dim_out, &(&1 == option))

      count =
        Enum.count(base, fn row ->
          val = Map.get(row, String.to_atom(dimension))
          other_dims_pass =
            case dimension do
              "team" ->
                matches_dim?(row.status, state.status_in, state.status_out) and
                matches_dim?(row.region, state.region_in, state.region_out)
              "status" ->
                matches_dim?(row.team,   state.team_in,   state.team_out) and
                matches_dim?(row.region, state.region_in, state.region_out)
              "region" ->
                matches_dim?(row.team,   state.team_in,   state.team_out) and
                matches_dim?(row.status, state.status_in, state.status_out)
            end

          other_dims_pass and
          (Enum.empty?(other_excludes) or val not in other_excludes) and
          val == option
        end)

      {option, count}
    end)
  end

  # ---------------------------------------------------------------------------
  # HTML rendering
  # ---------------------------------------------------------------------------

  defp render_filter_panel(state) do
    search_input = """
    <input type="text" name="query" value="#{state.query}" placeholder="Search reports…"
           data-role="search-input" data-search-query="#{state.query}"
           hx-get="/ui/reports/results" hx-target="#report-results"
           hx-trigger="keyup changed delay:300ms" hx-include="#report-filters"
           class="w-full rounded border border-slate-300 px-3 py-2 text-sm" />
    """

    quick_strip = render_quick_excludes(state)
    dim_groups  = Enum.map(["team", "status", "region"], &render_dimension_group(state, &1))

    """
    <div id="filter-panel" class="space-y-4">
      <div class="rounded bg-slate-50 px-3 py-2 text-xs text-slate-600" data-role="count-discipline">
        Counts reflect the active backend query semantics.
      </div>
      #{search_input}
      #{quick_strip}
      #{Enum.join(dim_groups, "\n")}
    </div>
    """
  end

  defp render_quick_excludes(state) do
    buttons =
      Enum.map(@quick_excludes, fn {dim, val} ->
        impact   = exclude_impact_counts(state, dim)
        dim_out  = Map.get(state, String.to_atom("#{dim}_out"), [])
        is_active = val in dim_out
        active_str = if is_active, do: "true", else: "false"
        checked    = if is_active, do: " checked", else: ""
        cls =
          if is_active,
            do: "flex items-center gap-1 rounded border border-red-300 bg-red-50 px-2 py-1 text-xs font-medium text-red-700 cursor-pointer",
            else: "flex items-center gap-1 rounded border border-slate-200 px-2 py-1 text-xs text-slate-600 cursor-pointer"

        """
        <label data-role="quick-exclude"
               data-quick-exclude-dimension="#{dim}"
               data-quick-exclude-value="#{val}"
               data-active="#{active_str}"
               class="#{cls}">
          <input type="checkbox" name="#{dim}_out" value="#{val}"#{checked} class="sr-only" />
          #{String.capitalize(val)}
          <span class="rounded bg-slate-100 px-1 ml-1">#{Map.get(impact, val, 0)}</span>
        </label>
        """
      end)

    """
    <div class="flex flex-wrap items-center gap-2 border-b border-slate-100 pb-3"
         data-role="quick-excludes-strip">
      <span class="text-xs font-semibold uppercase tracking-wide text-slate-400 self-center">Quick excludes</span>
      #{Enum.join(buttons, "")}
    </div>
    """
  end

  defp render_dimension_group(state, dimension) do
    inc_counts = facet_counts(state, dimension)
    exc_counts = exclude_impact_counts(state, dimension)
    dim_out    = Map.get(state, String.to_atom("#{dimension}_out"), [])
    dim_in     = Map.get(state, String.to_atom("#{dimension}_in"),  [])
    options    = Map.get(@facet_options, dimension, [])

    inc_options =
      Enum.map(options, fn option ->
        is_excluded  = option in dim_out
        is_checked   = option in dim_in
        opt_count    = if is_excluded, do: 0, else: Map.get(inc_counts, option, 0)
        excluded_attr = if is_excluded, do: ~s| data-excluded="true"|, else: ""
        disabled_attr = if is_excluded, do: " disabled", else: ""
        checked_attr  = if is_checked,  do: " checked",  else: ""
        label_extra   = if is_excluded, do: " opacity-50 cursor-not-allowed", else: ""

        """
        <label data-filter-dimension="#{dimension}" data-filter-option="#{option}"
               data-filter-mode="include" data-option-count="#{opt_count}"#{excluded_attr}
               class="flex items-center justify-between rounded border border-slate-200 px-3 py-2 text-sm#{label_extra}">
          <span class="flex items-center gap-2">
            <input type="checkbox" name="#{dimension}_in" value="#{option}"#{checked_attr}#{disabled_attr} />
            <span class="font-medium text-slate-800">#{String.capitalize(option)}</span>
          </span>
          <span data-role="option-count" class="rounded bg-slate-100 px-2 py-1 text-slate-600">#{opt_count}</span>
        </label>
        """
      end)

    exc_options =
      Enum.map(options, fn option ->
        is_active   = option in dim_out
        impact      = Map.get(exc_counts, option, 0)
        active_attr = if is_active, do: ~s| data-active="true"|, else: ""
        checked_attr = if is_active, do: " checked", else: ""
        border_cls   = if is_active, do: "border-red-200 bg-red-50", else: "border-slate-200"

        """
        <label data-filter-dimension="#{dimension}" data-filter-option="#{option}"
               data-filter-mode="exclude" data-option-count="#{impact}"#{active_attr}
               class="flex items-center justify-between rounded border #{border_cls} px-3 py-2 text-sm">
          <span class="flex items-center gap-2">
            <input type="checkbox" name="#{dimension}_out" value="#{option}"#{checked_attr} />
            <span class="font-medium text-slate-800">#{String.capitalize(option)}</span>
          </span>
          <span data-role="option-count" class="rounded bg-slate-100 px-2 py-1 text-slate-600">#{impact}</span>
        </label>
        """
      end)

    """
    <section data-filter-dimension="#{dimension}" class="space-y-2">
      <h3 class="text-xs font-semibold uppercase tracking-wide text-slate-500">#{dimension}</h3>
      <div data-role="include-options" class="space-y-1">
        <p class="text-xs text-slate-400 uppercase tracking-wide">Include</p>
        #{Enum.join(inc_options, "")}
      </div>
      <div data-role="exclude-options" class="mt-2 space-y-1">
        <p class="text-xs text-slate-400 uppercase tracking-wide">Exclude</p>
        #{Enum.join(exc_options, "")}
      </div>
    </section>
    """
  end

  defp render_results_fragment(state) do
    rows = state |> filter_rows() |> sort_rows(state.sort)
    n    = length(rows)
    fp   = fingerprint(state)

    sel_desc = if state.sort == "events_desc", do: " selected", else: ""
    sel_asc  = if state.sort == "events_asc",  do: " selected", else: ""
    sel_name = if state.sort == "name_asc",    do: " selected", else: ""

    sort_select = """
    <select name="sort" data-role="sort-select" data-sort-order="#{state.sort}"
            hx-get="/ui/reports/results" hx-target="#report-results"
            hx-include="#report-filters"
            class="rounded border border-slate-200 px-2 py-1 text-sm">
      <option value="events_desc"#{sel_desc}>Events: high &#x2192; low</option>
      <option value="events_asc"#{sel_asc}>Events: low &#x2192; high</option>
      <option value="name_asc"#{sel_name}>Name: A &#x2192; Z</option>
    </select>
    """

    cards =
      Enum.map(rows, fn row ->
        """
        <div class="rounded border border-slate-200 px-4 py-3 text-sm"
             data-report-id="#{row.report_id}">
          <strong>#{row.report_id}</strong>
          <span class="ml-2 text-slate-500">#{row.team} / #{row.status} / #{row.region}</span>
        </div>
        """
      end)

    """
    <div id="result-count" hx-swap-oob="true"
         data-role="result-count" data-result-count="#{n}"
         class="rounded bg-blue-50 px-3 py-1 text-sm font-medium text-blue-700">
      #{n} results
    </div>
    <section id="report-results"
             data-query-fingerprint="#{fp}"
             data-result-count="#{n}"
             data-search-query="#{state.query}"
             data-sort-order="#{state.sort}"
             class="space-y-2">
      <div data-role="active-filters" class="text-xs text-slate-500">#{fp}</div>
      #{sort_select}
      #{Enum.join(cards, "")}
    </section>
    """
  end

  defp render_full_page(state) do
    panel   = render_filter_panel(state)
    results = state |> filter_rows() |> sort_rows(state.sort)
    n       = length(results)
    fp      = fingerprint(state)

    sel_desc = if state.sort == "events_desc", do: " selected", else: ""
    sel_asc  = if state.sort == "events_asc",  do: " selected", else: ""
    sel_name = if state.sort == "name_asc",    do: " selected", else: ""

    """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <title>Reports</title>
      <script src="https://unpkg.com/htmx.org@1.9.10"></script>
      <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="font-sans">
      <h1 class="text-xl font-bold p-4 border-b">Reports</h1>
      <form id="report-filters"
            hx-get="/ui/reports/results"
            hx-target="#report-results"
            hx-trigger="change, submit">
        <div data-role="reports-layout" id="reports-layout" class="flex h-screen overflow-hidden">
          <aside id="filter-panel" class="w-72 flex-shrink-0 overflow-y-auto border-r p-4">
            #{panel}
          </aside>
          <main id="report-results-container" class="flex-1 overflow-y-auto p-4">
            <div id="result-count"
                 data-role="result-count"
                 data-result-count="#{n}"
                 class="rounded bg-blue-50 px-3 py-1 text-sm font-medium text-blue-700 mb-3">
              #{n} results
            </div>
            <select name="sort" data-role="sort-select" data-sort-order="#{state.sort}"
                    hx-get="/ui/reports/results" hx-target="#report-results"
                    hx-include="#report-filters"
                    class="rounded border border-slate-200 px-2 py-1 text-sm mb-3">
              <option value="events_desc"#{sel_desc}>Events: high &#x2192; low</option>
              <option value="events_asc"#{sel_asc}>Events: low &#x2192; high</option>
              <option value="name_asc"#{sel_name}>Name: A &#x2192; Z</option>
            </select>
            <section id="report-results"
                     data-query-fingerprint="#{fp}"
                     data-result-count="#{n}"
                     data-search-query="#{state.query}"
                     data-sort-order="#{state.sort}"
                     class="space-y-2">
              #{Enum.map_join(results, "", fn row ->
                ~s(<div class="rounded border border-slate-200 px-4 py-3 text-sm" data-report-id="#{row.report_id}"><strong>#{row.report_id}</strong></div>)
              end)}
            </section>
          </main>
        </div>
      </form>
    </body>
    </html>
    """
  end

  # ---------------------------------------------------------------------------
  # Router
  # ---------------------------------------------------------------------------

  defmodule Router do
    @moduledoc "Phoenix router for the faceted filter example."
    use Phoenix.Router

    scope "/", PhoenixFacetedFilterExample do
      get "/ui/reports",              Controller, :index
      get "/ui/reports/results",      Controller, :results
      get "/ui/reports/filter-panel", Controller, :filter_panel
      get "/healthz",                 Controller, :healthz
    end
  end

  # ---------------------------------------------------------------------------
  # Controller
  # ---------------------------------------------------------------------------

  defmodule Controller do
    @moduledoc "Phoenix controller for the faceted filter example."
    use Phoenix.Controller

    alias PhoenixFacetedFilterExample, as: FF

    def index(conn, params) do
      state = FF.build_query_state(params)
      html(conn, FF.render_full_page(state))
    end

    def results(conn, params) do
      state = FF.build_query_state(params)
      html(conn, FF.render_results_fragment(state))
    end

    def filter_panel(conn, params) do
      state = FF.build_query_state(params)
      html(conn, FF.render_filter_panel(state))
    end

    def healthz(conn, _params) do
      json(conn, %{status: "ok"})
    end
  end
end
