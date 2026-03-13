(ns clojure-kit-nextjdbc-hiccup-example.routes
  (:require [clojure.data.json :as json]
            [clojure-kit-nextjdbc-hiccup-example.db :as db]
            [clojure-kit-nextjdbc-hiccup-example.html :as html]
            [integrant.core :as ig]
            [reitit.ring :as ring]
            [ring.util.response :as response]))

(defn- json-response [payload]
  (-> (response/response (json/write-str payload))
      (response/content-type "application/json; charset=utf-8")))

(defn- html-response [body]
  (-> (response/response body)
      (response/content-type "text/html; charset=utf-8")))

(defn- health-handler [_]
  (json-response {:status "ok"
                  :service "clojure-kit-nextjdbc-hiccup-example"}))

(defn- report-handler [datasource]
  (fn [{{tenant-id :tenant-id} :path-params}]
    (let [{:keys [report_id total_events status]} (db/fetch-report datasource tenant-id)]
      (json-response {:service "clojure-kit-nextjdbc-hiccup-example"
                      :tenant_id tenant-id
                      :report_id report_id
                      :total_events total_events
                      :status status}))))

(defn- fragment-handler [datasource]
  (fn [{{tenant-id :tenant-id} :path-params}]
    (let [{:keys [total_events status]} (db/fetch-report datasource tenant-id)]
      (html-response (html/report-card tenant-id total_events status)))))

(defn- chart-handler [datasource]
  (fn [{{metric :metric} :path-params}]
    (let [points (mapv (fn [{:keys [bucket_day total]}]
                         {:x bucket_day :y total})
                       (db/fetch-series datasource metric))]
      (json-response {:metric metric
                      :series [{:name metric
                                :points points}]}))))

(defn app [datasource]
  (ring/ring-handler
   (ring/router
    [["/healthz" {:get health-handler}]
     ["/api/reports/:tenant-id" {:get (report-handler datasource)}]
     ["/fragments/report-card/:tenant-id" {:get (fragment-handler datasource)}]
     ["/data/chart/:metric" {:get (chart-handler datasource)}]])
   (ring/create-default-handler)))

(defmethod ig/init-key :app/routes [_ {:keys [db]}]
  (app db))
