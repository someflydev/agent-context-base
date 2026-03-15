"""
NATS JetStream + MongoDB pipeline example.

Verification level: structure-verified
No live NATS or MongoDB dependency is required to import this module.
The produce(), consume_once(), and run_consumer_loop() functions can be run
against a real NATS JetStream server and MongoDB instance by setting the
required environment variables.

Follow-on: add a docker-compose harness under
verification/scenarios/nats_mongo_min_app/ to raise this to smoke-verified.

Required environment variables:
    NATS_URL              — e.g. nats://localhost:4222
    MONGO_URI             — e.g. mongodb://localhost:27017
    MONGO_DB              — database name, e.g. test-reporting
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from datetime import date, datetime, timezone

import nats
import nats.errors
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# ---------------------------------------------------------------------------
# Logger
# ---------------------------------------------------------------------------

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Stream / consumer constants
# ---------------------------------------------------------------------------

STREAM_NAME = "REPORT_REQUESTS"
SUBJECT_PREFIX = "reports.requests"
CONSUMER_NAME = "report-enricher"
ACK_WAIT_SECONDS = 30
MAX_DELIVER = 5
DLQ_STREAM = "REPORT_REQUESTS_DLQ"
SUPPORTED_PAYLOAD_VERSIONS = {1}
PII_FIELDS = frozenset({"raw_ip", "email", "user_name"})

# ---------------------------------------------------------------------------
# Sample payload — one well-formed message from the acme tenant
# ---------------------------------------------------------------------------

SAMPLE_PAYLOAD: dict = {
    "payload_version": 1,
    "tenant_id": "acme",
    "report_id": "daily-signups",
    "correlation_id": "req-abc-123",
    "published_at": "2026-03-10T14:22:00Z",
    "request_method": "POST",
    "request_path": "/api/reports",
    "response_status": 200,
    "response_time_ms": 142,
    "source_ip_hash": "sha256:abcd1234ef567890",
}

# ---------------------------------------------------------------------------
# weekly_collection_name — standalone copy
#
# The authoritative version lives in:
#   examples/canonical-storage/mongo-weekly-reporting-example.md
# This is a standalone copy for use without an application context.
# It accepts a published_at ISO 8601 string rather than a date object so it
# can be called directly on enriched document fields.
# ---------------------------------------------------------------------------


def weekly_collection_name(published_at: str, prefix: str = "request_logs") -> str:
    """Return the weekly-bucketed MongoDB collection name for a published_at timestamp.

    Standalone copy for use without an application context. The authoritative
    version lives in examples/canonical-storage/mongo-weekly-reporting-example.md.

    Args:
        published_at: ISO 8601 UTC timestamp string (from the enriched document).
        prefix: collection name prefix. Defaults to 'request_logs'.

    Returns:
        Collection name in the form '<prefix>_<year>_w<week>', e.g.
        'request_logs_2026_w12'.
    """
    dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
    d = dt.date()
    year, week, _ = d.isocalendar()
    return f"{prefix}_{year}_w{week:02d}"


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate(payload: dict) -> None:
    """Raise ValueError if payload_version is not in SUPPORTED_PAYLOAD_VERSIONS.

    Args:
        payload: the decoded message payload dict.

    Raises:
        ValueError: on unknown payload_version.
    """
    version = payload.get("payload_version")
    if version not in SUPPORTED_PAYLOAD_VERSIONS:
        raise ValueError(
            f"Unknown payload_version: {version!r}. "
            f"Supported versions: {sorted(SUPPORTED_PAYLOAD_VERSIONS)}"
        )


# ---------------------------------------------------------------------------
# Cleaning
# ---------------------------------------------------------------------------


def clean(payload: dict) -> dict:
    """Return a copy of payload with all PII_FIELDS removed.

    Args:
        payload: the decoded message payload dict.

    Returns:
        New dict with PII fields stripped.
    """
    return {k: v for k, v in payload.items() if k not in PII_FIELDS}


# ---------------------------------------------------------------------------
# Enrichment
# ---------------------------------------------------------------------------


def enrich(payload: dict) -> dict:
    """Compute derived fields and return the enriched document.

    Adds response_time_class, error_category, and enriched_at to a copy of
    payload. Does not mutate the original.

    Thresholds (matching the .md spec):
        response_time_class:
            "fast"    — response_time_ms < 200
            "slow"    — 200 <= response_time_ms <= 2000
            "timeout" — response_time_ms > 2000
        error_category:
            "none"         — status < 400 or status == 0
            "client_error" — 400 <= status < 500
            "server_error" — status >= 500

    Args:
        payload: cleaned payload dict (PII already removed).

    Returns:
        New dict with original fields plus response_time_class, error_category,
        and enriched_at.
    """
    rt_ms = payload.get("response_time_ms") or 0
    status = payload.get("response_status", 0)

    if rt_ms < 200:
        response_time_class = "fast"
    elif rt_ms <= 2000:
        response_time_class = "slow"
    else:
        response_time_class = "timeout"

    if status == 0:
        error_category = "none"
    elif 400 <= status < 500:
        error_category = "client_error"
    elif status >= 500:
        error_category = "server_error"
    else:
        error_category = "none"

    return {
        **payload,
        "response_time_class": response_time_class,
        "error_category": error_category,
        "enriched_at": datetime.now(timezone.utc).isoformat(),
    }


# ---------------------------------------------------------------------------
# Subject helper
# ---------------------------------------------------------------------------


def _make_subject(payload: dict) -> str:
    """Return the full NATS subject string for a payload.

    Subject format: reports.requests.<tenant_id>.<report_id>
    Examples:
        reports.requests.acme.daily-signups
        reports.requests.globex.weekly-revenue
    """
    return f"{SUBJECT_PREFIX}.{payload['tenant_id']}.{payload['report_id']}"


# ---------------------------------------------------------------------------
# Producer
# ---------------------------------------------------------------------------


async def produce(nc, payload: dict) -> None:
    """Publish one bounded payload to the REPORT_REQUESTS JetStream stream.

    Args:
        nc: connected nats.aio.client.Client
        payload: validated, bounded payload dict (no PII, no raw bodies)

    The producer does not wait for consumer confirmation. Durability is
    provided by JetStream: once the broker acks the publish, the message
    is retained regardless of consumer availability.
    """
    js = nc.jetstream()
    subject = _make_subject(payload)
    await js.publish(subject, json.dumps(payload).encode())
    logger.info("Published to %s (correlation_id=%s)", subject, payload.get("correlation_id"))


# ---------------------------------------------------------------------------
# Stream setup
# ---------------------------------------------------------------------------


async def _ensure_stream(js) -> None:
    """Create REPORT_REQUESTS stream if it does not already exist.

    Uses subjects=['reports.requests.>'] and retention='workqueue'.
    Silently ignores the error if the stream already exists.
    """
    try:
        await js.add_stream(
            name=STREAM_NAME,
            subjects=[f"{SUBJECT_PREFIX}.>"],
            retention="workqueue",
        )
        logger.info("Stream %s created.", STREAM_NAME)
    except Exception as exc:  # nats.js.errors.BadRequestError when stream exists
        logger.debug("Stream %s already exists or creation skipped: %s", STREAM_NAME, exc)


# ---------------------------------------------------------------------------
# Consumer — single batch
# ---------------------------------------------------------------------------


async def consume_once(js, mongo_db) -> int:
    """Fetch and process one batch of messages from REPORT_REQUESTS.

    Creates a durable pull consumer named 'report-enricher' on first call.
    Fetches up to 10 messages with a 5-second timeout.

    For each message:
        1. Parse the JSON payload.
        2. validate() — reject unknown payload_version.
        3. clean()    — strip PII fields.
        4. enrich()   — compute response_time_class, error_category, enriched_at.
        5. insert_one() into the weekly-bucketed MongoDB collection.
        6. await msg.ack() — only after successful MongoDB insertion.

    Ack discipline: Ack only after the MongoDB insert confirms. Acking before
    the write creates data loss on crash.

    On any per-message exception: nack with a 5-second delay and log the error.
    NATS will redeliver up to MAX_DELIVER times before routing the advisory to
    REPORT_REQUESTS_DLQ.

    Note: pymongo is synchronous. In production use of both NATS (async) and
    MongoDB in the same service, consider motor for the async MongoDB path.

    Args:
        js: nats JetStream context
        mongo_db: pymongo Database instance

    Returns:
        Number of messages successfully processed and acked in this batch.
    """
    sub = await js.pull_subscribe(
        subject=f"{SUBJECT_PREFIX}.>",
        durable=CONSUMER_NAME,
        config=nats.js.api.ConsumerConfig(
            ack_policy=nats.js.api.AckPolicy.EXPLICIT,
            ack_wait=ACK_WAIT_SECONDS,
            max_deliver=MAX_DELIVER,
        ),
    )

    try:
        msgs = await sub.fetch(batch=10, timeout=5.0)
    except nats.errors.TimeoutError:
        logger.debug("consume_once: no messages available within timeout.")
        return 0

    acked = 0
    for msg in msgs:
        try:
            payload = json.loads(msg.data)
            validate(payload)
            cleaned = clean(payload)
            enriched = enrich(cleaned)

            collection_name = weekly_collection_name(enriched["published_at"])
            collection = mongo_db[collection_name]
            result = collection.insert_one(enriched)
            if not result.inserted_id:
                raise RuntimeError("insert_one returned no inserted_id")

            # ACK only after successful MongoDB insertion
            await msg.ack()
            acked += 1
            logger.info(
                "Processed correlation_id=%s -> %s (_id=%s)",
                enriched.get("correlation_id"),
                collection_name,
                result.inserted_id,
            )
        except Exception as exc:
            logger.error(
                "Processing failed for msg (correlation_id=%s): %s",
                json.loads(msg.data).get("correlation_id") if msg.data else "unknown",
                exc,
            )
            await msg.nak(delay=5)

    return acked


# ---------------------------------------------------------------------------
# Consumer — long-running loop
# ---------------------------------------------------------------------------


async def run_consumer_loop(js, mongo_db, max_iterations: int | None = None) -> None:
    """Run the consume_once loop continuously (or for a bounded number of iterations).

    Args:
        js: nats JetStream context
        mongo_db: pymongo Database instance
        max_iterations: stop after this many iterations (None = run forever).
            Pass an integer for bounded runs during testing or one-shot drains.

    TimeoutError from fetch is caught and silently continued (no messages
    available). Other exceptions are logged and the loop continues.
    """
    iteration = 0
    while max_iterations is None or iteration < max_iterations:
        try:
            await consume_once(js, mongo_db)
        except nats.errors.TimeoutError:
            pass  # no messages; keep polling
        except Exception as exc:
            logger.error("run_consumer_loop: unexpected error: %s", exc)
        iteration += 1


# ---------------------------------------------------------------------------
# Async entrypoint
# ---------------------------------------------------------------------------


async def main() -> None:
    """End-to-end pipeline demonstration.

    Requires a running NATS JetStream server and MongoDB instance.

    Steps:
        1. Read NATS_URL, MONGO_URI, MONGO_DB from environment.
        2. Connect to NATS.
        3. Ensure REPORT_REQUESTS stream exists.
        4. Publish SAMPLE_PAYLOAD via produce().
        5. Connect to MongoDB.
        6. Call consume_once() to process the published message.
        7. Query MongoDB for the inserted document by correlation_id.
        8. Assert the document exists and has enrichment fields.
        9. Print success with collection name and inserted _id.
        10. Disconnect from NATS.

    Raises:
        AssertionError: if the inserted document cannot be found or is missing
            expected enrichment fields.
        KeyError: if a required environment variable is not set.
    """
    nats_url = os.environ["NATS_URL"]
    mongo_uri = os.environ["MONGO_URI"]
    mongo_db_name = os.environ["MONGO_DB"]

    # --- Connect to NATS ---
    nc = await nats.connect(nats_url)
    js = nc.jetstream()

    # --- Ensure stream ---
    await _ensure_stream(js)

    # --- Publish sample payload ---
    await produce(nc, SAMPLE_PAYLOAD)
    print(f"Published SAMPLE_PAYLOAD (correlation_id={SAMPLE_PAYLOAD['correlation_id']})")

    # --- Connect to MongoDB (synchronous pymongo) ---
    # Note: production code that runs both NATS (async) and MongoDB in the
    # same service would typically use motor for the async MongoDB path.
    mongo_client = MongoClient(mongo_uri)
    mongo_db = mongo_client[mongo_db_name]

    # --- Consume one batch ---
    acked = await consume_once(js, mongo_db)
    print(f"consume_once() processed and acked {acked} message(s).")

    # --- Verify the document was inserted ---
    collection_name = weekly_collection_name(SAMPLE_PAYLOAD["published_at"])
    collection = mongo_db[collection_name]
    doc = collection.find_one({"correlation_id": SAMPLE_PAYLOAD["correlation_id"]})

    assert doc is not None, (
        f"Expected document with correlation_id={SAMPLE_PAYLOAD['correlation_id']!r} "
        f"in collection '{collection_name}', but find_one() returned None."
    )
    assert "response_time_class" in doc, (
        f"Enriched document is missing 'response_time_class'. Document keys: {list(doc.keys())}"
    )
    assert "error_category" in doc, (
        f"Enriched document is missing 'error_category'. Document keys: {list(doc.keys())}"
    )

    print(
        f"OK — document inserted into '{collection_name}' "
        f"(_id={doc['_id']}, "
        f"response_time_class={doc['response_time_class']!r}, "
        f"error_category={doc['error_category']!r})"
    )

    # --- Disconnect ---
    await nc.drain()


# ---------------------------------------------------------------------------
# Entry guard
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
