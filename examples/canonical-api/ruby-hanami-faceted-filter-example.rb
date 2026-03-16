# ruby-hanami-faceted-filter-example.rb
#
# Demonstrates the full split include/exclude filter panel pattern with Ruby Hanami.
# HTML is built using Ruby heredoc strings with interpolation. No template file required.
#
# Multi-value params: Array(params[:status_out]) handles both single and array values.
# Hanami parses ?status_out[]=archived&status_out[]=paused into params[:status_out] as an array.

require "hanami/action"
require "hanami/router"

module RubyHanamiFacetedFilterExample

  # ---------------------------------------------------------------------------
  # Dataset
  # ---------------------------------------------------------------------------

  REPORT_ROWS = [
    { report_id: "daily-signups",     team: "growth",   status: "active",   region: "us",   events: 12 },
    { report_id: "trial-conversions", team: "growth",   status: "active",   region: "us",   events: 7  },
    { report_id: "api-latency",       team: "platform", status: "paused",   region: "eu",   events: 5  },
    { report_id: "checkout-failures", team: "growth",   status: "active",   region: "eu",   events: 9  },
    { report_id: "queue-depth",       team: "platform", status: "active",   region: "apac", events: 11 },
    { report_id: "legacy-import",     team: "platform", status: "archived", region: "us",   events: 4  },
  ].freeze

  FACET_OPTIONS = {
    "team"   => ["growth", "platform"],
    "status" => ["active", "paused", "archived"],
    "region" => ["us", "eu", "apac"],
  }.freeze

  QUICK_EXCLUDES = [["status", "archived"], ["status", "paused"]].freeze

  # ---------------------------------------------------------------------------
  # Query state
  # ---------------------------------------------------------------------------

  QueryState = Struct.new(
    :team_in, :team_out,
    :status_in, :status_out,
    :region_in, :region_out,
    keyword_init: true
  )

  module FilterService
    def self.normalize(values)
      Array(values)
        .map { |v| v.to_s.strip.downcase }
        .reject(&:empty?)
        .sort
        .uniq
    end

    def self.build_query_state(params)
      QueryState.new(
        team_in:    normalize(params[:team_in]    || params["team_in"]),
        team_out:   normalize(params[:team_out]   || params["team_out"]),
        status_in:  normalize(params[:status_in]  || params["status_in"]),
        status_out: normalize(params[:status_out] || params["status_out"]),
        region_in:  normalize(params[:region_in]  || params["region_in"]),
        region_out: normalize(params[:region_out] || params["region_out"]),
      )
    end

    def self.fingerprint(state)
      [
        "team_in=#{state.team_in.join(",")}",
        "team_out=#{state.team_out.join(",")}",
        "status_in=#{state.status_in.join(",")}",
        "status_out=#{state.status_out.join(",")}",
        "region_in=#{state.region_in.join(",")}",
        "region_out=#{state.region_out.join(",")}",
      ].join("|")
    end

    def self.matches_dim?(value, includes, excludes)
      (includes.empty? || includes.include?(value)) &&
        (excludes.empty? || !excludes.include?(value))
    end

    def self.filter_rows(state)
      REPORT_ROWS.select do |row|
        matches_dim?(row[:team],   state.team_in,   state.team_out)   &&
        matches_dim?(row[:status], state.status_in, state.status_out) &&
        matches_dim?(row[:region], state.region_in, state.region_out)
      end
    end

    def self.facet_counts(state, dimension)
      options = FACET_OPTIONS[dimension] || []
      counts  = options.map { |o| [o, 0] }.to_h

      REPORT_ROWS.each do |row|
        pass = case dimension
        when "team"
          matches_dim?(row[:status], state.status_in, state.status_out) &&
          matches_dim?(row[:region], state.region_in, state.region_out) &&
          matches_dim?(row[:team],   [],              state.team_out)
        when "status"
          matches_dim?(row[:team],   state.team_in,   state.team_out)   &&
          matches_dim?(row[:region], state.region_in, state.region_out) &&
          matches_dim?(row[:status], [],              state.status_out)
        else
          matches_dim?(row[:team],   state.team_in,   state.team_out)   &&
          matches_dim?(row[:status], state.status_in, state.status_out) &&
          matches_dim?(row[:region], [],              state.region_out)
        end

        if pass
          val = row[dimension.to_sym]
          counts[val] += 1 if counts.key?(val)
        end
      end
      counts
    end

    def self.exclude_impact_counts(state, dimension)
      options = FACET_OPTIONS[dimension] || []
      dim_out = state.public_send(:"#{dimension}_out")

      options.each_with_object({}) do |option, counts|
        other_excludes = dim_out.reject { |v| v == option }
        count = REPORT_ROWS.count do |row|
          val = row[dimension.to_sym]
          other_dims_pass = case dimension
          when "team"
            matches_dim?(row[:status], state.status_in, state.status_out) &&
            matches_dim?(row[:region], state.region_in, state.region_out)
          when "status"
            matches_dim?(row[:team],   state.team_in,   state.team_out)   &&
            matches_dim?(row[:region], state.region_in, state.region_out)
          else
            matches_dim?(row[:team],   state.team_in,   state.team_out)   &&
            matches_dim?(row[:status], state.status_in, state.status_out)
          end
          other_dims_pass &&
          (other_excludes.empty? || !other_excludes.include?(val)) &&
          val == option
        end
        counts[option] = count
      end
    end

    # -------------------------------------------------------------------------
    # HTML rendering
    # -------------------------------------------------------------------------

    def self.render_filter_panel(state)
      quick_strip = render_quick_excludes(state)
      dim_groups  = ["team", "status", "region"].map { |dim| render_dimension_group(state, dim) }.join

      <<~HTML
        <div id="filter-panel" class="space-y-4">
          <div class="rounded bg-slate-50 px-3 py-2 text-xs text-slate-600" data-role="count-discipline">
            Counts reflect the active backend query semantics.
          </div>
          #{quick_strip}
          #{dim_groups}
        </div>
      HTML
    end

    def self.render_quick_excludes(state)
      buttons = QUICK_EXCLUDES.map do |dim, val|
        impact    = exclude_impact_counts(state, dim)
        dim_out   = state.public_send(:"#{dim}_out")
        is_active = dim_out.include?(val)
        active_str = is_active ? "true" : "false"
        checked    = is_active ? " checked" : ""
        cls = if is_active
          "flex items-center gap-1 rounded border border-red-300 bg-red-50 px-2 py-1 text-xs font-medium text-red-700 cursor-pointer"
        else
          "flex items-center gap-1 rounded border border-slate-200 px-2 py-1 text-xs text-slate-600 cursor-pointer"
        end

        <<~HTML
          <label data-role="quick-exclude"
                 data-quick-exclude-dimension="#{dim}"
                 data-quick-exclude-value="#{val}"
                 data-active="#{active_str}"
                 class="#{cls}">
            <input type="checkbox" name="#{dim}_out" value="#{val}"#{checked} class="sr-only" />
            #{val.capitalize}
            <span class="rounded bg-slate-100 px-1 ml-1">#{impact[val] || 0}</span>
          </label>
        HTML
      end.join

      <<~HTML
        <div class="flex flex-wrap items-center gap-2 border-b border-slate-100 pb-3"
             data-role="quick-excludes-strip">
          <span class="text-xs font-semibold uppercase tracking-wide text-slate-400 self-center">Quick excludes</span>
          #{buttons}
        </div>
      HTML
    end

    def self.render_dimension_group(state, dimension)
      inc_counts = facet_counts(state, dimension)
      exc_counts = exclude_impact_counts(state, dimension)
      dim_out    = state.public_send(:"#{dimension}_out")
      dim_in     = state.public_send(:"#{dimension}_in")
      options    = FACET_OPTIONS[dimension] || []

      inc_options = options.map do |option|
        is_excluded  = dim_out.include?(option)
        is_checked   = dim_in.include?(option)
        opt_count    = is_excluded ? 0 : (inc_counts[option] || 0)
        excluded_attr = is_excluded ? ' data-excluded="true"' : ""
        disabled_attr = is_excluded ? " disabled" : ""
        checked_attr  = is_checked  ? " checked"  : ""
        label_extra   = is_excluded ? " opacity-50 cursor-not-allowed" : ""

        <<~HTML
          <label data-filter-dimension="#{dimension}" data-filter-option="#{option}"
                 data-filter-mode="include" data-option-count="#{opt_count}"#{excluded_attr}
                 class="flex items-center justify-between rounded border border-slate-200 px-3 py-2 text-sm#{label_extra}">
            <span class="flex items-center gap-2">
              <input type="checkbox" name="#{dimension}_in" value="#{option}"#{checked_attr}#{disabled_attr} />
              <span class="font-medium text-slate-800">#{option.capitalize}</span>
            </span>
            <span data-role="option-count" class="rounded bg-slate-100 px-2 py-1 text-slate-600">#{opt_count}</span>
          </label>
        HTML
      end.join

      exc_options = options.map do |option|
        is_active    = dim_out.include?(option)
        impact       = exc_counts[option] || 0
        active_attr  = is_active ? ' data-active="true"' : ""
        checked_attr = is_active ? " checked" : ""
        border_cls   = is_active ? "border-red-200 bg-red-50" : "border-slate-200"

        <<~HTML
          <label data-filter-dimension="#{dimension}" data-filter-option="#{option}"
                 data-filter-mode="exclude" data-option-count="#{impact}"#{active_attr}
                 class="flex items-center justify-between rounded border #{border_cls} px-3 py-2 text-sm">
            <span class="flex items-center gap-2">
              <input type="checkbox" name="#{dimension}_out" value="#{option}"#{checked_attr} />
              <span class="font-medium text-slate-800">#{option.capitalize}</span>
            </span>
            <span data-role="option-count" class="rounded bg-slate-100 px-2 py-1 text-slate-600">#{impact}</span>
          </label>
        HTML
      end.join

      <<~HTML
        <section data-filter-dimension="#{dimension}" class="space-y-2">
          <h3 class="text-xs font-semibold uppercase tracking-wide text-slate-500">#{dimension.capitalize}</h3>
          <div data-role="include-options" class="space-y-1">
            <p class="text-xs text-slate-400 uppercase tracking-wide">Include</p>
            #{inc_options}
          </div>
          <div data-role="exclude-options" class="mt-2 space-y-1">
            <p class="text-xs text-slate-400 uppercase tracking-wide">Exclude</p>
            #{exc_options}
          </div>
        </section>
      HTML
    end

    def self.render_results_fragment(state)
      rows  = filter_rows(state)
      n     = rows.length
      fp    = fingerprint(state)
      cards = rows.map { |row|
        <<~HTML
          <div class="rounded border border-slate-200 px-4 py-3 text-sm" data-report-id="#{row[:report_id]}">
            <strong>#{row[:report_id]}</strong>
            <span class="text-slate-500">#{row[:team]} / #{row[:status]} / #{row[:region]}</span>
          </div>
        HTML
      }.join

      <<~HTML
        <div id="result-count" hx-swap-oob="true"
             data-role="result-count" data-result-count="#{n}"
             class="rounded bg-blue-50 px-3 py-1 text-sm font-medium text-blue-700">
          #{n} results
        </div>
        <section id="report-results"
                 data-query-fingerprint="#{fp}"
                 data-result-count="#{n}"
                 class="space-y-2">
          <div data-role="active-filters" class="text-xs text-slate-500">#{fp}</div>
          #{cards}
        </section>
      HTML
    end

    def self.render_full_page(state)
      panel   = render_filter_panel(state)
      results = filter_rows(state)
      n       = results.length
      fp      = fingerprint(state)
      cards   = results.map { |row|
        %(<div class="rounded border border-slate-200 px-4 py-3 text-sm" data-report-id="#{row[:report_id]}"><strong>#{row[:report_id]}</strong></div>)
      }.join("\n")

      <<~HTML
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="UTF-8" />
          <title>Reports</title>
          <script src="https://unpkg.com/htmx.org@1.9.10"></script>
          <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="p-6 font-sans">
          <h1 class="text-xl font-bold mb-4">Reports</h1>
          <form id="report-filters"
                hx-get="/ui/reports/results"
                hx-target="#report-results"
                hx-trigger="change, submit">
            <div class="flex gap-6">
              <aside class="w-64 shrink-0">#{panel}</aside>
              <main class="flex-1">
                <div id="result-count"
                     data-role="result-count"
                     data-result-count="#{n}"
                     class="rounded bg-blue-50 px-3 py-1 text-sm font-medium text-blue-700 mb-3">
                  #{n} results
                </div>
                <section id="report-results"
                         data-query-fingerprint="#{fp}"
                         data-result-count="#{n}"
                         class="space-y-2">
                  #{cards}
                </section>
              </main>
            </div>
          </form>
        </body>
        </html>
      HTML
    end
  end

  # ---------------------------------------------------------------------------
  # Actions
  # ---------------------------------------------------------------------------

  class UiReports < Hanami::Action
    def handle(request, response)
      state = FilterService.build_query_state(request.params)
      response.format = :html
      response.body   = FilterService.render_full_page(state)
    end
  end

  class UiReportsResults < Hanami::Action
    def handle(request, response)
      state = FilterService.build_query_state(request.params)
      response.format = :html
      response.body   = FilterService.render_results_fragment(state)
    end
  end

  class UiReportsFilterPanel < Hanami::Action
    def handle(request, response)
      state = FilterService.build_query_state(request.params)
      response.format = :html
      response.body   = FilterService.render_filter_panel(state)
    end
  end

  class Healthz < Hanami::Action
    def handle(_request, response)
      response.format = :json
      response.body   = '{"status":"ok"}'
    end
  end

  # ---------------------------------------------------------------------------
  # Router
  # ---------------------------------------------------------------------------

  Routes = Hanami::Router.new do
    get "/ui/reports",              to: UiReports.new
    get "/ui/reports/results",      to: UiReportsResults.new
    get "/ui/reports/filter-panel", to: UiReportsFilterPanel.new
    get "/healthz",                 to: Healthz.new
  end

end
