import 'package:dart_frog/dart_frog.dart';

Response onRequest(RequestContext context) {
  return Response.json(
    body: const <String, Object>{
      'service': 'dart-dartfrog-example',
      'status': 'ok',
      'endpoints': <String>[
        '/healthz',
        '/api/reports/:tenant_id',
        '/fragments/report-card/:tenant_id',
        '/data/chart/:metric',
      ],
    },
  );
}
