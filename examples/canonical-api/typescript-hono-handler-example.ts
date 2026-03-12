import { Hono } from "hono";
import { desc, eq } from "drizzle-orm";

import { db } from "../db/client";
import { reportRuns } from "../db/schema";

export const reportsRouter = new Hono();

reportsRouter.get("/tenants/:tenantId/reports", async (context) => {
  const tenantId = context.req.param("tenantId");
  const limit = Number.parseInt(context.req.query("limit") ?? "10", 10);

  const rows = await db
    .select({
      reportId: reportRuns.reportId,
      completedAt: reportRuns.completedAt,
      totalEvents: reportRuns.totalEvents,
    })
    .from(reportRuns)
    .where(eq(reportRuns.tenantId, tenantId))
    .orderBy(desc(reportRuns.completedAt))
    .limit(Number.isNaN(limit) ? 10 : Math.min(limit, 50));

  return context.html(
    <section class="report-list">
      <h1>Recent runs for {tenantId}</h1>
      <ul>
        {rows.map((row) => (
          <li>
            <strong>{row.reportId}</strong>
            <span>{row.totalEvents} events</span>
            <time>{row.completedAt.toISOString()}</time>
          </li>
        ))}
      </ul>
    </section>,
  );
});

