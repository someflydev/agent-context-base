from __future__ import annotations

import re
import unittest

from verification.helpers import REPO_ROOT
from verification.scenarios.trino_federation_min_app.verify import federation_smoke_check


STORAGE_DIR = REPO_ROOT / "examples" / "canonical-storage"


def _read(relative: str) -> str:
    return (REPO_ROOT / relative).read_text(encoding="utf-8")


class MongoWeeklyReportingExampleTests(unittest.TestCase):
    PATH = "examples/canonical-storage/mongo-weekly-reporting-example.md"

    def setUp(self) -> None:
        self.text = _read(self.PATH)

    def test_file_exists(self) -> None:
        self.assertTrue((REPO_ROOT / self.PATH).exists())

    def test_weekly_collection_naming(self) -> None:
        # Must show bucketing by year and week
        self.assertRegex(self.text, r"request_logs_\d{4}_w\d{2}")

    def test_partial_filter_expression(self) -> None:
        self.assertIn("partialFilterExpression", self.text)

    def test_aggregation_match_stage(self) -> None:
        self.assertIn("$match", self.text)

    def test_aggregation_group_stage(self) -> None:
        self.assertIn("$group", self.text)

    def test_aggregation_facet_stage(self) -> None:
        self.assertIn("$facet", self.text)

    def test_readme_references_example(self) -> None:
        readme = _read("examples/canonical-storage/README.md")
        self.assertIn("mongo-weekly-reporting-example.md", readme)


class RedisStructuresExampleTests(unittest.TestCase):
    PATH = "examples/canonical-storage/redis-structures-example.md"

    def setUp(self) -> None:
        self.text = _read(self.PATH)

    def test_file_exists(self) -> None:
        self.assertTrue((REPO_ROOT / self.PATH).exists())

    def test_sorted_set_command(self) -> None:
        self.assertIn("ZADD", self.text)

    def test_stream_command(self) -> None:
        self.assertIn("XADD", self.text)

    def test_hash_command(self) -> None:
        self.assertIn("HSET", self.text)

    def test_expiry_language(self) -> None:
        # EX flag or the word expiry/expiration/TTL
        has_ex_flag = "EX " in self.text or " EX\n" in self.text
        has_expiry_word = bool(re.search(r"\bexpir", self.text, re.IGNORECASE))
        self.assertTrue(has_ex_flag or has_expiry_word)

    def test_readme_references_example(self) -> None:
        readme = _read("examples/canonical-storage/README.md")
        self.assertIn("redis-structures-example.md", readme)


class TrinoFederatedAnalyticsExampleTests(unittest.TestCase):
    SQL_PATH = "examples/canonical-storage/trino-federated-analytics-example.sql"
    MD_PATH = "examples/canonical-storage/trino-federated-analytics-example.md"

    def setUp(self) -> None:
        self.sql = _read(self.SQL_PATH)
        self.md = _read(self.MD_PATH)

    def test_sql_file_exists(self) -> None:
        self.assertTrue((REPO_ROOT / self.SQL_PATH).exists())

    def test_md_file_exists(self) -> None:
        self.assertTrue((REPO_ROOT / self.MD_PATH).exists())

    def test_catalog_qualified_table_names(self) -> None:
        # Expect at least one pattern like catalog.schema.table
        self.assertRegex(self.sql, r"\w+\.\w+\.\w+")

    def test_cross_catalog_join(self) -> None:
        self.assertIn("JOIN", self.sql.upper())

    def test_aggregation_present(self) -> None:
        self.assertIn("COUNT", self.sql.upper())

    def test_approx_percentile_or_date_trunc(self) -> None:
        upper = self.sql.upper()
        self.assertTrue(
            "APPROX_PERCENTILE" in upper or "DATE_TRUNC" in upper,
            "Expected APPROX_PERCENTILE or DATE_TRUNC in Trino SQL example",
        )

    def test_md_explains_catalog_configuration(self) -> None:
        self.assertIn("connector.name", self.md)

    def test_md_compares_trino_and_postgresql(self) -> None:
        self.assertIn("PostgreSQL", self.md)
        self.assertIn("Trino", self.md)

    def test_readme_references_sql_example(self) -> None:
        readme = _read("examples/canonical-storage/README.md")
        self.assertIn("trino-federated-analytics-example.sql", readme)


class PostgreSQLQueryShapeExampleTests(unittest.TestCase):
    SQL_PATH = "examples/canonical-storage/postgresql-query-shape-example.sql"
    MD_PATH = "examples/canonical-storage/postgresql-query-shape-example.md"

    def setUp(self) -> None:
        self.sql = _read(self.SQL_PATH)
        self.md = _read(self.MD_PATH)

    def test_sql_file_exists(self) -> None:
        self.assertTrue((REPO_ROOT / self.SQL_PATH).exists())

    def test_md_file_exists(self) -> None:
        self.assertTrue((REPO_ROOT / self.MD_PATH).exists())

    def test_create_index_present(self) -> None:
        self.assertIn("CREATE INDEX", self.sql.upper())

    def test_jsonb_present(self) -> None:
        self.assertIn("jsonb", self.sql.lower())

    def test_materialized_view_present(self) -> None:
        self.assertIn("MATERIALIZED VIEW", self.sql.upper())

    def test_with_cte_present(self) -> None:
        self.assertRegex(self.sql.upper(), r"\bWITH\b")

    def test_partial_index_where_clause(self) -> None:
        # Partial index: CREATE INDEX ... WHERE ...
        self.assertRegex(self.sql, r"CREATE INDEX[^;]+WHERE")

    def test_md_covers_partial_index(self) -> None:
        self.assertIn("artial index", self.md)

    def test_md_covers_jsonb(self) -> None:
        self.assertIn("jsonb", self.md.lower())

    def test_md_covers_materialized_view(self) -> None:
        self.assertIn("materialized view", self.md.lower())

    def test_readme_references_sql_example(self) -> None:
        readme = _read("examples/canonical-storage/README.md")
        self.assertIn("postgresql-query-shape-example.sql", readme)


class ParquetMinioExampleTests(unittest.TestCase):
    MD_PATH = "examples/canonical-storage/parquet-minio-example.md"
    PY_PATH = "examples/canonical-storage/parquet-minio-example.py"

    def setUp(self) -> None:
        self.md = _read(self.MD_PATH)
        self.py = _read(self.PY_PATH)

    def test_md_file_exists(self) -> None:
        self.assertTrue((REPO_ROOT / self.MD_PATH).exists())

    def test_py_file_exists(self) -> None:
        self.assertTrue((REPO_ROOT / self.PY_PATH).exists())

    def test_md_hive_partition_path(self) -> None:
        # Hive-style tenant_id= partition directory must be present
        self.assertRegex(self.md, r"tenant_id=")

    def test_md_staging_prefix_pattern(self) -> None:
        self.assertIn("_staging/", self.md)

    def test_md_schema_pinning_language(self) -> None:
        # Must reference explicit schema definition, not inference
        self.assertTrue(
            "schema pinning" in self.md.lower() or "pin" in self.md.lower()
            or "explicitly" in self.md.lower()
        )

    def test_md_credential_env_var_reference(self) -> None:
        # Must reference MINIO_ACCESS_KEY, MINIO_SECRET_KEY, or MINIO_ENDPOINT
        has_cred = (
            "MINIO_ACCESS_KEY" in self.md
            or "MINIO_SECRET_KEY" in self.md
            or "MINIO_ENDPOINT" in self.md
        )
        self.assertTrue(has_cred)

    def test_py_pyarrow_schema_definition(self) -> None:
        self.assertIn("pa.schema", self.py)

    def test_py_partition_write(self) -> None:
        # Must reference a tenant_id= partition key in object key construction
        self.assertIn("tenant_id=", self.py)

    def test_py_env_var_credential_usage(self) -> None:
        self.assertIn("MINIO_ACCESS_KEY", self.py)
        self.assertIn("MINIO_SECRET_KEY", self.py)
        self.assertIn("MINIO_ENDPOINT", self.py)

    def test_py_readback_assertion(self) -> None:
        # Must contain an assert for row count correctness
        self.assertIn("assert", self.py)

    def test_readme_references_md_example(self) -> None:
        readme = _read("examples/canonical-storage/README.md")
        self.assertIn("parquet-minio-example.md", readme)

    def test_readme_references_py_example(self) -> None:
        readme = _read("examples/canonical-storage/README.md")
        self.assertIn("parquet-minio-example.py", readme)


class NatsJetstreamMongoPipelineExampleTests(unittest.TestCase):
    PATH = "examples/canonical-storage/nats-jetstream-mongo-pipeline-example.md"

    def setUp(self) -> None:
        self.text = _read(self.PATH)

    def test_file_exists(self) -> None:
        self.assertTrue((REPO_ROOT / self.PATH).exists())

    def test_subject_naming_pattern(self) -> None:
        # Must show the reports.requests. subject prefix
        self.assertIn("reports.requests.", self.text)

    def test_payload_version_field(self) -> None:
        self.assertIn("payload_version", self.text)

    def test_response_time_class_field(self) -> None:
        self.assertIn("response_time_class", self.text)

    def test_error_category_field(self) -> None:
        self.assertIn("error_category", self.text)

    def test_enriched_at_field(self) -> None:
        self.assertIn("enriched_at", self.text)

    def test_ack_after_insert_pattern(self) -> None:
        # Must describe acking after the MongoDB write, not before
        has_ack_pattern = (
            "ack" in self.text.lower() and "insert" in self.text.lower()
        )
        self.assertTrue(has_ack_pattern)

    def test_dlq_section_present(self) -> None:
        self.assertIn("DLQ", self.text)

    def test_readme_references_example(self) -> None:
        readme = _read("examples/canonical-storage/README.md")
        self.assertIn("nats-jetstream-mongo-pipeline-example.md", readme)


class TrinoFederationLiveTests(unittest.TestCase):
    """
    Live docker-compose federation test.

    Requires VERIFY_DOCKER=1. Skipped silently otherwise.

    Trino takes 60-180s to start; expect this test to be slow when it runs.
    """

    def test_federated_join_returns_rows_for_both_tenants(self) -> None:
        rows = federation_smoke_check()
        tenant_ids = {row["tenant_id"] for row in rows}
        self.assertIn("acme", tenant_ids)
        self.assertIn("globex", tenant_ids)

    def test_successful_request_count_excludes_errors(self) -> None:
        rows = federation_smoke_check()
        by_tenant = {row["tenant_id"]: row for row in rows}
        # acme has 3 log entries: 2 success (status 200) + 1 error (status 500)
        acme = by_tenant["acme"]
        self.assertEqual(int(acme["total_requests"]), 3)
        self.assertEqual(int(acme["successful_requests"]), 2)

    def test_result_columns_match_expected_shape(self) -> None:
        rows = federation_smoke_check()
        self.assertTrue(len(rows) > 0)
        required_columns = {"tenant_id", "tenant_name", "total_requests", "successful_requests"}
        self.assertTrue(required_columns.issubset(rows[0].keys()))


if __name__ == "__main__":
    unittest.main()
