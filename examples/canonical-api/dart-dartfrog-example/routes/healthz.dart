import 'package:dart_frog/dart_frog.dart';

Response onRequest(RequestContext context) {
  return Response.json(
    body: const <String, Object>{
      'status': 'ok',
      'service': 'dart-dartfrog-example',
    },
  );
}
