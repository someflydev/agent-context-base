import 'package:dart_frog/dart_frog.dart';

Map<String, Object> reportPayload({
  required String tenantId,
  required String window,
}) {
  return <String, Object>{
    'service': 'dart-dartfrog',
    'tenant_id': tenantId,
    'window': window,
    'report_id': 'daily-signups',
    'total_events': 42,
    'status': 'ready',
  };
}

Response onRequest(RequestContext context) {
  final tenantId = context.request.uri.pathSegments.last;
  final window = context.request.uri.queryParameters['window'] ?? '24h';

  return Response.json(
    body: reportPayload(tenantId: tenantId, window: window),
  );
}
