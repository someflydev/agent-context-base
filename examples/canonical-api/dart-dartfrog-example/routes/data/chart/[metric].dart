import 'package:dart_frog/dart_frog.dart';

Map<String, Object> chartPayload(String metric) {
  return <String, Object>{
    'metric': metric,
    'series': <Map<String, Object>>[
      <String, Object>{
        'name': metric,
        'points': <Map<String, Object>>[
          <String, Object>{'x': '2026-03-01', 'y': 18},
          <String, Object>{'x': '2026-03-02', 'y': 24},
          <String, Object>{'x': '2026-03-03', 'y': 31},
        ],
      },
    ],
  };
}

Response onRequest(RequestContext context, String metric) {
  return Response.json(body: chartPayload(metric));
}
