;; Seam example: Clojure Langohr producer → RabbitMQ topic exchange
;; This is a seam-focused example — shows only connection setup, exchange declaration,
;; publish, and a health endpoint. For full application scaffolding, see
;; context/stacks/clojure-kit-nextjdbc-hiccup.md
;;
;; deps.edn:
;;   {:paths ["src"]
;;    :deps {com.novemberain/langohr          {:mvn/version "5.4.0"}
;;           cheshire/cheshire                {:mvn/version "5.13.0"}
;;           ring/ring-core                   {:mvn/version "1.12.0"}
;;           ring/ring-jetty-adapter          {:mvn/version "1.12.0"}}}
;;
;; Environment:
;;   RABBITMQ_HOST  (default: "rabbitmq")
;;   RABBITMQ_USER  (default: "guest")
;;   RABBITMQ_PASS  (default: "guest")
;;   HTTP_PORT      (default: "8180")

(ns clojure-side.core
  (:require [langohr.core       :as rmq]
            [langohr.channel    :as lch]
            [langohr.exchange   :as le]
            [langohr.basic      :as lb]
            [cheshire.core      :as json]
            [ring.adapter.jetty :refer [run-jetty]]
            [ring.util.response :refer [response content-type]])
  (:gen-class))

(defn amqp-connect []
  (let [host (or (System/getenv "RABBITMQ_HOST") "rabbitmq")
        user (or (System/getenv "RABBITMQ_USER") "guest")
        pass (or (System/getenv "RABBITMQ_PASS") "guest")]
    (rmq/connect {:host host :username user :password pass})))

(defn publish-task-event [conn exchange routing-key event]
  ;; Declare exchange idempotently before each publish — safe to call repeatedly
  (let [ch      (lch/open conn)
        payload (json/encode event)]
    (le/declare ch exchange "topic" {:durable true})
    (lb/publish ch exchange routing-key payload
                {:content-type   "application/json"
                 :persistent     true
                 :correlation-id (get event :correlation-id "")})
    (lch/close ch)
    (println (str "published " routing-key
                  " correlation_id=" (:correlation-id event)
                  " entity_id=" (:entity_id event)))))

(defn health-handler [_request]
  (-> (response "ok")
      (content-type "text/plain")))

(defn -main [& _args]
  (let [conn     (amqp-connect)
        exchange "domain-events"
        now      (str (java.time.Instant/now))
        event    {:payload_version 1
                  :correlation_id  "req-demo-001"
                  :published_at    now
                  :routing_key     "domain.tasks.created"
                  :tenant_id       "demo"
                  :entity_id       "task-001"
                  :event_type      "task.enriched"
                  :data            {:priority      "normal"
                                    :category      "billing"
                                    :enriched_at   now
                                    :source_system "clojure-enricher"}}
        port     (Integer/parseInt (or (System/getenv "HTTP_PORT") "8180"))]
    ;; Publish one demo event at startup to demonstrate the seam
    (publish-task-event conn exchange "domain.tasks.created" event)
    ;; Start health endpoint
    (println (str "health endpoint listening on port " port))
    (run-jetty health-handler {:port port :join? true})))
