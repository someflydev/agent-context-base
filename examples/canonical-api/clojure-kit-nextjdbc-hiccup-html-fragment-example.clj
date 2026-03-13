(ns clojure-kit-nextjdbc-hiccup-html-fragment-example
  (:require [hiccup2.core :as h]))

(defn report-card-fragment [tenant-id total-events]
  (str
   (h/html
    [:section {:id (str "report-card-" tenant-id)
               :class "report-card"
               :hx-swap-oob "true"}
     [:strong (str "Tenant " tenant-id)]
     [:span (str total-events " events in the last hour")]])))

(def fragment-route
  ["/fragments/report-card/:tenant-id"
   {:get
    (fn [{{tenant-id :tenant-id} :path-params}]
      {:status 200
       :headers {"content-type" "text/html; charset=utf-8"}
       :body (report-card-fragment tenant-id 42)})}])
