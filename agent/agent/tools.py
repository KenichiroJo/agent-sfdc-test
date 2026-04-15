import json
from typing import Optional

from langchain_core.tools import tool

from agent.data.loader import (
    ACTIVITIES,
    ARTICLES_BY_ID,
    CUSTOMERS,
    CUSTOMERS_BY_ID,
    DEALS,
    DEALS_BY_ID,
    KNOWLEDGE_ARTICLES,
    PERFORMANCE_METRICS,
    REPS_BY_ID,
    SALES_REPS,
)


def _json(data: object) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


# ============================================================
# 共通ツール
# ============================================================


@tool
def list_sales_reps() -> str:
    """営業担当者の一覧を取得します。名前、チーム、テリトリー、役割を含みます。"""
    return _json(
        [
            {
                "id": r["id"],
                "name": r["name"],
                "team": r["team"],
                "role": r["role"],
                "territory": r["territory"],
            }
            for r in SALES_REPS
        ]
    )


@tool
def get_rep_info(rep_id: str) -> str:
    """指定された営業担当者の詳細情報を取得します。

    Args:
        rep_id: 営業担当者のID（例: REP001）
    """
    rep = REPS_BY_ID.get(rep_id)
    if not rep:
        return f"担当者ID '{rep_id}' が見つかりません。list_sales_repsで一覧を確認してください。"
    return _json(rep)


@tool
def get_customer_info(customer_id: str) -> str:
    """指定された顧客企業の詳細情報を取得します。

    Args:
        customer_id: 顧客ID（例: CUST001）
    """
    cust = CUSTOMERS_BY_ID.get(customer_id)
    if not cust:
        return f"顧客ID '{customer_id}' が見つかりません。"
    return _json(cust)


@tool
def list_customers(segment: Optional[str] = None) -> str:
    """顧客企業の一覧を取得します。セグメントでフィルタリング可能です。

    Args:
        segment: フィルタするセグメント名（例: 企業制服, イベント・プロモーション）。省略時は全件。
    """
    results = CUSTOMERS
    if segment:
        results = [c for c in results if segment in c["segment"]]
    return _json(
        [
            {
                "id": c["id"],
                "company_name": c["company_name"],
                "segment": c["segment"],
                "region": c["region"],
            }
            for c in results
        ]
    )


# ============================================================
# Agent 1: 営業活動自動要約ツール
# ============================================================


@tool
def get_activities_by_rep(rep_id: str, limit: int = 10) -> str:
    """指定された営業担当者の最近の活動記録を取得します。

    Args:
        rep_id: 営業担当者のID（例: REP001）
        limit: 取得する件数の上限（デフォルト: 10）
    """
    acts = [a for a in ACTIVITIES if a["rep_id"] == rep_id]
    acts.sort(key=lambda x: x["date"], reverse=True)
    return _json(acts[:limit])


@tool
def get_activity_detail(activity_id: str) -> str:
    """指定された活動記録の詳細を取得します。

    Args:
        activity_id: 活動ID（例: ACT001）
    """
    for a in ACTIVITIES:
        if a["id"] == activity_id:
            result = dict(a)
            if a.get("customer_id") and a["customer_id"] in CUSTOMERS_BY_ID:
                result["customer_name"] = CUSTOMERS_BY_ID[a["customer_id"]][
                    "company_name"
                ]
            if a.get("rep_id") and a["rep_id"] in REPS_BY_ID:
                result["rep_name"] = REPS_BY_ID[a["rep_id"]]["name"]
            return _json(result)
    return f"活動ID '{activity_id}' が見つかりません。"


@tool
def get_activities_by_customer(customer_id: str, limit: int = 10) -> str:
    """指定された顧客企業に関する活動記録を取得します。

    Args:
        customer_id: 顧客ID（例: CUST001）
        limit: 取得する件数の上限（デフォルト: 10）
    """
    acts = [a for a in ACTIVITIES if a["customer_id"] == customer_id]
    acts.sort(key=lambda x: x["date"], reverse=True)
    return _json(acts[:limit])


# ============================================================
# Agent 2: フィードバック・ネクストアクション提案ツール
# ============================================================


@tool
def get_team_activities_summary(team: str, limit: int = 20) -> str:
    """チーム全体の活動概要を取得します。各担当者の最近の活動数と内容を含みます。

    Args:
        team: チーム名（例: 東日本営業部, 西日本営業部）
        limit: 各担当者あたりの活動取得件数
    """
    team_reps = [r for r in SALES_REPS if r["team"] == team and r["role"] != "マネージャー"]
    summary = []
    for rep in team_reps:
        rep_acts = [a for a in ACTIVITIES if a["rep_id"] == rep["id"]]
        rep_acts.sort(key=lambda x: x["date"], reverse=True)
        summary.append(
            {
                "rep_id": rep["id"],
                "rep_name": rep["name"],
                "territory": rep["territory"],
                "total_activities": len(rep_acts),
                "recent_activities": [
                    {
                        "id": a["id"],
                        "date": a["date"],
                        "type": a["activity_type"],
                        "subject": a["subject"],
                        "customer_id": a["customer_id"],
                        "sentiment": a["sentiment"],
                    }
                    for a in rep_acts[:limit]
                ],
            }
        )
    return _json(summary)


@tool
def get_rep_recent_activities_with_deals(rep_id: str) -> str:
    """担当者の最近の活動と関連する商談情報を合わせて取得します。フィードバック生成に使用します。

    Args:
        rep_id: 営業担当者のID
    """
    rep = REPS_BY_ID.get(rep_id)
    if not rep:
        return f"担当者ID '{rep_id}' が見つかりません。"

    acts = [a for a in ACTIVITIES if a["rep_id"] == rep_id]
    acts.sort(key=lambda x: x["date"], reverse=True)

    enriched = []
    for a in acts[:10]:
        entry = dict(a)
        if a.get("customer_id") and a["customer_id"] in CUSTOMERS_BY_ID:
            entry["customer_name"] = CUSTOMERS_BY_ID[a["customer_id"]]["company_name"]
        if a.get("deal_id") and a["deal_id"] in DEALS_BY_ID:
            deal = DEALS_BY_ID[a["deal_id"]]
            entry["deal_info"] = {
                "deal_name": deal["deal_name"],
                "stage": deal["stage"],
                "amount": deal["amount"],
                "probability": deal["probability"],
            }
        enriched.append(entry)

    return _json({"rep_name": rep["name"], "team": rep["team"], "activities": enriched})


@tool
def get_rep_performance_context(rep_id: str) -> str:
    """担当者のパフォーマンス指標を取得します。フィードバックのコンテキストに使用します。

    Args:
        rep_id: 営業担当者のID
    """
    metrics = [m for m in PERFORMANCE_METRICS if m["rep_id"] == rep_id]
    metrics.sort(key=lambda x: x["period"], reverse=True)

    rep = REPS_BY_ID.get(rep_id)
    if not rep:
        return f"担当者ID '{rep_id}' が見つかりません。"

    return _json(
        {
            "rep_name": rep["name"],
            "team": rep["team"],
            "target_quarterly_revenue": rep["target_quarterly_revenue"],
            "metrics": metrics,
        }
    )


# ============================================================
# Agent 3: ナレッジ検索ツール
# ============================================================


@tool
def search_knowledge_base(query: str, category: Optional[str] = None) -> str:
    """ナレッジベースをキーワードで検索します。

    Args:
        query: 検索キーワード（例: ドライTシャツ, 価格交渉, 入札）
        category: カテゴリフィルタ（例: 営業ノウハウ, 商品知識, 成功事例, 業界動向, 競合情報）
    """
    results = KNOWLEDGE_ARTICLES
    if category:
        results = [a for a in results if a["category"] == category]

    query_lower = query.lower()
    scored = []
    for article in results:
        score = 0
        searchable = (
            article["title"]
            + " "
            + article["content"]
            + " "
            + " ".join(article["tags"])
        ).lower()
        for word in query_lower.split():
            if word in searchable:
                score += searchable.count(word)
        if score > 0:
            scored.append((score, article))

    scored.sort(key=lambda x: x[0], reverse=True)
    return _json(
        [
            {
                "id": a["id"],
                "title": a["title"],
                "category": a["category"],
                "tags": a["tags"],
                "helpfulness_score": a["helpfulness_score"],
                "views": a["views"],
                "content_preview": a["content"][:200] + "...",
            }
            for _, a in scored[:5]
        ]
    )


@tool
def get_knowledge_article(article_id: str) -> str:
    """指定されたナレッジ記事の全文を取得します。

    Args:
        article_id: 記事ID（例: KN001）
    """
    article = ARTICLES_BY_ID.get(article_id)
    if not article:
        return f"記事ID '{article_id}' が見つかりません。"
    return _json(article)


@tool
def list_knowledge_categories() -> str:
    """ナレッジベースのカテゴリ一覧と各カテゴリの記事数を取得します。"""
    categories: dict[str, int] = {}
    for a in KNOWLEDGE_ARTICLES:
        cat = a["category"]
        categories[cat] = categories.get(cat, 0) + 1
    return _json(categories)


# ============================================================
# Agent 4: 未入力商談データ補完ツール
# ============================================================


@tool
def find_incomplete_deals() -> str:
    """未入力フィールドがある商談を検索します。金額、確度、クローズ予定日、商品カテゴリなどが未入力の商談を返します。"""
    incomplete = []
    check_fields = [
        "amount",
        "probability",
        "expected_close_date",
        "product_category",
        "quantity_estimate",
        "customer_id",
    ]
    for d in DEALS:
        if d["stage"] in ("受注", "失注"):
            continue
        missing = [f for f in check_fields if d.get(f) is None]
        if missing:
            entry = {
                "id": d["id"],
                "deal_name": d["deal_name"],
                "rep_id": d["rep_id"],
                "stage": d["stage"],
                "missing_fields": missing,
            }
            if d["rep_id"] in REPS_BY_ID:
                entry["rep_name"] = REPS_BY_ID[d["rep_id"]]["name"]
            incomplete.append(entry)
    return _json(incomplete)


@tool
def get_deal_detail(deal_id: str) -> str:
    """指定された商談の詳細情報を取得します。

    Args:
        deal_id: 商談ID（例: DEAL001）
    """
    deal = DEALS_BY_ID.get(deal_id)
    if not deal:
        return f"商談ID '{deal_id}' が見つかりません。"
    result = dict(deal)
    if deal.get("rep_id") and deal["rep_id"] in REPS_BY_ID:
        result["rep_name"] = REPS_BY_ID[deal["rep_id"]]["name"]
    if deal.get("customer_id") and deal["customer_id"] in CUSTOMERS_BY_ID:
        result["customer_name"] = CUSTOMERS_BY_ID[deal["customer_id"]]["company_name"]
    return _json(result)


@tool
def suggest_deal_field_values(deal_id: str) -> str:
    """活動履歴から商談の未入力フィールドの推定値を提案します。

    Args:
        deal_id: 商談ID
    """
    deal = DEALS_BY_ID.get(deal_id)
    if not deal:
        return f"商談ID '{deal_id}' が見つかりません。"

    related_acts = [a for a in ACTIVITIES if a.get("deal_id") == deal_id]
    rep_acts = [a for a in ACTIVITIES if a["rep_id"] == deal["rep_id"]]

    suggestions: dict[str, object] = {"deal_id": deal_id, "suggestions": {}}
    sugg = suggestions["suggestions"]
    assert isinstance(sugg, dict)

    if deal.get("amount") is None and related_acts:
        for a in related_acts:
            comment = a.get("comment", "")
            if "万円" in comment or "枚" in comment:
                sugg["amount"] = "活動コメントに予算・数量の記載あり。確認推奨。"
                break

    if deal.get("customer_id") is None:
        for a in rep_acts:
            if a.get("customer_id"):
                sugg["customer_id"] = (
                    f"担当者の活動から推定: {a['customer_id']} "
                    f"({CUSTOMERS_BY_ID.get(a['customer_id'], {}).get('company_name', '不明')})"
                )
                break

    if deal.get("product_category") is None:
        tags_all = []
        for a in related_acts:
            tags_all.extend(a.get("tags", []))
        product_tags = [
            t
            for t in tags_all
            if any(
                kw in t
                for kw in ["Tシャツ", "ポロシャツ", "スウェット", "パーカー", "ドライ", "ヘビーウェイト"]
            )
        ]
        if product_tags:
            sugg["product_category"] = f"活動タグから推定: {', '.join(set(product_tags))}"

    return _json(suggestions)


@tool
def list_deals_by_rep(rep_id: str) -> str:
    """指定された担当者の商談一覧を取得します。

    Args:
        rep_id: 営業担当者のID
    """
    deals = [d for d in DEALS if d["rep_id"] == rep_id]
    deals.sort(key=lambda x: x.get("expected_close_date") or "9999-12-31")
    return _json(
        [
            {
                "id": d["id"],
                "deal_name": d["deal_name"],
                "stage": d["stage"],
                "amount": d["amount"],
                "probability": d["probability"],
                "expected_close_date": d["expected_close_date"],
            }
            for d in deals
        ]
    )


# ============================================================
# Agent 5: パフォーマンス分析ツール
# ============================================================


@tool
def get_team_performance_metrics(team: str, period: Optional[str] = None) -> str:
    """チーム全体のパフォーマンス指標を取得します。

    Args:
        team: チーム名（例: 東日本営業部, 西日本営業部）
        period: 期間フィルタ（例: 2026-Q1）。省略時は全期間。
    """
    team_rep_ids = {
        r["id"] for r in SALES_REPS if r["team"] == team and r["role"] != "マネージャー"
    }
    metrics = [m for m in PERFORMANCE_METRICS if m["rep_id"] in team_rep_ids]
    if period:
        metrics = [m for m in metrics if m["period"] == period]

    if not metrics:
        return f"チーム '{team}' の指標が見つかりません。"

    result = []
    for m in metrics:
        entry = dict(m)
        entry["rep_name"] = REPS_BY_ID.get(m["rep_id"], {}).get("name", "不明")
        result.append(entry)
    return _json(result)


@tool
def compare_rep_performance(rep_ids: str) -> str:
    """複数の担当者のパフォーマンスを比較します。

    Args:
        rep_ids: カンマ区切りの担当者ID（例: REP001,REP002,REP005）
    """
    ids = [rid.strip() for rid in rep_ids.split(",")]
    comparison = []
    for rid in ids:
        rep = REPS_BY_ID.get(rid)
        if not rep:
            continue
        latest = [m for m in PERFORMANCE_METRICS if m["rep_id"] == rid]
        latest.sort(key=lambda x: x["period"], reverse=True)
        if latest:
            entry = dict(latest[0])
            entry["rep_name"] = rep["name"]
            entry["team"] = rep["team"]
            comparison.append(entry)
    return _json(comparison)


@tool
def get_performance_trends(rep_id: str) -> str:
    """担当者のパフォーマンス推移を取得します。四半期ごとのトレンドを表示します。

    Args:
        rep_id: 営業担当者のID
    """
    rep = REPS_BY_ID.get(rep_id)
    if not rep:
        return f"担当者ID '{rep_id}' が見つかりません。"

    metrics = [m for m in PERFORMANCE_METRICS if m["rep_id"] == rep_id]
    metrics.sort(key=lambda x: x["period"])
    return _json({"rep_name": rep["name"], "trends": metrics})


@tool
def get_pipeline_analysis(team: Optional[str] = None) -> str:
    """パイプライン分析を行います。商談ステージごとの件数と金額を集計します。

    Args:
        team: チーム名でフィルタ（省略時は全チーム）
    """
    active_deals = [d for d in DEALS if d["stage"] not in ("受注", "失注")]

    if team:
        team_rep_ids = {
            r["id"]
            for r in SALES_REPS
            if r["team"] == team and r["role"] != "マネージャー"
        }
        active_deals = [d for d in active_deals if d["rep_id"] in team_rep_ids]

    stages: dict[str, dict] = {}
    for d in active_deals:
        stage = d["stage"]
        if stage not in stages:
            stages[stage] = {"count": 0, "total_amount": 0, "deals": []}
        stages[stage]["count"] += 1
        stages[stage]["total_amount"] += d.get("amount") or 0
        stages[stage]["deals"].append(
            {
                "id": d["id"],
                "deal_name": d["deal_name"],
                "amount": d["amount"],
                "rep_name": REPS_BY_ID.get(d["rep_id"], {}).get("name", "不明"),
            }
        )

    return _json(stages)


# ============================================================
# ツールセット定義
# ============================================================

COMMON_TOOLS = [list_sales_reps, get_rep_info, get_customer_info, list_customers]

SUMMARY_TOOLS = COMMON_TOOLS + [
    get_activities_by_rep,
    get_activity_detail,
    get_activities_by_customer,
]

FEEDBACK_TOOLS = COMMON_TOOLS + [
    get_team_activities_summary,
    get_rep_recent_activities_with_deals,
    get_rep_performance_context,
    get_activities_by_rep,
]

KNOWLEDGE_TOOLS = COMMON_TOOLS + [
    search_knowledge_base,
    get_knowledge_article,
    list_knowledge_categories,
]

DATA_COMPLETION_TOOLS = COMMON_TOOLS + [
    find_incomplete_deals,
    get_deal_detail,
    suggest_deal_field_values,
    list_deals_by_rep,
    get_activities_by_rep,
]

PERFORMANCE_TOOLS = COMMON_TOOLS + [
    get_team_performance_metrics,
    compare_rep_performance,
    get_performance_trends,
    get_pipeline_analysis,
]

ALL_TOOLS = list(
    {
        t
        for tools in [
            SUMMARY_TOOLS,
            FEEDBACK_TOOLS,
            KNOWLEDGE_TOOLS,
            DATA_COMPLETION_TOOLS,
            PERFORMANCE_TOOLS,
        ]
        for t in tools
    }
)
