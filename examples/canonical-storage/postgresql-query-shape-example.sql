-- PostgreSQL Query Shape Example
--
-- Demonstrates representative PostgreSQL patterns:
--   - migration-style DDL with explicit index creation
--   - jsonb for bounded, queryable metadata
--   - reporting query with CTE and window function
--   - materialized view with unique index for concurrent refresh
--
-- This is documentation-shaped SQL. It is syntax-plausible but is not
-- run against a live database in the default verification tier.

-- -----------------------------------------------------------------------
-- Schema
-- -----------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS report_runs (
    id              BIGSERIAL    PRIMARY KEY,
    tenant_id       TEXT         NOT NULL,
    report_id       TEXT         NOT NULL,
    status          TEXT         NOT NULL
                                 CHECK (status IN ('queued', 'running', 'ready', 'failed')),
    payload_version SMALLINT     NOT NULL DEFAULT 1,
    row_count       INTEGER,
    response_ms     INTEGER,
    error_code      TEXT,
    metadata        JSONB,
    requested_at    TIMESTAMPTZ  NOT NULL DEFAULT now(),
    finished_at     TIMESTAMPTZ
);

-- Partial index covering the hot reporting query path.
-- Rows in queued, running, or failed state are excluded, keeping the
-- index small relative to total table size.
CREATE INDEX IF NOT EXISTS idx_report_runs_tenant_report
    ON report_runs (tenant_id, report_id, requested_at DESC)
    WHERE status = 'ready';

-- Partial index for error-rate monitoring queries.
CREATE INDEX IF NOT EXISTS idx_report_runs_failed
    ON report_runs (tenant_id, error_code)
    WHERE status = 'failed';

-- Bounded jsonb usage: metadata stores small, queryable extra fields.
-- Do not store large blobs or arrays with unbounded growth here.
-- Index a specific jsonb path when queries filter on it.
CREATE INDEX IF NOT EXISTS idx_report_runs_metadata_source
    ON report_runs ((metadata->>'source'))
    WHERE metadata ? 'source';

-- -----------------------------------------------------------------------
-- Reporting query: weekly success rate per tenant
-- -----------------------------------------------------------------------

WITH weekly_counts AS (
    SELECT
        tenant_id,
        DATE_TRUNC('week', requested_at)                        AS week_start,
        COUNT(*)                                                AS total_runs,
        COUNT(*) FILTER (WHERE status = 'ready')               AS successful_runs,
        AVG(response_ms) FILTER (WHERE status = 'ready')       AS avg_response_ms,
        PERCENTILE_CONT(0.95) WITHIN GROUP (
            ORDER BY response_ms
        ) FILTER (WHERE status = 'ready')                      AS p95_response_ms
    FROM report_runs
    WHERE requested_at >= CURRENT_DATE - INTERVAL '8 weeks'
    GROUP BY tenant_id, DATE_TRUNC('week', requested_at)
),
ranked AS (
    SELECT
        *,
        ROUND(
            successful_runs::NUMERIC / NULLIF(total_runs, 0) * 100,
            1
        )                                                       AS success_pct,
        ROW_NUMBER() OVER (
            PARTITION BY week_start ORDER BY successful_runs DESC
        )                                                       AS rank_this_week
    FROM weekly_counts
)
SELECT
    tenant_id,
    week_start,
    total_runs,
    successful_runs,
    success_pct,
    ROUND(avg_response_ms::NUMERIC, 0)   AS avg_response_ms,
    ROUND(p95_response_ms::NUMERIC, 0)   AS p95_response_ms,
    rank_this_week
FROM ranked
ORDER BY week_start DESC, rank_this_week;

-- -----------------------------------------------------------------------
-- Materialized view for pre-aggregated reporting
--
-- Use when the reporting query runs frequently against a large table.
-- REFRESH MATERIALIZED VIEW CONCURRENTLY requires a UNIQUE INDEX on the
-- view and allows reads during the refresh.
-- Trigger refresh from a scheduled job or a post-write hook, not on
-- every request.
-- -----------------------------------------------------------------------

CREATE MATERIALIZED VIEW IF NOT EXISTS report_runs_weekly_summary AS
SELECT
    tenant_id,
    DATE_TRUNC('week', requested_at)                        AS week_start,
    COUNT(*)                                                AS total_runs,
    COUNT(*) FILTER (WHERE status = 'ready')               AS successful_runs,
    ROUND(
        AVG(response_ms) FILTER (WHERE status = 'ready')::NUMERIC,
        0
    )                                                       AS avg_response_ms
FROM report_runs
GROUP BY tenant_id, DATE_TRUNC('week', requested_at)
WITH DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_report_runs_weekly_summary_pk
    ON report_runs_weekly_summary (tenant_id, week_start);

-- Refresh command (run on schedule):
-- REFRESH MATERIALIZED VIEW CONCURRENTLY report_runs_weekly_summary;
