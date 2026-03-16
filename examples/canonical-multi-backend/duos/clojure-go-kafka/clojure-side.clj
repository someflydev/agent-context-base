;; This is a seam-focused example.
;; For a full application scaffold, see context/archetypes/multi-backend-service.md.
;;
;; clojure-side.clj — Clojure Kafka producer seam example.
;; On startup: creates a producer, publishes one demo event to
;; "domain.orders.enriched" (partition key: tenant_id), then starts
;; an HTTP health endpoint.
;;
;; Dependencies (deps.edn — provided by the Dockerfile):
;;   fundingcircle/jackdaw {:mvn/version "0.9.12"}
;;   http-kit/http-kit     {:mvn/version "2.7.0"}
;;   cheshire/cheshire     {:mvn/version "5.12.0"}

(ns clojure-side.core
  (:require [jackdaw.client :as jc]
            [cheshire.core :as json]
            [org.httpkit.server :as httpkit])
  (:import [java.time Instant]))

(def kafka-bootstrap (or (System/getenv "KAFKA_BOOTSTRAP_SERVERS") "kafka:9092"))
(def http-port       (Integer/parseInt (or (System/getenv "HTTP_PORT") "8180")))
(def output-topic    "domain.orders.enriched")

;;; Kafka producer config — acks=all + idempotence for strongest durability.
(def producer-config
  {"bootstrap.servers"  kafka-bootstrap
   "acks"               "all"
   "enable.idempotence" "true"
   "retries"            "5"
   "key.serializer"     "org.apache.kafka.common.serialization.StringSerializer"
   "value.serializer"   "org.apache.kafka.common.serialization.StringSerializer"})

;;; Demo event published on startup to prove the seam.
(def demo-event
  {:payload_version 1
   :correlation_id  "req-demo-001"
   :tenant_id       "demo"
   :event_type      "order.risk_scored"
   :entity_id       "ord-001"
   :data            {:risk_score      0.12
                     :risk_tier       "low"
                     :rule_version    "2026-Q1"
                     :triggered_rules ["velocity_check"]}})

;;; producer atom — set at startup so the health handler can report readiness.
(def kafka-producer (atom nil))

(defn publish-event!
  "Publish a single event to the Kafka topic, keyed by tenant_id.
  Blocks until the broker acknowledges delivery."
  [producer topic event]
  (let [event-with-ts (assoc event :published_at (str (Instant/now)))]
    @(jc/produce! producer
                  {:topic-name topic}
                  (str (:tenant_id event))
                  (json/encode event-with-ts))))

(defn health-handler
  "GET /healthz — returns 200 ok if producer is initialised."
  [_req]
  (if @kafka-producer
    {:status  200
     :headers {"Content-Type" "application/json"}
     :body    "{\"status\":\"ok\"}"}
    {:status  503
     :headers {"Content-Type" "application/json"}
     :body    "{\"status\":\"degraded\",\"reason\":\"producer not initialised\"}"}))

(defn -main [& _args]
  (println (str "connecting to Kafka at " kafka-bootstrap))
  (let [producer (jc/producer producer-config)]
    (reset! kafka-producer producer)
    (println (str "publishing demo event to " output-topic))
    (publish-event! producer output-topic demo-event)
    (println "event published — starting HTTP health endpoint")
    (httpkit/run-server health-handler {:port http-port})
    (println (str "healthz listening on :" http-port))
    ;; Block forever; http-kit runs in its own thread pool.
    @(promise)))
