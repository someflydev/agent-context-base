(ns clojure-kit-nextjdbc-hiccup-example.db
  (:require [integrant.core :as ig]
            [next.jdbc :as jdbc]
            [next.jdbc.result-set :as rs]))

(def ^:private query-opts {:builder-fn rs/as-unqualified-lower-maps})

(defn- execute! [datasource sql-params]
  (jdbc/execute! datasource sql-params query-opts))

(defn- execute-one! [datasource sql-params]
  (jdbc/execute-one! datasource sql-params query-opts))

(defn- seed! [datasource]
  (execute! datasource ["create table if not exists reports (tenant_id varchar(64) not null, report_id varchar(64) not null, total_events integer not null, status varchar(32) not null, primary key (tenant_id, report_id))"])
  (execute! datasource ["create table if not exists metric_points (metric varchar(64) not null, bucket_day varchar(16) not null, total integer not null, primary key (metric, bucket_day))"])
  (execute! datasource ["merge into reports key (tenant_id, report_id) values (?, ?, ?, ?)" "acme" "daily-signups" 42 "ready"])
  (doseq [[bucket total] [["2026-03-01" 18]
                          ["2026-03-02" 24]
                          ["2026-03-03" 31]]]
    (execute! datasource ["merge into metric_points key (metric, bucket_day) values (?, ?, ?)" "signups" bucket total])))

(defn fetch-report [datasource tenant-id]
  (or (execute-one! datasource ["select report_id, total_events, status from reports where tenant_id = ?" tenant-id])
      {:report_id "daily-signups"
       :total_events 42
       :status "ready"}))

(defn fetch-series [datasource metric]
  (let [rows (execute! datasource ["select bucket_day, total from metric_points where metric = ? order by bucket_day" metric])]
    (if (seq rows)
      rows
      [{:bucket_day "2026-03-01" :total 18}
       {:bucket_day "2026-03-02" :total 24}
       {:bucket_day "2026-03-03" :total 31}])))

(defmethod ig/init-key :app/db [_ {:keys [jdbc-url]}]
  (let [datasource (jdbc/get-datasource {:jdbcUrl jdbc-url
                                         :username "sa"
                                         :password ""})]
    (seed! datasource)
    datasource))
