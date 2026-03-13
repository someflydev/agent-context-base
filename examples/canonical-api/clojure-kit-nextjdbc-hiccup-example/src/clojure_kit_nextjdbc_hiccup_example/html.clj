(ns clojure-kit-nextjdbc-hiccup-example.html
  (:require [hiccup2.core :as h]))

(defn report-card [tenant-id total-events status]
  (str
   (h/html
    [:section {:id (str "report-card-" tenant-id)
               :class "report-card"
               :hx-swap-oob "true"}
     [:header {:class "report-card__header"} (str "Tenant " tenant-id)]
     [:strong {:class "report-card__value"} total-events]
     [:span {:class "report-card__status"} status]])))
