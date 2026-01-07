from celery import shared_task
from sentinel.pipeline.ingest import ingest_tick

@shared_task(name="sentinel.tick_industry")
def tick_industry(industry_key: str) -> str:
    ingest_tick(industry_key)
    return f"ok:{industry_key}"
