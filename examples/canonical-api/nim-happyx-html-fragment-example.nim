import happyx
import jester
import strformat

component ReportSummaryCard:
  @prop tenantId: cstring
  @prop totalEvents: int
  template:
    tDiv(class = "report-summary-card", id = "report-summary-card"):
      tStrong:
        "Tenant " & $tenantId
      tSpan:
        $totalEvents & " events in the last hour"

proc renderReportSummaryCard*(tenantId: string; totalEvents: int): string =
  fmt"""
<section id="report-summary-card" class="report-summary-card" hx-swap-oob="true">
  <strong>Tenant {tenantId}</strong>
  <span>{totalEvents} events in the last hour</span>
</section>
"""

routes:
  get "/fragments/report-summary/@tenantId":
    resp renderReportSummaryCard(@"tenantId", 42)
