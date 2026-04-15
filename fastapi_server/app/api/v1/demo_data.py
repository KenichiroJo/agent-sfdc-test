"""デモデータ提供API - ダッシュボード・レビュー・ナレッジページ用"""

from typing import Optional

from fastapi import APIRouter, Query

from app.data.loader import (
    ACTIVITIES,
    CUSTOMERS,
    CUSTOMERS_BY_ID,
    DEALS,
    KNOWLEDGE_ARTICLES,
    PERFORMANCE_METRICS,
    REPS_BY_ID,
    SALES_REPS,
)

demo_router = APIRouter(prefix="/demo", tags=["demo"])


@demo_router.get("/reps")
def get_reps(team: Optional[str] = Query(None)):
    reps = SALES_REPS
    if team:
        reps = [r for r in reps if r["team"] == team]
    return reps


@demo_router.get("/reps/{rep_id}")
def get_rep(rep_id: str):
    rep = REPS_BY_ID.get(rep_id)
    if not rep:
        return {"error": f"Rep {rep_id} not found"}
    return rep


@demo_router.get("/reps/{rep_id}/activities")
def get_rep_activities(rep_id: str, limit: int = Query(20)):
    acts = [a for a in ACTIVITIES if a["rep_id"] == rep_id]
    acts.sort(key=lambda x: x["date"], reverse=True)
    for a in acts:
        if a.get("customer_id") and a["customer_id"] in CUSTOMERS_BY_ID:
            a = {**a, "customer_name": CUSTOMERS_BY_ID[a["customer_id"]]["company_name"]}
    enriched = []
    for a in acts[:limit]:
        entry = dict(a)
        if a.get("customer_id") and a["customer_id"] in CUSTOMERS_BY_ID:
            entry["customer_name"] = CUSTOMERS_BY_ID[a["customer_id"]]["company_name"]
        enriched.append(entry)
    return enriched


@demo_router.get("/customers")
def get_customers(segment: Optional[str] = Query(None)):
    custs = CUSTOMERS
    if segment:
        custs = [c for c in custs if segment in c["segment"]]
    return custs


@demo_router.get("/deals")
def get_deals(
    rep_id: Optional[str] = Query(None),
    stage: Optional[str] = Query(None),
):
    results = DEALS
    if rep_id:
        results = [d for d in results if d["rep_id"] == rep_id]
    if stage:
        results = [d for d in results if d["stage"] == stage]
    return results


@demo_router.get("/deals/incomplete")
def get_incomplete_deals():
    check_fields = [
        "amount", "probability", "expected_close_date",
        "product_category", "quantity_estimate", "customer_id",
    ]
    incomplete = []
    for d in DEALS:
        if d["stage"] in ("受注", "失注"):
            continue
        missing = [f for f in check_fields if d.get(f) is None]
        if missing:
            entry = dict(d)
            entry["missing_fields"] = missing
            if d["rep_id"] in REPS_BY_ID:
                entry["rep_name"] = REPS_BY_ID[d["rep_id"]]["name"]
            incomplete.append(entry)
    return incomplete


@demo_router.get("/knowledge")
def get_knowledge(
    category: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
):
    results = KNOWLEDGE_ARTICLES
    if category:
        results = [a for a in results if a["category"] == category]
    if q:
        q_lower = q.lower()
        scored = []
        for article in results:
            searchable = (
                article["title"] + " " + article["content"] + " " + " ".join(article["tags"])
            ).lower()
            score = sum(1 for word in q_lower.split() if word in searchable)
            if score > 0:
                scored.append((score, article))
        scored.sort(key=lambda x: x[0], reverse=True)
        results = [a for _, a in scored]
    return results


@demo_router.get("/metrics")
def get_metrics(
    team: Optional[str] = Query(None),
    period: Optional[str] = Query(None),
):
    results = PERFORMANCE_METRICS
    if team:
        team_rep_ids = {r["id"] for r in SALES_REPS if r["team"] == team and r["role"] != "マネージャー"}
        results = [m for m in results if m["rep_id"] in team_rep_ids]
    if period:
        results = [m for m in results if m["period"] == period]
    enriched = []
    for m in results:
        entry = dict(m)
        entry["rep_name"] = REPS_BY_ID.get(m["rep_id"], {}).get("name", "不明")
        enriched.append(entry)
    return enriched


@demo_router.get("/dashboard/summary")
def get_dashboard_summary():
    """ダッシュボード用のKPI集計データ"""
    current_period = "2026-Q1"
    current_metrics = [m for m in PERFORMANCE_METRICS if m["period"] == current_period]

    total_reps = len([r for r in SALES_REPS if r["role"] != "マネージャー"])
    total_activities = sum(m["activities_count"] for m in current_metrics)
    total_revenue_won = sum(m["revenue_won"] for m in current_metrics)
    total_pipeline = sum(m["pipeline_value"] for m in current_metrics)
    avg_summary_rate = (
        sum(m["activity_summary_rate"] for m in current_metrics) / len(current_metrics)
        if current_metrics else 0
    )
    avg_feedback_rate = (
        sum(m["feedback_utilization_rate"] for m in current_metrics) / len(current_metrics)
        if current_metrics else 0
    )

    # 未入力商談数
    check_fields = ["amount", "probability", "expected_close_date", "product_category", "quantity_estimate", "customer_id"]
    incomplete_count = sum(
        1 for d in DEALS
        if d["stage"] not in ("受注", "失注")
        and any(d.get(f) is None for f in check_fields)
    )

    # アクティブ商談数
    active_deals = [d for d in DEALS if d["stage"] not in ("受注", "失注")]

    # チーム別集計
    teams = {}
    for m in current_metrics:
        rep = REPS_BY_ID.get(m["rep_id"], {})
        team = rep.get("team", "不明")
        if team not in teams:
            teams[team] = {"revenue_won": 0, "pipeline_value": 0, "activities": 0, "reps": 0}
        teams[team]["revenue_won"] += m["revenue_won"]
        teams[team]["pipeline_value"] += m["pipeline_value"]
        teams[team]["activities"] += m["activities_count"]
        teams[team]["reps"] += 1

    return {
        "period": current_period,
        "total_reps": total_reps,
        "total_activities": total_activities,
        "total_revenue_won": total_revenue_won,
        "total_pipeline": total_pipeline,
        "avg_activity_summary_rate": round(avg_summary_rate, 2),
        "avg_feedback_utilization_rate": round(avg_feedback_rate, 2),
        "incomplete_deals_count": incomplete_count,
        "active_deals_count": len(active_deals),
        "teams": teams,
    }
