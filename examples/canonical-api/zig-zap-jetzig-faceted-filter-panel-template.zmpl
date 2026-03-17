@* zig-zap-jetzig-faceted-filter-panel-template.zmpl
   Split include/exclude filter panel template for Jetzig.
   All data-* attributes required by the Playwright verification contract are present.
   Values are passed from the handler via the data object (see zig-zap-jetzig-faceted-filter-example.zig).
*@

<div data-role="reports-layout" id="reports-layout" class="flex h-screen overflow-hidden">

  <aside id="filter-panel" class="w-72 flex-shrink-0 overflow-y-auto border-r p-4 space-y-4">

    <input type="text" name="query" value="{{query}}" placeholder="Search reports…"
           data-role="search-input" data-search-query="{{query}}"
           hx-get="/ui/reports/results" hx-target="#report-results"
           hx-trigger="keyup changed delay:300ms" hx-include="#report-filters" />

    <div class="rounded bg-slate-50 px-3 py-2 text-xs text-slate-600" data-role="count-discipline">
      Counts reflect the active backend query semantics.
    </div>

    @* ─── Quick excludes strip ─────────────────────────────────────────── *@
    <div class="flex flex-wrap items-center gap-2 border-b border-slate-100 pb-3"
         data-role="quick-excludes-strip">
      <span class="text-xs font-semibold uppercase tracking-wide text-slate-400 self-center">
        Quick excludes
      </span>

      @* status:archived quick exclude *@
      <label data-role="quick-exclude"
             data-quick-exclude-dimension="status"
             data-quick-exclude-value="archived"
             data-active="{{archived_active}}"
             class="flex items-center gap-1 rounded border border-slate-200 px-2 py-1 text-xs text-slate-600 cursor-pointer">
        <input type="checkbox" name="status_out" value="archived"
               class="sr-only" />
        Archived
        <span class="rounded bg-slate-100 px-1 ml-1">{{archived_impact}}</span>
      </label>

      @* status:paused quick exclude *@
      <label data-role="quick-exclude"
             data-quick-exclude-dimension="status"
             data-quick-exclude-value="paused"
             data-active="{{paused_active}}"
             class="flex items-center gap-1 rounded border border-slate-200 px-2 py-1 text-xs text-slate-600 cursor-pointer">
        <input type="checkbox" name="status_out" value="paused"
               class="sr-only" />
        Paused
        <span class="rounded bg-slate-100 px-1 ml-1">{{paused_impact}}</span>
      </label>
    </div>

    @* ─── Team dimension ───────────────────────────────────────────────── *@
    <section data-filter-dimension="team" class="space-y-2">
      <h3 class="text-xs font-semibold uppercase tracking-wide text-slate-500">Team</h3>

      <div data-role="include-options" class="space-y-1">
        <p class="text-xs text-slate-400 uppercase tracking-wide">Include</p>

        <label data-filter-dimension="team"
               data-filter-option="growth"
               data-filter-mode="include"
               data-option-count="{{team_growth_count}}"
               class="flex items-center justify-between rounded border border-slate-200 px-3 py-2 text-sm">
          <span class="flex items-center gap-2">
            <input type="checkbox" name="team_in" value="growth" />
            <span class="font-medium text-slate-800">Growth</span>
          </span>
          <span data-role="option-count" class="rounded bg-slate-100 px-2 py-1 text-slate-600">
            {{team_growth_count}}
          </span>
        </label>

        <label data-filter-dimension="team"
               data-filter-option="platform"
               data-filter-mode="include"
               data-option-count="{{team_platform_count}}"
               class="flex items-center justify-between rounded border border-slate-200 px-3 py-2 text-sm">
          <span class="flex items-center gap-2">
            <input type="checkbox" name="team_in" value="platform" />
            <span class="font-medium text-slate-800">Platform</span>
          </span>
          <span data-role="option-count" class="rounded bg-slate-100 px-2 py-1 text-slate-600">
            {{team_platform_count}}
          </span>
        </label>
      </div>

      <div data-role="exclude-options" class="mt-2 space-y-1">
        <p class="text-xs text-slate-400 uppercase tracking-wide">Exclude</p>

        <label data-filter-dimension="team"
               data-filter-option="growth"
               data-filter-mode="exclude"
               data-option-count="{{team_growth_impact}}"
               class="flex items-center justify-between rounded border border-slate-200 px-3 py-2 text-sm">
          <span class="flex items-center gap-2">
            <input type="checkbox" name="team_out" value="growth" />
            <span class="font-medium text-slate-800">Growth</span>
          </span>
          <span data-role="option-count" class="rounded bg-slate-100 px-2 py-1 text-slate-600">
            {{team_growth_impact}}
          </span>
        </label>

        <label data-filter-dimension="team"
               data-filter-option="platform"
               data-filter-mode="exclude"
               data-option-count="{{team_platform_impact}}"
               class="flex items-center justify-between rounded border border-slate-200 px-3 py-2 text-sm">
          <span class="flex items-center gap-2">
            <input type="checkbox" name="team_out" value="platform" />
            <span class="font-medium text-slate-800">Platform</span>
          </span>
          <span data-role="option-count" class="rounded bg-slate-100 px-2 py-1 text-slate-600">
            {{team_platform_impact}}
          </span>
        </label>
      </div>
    </section>

    @* ─── Status dimension ─────────────────────────────────────────────── *@
    <section data-filter-dimension="status" class="space-y-2">
      <h3 class="text-xs font-semibold uppercase tracking-wide text-slate-500">Status</h3>

      <div data-role="include-options" class="space-y-1">
        <p class="text-xs text-slate-400 uppercase tracking-wide">Include</p>

        @* active — never excluded by quick excludes *@
        <label data-filter-dimension="status"
               data-filter-option="active"
               data-filter-mode="include"
               data-option-count="{{status_active_count}}"
               class="flex items-center justify-between rounded border border-slate-200 px-3 py-2 text-sm">
          <span class="flex items-center gap-2">
            <input type="checkbox" name="status_in" value="active" />
            <span class="font-medium text-slate-800">Active</span>
          </span>
          <span data-role="option-count" class="rounded bg-slate-100 px-2 py-1 text-slate-600">
            {{status_active_count}}
          </span>
        </label>

        @* paused — greyed when status_out contains "paused" *@
        <label data-filter-dimension="status"
               data-filter-option="paused"
               data-filter-mode="include"
               data-option-count="{{status_paused_inc_count}}"
               class="flex items-center justify-between rounded border border-slate-200 px-3 py-2 text-sm">
          <span class="flex items-center gap-2">
            <input type="checkbox" name="status_in" value="paused" />
            <span class="font-medium text-slate-800">Paused</span>
          </span>
          <span data-role="option-count" class="rounded bg-slate-100 px-2 py-1 text-slate-600">
            {{status_paused_inc_count}}
          </span>
        </label>

        @* archived — greyed when status_out contains "archived" *@
        <label data-filter-dimension="status"
               data-filter-option="archived"
               data-filter-mode="include"
               data-option-count="{{status_archived_inc_count}}"
               class="flex items-center justify-between rounded border border-slate-200 px-3 py-2 text-sm">
          <span class="flex items-center gap-2">
            <input type="checkbox" name="status_in" value="archived" />
            <span class="font-medium text-slate-800">Archived</span>
          </span>
          <span data-role="option-count" class="rounded bg-slate-100 px-2 py-1 text-slate-600">
            {{status_archived_inc_count}}
          </span>
        </label>
      </div>

      <div data-role="exclude-options" class="mt-2 space-y-1">
        <p class="text-xs text-slate-400 uppercase tracking-wide">Exclude</p>

        <label data-filter-dimension="status"
               data-filter-option="active"
               data-filter-mode="exclude"
               data-option-count="{{status_active_impact}}"
               class="flex items-center justify-between rounded border border-slate-200 px-3 py-2 text-sm">
          <span class="flex items-center gap-2">
            <input type="checkbox" name="status_out" value="active" />
            <span class="font-medium text-slate-800">Active</span>
          </span>
          <span data-role="option-count" class="rounded bg-slate-100 px-2 py-1 text-slate-600">
            {{status_active_impact}}
          </span>
        </label>

        <label data-filter-dimension="status"
               data-filter-option="paused"
               data-filter-mode="exclude"
               data-option-count="{{paused_impact}}"
               class="flex items-center justify-between rounded border border-slate-200 px-3 py-2 text-sm">
          <span class="flex items-center gap-2">
            <input type="checkbox" name="status_out" value="paused" />
            <span class="font-medium text-slate-800">Paused</span>
          </span>
          <span data-role="option-count" class="rounded bg-slate-100 px-2 py-1 text-slate-600">
            {{paused_impact}}
          </span>
        </label>

        <label data-filter-dimension="status"
               data-filter-option="archived"
               data-filter-mode="exclude"
               data-option-count="{{archived_impact}}"
               class="flex items-center justify-between rounded border border-slate-200 px-3 py-2 text-sm">
          <span class="flex items-center gap-2">
            <input type="checkbox" name="status_out" value="archived" />
            <span class="font-medium text-slate-800">Archived</span>
          </span>
          <span data-role="option-count" class="rounded bg-slate-100 px-2 py-1 text-slate-600">
            {{archived_impact}}
          </span>
        </label>
      </div>
    </section>

    @* ─── Region dimension ─────────────────────────────────────────────── *@
    <section data-filter-dimension="region" class="space-y-2">
      <h3 class="text-xs font-semibold uppercase tracking-wide text-slate-500">Region</h3>

      <div data-role="include-options" class="space-y-1">
        <p class="text-xs text-slate-400 uppercase tracking-wide">Include</p>

        <label data-filter-dimension="region" data-filter-option="us"
               data-filter-mode="include" data-option-count="{{region_us_count}}"
               class="flex items-center justify-between rounded border border-slate-200 px-3 py-2 text-sm">
          <span class="flex items-center gap-2">
            <input type="checkbox" name="region_in" value="us" />
            <span class="font-medium text-slate-800">Us</span>
          </span>
          <span data-role="option-count" class="rounded bg-slate-100 px-2 py-1 text-slate-600">{{region_us_count}}</span>
        </label>

        <label data-filter-dimension="region" data-filter-option="eu"
               data-filter-mode="include" data-option-count="{{region_eu_count}}"
               class="flex items-center justify-between rounded border border-slate-200 px-3 py-2 text-sm">
          <span class="flex items-center gap-2">
            <input type="checkbox" name="region_in" value="eu" />
            <span class="font-medium text-slate-800">Eu</span>
          </span>
          <span data-role="option-count" class="rounded bg-slate-100 px-2 py-1 text-slate-600">{{region_eu_count}}</span>
        </label>

        <label data-filter-dimension="region" data-filter-option="apac"
               data-filter-mode="include" data-option-count="{{region_apac_count}}"
               class="flex items-center justify-between rounded border border-slate-200 px-3 py-2 text-sm">
          <span class="flex items-center gap-2">
            <input type="checkbox" name="region_in" value="apac" />
            <span class="font-medium text-slate-800">Apac</span>
          </span>
          <span data-role="option-count" class="rounded bg-slate-100 px-2 py-1 text-slate-600">{{region_apac_count}}</span>
        </label>
      </div>

      <div data-role="exclude-options" class="mt-2 space-y-1">
        <p class="text-xs text-slate-400 uppercase tracking-wide">Exclude</p>

        <label data-filter-dimension="region" data-filter-option="us"
               data-filter-mode="exclude" data-option-count="{{region_us_impact}}"
               class="flex items-center justify-between rounded border border-slate-200 px-3 py-2 text-sm">
          <span class="flex items-center gap-2">
            <input type="checkbox" name="region_out" value="us" />
            <span class="font-medium text-slate-800">Us</span>
          </span>
          <span data-role="option-count" class="rounded bg-slate-100 px-2 py-1 text-slate-600">{{region_us_impact}}</span>
        </label>

        <label data-filter-dimension="region" data-filter-option="eu"
               data-filter-mode="exclude" data-option-count="{{region_eu_impact}}"
               class="flex items-center justify-between rounded border border-slate-200 px-3 py-2 text-sm">
          <span class="flex items-center gap-2">
            <input type="checkbox" name="region_out" value="eu" />
            <span class="font-medium text-slate-800">Eu</span>
          </span>
          <span data-role="option-count" class="rounded bg-slate-100 px-2 py-1 text-slate-600">{{region_eu_impact}}</span>
        </label>

        <label data-filter-dimension="region" data-filter-option="apac"
               data-filter-mode="exclude" data-option-count="{{region_apac_impact}}"
               class="flex items-center justify-between rounded border border-slate-200 px-3 py-2 text-sm">
          <span class="flex items-center gap-2">
            <input type="checkbox" name="region_out" value="apac" />
            <span class="font-medium text-slate-800">Apac</span>
          </span>
          <span data-role="option-count" class="rounded bg-slate-100 px-2 py-1 text-slate-600">{{region_apac_impact}}</span>
        </label>
      </div>
    </section>

  </aside>

  <main id="report-results-container" class="flex-1 overflow-y-auto p-4">

    <select name="sort" data-role="sort-select" data-sort-order="{{sort}}"
            hx-get="/ui/reports/results" hx-target="#report-results" hx-include="#report-filters">
      <option value="events_desc"
        @if (sort_events_desc_selected) { selected } >Events: high → low</option>
      <option value="events_asc"
        @if (sort_events_asc_selected) { selected } >Events: low → high</option>
      <option value="name_asc"
        @if (sort_name_asc_selected) { selected } >Name: A → Z</option>
    </select>

    <section id="report-results"
             data-search-query="{{query}}"
             data-sort-order="{{sort}}"
             class="space-y-2 mt-3">
      @for (rows) |row| {
        <div class="rounded border border-slate-200 px-4 py-3 text-sm"
             data-report-id="{{row.report_id}}">
          <strong>{{row.report_id}}</strong>
          <span class="text-slate-500">{{row.team}} / {{row.status}} / {{row.region}}</span>
        </div>
      }
    </section>

  </main>

</div>
