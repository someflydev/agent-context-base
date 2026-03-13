(ns clojure-kit-nextjdbc-hiccup-api-endpoint-example
  (:require [clojure.data.json :as json]
            [next.jdbc :as jdbc]
            [next.jdbc.result-set :as rs]))

(defn report-endpoint [datasource]
  ["/api/reports/:tenant-id"
   {:get
    (fn [{{tenant-id :tenant-id} :path-params}]
      (let [report (jdbc/execute-one!
                    datasource
                    ["select report_id, total_events, status from reports where tenant_id = ?" tenant-id]
                    {:builder-fn rs/as-unqualified-lower-maps})]
        {:status 200
         :headers {"content-type" "application/json; charset=utf-8"}
         :body (json/write-str
                {:service "clojure-kit-nextjdbc-hiccup"
                 :tenant_id tenant-id
                 :report_id (:report_id report)
                 :total_events (:total_events report)
                 :status (:status report)})}))}])
