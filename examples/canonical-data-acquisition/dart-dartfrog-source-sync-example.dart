import 'dart:convert';
import 'dart:io';

import 'package:dart_frog/dart_frog.dart';

const sourceName = 'github-releases';
const adapterVersion = 'github-releases-v1';

class SyncCursor {
  const SyncCursor({
    required this.owner,
    required this.repo,
    this.page = 1,
    this.etag,
  });

  final String owner;
  final String repo;
  final int page;
  final String? etag;

  String get checkpointToken => etag ?? 'page=$page';

  SyncCursor copyWith({
    int? page,
    String? etag,
  }) {
    return SyncCursor(
      owner: owner,
      repo: repo,
      page: page ?? this.page,
      etag: etag ?? this.etag,
    );
  }
}

class FetchResult {
  const FetchResult({
    required this.body,
    required this.fetchedAt,
    required this.statusCode,
    required this.requestUrl,
    required this.checkpointToken,
    required this.nextPage,
  });

  final String body;
  final DateTime fetchedAt;
  final int statusCode;
  final String requestUrl;
  final String checkpointToken;
  final int? nextPage;
}

class RawCapture {
  const RawCapture({
    required this.sourceName,
    required this.owner,
    required this.repo,
    required this.fetchedAt,
    required this.rawPath,
    required this.metadataPath,
    required this.checksum,
    required this.checkpointToken,
    required this.requestUrl,
  });

  final String sourceName;
  final String owner;
  final String repo;
  final String fetchedAt;
  final String rawPath;
  final String metadataPath;
  final String checksum;
  final String checkpointToken;
  final String requestUrl;

  Map<String, Object?> toJson() {
    return <String, Object?>{
      'source_name': sourceName,
      'owner': owner,
      'repo': repo,
      'fetched_at': fetchedAt,
      'raw_path': rawPath,
      'metadata_path': metadataPath,
      'checksum': checksum,
      'checkpoint_token': checkpointToken,
      'request_url': requestUrl,
    };
  }
}

class ReleaseProvenance {
  const ReleaseProvenance({
    required this.sourceName,
    required this.rawPath,
    required this.fetchedAt,
    required this.checksum,
    required this.checkpointToken,
    required this.adapterVersion,
  });

  final String sourceName;
  final String rawPath;
  final String fetchedAt;
  final String checksum;
  final String checkpointToken;
  final String adapterVersion;

  Map<String, Object?> toJson() {
    return <String, Object?>{
      'source_name': sourceName,
      'raw_path': rawPath,
      'fetched_at': fetchedAt,
      'checksum': checksum,
      'checkpoint_token': checkpointToken,
      'adapter_version': adapterVersion,
    };
  }
}

class NormalizedReleaseRecord {
  const NormalizedReleaseRecord({
    required this.canonicalId,
    required this.sourceId,
    required this.owner,
    required this.repo,
    required this.tagName,
    required this.title,
    required this.publishedAt,
    required this.releaseUrl,
    required this.provenance,
  });

  final String canonicalId;
  final int sourceId;
  final String owner;
  final String repo;
  final String tagName;
  final String title;
  final String publishedAt;
  final String releaseUrl;
  final ReleaseProvenance provenance;

  Map<String, Object?> toJson() {
    return <String, Object?>{
      'canonical_id': canonicalId,
      'source_id': sourceId,
      'owner': owner,
      'repo': repo,
      'tag_name': tagName,
      'title': title,
      'published_at': publishedAt,
      'release_url': releaseUrl,
      'provenance': provenance.toJson(),
    };
  }
}

class SyncReceipt {
  const SyncReceipt({
    required this.sourceName,
    required this.rawPath,
    required this.normalizedCount,
    required this.checkpointToken,
    required this.nextPage,
  });

  final String sourceName;
  final String rawPath;
  final int normalizedCount;
  final String checkpointToken;
  final int? nextPage;

  Map<String, Object?> toJson() {
    return <String, Object?>{
      'source_name': sourceName,
      'raw_capture_path': rawPath,
      'normalized_count': normalizedCount,
      'checkpoint_token': checkpointToken,
      'next_page': nextPage,
    };
  }
}

abstract interface class ReleaseSourceClient {
  Future<FetchResult> fetchReleasePage(SyncCursor cursor);
}

class GitHubReleaseAdapter implements ReleaseSourceClient {
  GitHubReleaseAdapter({HttpClient? httpClient})
      : _httpClient = httpClient ?? HttpClient();

  final HttpClient _httpClient;

  @override
  Future<FetchResult> fetchReleasePage(SyncCursor cursor) async {
    final requestUri = Uri.https(
      'api.github.com',
      '/repos/${cursor.owner}/${cursor.repo}/releases',
      <String, String>{
        'per_page': '50',
        'page': '${cursor.page < 1 ? 1 : cursor.page}',
      },
    );

    final request = await _httpClient.getUrl(requestUri);
    request.headers.set('accept', 'application/vnd.github+json');
    request.headers.set('user-agent', 'agent-context-base-canonical-example');
    request.headers.set('x-github-api-version', '2022-11-28');
    if (cursor.etag != null) {
      request.headers.set('if-none-match', cursor.etag!);
    }

    final response = await request.close();
    final body = await utf8.decodeStream(response);
    final etag = response.headers.value('etag');

    return FetchResult(
      body: body,
      fetchedAt: DateTime.now().toUtc(),
      statusCode: response.statusCode,
      requestUrl: requestUri.toString(),
      checkpointToken: etag ?? cursor.checkpointToken,
      nextPage: body.trim().isEmpty ? null : cursor.page + 1,
    );
  }
}

class SourceCheckpointStore {
  final Map<String, SyncCursor> _records = <String, SyncCursor>{};

  SyncCursor? load(String owner, String repo) {
    return _records['$owner/$repo'];
  }

  void save(SyncCursor cursor) {
    _records['${cursor.owner}/${cursor.repo}'] = cursor;
  }
}

class ReleaseRepository {
  final Map<String, NormalizedReleaseRecord> _records =
      <String, NormalizedReleaseRecord>{};

  Future<void> upsert(List<NormalizedReleaseRecord> records) async {
    for (final record in records) {
      _records[record.canonicalId] = record;
    }
  }
}

class FileArchive {
  FileArchive(this.archiveRoot);

  final Directory archiveRoot;

  Future<RawCapture> archiveRawCapture(
    SyncCursor cursor,
    FetchResult fetchResult,
  ) async {
    final fetchStamp = fetchResult.fetchedAt.toIso8601String().replaceAll(':', '');
    final captureDir = Directory(
      '${archiveRoot.path}/$sourceName/${cursor.owner}/${cursor.repo}/$fetchStamp',
    );
    await captureDir.create(recursive: true);

    final rawFile = File('${captureDir.path}/page-${cursor.page}.json');
    final metadataFile = File('${captureDir.path}/page-${cursor.page}.metadata.json');
    await rawFile.writeAsString(fetchResult.body);

    final rawCapture = RawCapture(
      sourceName: sourceName,
      owner: cursor.owner,
      repo: cursor.repo,
      fetchedAt: fetchResult.fetchedAt.toIso8601String(),
      rawPath: rawFile.path,
      metadataPath: metadataFile.path,
      checksum: _checksum(fetchResult.body),
      checkpointToken: fetchResult.checkpointToken,
      requestUrl: fetchResult.requestUrl,
    );
    await metadataFile.writeAsString(
      const JsonEncoder.withIndent('  ').convert(rawCapture.toJson()),
    );
    return rawCapture;
  }

  Future<List<Map<String, dynamic>>> parseArchivedReleasePayload(
    RawCapture rawCapture,
  ) async {
    final decoded = jsonDecode(await File(rawCapture.rawPath).readAsString());
    if (decoded is! List) {
      throw const FormatException('GitHub releases payload must be a JSON list');
    }
    return decoded.whereType<Map<String, dynamic>>().toList();
  }

  String _checksum(String body) {
    var hash = 0xcbf29ce484222325;
    for (final byte in utf8.encode(body)) {
      hash ^= byte;
      hash = (hash * 0x100000001b3) & 0xffffffffffffffff;
    }
    return hash.toRadixString(16).padLeft(16, '0');
  }
}

class GitHubReleaseSyncService {
  GitHubReleaseSyncService({
    required ReleaseSourceClient sourceClient,
    required FileArchive archive,
    required SourceCheckpointStore checkpoints,
    required ReleaseRepository releases,
  })  : _sourceClient = sourceClient,
        _archive = archive,
        _checkpoints = checkpoints,
        _releases = releases;

  final ReleaseSourceClient _sourceClient;
  final FileArchive _archive;
  final SourceCheckpointStore _checkpoints;
  final ReleaseRepository _releases;

  Future<SyncReceipt> syncPage({
    required String owner,
    required String repo,
    required int? requestedPage,
  }) async {
    final storedCursor = _checkpoints.load(owner, repo);
    final cursor = storedCursor?.copyWith(page: requestedPage ?? storedCursor.page) ??
        SyncCursor(owner: owner, repo: repo, page: requestedPage ?? 1);

    final fetchResult = await _sourceClient.fetchReleasePage(cursor);
    final rawCapture = await _archive.archiveRawCapture(cursor, fetchResult);
    final records = await replayFromArchive(rawCapture);

    final nextCursor = fetchResult.nextPage == null
        ? null
        : cursor.copyWith(
            page: fetchResult.nextPage,
            etag: fetchResult.checkpointToken,
          );
    if (nextCursor != null) {
      _checkpoints.save(nextCursor);
    }
    await _releases.upsert(records);

    return SyncReceipt(
      sourceName: rawCapture.sourceName,
      rawPath: rawCapture.rawPath,
      normalizedCount: records.length,
      checkpointToken: rawCapture.checkpointToken,
      nextPage: nextCursor?.page,
    );
  }

  Future<List<NormalizedReleaseRecord>> replayFromArchive(
    RawCapture rawCapture,
  ) async {
    final payload = await _archive.parseArchivedReleasePayload(rawCapture);
    return normalizeReleaseRecords(rawCapture, payload);
  }

  List<NormalizedReleaseRecord> normalizeReleaseRecords(
    RawCapture rawCapture,
    List<Map<String, dynamic>> payload,
  ) {
    final provenance = ReleaseProvenance(
      sourceName: rawCapture.sourceName,
      rawPath: rawCapture.rawPath,
      fetchedAt: rawCapture.fetchedAt,
      checksum: rawCapture.checksum,
      checkpointToken: rawCapture.checkpointToken,
      adapterVersion: adapterVersion,
    );

    final releases = <NormalizedReleaseRecord>[];
    for (final item in payload) {
      if (item['draft'] == true) {
        continue;
      }

      releases.add(
        NormalizedReleaseRecord(
          canonicalId:
              '$sourceName:${rawCapture.owner}/${rawCapture.repo}:${item['id']}',
          sourceId: (item['id'] as num).toInt(),
          owner: rawCapture.owner,
          repo: rawCapture.repo,
          tagName: '${item['tag_name'] ?? ''}',
          title: '${item['name'] ?? item['tag_name'] ?? 'untitled-release'}',
          publishedAt: '${item['published_at'] ?? ''}',
          releaseUrl: '${item['html_url'] ?? ''}',
          provenance: provenance,
        ),
      );
    }

    releases.sort(
      (left, right) => right.publishedAt.compareTo(left.publishedAt),
    );
    return releases;
  }
}

final _service = GitHubReleaseSyncService(
  sourceClient: GitHubReleaseAdapter(),
  archive: FileArchive(Directory.systemTemp.createTempSync('dartfrog-sync-archive')),
  checkpoints: SourceCheckpointStore(),
  releases: ReleaseRepository(),
);

Future<Response> onRequest(RequestContext context) async {
  if (context.request.method != HttpMethod.post) {
    return Response(statusCode: HttpStatus.methodNotAllowed);
  }

  final segments = context.request.uri.pathSegments;
  final owner = segments[segments.length - 2];
  final repo = segments.last;
  final requestedPage =
      int.tryParse(context.request.uri.queryParameters['page'] ?? '');

  final receipt = await _service.syncPage(
    owner: owner,
    repo: repo,
    requestedPage: requestedPage,
  );

  return Response.json(body: receipt.toJson());
}
