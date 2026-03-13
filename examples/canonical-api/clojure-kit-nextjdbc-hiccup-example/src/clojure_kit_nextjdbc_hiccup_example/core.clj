(ns clojure-kit-nextjdbc-hiccup-example.core
  (:gen-class)
  (:require [clojure-kit-nextjdbc-hiccup-example.config :as config]
            [clojure-kit-nextjdbc-hiccup-example.routes]
            [integrant.core :as ig]
            [ring.adapter.jetty :as jetty]))

(defmethod ig/init-key :app/server [_ {:keys [handler port join?]}]
  (jetty/run-jetty handler {:port port :join? join?}))

(defmethod ig/halt-key! :app/server [_ server]
  (.stop server))

(defonce ^:private system (atom nil))

(defn stop! []
  (when-let [running @system]
    (ig/halt! running)
    (reset! system nil)))

(defn start! []
  (stop!)
  (reset! system (ig/init (config/system-config))))

(defn -main [& _]
  (start!)
  @(promise))
