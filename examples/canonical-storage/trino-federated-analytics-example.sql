-- Trino Federated Analytics Example
--
-- Joins a transactional PostgreSQL source with a MongoDB event log to
-- produce a weekly summary of report completions per tenant.
--
-- Catalog assumptions:
--   postgresql_prod  -> Trino PostgreSQL connector, host: postgres:5432
--   mongo_events     -> Trino MongoDB connector,   host: mongo:27017
--
-- Both catalogs must be registered in Trino's etc/catalog/ directory
-- before this query runs. Names here are illustrative; substitute the
-- actual catalog names used in your deployment.
--
-- This is an analytics read path. Do NOT route OLTP writes through Trino.

-- -----------------------------------------------------------------------
-- Per-tenant weekly summary
-- -----------------------------------------------------------------------

SELECT
    t.tenant_id,
    t.tenant_name,
    DATE_TRUNC('week', CAST(e.request_at AS TIMESTAMP))    AS week_start,
    COUNT(*)                                               AS total_requests,
    COUNT(*) FILTER (WHERE e.response_status < 400)       AS successful_requests,
    ROUND(AVG(e.response_ms), 0)                          AS avg_response_ms
FROM
    postgresql_prod.public.tenants AS t
    JOIN mongo_events.reporting.request_logs AS e
        ON t.tenant_id = e.tenant_id
WHERE
    e.request_at >= CURRENT_DATE - INTERVAL '8' WEEK
    AND e.response_status IS NOT NULL
GROUP BY
    t.tenant_id,
    t.tenant_name,
    DATE_TRUNC('week', CAST(e.request_at AS TIMESTAMP))
ORDER BY
    week_start DESC,
    total_requests DESC;

-- -----------------------------------------------------------------------
-- Admin rollup: aggregate across all tenants
--
-- Replace the per-tenant join with a grouped rollup when the tenant
-- dimension is not needed.
-- -----------------------------------------------------------------------

SELECT
    DATE_TRUNC('week', CAST(request_at AS TIMESTAMP))     AS week_start,
    COUNT(*)                                              AS total_requests,
    COUNT(*) FILTER (WHERE response_status < 400)        AS successful_requests,
    APPROX_PERCENTILE(response_ms, 0.95)                 AS p95_response_ms
FROM
    mongo_events.reporting.request_logs
WHERE
    request_at >= CURRENT_DATE - INTERVAL '8' WEEK
GROUP BY
    DATE_TRUNC('week', CAST(request_at AS TIMESTAMP))
ORDER BY
    week_start DESC;
