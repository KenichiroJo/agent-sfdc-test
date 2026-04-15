import json
from pathlib import Path

DATA_DIR = Path(__file__).parent


def _load_json(filename: str) -> list[dict]:
    with open(DATA_DIR / filename, "r", encoding="utf-8") as f:
        return json.load(f)


SALES_REPS: list[dict] = _load_json("sales_reps.json")
CUSTOMERS: list[dict] = _load_json("customers.json")
ACTIVITIES: list[dict] = _load_json("activities.json")
DEALS: list[dict] = _load_json("deals.json")
KNOWLEDGE_ARTICLES: list[dict] = _load_json("knowledge_articles.json")
PERFORMANCE_METRICS: list[dict] = _load_json("performance_metrics.json")

# Index lookups
REPS_BY_ID: dict[str, dict] = {r["id"]: r for r in SALES_REPS}
CUSTOMERS_BY_ID: dict[str, dict] = {c["id"]: c for c in CUSTOMERS}
DEALS_BY_ID: dict[str, dict] = {d["id"]: d for d in DEALS}
ARTICLES_BY_ID: dict[str, dict] = {a["id"]: a for a in KNOWLEDGE_ARTICLES}
