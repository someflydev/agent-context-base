(ns clojure-kit-nextjdbc-hiccup-data-endpoint-example
  (:require [clojure.data.json :as json]
            [next.jdbc :as jdbc]
            [next.jdbc.result-set :as rs]))

(defn chart-endpoint [datasource]
  ["/data/chart/:metric"
   {:get
    (fn [{{metric :metric} :path-params}]
      (let [rows (jdbc/execute!
                  datasource
                  ["select bucket_day, total from metric_points where metric = ? order by bucket_day" metric]
                  {:builder-fn rs/as-unqualified-lower-maps})
            points (mapv (fn [{:keys [bucket_day total]}]
                           {:x bucket_day :y total})
                         rows)]
        {:status 200
         :headers {"content-type" "application/json; charset=utf-8"}
         :body (json/write-str
                {:metric metric
                 :series [{:name metric
                           :points points}]})}))}])
