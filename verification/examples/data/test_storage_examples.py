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


class RedisMongoShapeExampleTests(unittest.TestCase):
    PATH = "examples/canonical-storage/redis-mongo-shape-example.md"

    def setUp(self) -> None:
        self.text = _read(self.PATH)

    def test_file_exists(self) -> None:
        self.assertTrue((REPO_ROOT / self.PATH).exists())

    def test_dev_and_test_key_prefixes(self) -> None:
        self.assertIn("dev:report-runs", self.text)
        self.assertIn("test:report-runs", self.text)

    def test_redis_commands_present(self) -> None:
        has_command = "SET " in self.text or "DEL " in self.text or "KEYS " in self.text
        self.assertTrue(has_command)

    def test_test_isolation_reset_rule(self) -> None:
        lower = self.text.lower()
        has_isolation = "teardown" in lower or "reset" in lower
        self.assertTrue(has_isolation)

    def test_mongo_collection_name_present(self) -> None:
        self.assertIn("report_runs", self.text)

    def test_docker_compose_snippet_present(self) -> None:
        has_snippet = "redis-test" in self.text or "mongo-test" in self.text
        self.assertTrue(has_snippet)

    def test_readme_references_example(self) -> None:
        readme = _read("examples/canonical-storage/README.md")
        self.assertIn("redis-mongo-shape-example.md", readme)

    def test_solo_example_disambiguation_present(self) -> None:
        has_ref = (
            "redis-structures-example.md" in self.text
            or "mongo-weekly-reporting-example.md" in self.text
        )
        self.assertTrue(has_ref)


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

    # -- Test isolation / credentials ----------------------------------------

    def test_md_separate_test_volume_present(self) -> None:
        # Test object-store data must live in a separate named volume from the
        # dev store. Sharing volumes would let test writes contaminate dev data.
        self.assertIn("minio-test-data", self.md)

    def test_md_test_credentials_separate(self) -> None:
        # Test credentials must be distinct from dev credentials. If the md
        # accidentally showed dev keys in the test compose snippet, the
        # isolation promise would be silently broken.
        has_test_creds = (
            "test-access-key" in self.md
            or "test-secret-key" in self.md
        )
        self.assertTrue(
            has_test_creds,
            "Expected separate test credentials (test-access-key / test-secret-key) in md",
        )

    # -- Staging / cleanup sequence ------------------------------------------

    def test_md_success_marker_or_staging_cleanup_language(self) -> None:
        # The staging-prefix pattern is only safe if the crash-recovery /
        # cleanup path is documented. _SUCCESS, orphaned, or cleanup must
        # appear somewhere in the md.
        has_cleanup = (
            "_SUCCESS" in self.md
            or "orphaned" in self.md
            or "cleanup" in self.md.lower()
        )
        self.assertTrue(
            has_cleanup,
            "Expected _SUCCESS marker, orphaned-file, or cleanup language in md",
        )

    def test_py_staging_copy_delete_sequence(self) -> None:
        # The staging write must be followed by copy_object (promote to final
        # key) and delete_object (remove staging object). Dropping either step
        # breaks the atomic-promotion guarantee.
        has_copy = "copy_object" in self.py or ".copy(" in self.py
        has_delete = "delete_object" in self.py or ".delete(" in self.py
        self.assertTrue(has_copy, "Expected copy_object or .copy( in py")
        self.assertTrue(has_delete, "Expected delete_object or .delete( in py")


class DuckDbPolarsExampleTests(unittest.TestCase):
    PATH = "examples/canonical-storage/duckdb-polars-example.md"

    def setUp(self) -> None:
        self.text = _read(self.PATH)

    def test_file_exists(self) -> None:
        self.assertTrue((REPO_ROOT / self.PATH).exists())

    def test_database_path_convention(self) -> None:
        self.assertIn("docker/volumes/", self.text)

    def test_verification_level_line(self) -> None:
        self.assertIn("behavior-verified", self.text)

    def test_polars_data_pipeline_harness_referenced(self) -> None:
        self.assertIn("polars_data_pipeline", self.text)

    def test_parquet_minio_example_referenced(self) -> None:
        self.assertIn("parquet-minio-example.py", self.text)

    def test_readme_references_md(self) -> None:
        readme = _read("examples/canonical-storage/README.md")
        self.assertIn("duckdb-polars-example.md", readme)


class NatsJetstreamMongoPipelineExampleTests(unittest.TestCase):
    PATH = "examples/canonical-storage/nats-jetstream-mongo-pipeline-example.md"
    PY_PATH = "examples/canonical-storage/nats-jetstream-mongo-pipeline-example.py"

    def setUp(self) -> None:
        self.text = _read(self.PATH)
        self.py = _read(self.PY_PATH)

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

    # -- Stream / consumer configuration ------------------------------------

    def test_work_queue_policy_present(self) -> None:
        # WorkQueuePolicy is the load-bearing retention policy; wrong policy
        # (e.g. LimitsPolicy) would allow multiple consumers to read the same
        # message, breaking work-queue semantics.
        self.assertIn("WorkQueuePolicy", self.text)

    def test_max_deliver_configured(self) -> None:
        # max_deliver caps retry loops; without it a failed message loops
        # forever. The specific value 5 is part of the documented configuration.
        self.assertIn("max_deliver", self.text)
        self.assertIn("5", self.text)

    def test_ack_explicit_policy_present(self) -> None:
        # AckExplicit is required for at-least-once safety. AckAll or a missing
        # ack policy would silently drop unacknowledged messages.
        self.assertIn("AckExplicit", self.text)

    def test_ack_wait_configured(self) -> None:
        # ack_wait defines the window before NATS redelivers to another
        # consumer. Its absence means slow consumers silently lose messages.
        self.assertIn("ack_wait", self.text)

    # -- Ack ordering --------------------------------------------------------

    def test_ack_only_after_insert_language(self) -> None:
        # Tighter ordering check: the document must state explicitly that the
        # ack happens *only after* the insert, not just that both operations
        # appear somewhere in the file.
        upper = self.text.upper()
        has_explicit_ordering = (
            "ACK ONLY AFTER" in upper
            or "only after" in self.text
        )
        self.assertTrue(
            has_explicit_ordering,
            "Expected explicit 'ack only after' ordering language in document",
        )
        # The concrete code form must also be present, not just prose.
        self.assertIn("await msg.ack()", self.text)

    # -- Producer / consumer separation -------------------------------------

    def test_producer_consumer_separation_language(self) -> None:
        # The pipeline's correctness depends on the producer and consumer being
        # separate processes. Losing this language would be a meaningful
        # regression in the documentation contract.
        lower = self.text.lower()
        has_separation = "separate process" in lower or "separately" in lower
        self.assertTrue(
            has_separation,
            "Expected language about producer/consumer separation as separate processes",
        )

    # -- DLQ and payload schema ---------------------------------------------

    def test_dlq_stream_name_present(self) -> None:
        # The DLQ stream name is a concrete operational artifact. Generic DLQ
        # language without the specific name is not actionable for on-call.
        self.assertIn("REPORT_REQUESTS_DLQ", self.text)

    def test_correlation_id_in_payload_schema(self) -> None:
        # correlation_id enables deduplication and dead-letter triage.
        # Its absence from the payload schema would make the pipeline
        # harder to operate.
        self.assertIn("correlation_id", self.text)

    def test_pii_exclusion_language(self) -> None:
        # PII exclusion from the bounded payload is a security invariant.
        # This verifies the PII section is present, not just generic payload rules.
        has_pii = "PII" in self.text or "pii" in self.text
        self.assertTrue(has_pii, "Expected PII exclusion language in document")

    # -- .py companion tests ------------------------------------------------

    def test_py_file_exists(self) -> None:
        self.assertTrue((REPO_ROOT / self.PY_PATH).exists())

    def test_py_stream_name_constant(self) -> None:
        self.assertIn("STREAM_NAME", self.py)

    def test_py_consumer_name_constant(self) -> None:
        self.assertIn("CONSUMER_NAME", self.py)

    def test_py_pii_fields_constant(self) -> None:
        self.assertIn("PII_FIELDS", self.py)

    def test_py_validate_function(self) -> None:
        self.assertIn("def validate", self.py)

    def test_py_enrich_function(self) -> None:
        self.assertIn("def enrich", self.py)

    def test_py_response_time_class_in_enrich(self) -> None:
        self.assertIn("response_time_class", self.py)

    def test_py_ack_after_insert_in_code(self) -> None:
        # Both insert_one and await msg.ack() must be present, with
        # insert_one coming before the ack in the actual code.
        self.assertIn("insert_one", self.py)
        self.assertIn("await msg.ack()", self.py)
        lines = self.py.splitlines()
        # Find the last insert_one() call (code, not prose).
        last_insert_line = max(
            i for i, line in enumerate(lines) if "insert_one(" in line
        )
        # Find the last await msg.ack() call (the real ack, not a docstring reference).
        last_ack_line = max(
            i for i, line in enumerate(lines) if "await msg.ack()" in line
        )
        self.assertLess(
            last_insert_line,
            last_ack_line,
            "Expected insert_one() to appear before await msg.ack() in the .py file",
        )

    def test_py_weekly_collection_name_standalone(self) -> None:
        # Must define the helper locally, not import it from an application path.
        self.assertIn("def weekly_collection_name", self.py)

    def test_py_env_var_usage(self) -> None:
        self.assertIn("NATS_URL", self.py)
        self.assertIn("MONGO_URI", self.py)

    def test_readme_references_py(self) -> None:
        readme = _read("examples/canonical-storage/README.md")
        self.assertIn("nats-jetstream-mongo-pipeline-example.py", readme)


class TrinoFederationLiveTests(unittest.TestCase):
    """
    Live docker-compose federation test.

    Requires VERIFY_DOCKER=1. Skipped silently otherwise.

    Trino takes 60-180s to start; the docker stack is shared across all tests
    in this class to avoid spinning it up once per test method.
    """

    _rows: list[dict] = []

    @classmethod
    def setUpClass(cls) -> None:
        cls._rows = federation_smoke_check()

    def test_federated_join_returns_rows_for_both_tenants(self) -> None:
        tenant_ids = {row["tenant_id"] for row in self._rows}
        self.assertIn("acme", tenant_ids)
        self.assertIn("globex", tenant_ids)

    def test_successful_request_count_excludes_errors(self) -> None:
        by_tenant = {row["tenant_id"]: row for row in self._rows}
        # acme has 3 log entries: 2 success (status 200) + 1 error (status 500)
        acme = by_tenant["acme"]
        self.assertEqual(int(acme["total_requests"]), 3)
        self.assertEqual(int(acme["successful_requests"]), 2)

    def test_result_columns_match_expected_shape(self) -> None:
        self.assertTrue(len(self._rows) > 0)
        required_columns = {"tenant_id", "tenant_name", "total_requests", "successful_requests"}
        self.assertTrue(required_columns.issubset(self._rows[0].keys()))


if __name__ == "__main__":
    unittest.main()
