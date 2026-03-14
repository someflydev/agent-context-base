open Lwt.Syntax
open Caqti_request.Infix

type db = (module Caqti_lwt.CONNECTION)

type sync_cursor = {
  owner : string;
  repo : string;
  page : int;
  etag : string option;
}

type fetch_result = {
  body : string;
  fetched_at : string;
  request_url : string;
  checkpoint_token : string;
  next_page : int option;
}

type raw_capture = {
  source_name : string;
  owner : string;
  repo : string;
  fetched_at : string;
  raw_path : string;
  metadata_path : string;
  checksum : string;
  checkpoint_token : string;
  request_url : string;
}

type release_provenance = {
  source_name : string;
  raw_path : string;
  fetched_at : string;
  checksum : string;
  checkpoint_token : string;
  adapter_version : string;
}

type normalized_release_record = {
  canonical_id : string;
  source_id : int;
  owner : string;
  repo : string;
  tag_name : string;
  title : string;
  published_at : string;
  release_url : string;
  provenance : release_provenance;
}

type sync_receipt = {
  source_name : string;
  raw_capture_path : string;
  normalized_count : int;
  checkpoint_token : string;
  next_page : int option;
}

let source_name = "github-releases"
let adapter_version = "github-releases-v1"

let checkpoint_token cursor =
  match cursor.etag with
  | Some etag -> etag
  | None -> Printf.sprintf "page=%d" cursor.page

let raw_capture_to_yojson raw_capture =
  `Assoc
    [
      ("source_name", `String raw_capture.source_name);
      ("owner", `String raw_capture.owner);
      ("repo", `String raw_capture.repo);
      ("fetched_at", `String raw_capture.fetched_at);
      ("raw_path", `String raw_capture.raw_path);
      ("metadata_path", `String raw_capture.metadata_path);
      ("checksum", `String raw_capture.checksum);
      ("checkpoint_token", `String raw_capture.checkpoint_token);
      ("request_url", `String raw_capture.request_url);
    ]

let provenance_to_yojson provenance =
  `Assoc
    [
      ("source_name", `String provenance.source_name);
      ("raw_path", `String provenance.raw_path);
      ("fetched_at", `String provenance.fetched_at);
      ("checksum", `String provenance.checksum);
      ("checkpoint_token", `String provenance.checkpoint_token);
      ("adapter_version", `String provenance.adapter_version);
    ]

let normalized_release_to_yojson record =
  `Assoc
    [
      ("canonical_id", `String record.canonical_id);
      ("source_id", `Int record.source_id);
      ("owner", `String record.owner);
      ("repo", `String record.repo);
      ("tag_name", `String record.tag_name);
      ("title", `String record.title);
      ("published_at", `String record.published_at);
      ("release_url", `String record.release_url);
      ("provenance", provenance_to_yojson record.provenance);
    ]

let sync_receipt_to_yojson receipt =
  `Assoc
    [
      ("source_name", `String receipt.source_name);
      ("raw_capture_path", `String receipt.raw_capture_path);
      ("normalized_count", `Int receipt.normalized_count);
      ("checkpoint_token", `String receipt.checkpoint_token);
      ( "next_page",
        match receipt.next_page with
        | Some page -> `Int page
        | None -> `Null );
    ]

type source_client = {
  fetch_release_page : sync_cursor -> fetch_result Lwt.t;
}

type archive_store = {
  archive_raw_capture : sync_cursor -> fetch_result -> raw_capture Lwt.t;
  parse_archived_release_payload : raw_capture -> Yojson.Safe.t list Lwt.t;
}

type checkpoint_store = {
  load_cursor : owner:string -> repo:string -> sync_cursor option Lwt.t;
  save_cursor : sync_cursor -> unit Lwt.t;
}

type release_repository = {
  save : normalized_release_record list -> unit Lwt.t;
}

let select_checkpoint =
  Caqti_type.(t3 string string string ->? t2 int string)
    {|
      SELECT page, checkpoint_token
      FROM source_checkpoints
      WHERE source_name = ? AND owner = ? AND repo = ?
    |}

let upsert_checkpoint =
  Caqti_type.(t5 string string string int string ->. unit)
    {|
      INSERT INTO source_checkpoints (source_name, owner, repo, page, checkpoint_token)
      VALUES (?, ?, ?, ?, ?)
      ON CONFLICT (source_name, owner, repo) DO UPDATE SET
        page = excluded.page,
        checkpoint_token = excluded.checkpoint_token
    |}

let upsert_release =
  Caqti_type.(t9 string int string string string string string string string ->. unit)
    {|
      INSERT INTO normalized_releases
        (canonical_id, source_id, owner, repo, tag_name, title, published_at, release_url, provenance_json)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
      ON CONFLICT (canonical_id) DO UPDATE SET
        title = excluded.title,
        published_at = excluded.published_at,
        release_url = excluded.release_url,
        provenance_json = excluded.provenance_json
    |}

let checkpoint_store_of_db (db : db) : checkpoint_store =
  let module Db = (val db : Caqti_lwt.CONNECTION) in
  {
    load_cursor =
      (fun ~owner ~repo ->
        let* row =
          Db.find_opt select_checkpoint (source_name, owner, repo) >>= Caqti_lwt.or_fail
        in
        match row with
        | None -> Lwt.return_none
        | Some (page, token) ->
            Lwt.return_some { owner; repo; page; etag = Some token });
    save_cursor =
      (fun cursor ->
        Db.exec
          upsert_checkpoint
          ( source_name,
            cursor.owner,
            cursor.repo,
            cursor.page,
            checkpoint_token cursor )
        >>= Caqti_lwt.or_fail);
  }

let release_repository_of_db (db : db) : release_repository =
  let module Db = (val db : Caqti_lwt.CONNECTION) in
  {
    save =
      (fun records ->
        Lwt_list.iter_s
          (fun record ->
            Db.exec
              upsert_release
              ( record.canonical_id,
                record.source_id,
                record.owner,
                record.repo,
                record.tag_name,
                record.title,
                record.published_at,
                record.release_url,
                Yojson.Safe.to_string (provenance_to_yojson record.provenance) )
            >>= Caqti_lwt.or_fail)
          records);
  }

let rec mkdir_p path =
  if path = "" || path = Filename.dir_sep then ()
  else if Sys.file_exists path then ()
  else (
    mkdir_p (Filename.dirname path);
    Unix.mkdir path 0o755)

let file_archive ~archive_root : archive_store =
  {
    archive_raw_capture =
      (fun cursor fetch_result ->
        let fetch_stamp = String.map (fun c -> if c = ':' then '-' else c) fetch_result.fetched_at in
        let capture_dir =
          Filename.concat archive_root
            (Printf.sprintf "%s/%s/%s/%s" source_name cursor.owner cursor.repo fetch_stamp)
        in
        let raw_path = Filename.concat capture_dir (Printf.sprintf "page-%d.json" cursor.page) in
        let metadata_path =
          Filename.concat capture_dir (Printf.sprintf "page-%d.metadata.json" cursor.page)
        in
        let checksum = Digest.to_hex (Digest.string fetch_result.body) in
        let raw_capture =
          {
            source_name;
            owner = cursor.owner;
            repo = cursor.repo;
            fetched_at = fetch_result.fetched_at;
            raw_path;
            metadata_path;
            checksum;
            checkpoint_token = fetch_result.checkpoint_token;
            request_url = fetch_result.request_url;
          }
        in
        let () = mkdir_p capture_dir in
        let* () = Lwt_io.with_file ~mode:Lwt_io.output raw_path (fun channel -> Lwt_io.write channel fetch_result.body) in
        let* () =
          Lwt_io.with_file ~mode:Lwt_io.output metadata_path (fun channel ->
              Lwt_io.write channel (Yojson.Safe.pretty_to_string (raw_capture_to_yojson raw_capture)))
        in
        Lwt.return raw_capture);
    parse_archived_release_payload =
      (fun raw_capture ->
        let* raw_text =
          Lwt_io.with_file ~mode:Lwt_io.input raw_capture.raw_path Lwt_io.read
        in
        match Yojson.Safe.from_string raw_text with
        | `List items -> Lwt.return items
        | _ -> Lwt.fail_with "GitHub releases payload must be a JSON list");
  }

let normalize_release_payload raw_capture payload =
  let provenance =
    {
      source_name = raw_capture.source_name;
      raw_path = raw_capture.raw_path;
      fetched_at = raw_capture.fetched_at;
      checksum = raw_capture.checksum;
      checkpoint_token = raw_capture.checkpoint_token;
      adapter_version;
    }
  in
  payload
  |> List.filter_map (fun item ->
         let open Yojson.Safe.Util in
         let draft = item |> member "draft" |> to_bool_option |> Option.value ~default:false in
         if draft then None
         else
           let source_id = item |> member "id" |> to_int in
           let tag_name = item |> member "tag_name" |> to_string_option |> Option.value ~default:"" in
           let title =
             item |> member "name" |> to_string_option |> Option.value ~default:tag_name
           in
           let published_at =
             item |> member "published_at" |> to_string_option |> Option.value ~default:""
           in
           let release_url =
             item |> member "html_url" |> to_string_option |> Option.value ~default:""
           in
           Some
             {
               canonical_id =
                 Printf.sprintf "%s:%s/%s:%d" source_name raw_capture.owner raw_capture.repo source_id;
               source_id;
               owner = raw_capture.owner;
               repo = raw_capture.repo;
               tag_name;
               title;
               published_at;
               release_url;
               provenance;
             })
  |> List.sort (fun left right -> String.compare right.published_at left.published_at)

let replay_from_archive archive_store raw_capture =
  let* payload = archive_store.parse_archived_release_payload raw_capture in
  Lwt.return (normalize_release_payload raw_capture payload)

let sync_release_page source_client checkpoint_store archive_store release_repository owner repo requested_page =
  let* stored_cursor = checkpoint_store.load_cursor ~owner ~repo in
  let cursor =
    match stored_cursor with
    | Some cursor ->
        { cursor with page = Option.value requested_page ~default:cursor.page }
    | None ->
        { owner; repo; page = Option.value requested_page ~default:1; etag = None }
  in
  let* fetch_result = source_client.fetch_release_page cursor in
  let* raw_capture = archive_store.archive_raw_capture cursor fetch_result in
  let* records = replay_from_archive archive_store raw_capture in
  let next_cursor =
    Option.map
      (fun page -> { cursor with page; etag = Some fetch_result.checkpoint_token })
      fetch_result.next_page
  in
  let* () =
    match next_cursor with
    | Some cursor -> checkpoint_store.save_cursor cursor
    | None -> Lwt.return_unit
  in
  let* () = release_repository.save records in
  Lwt.return
    {
      source_name = raw_capture.source_name;
      raw_capture_path = raw_capture.raw_path;
      normalized_count = List.length records;
      checkpoint_token = raw_capture.checkpoint_token;
      next_page = fetch_result.next_page;
    }

let sync_handler source_client checkpoint_store archive_store release_repository request =
  let owner = Dream.param request "owner" in
  let repo = Dream.param request "repo" in
  let requested_page = Dream.query request "page" |> Option.bind int_of_string_opt in
  let* receipt =
    sync_release_page source_client checkpoint_store archive_store release_repository owner repo requested_page
  in
  Dream.json (Yojson.Safe.to_string (sync_receipt_to_yojson receipt))

let last_sync_fragment checkpoint_store request =
  let owner = Dream.param request "owner" in
  let repo = Dream.param request "repo" in
  let* cursor = checkpoint_store.load_cursor ~owner ~repo in
  let checkpoint_text, resume_text =
    match cursor with
    | Some stored_cursor ->
        ( checkpoint_token stored_cursor,
          Printf.sprintf "resume from page %d" stored_cursor.page )
    | None -> ("none yet", "start from page 1")
  in
  let open Tyxml.Html in
  let fragment =
    div
      ~a:[ a_class [ "sync-card" ]; Unsafe.string_attrib "hx-swap-oob" "true" ]
      [
        h2 [ txt (Printf.sprintf "Source sync for %s/%s" owner repo) ];
        p [ txt ("checkpoint: " ^ checkpoint_text) ];
        p [ txt resume_text ];
      ]
  in
  Dream.html (Format.asprintf "%a" (pp_elt ()) fragment)

let routes source_client (db : db) archive_root =
  let checkpoint_store = checkpoint_store_of_db db in
  let archive_store = file_archive ~archive_root in
  let release_repository = release_repository_of_db db in
  [
    Dream.post "/source-sync/:owner/:repo"
      (sync_handler source_client checkpoint_store archive_store release_repository);
    Dream.get "/source-sync/:owner/:repo/last-run"
      (last_sync_fragment checkpoint_store);
  ]
