import json
import time
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

KAFKA_BROKER = "kafka:9092"
TOPIC = "agent.job.events"

# Global cached producer (lazy loaded)
producer_instance = None


def get_producer():
    """
    Lazily create KafkaProducer.
    Never block FastAPI startup.
    """
    global producer_instance

    if producer_instance:
        return producer_instance

    retries = 0
    while retries < 20:   # retry for ~40 seconds max
        try:
            producer_instance = KafkaProducer(
                bootstrap_servers=KAFKA_BROKER,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                retries=5,
            )
            print("✅ Kafka Producer connected!")
            return producer_instance

        except NoBrokersAvailable:
            retries += 1
            print(f"⚠ Kafka not ready ({retries}), retrying in 2s...")
            time.sleep(2)

    print("❌ Kafka unavailable — running without Kafka.")
    producer_instance = None
    return None


def publish_event(job_id: str, status: str, metadata: dict | None = None):
    """
    Publish dynamic job events to Kafka
    Example event:
    {
        "job_id": "uuid",
        "status": "created|running|completed|failed",
        "timestamp": "2025-12-02T10:00:00Z",
        "metadata": {...}
    }
    """
    producer = get_producer()

    event = {
        "job_id": job_id,
        "status": status,
        "timestamp": time.time(),
        "metadata": metadata or {},
    }

    # If Kafka is down, skip but don't break FastAPI
    if not producer:
        print("⚠ Kafka unavailable — event skipped", event)
        return event

    future = producer.send(TOPIC, event)
    future.get(timeout=5)

    print(f"📤 Published event: {event}")

    return event
