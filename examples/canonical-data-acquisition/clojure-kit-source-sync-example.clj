(ns clojure-kit-source-sync-example
  (:require [clojure.data.json :as json]
            [clojure.java.io :as io]
            [clojure.string :as str]
            [hiccup2.core :as h]
            [next.jdbc :as jdbc]
            [next.jdbc.result-set :as rs]))

(def source-name "github-releases")
(def adapter-version "github-releases-v1")

(defprotocol ReleaseSourceAdapter
  (fetch-release-page [this cursor]))

(defn checkpoint-token [{:keys [page etag]}]
  (or etag (str "page=" page)))

(defn find-source-checkpoint [datasource owner repo]
  (jdbc/execute-one!
   datasource
   ["select owner, repo, page, etag, checkpoint_token
     from source_checkpoints
     where source_name = ? and owner = ? and repo = ?"
    source-name
    owner
    repo]
   {:builder-fn rs/as-unqualified-lower-maps}))

(defn archive-raw-capture!
  [archive-root {:keys [owner repo page]} {:keys [body fetched-at request-url checkpoint-token]}]
  (let [capture-stamp (-> fetched-at
                          (str/replace ":" "")
                          (str/replace "T" "-"))
        capture-dir (io/file archive-root source-name owner repo capture-stamp)
        raw-file (io/file capture-dir (format "page-%s.json" page))
        metadata-file (io/file capture-dir (format "page-%s.metadata.json" page))
        checksum (format "%064x" (BigInteger. 1 (.digest (doto (java.security.MessageDigest/getInstance "SHA-256")
                                                           (.update (.getBytes body "UTF-8"))))))
        raw-capture {:source-name source-name
                     :owner owner
                     :repo repo
                     :fetched-at fetched-at
                     :raw-path (.getPath raw-file)
                     :metadata-path (.getPath metadata-file)
                     :sha256 checksum
                     :checkpoint-token checkpoint-token
                     :request-url request-url}]
    (.mkdirs capture-dir)
    (spit raw-file body)
    (spit metadata-file (json/write-str raw-capture))
    raw-capture))

(defn parse-archived-release-payload [raw-capture]
  (let [payload (json/read-str (slurp (:raw-path raw-capture)) :key-fn keyword)]
    (if (vector? payload)
      payload
      (throw (ex-info "GitHub releases payload must be a JSON array" {:raw-path (:raw-path raw-capture)})))))

(defn normalize-release-records [raw-capture payload]
  (->> payload
       (remove :draft)
       (mapv
        (fn [release]
          (let [external-slug (or (:name release) (:tag_name release) "untitled-release")]
            {:canonical-id (format "%s:%s/%s:%s"
                                   source-name
                                   (:owner raw-capture)
                                   (:repo raw-capture)
                                   (:id release))
             :source-id (:id release)
             :owner (:owner raw-capture)
             :repo (:repo raw-capture)
             :tag-name (or (:tag_name release) "")
             :title external-slug
             :published-at (or (:published_at release) "")
             :html-url (or (:html_url release) "")
             :provenance {:source-name (:source-name raw-capture)
                          :raw-path (:raw-path raw-capture)
                          :fetched-at (:fetched-at raw-capture)
                          :sha256 (:sha256 raw-capture)
                          :checkpoint-token (:checkpoint-token raw-capture)
                          :adapter-version adapter-version}})))
       (sort-by :published-at)
       reverse
       vec))

(defn persist-sync-result!
  [datasource {:keys [owner repo page]} {:keys [checkpoint-token]} records]
  (jdbc/execute!
   datasource
   ["insert into source_checkpoints (source_name, owner, repo, page, checkpoint_token)
     values (?, ?, ?, ?, ?)
     on conflict (source_name, owner, repo)
     do update set page = excluded.page, checkpoint_token = excluded.checkpoint_token"
    source-name owner repo (inc page) checkpoint-token])
  (doseq [record records]
    (jdbc/execute!
     datasource
     ["insert into normalized_releases
        (canonical_id, source_id, owner, repo, tag_name, title, published_at, html_url, provenance_json)
       values (?, ?, ?, ?, ?, ?, ?, ?, ?)
       on conflict (canonical_id)
       do update set title = excluded.title, published_at = excluded.published_at, provenance_json = excluded.provenance_json"
      (:canonical-id record)
      (:source-id record)
      (:owner record)
      (:repo record)
      (:tag-name record)
      (:title record)
      (:published-at record)
      (:html-url record)
      (json/write-str (:provenance record))])))

(defn replay-from-archive [raw-capture]
  (->> raw-capture
       parse-archived-release-payload
       (normalize-release-records raw-capture)))

(defn sync-release-page!
  [{:keys [datasource archive-root adapter]} owner repo]
  (let [checkpoint (or (find-source-checkpoint datasource owner repo)
                       {:owner owner :repo repo :page 1 :etag nil :checkpoint-token "page=1"})
        fetch-result (fetch-release-page adapter checkpoint)
        raw-capture (archive-raw-capture! archive-root checkpoint fetch-result)
        records (replay-from-archive raw-capture)]
    (persist-sync-result! datasource checkpoint raw-capture records)
    {:raw-capture raw-capture
     :normalized-count (count records)
     :next-cursor {:owner owner
                   :repo repo
                   :page (inc (:page checkpoint))
                   :etag (:checkpoint-token raw-capture)
                   :checkpoint-token (:checkpoint-token raw-capture)}}))

(defn render-sync-card [{:keys [raw-capture normalized-count next-cursor]}]
  (str
   (h/html
    [:article {:class "source-sync-card" :data-source source-name}
     [:h2 "Source Sync Completed"]
     [:p [:strong "Raw capture: "] (:raw-path raw-capture)]
     [:p [:strong "Normalized records: "] normalized-count]
     [:p [:strong "Checkpoint token: "] (:checkpoint-token raw-capture)]
     [:p [:strong "Resume page: "] (get next-cursor :page)]
     [:p [:strong "Replay safe: "] "parse and normalize can run from archived payloads"]])))

(defn sync-handler [deps]
  ["/admin/source-sync/:owner/:repo"
   {:post
    (fn [{{:keys [owner repo]} :path-params}]
      (let [result (sync-release-page! deps owner repo)]
        {:status 202
         :headers {"content-type" "text/html; charset=utf-8"
                   "x-source-sync-checkpoint" (get-in result [:raw-capture :checkpoint-token])}
         :body (render-sync-card result)}))}])
