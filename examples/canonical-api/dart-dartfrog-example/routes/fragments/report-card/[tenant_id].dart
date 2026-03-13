import 'package:dart_frog/dart_frog.dart';

String renderReportCard({
  required String tenantId,
  required int totalEvents,
}) {
  return '''
<section id="report-card-$tenantId" class="report-card" hx-swap-oob="true">
  <header class="report-card__header">Tenant $tenantId</header>
  <strong class="report-card__value">$totalEvents</strong>
  <span class="report-card__status">updated just now</span>
</section>
''';
}

Response onRequest(RequestContext context, String tenantId) {
  return Response(
    body: renderReportCard(tenantId: tenantId, totalEvents: 42),
    headers: const {'content-type': 'text/html; charset=utf-8'},
  );
}
