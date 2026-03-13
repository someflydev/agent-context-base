(ns clojure-kit-nextjdbc-hiccup-example.config
  (:require [integrant.core :as ig]))

(defn- env-int [name fallback]
  (Integer/parseInt (or (System/getenv name) fallback)))

(defn system-config []
  {:app/db {:jdbc-url (or (System/getenv "JDBC_URL")
                          "jdbc:h2:mem:kitruntime;DB_CLOSE_DELAY=-1;MODE=PostgreSQL")}
   :app/routes {:db (ig/ref :app/db)}
   :app/server {:handler (ig/ref :app/routes)
                :port (env-int "PORT" "3000")
                :join? false}})
