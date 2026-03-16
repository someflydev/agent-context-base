(ns clojure-kit-nextjdbc-hiccup-faceted-filter-example
  "Split include/exclude filter panel example using Hiccup2 + Reitit routes.
   HTML is rendered using hiccup2.core/html with nested Hiccup vectors.

   Multi-value params: (get-in request [:params :status_out]) returns a vector
   when multiple values are present in a Kit/Reitit ring handler.

   data-* attributes in Hiccup: use keyword keys with hyphens, e.g.
   {:data-filter-dimension \"team\" :data-filter-option \"growth\"}"
  (:require [hiccup2.core :as h]
            [clojure.string :as str]))

;; ---------------------------------------------------------------------------
;; Dataset
;; ---------------------------------------------------------------------------

(def report-rows
  [{:report-id "daily-signups"     :team "growth"   :status "active"   :region "us"   :events 12}
   {:report-id "trial-conversions" :team "growth"   :status "active"   :region "us"   :events 7}
   {:report-id "api-latency"       :team "platform" :status "paused"   :region "eu"   :events 5}
   {:report-id "checkout-failures" :team "growth"   :status "active"   :region "eu"   :events 9}
   {:report-id "queue-depth"       :team "platform" :status "active"   :region "apac" :events 11}
   {:report-id "legacy-import"     :team "platform" :status "archived" :region "us"   :events 4}])

(def facet-options
  {"team"   ["growth" "platform"]
   "status" ["active" "paused" "archived"]
   "region" ["us" "eu" "apac"]})

(def quick-excludes
  [["status" "archived"] ["status" "paused"]])

;; ---------------------------------------------------------------------------
;; Query state
;; ---------------------------------------------------------------------------

(defn normalize [values]
  (->> (if (sequential? values) values (if (nil? values) [] [values]))
       (map #(-> % str str/trim str/lower-case))
       (filter #(not (str/blank? %)))
       sort
       distinct
       vec))

(defn build-query-state [params]
  {:team-in    (normalize (get params :team_in    (get params "team_in")))
   :team-out   (normalize (get params :team_out   (get params "team_out")))
   :status-in  (normalize (get params :status_in  (get params "status_in")))
   :status-out (normalize (get params :status_out (get params "status_out")))
   :region-in  (normalize (get params :region_in  (get params "region_in")))
   :region-out (normalize (get params :region_out (get params "region_out")))})

(defn fingerprint [state]
  (str/join "|"
    [(str "team_in="    (str/join "," (:team-in    state)))
     (str "team_out="   (str/join "," (:team-out   state)))
     (str "status_in="  (str/join "," (:status-in  state)))
     (str "status_out=" (str/join "," (:status-out state)))
     (str "region_in="  (str/join "," (:region-in  state)))
     (str "region_out=" (str/join "," (:region-out state)))]))

;; ---------------------------------------------------------------------------
;; Filter helpers
;; ---------------------------------------------------------------------------

(defn- matches-dim? [value includes excludes]
  (and (or (empty? includes) (some #{value} includes))
       (not (and (seq excludes) (some #{value} excludes)))))

(defn filter-rows [state]
  (filter (fn [row]
            (and (matches-dim? (:team   row) (:team-in   state) (:team-out   state))
                 (matches-dim? (:status row) (:status-in state) (:status-out state))
                 (matches-dim? (:region row) (:region-in state) (:region-out state))))
          report-rows))

(defn facet-counts [state dimension]
  (let [options  (get facet-options dimension [])
        zero-map (into {} (map #(vector % 0) options))
        dim-key  (keyword dimension)
        rows
        (case dimension
          "team"
          (filter (fn [r]
                    (and (matches-dim? (:status r) (:status-in state) (:status-out state))
                         (matches-dim? (:region r) (:region-in state) (:region-out state))
                         (matches-dim? (:team   r) []               (:team-out   state))))
                  report-rows)
          "status"
          (filter (fn [r]
                    (and (matches-dim? (:team   r) (:team-in   state) (:team-out   state))
                         (matches-dim? (:region r) (:region-in state) (:region-out state))
                         (matches-dim? (:status r) []               (:status-out state))))
                  report-rows)
          ;; region
          (filter (fn [r]
                    (and (matches-dim? (:team   r) (:team-in   state) (:team-out   state))
                         (matches-dim? (:status r) (:status-in state) (:status-out state))
                         (matches-dim? (:region r) []               (:region-out state))))
                  report-rows))]
    (reduce (fn [acc row]
              (let [val (get row dim-key)]
                (if (contains? acc val) (update acc val inc) acc)))
            zero-map
            rows)))

(defn exclude-impact-counts [state dimension]
  (let [options  (get facet-options dimension [])
        dim-out  (get state (keyword (str dimension "-out")) [])
        dim-key  (keyword dimension)]
    (into {}
      (for [option options]
        (let [other-excludes (remove #(= % option) dim-out)
              count
              (count
               (filter (fn [row]
                         (let [val (get row dim-key)
                               other-pass
                               (case dimension
                                 "team"
                                 (and (matches-dim? (:status row) (:status-in state) (:status-out state))
                                      (matches-dim? (:region row) (:region-in state) (:region-out state)))
                                 "status"
                                 (and (matches-dim? (:team   row) (:team-in   state) (:team-out   state))
                                      (matches-dim? (:region row) (:region-in state) (:region-out state)))
                                 ;; region
                                 (and (matches-dim? (:team   row) (:team-in   state) (:team-out   state))
                                      (matches-dim? (:status row) (:status-in state) (:status-out state))))]
                           (and other-pass
                                (or (empty? other-excludes) (not (some #{val} other-excludes)))
                                (= val option))))
                       report-rows))]
          [option count])))))

;; ---------------------------------------------------------------------------
;; HTML rendering (Hiccup)
;; ---------------------------------------------------------------------------

(defn- quick-exclude-toggle [state dim val]
  (let [impact    (exclude-impact-counts state dim)
        dim-out   (get state (keyword (str dim "-out")) [])
        is-active (some #{val} dim-out)
        active-str (if is-active "true" "false")
        cls (if is-active
              "flex items-center gap-1 rounded border border-red-300 bg-red-50 px-2 py-1 text-xs font-medium text-red-700 cursor-pointer"
              "flex items-center gap-1 rounded border border-slate-200 px-2 py-1 text-xs text-slate-600 cursor-pointer")]
    [:label {:data-role "quick-exclude"
             :data-quick-exclude-dimension dim
             :data-quick-exclude-value val
             :data-active active-str
             :class cls}
     [:input (merge {:type "checkbox" :name (str dim "_out") :value val :class "sr-only"}
                    (when is-active {:checked true}))]
     (str/capitalize val)
     [:span {:class "rounded bg-slate-100 px-1 ml-1"} (get impact val 0)]]))

(defn- include-option [state dimension option inc-counts]
  (let [dim-out    (get state (keyword (str dimension "-out")) [])
        dim-in     (get state (keyword (str dimension "-in"))  [])
        is-excluded (some #{option} dim-out)
        is-checked  (some #{option} dim-in)
        opt-count   (if is-excluded 0 (get inc-counts option 0))
        label-extra (if is-excluded " opacity-50 cursor-not-allowed" "")
        attrs       (cond-> {:data-filter-dimension dimension
                             :data-filter-option option
                             :data-filter-mode "include"
                             :data-option-count (str opt-count)
                             :class (str "flex items-center justify-between rounded border border-slate-200 px-3 py-2 text-sm" label-extra)}
                      is-excluded (assoc :data-excluded "true"))
        input-attrs (cond-> {:type "checkbox" :name (str dimension "_in") :value option}
                      is-checked  (assoc :checked true)
                      is-excluded (assoc :disabled true))]
    [:label attrs
     [:span {:class "flex items-center gap-2"}
      [:input input-attrs]
      [:span {:class "font-medium text-slate-800"} (str/capitalize option)]]
     [:span {:data-role "option-count" :class "rounded bg-slate-100 px-2 py-1 text-slate-600"} opt-count]]))

(defn- exclude-option [state dimension option exc-counts]
  (let [dim-out   (get state (keyword (str dimension "-out")) [])
        is-active (some #{option} dim-out)
        impact    (get exc-counts option 0)
        border-cls (if is-active "border-red-200 bg-red-50" "border-slate-200")
        attrs     (cond-> {:data-filter-dimension dimension
                           :data-filter-option option
                           :data-filter-mode "exclude"
                           :data-option-count (str impact)
                           :class (str "flex items-center justify-between rounded border " border-cls " px-3 py-2 text-sm")}
                    is-active (assoc :data-active "true"))
        input-attrs (cond-> {:type "checkbox" :name (str dimension "_out") :value option}
                      is-active (assoc :checked true))]
    [:label attrs
     [:span {:class "flex items-center gap-2"}
      [:input input-attrs]
      [:span {:class "font-medium text-slate-800"} (str/capitalize option)]]
     [:span {:data-role "option-count" :class "rounded bg-slate-100 px-2 py-1 text-slate-600"} impact]]))

(defn render-filter-panel [state]
  (str
   (h/html
    [:div {:id "filter-panel" :class "space-y-4"}
     [:div {:class "rounded bg-slate-50 px-3 py-2 text-xs text-slate-600"
            :data-role "count-discipline"}
      "Counts reflect the active backend query semantics."]

     ;; Quick excludes strip
     [:div {:class "flex flex-wrap items-center gap-2 border-b border-slate-100 pb-3"
            :data-role "quick-excludes-strip"}
      [:span {:class "text-xs font-semibold uppercase tracking-wide text-slate-400 self-center"}
       "Quick excludes"]
      (for [[dim val] quick-excludes]
        (quick-exclude-toggle state dim val))]

     ;; Per-dimension groups
     (for [dimension ["team" "status" "region"]]
       (let [inc-counts (facet-counts state dimension)
             exc-counts (exclude-impact-counts state dimension)
             options    (get facet-options dimension [])]
         [:section {:data-filter-dimension dimension :class "space-y-2"}
          [:h3 {:class "text-xs font-semibold uppercase tracking-wide text-slate-500"}
           (str/capitalize dimension)]
          [:div {:data-role "include-options" :class "space-y-1"}
           [:p {:class "text-xs text-slate-400 uppercase tracking-wide"} "Include"]
           (for [option options]
             (include-option state dimension option inc-counts))]
          [:div {:data-role "exclude-options" :class "mt-2 space-y-1"}
           [:p {:class "text-xs text-slate-400 uppercase tracking-wide"} "Exclude"]
           (for [option options]
             (exclude-option state dimension option exc-counts))]]))])))

(defn render-results-fragment [state]
  (let [rows (filter-rows state)
        n    (count rows)
        fp   (fingerprint state)]
    (str
     (h/html
      [:div {:id "result-count"
             :hx-swap-oob "true"
             :data-role "result-count"
             :data-result-count (str n)
             :class "rounded bg-blue-50 px-3 py-1 text-sm font-medium text-blue-700"}
       (str n " results")])
     (h/html
      [:section {:id "report-results"
                 :data-query-fingerprint fp
                 :data-result-count (str n)
                 :class "space-y-2"}
       [:div {:data-role "active-filters" :class "text-xs text-slate-500"} fp]
       (for [row rows]
         [:div {:class "rounded border border-slate-200 px-4 py-3 text-sm"
                :data-report-id (:report-id row)}
          [:strong (:report-id row)]
          [:span {:class "text-slate-500 ml-2"}
           (str (:team row) " / " (:status row) " / " (:region row))]])]))))

(defn- render-full-page [state]
  (let [panel (render-filter-panel state)
        rows  (filter-rows state)
        n     (count rows)
        fp    (fingerprint state)]
    (str
     "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"UTF-8\"><title>Reports</title>"
     "<script src=\"https://unpkg.com/htmx.org@1.9.10\"></script>"
     "<script src=\"https://cdn.tailwindcss.com\"></script></head>"
     "<body class=\"p-6 font-sans\">"
     "<h1 class=\"text-xl font-bold mb-4\">Reports</h1>"
     "<form id=\"report-filters\" hx-get=\"/ui/reports/results\" hx-target=\"#report-results\" hx-trigger=\"change, submit\">"
     "<div class=\"flex gap-6\"><aside class=\"w-64 shrink-0\">"
     panel
     "</aside><main class=\"flex-1\">"
     (str (h/html
           [:div {:id "result-count" :data-role "result-count" :data-result-count (str n)
                  :class "rounded bg-blue-50 px-3 py-1 text-sm font-medium text-blue-700 mb-3"}
            (str n " results")]))
     (str (h/html
           [:section {:id "report-results" :data-query-fingerprint fp :data-result-count (str n)
                      :class "space-y-2"}
            (for [row rows]
              [:div {:class "rounded border border-slate-200 px-4 py-3 text-sm"
                     :data-report-id (:report-id row)}
               [:strong (:report-id row)]])]))
     "</main></div></form></body></html>")))

;; ---------------------------------------------------------------------------
;; Routes (Reitit-compatible)
;; ---------------------------------------------------------------------------

(def routes
  [["/ui/reports"
    {:get (fn [request]
            {:status  200
             :headers {"content-type" "text/html; charset=utf-8"}
             :body    (render-full-page (build-query-state (:params request)))})}]

   ["/ui/reports/results"
    {:get (fn [request]
            {:status  200
             :headers {"content-type" "text/html; charset=utf-8"}
             :body    (render-results-fragment (build-query-state (:params request)))})}]

   ["/ui/reports/filter-panel"
    {:get (fn [request]
            {:status  200
             :headers {"content-type" "text/html; charset=utf-8"}
             :body    (render-filter-panel (build-query-state (:params request)))})}]

   ["/healthz"
    {:get (fn [_]
            {:status  200
             :headers {"content-type" "application/json"}
             :body    "{\"status\":\"ok\"}"})}]])
