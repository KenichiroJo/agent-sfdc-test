# Copyright 2026 DataRobot, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import re
from typing import Any, Optional, Union

from datarobot_genai.core.agents import make_system_prompt
from datarobot_genai.langgraph.agent import LangGraphAgent
from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool
from langchain_litellm.chat_models import ChatLiteLLM
from langgraph.graph import END, START, MessagesState, StateGraph

from agent.config import Config
from agent.tools import (
    ALL_TOOLS,
    DATA_COMPLETION_TOOLS,
    FEEDBACK_TOOLS,
    KNOWLEDGE_TOOLS,
    PERFORMANCE_TOOLS,
    SUMMARY_TOOLS,
)

# ルーティング先の定義
ROUTE_SUMMARY = "summary"
ROUTE_FEEDBACK = "feedback"
ROUTE_KNOWLEDGE = "knowledge"
ROUTE_DATA_COMPLETION = "data_completion"
ROUTE_PERFORMANCE = "performance"

VALID_ROUTES = {
    ROUTE_SUMMARY,
    ROUTE_FEEDBACK,
    ROUTE_KNOWLEDGE,
    ROUTE_DATA_COMPLETION,
    ROUTE_PERFORMANCE,
}


def _extract_route(text: str) -> str:
    """AIメッセージからルーティングタグを抽出する"""
    match = re.search(r"\[ROUTE:(\w+)\]", text)
    if match:
        route = match.group(1)
        if route in VALID_ROUTES:
            return route
    # キーワードベースのフォールバック
    text_lower = text.lower()
    if any(kw in text_lower for kw in ["要約", "summary", "活動コメント", "まとめ"]):
        return ROUTE_SUMMARY
    if any(
        kw in text_lower
        for kw in ["フィードバック", "feedback", "ネクストアクション", "指導", "アドバイス"]
    ):
        return ROUTE_FEEDBACK
    if any(
        kw in text_lower
        for kw in ["ナレッジ", "knowledge", "ノウハウ", "事例", "検索"]
    ):
        return ROUTE_KNOWLEDGE
    if any(
        kw in text_lower
        for kw in ["未入力", "補完", "missing", "incomplete", "データ不足"]
    ):
        return ROUTE_DATA_COMPLETION
    if any(
        kw in text_lower
        for kw in [
            "パフォーマンス",
            "performance",
            "分析",
            "成績",
            "KPI",
            "実績",
        ]
    ):
        return ROUTE_PERFORMANCE
    return ROUTE_SUMMARY


class MyAgent(LangGraphAgent):
    """キャブ株式会社（United Athle）フィールドセールス活動支援AIエージェント。

    5つの機能を持つ営業支援エージェント:
    1. 営業活動自動要約
    2. マネージャー向けフィードバック・ネクストアクション提案
    3. ナレッジ自動蓄積・検索
    4. 未入力商談データ補完
    5. 営業パフォーマンス分析・改善提案
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        model: Optional[str] = None,
        verbose: Optional[Union[bool, str]] = True,
        timeout: Optional[int] = 90,
        *,
        llm: Optional[BaseChatModel] = None,
        workflow_tools: Optional[list[BaseTool]] = None,
        **kwargs: Any,
    ):
        super().__init__(
            api_key=api_key,
            api_base=api_base,
            model=model,
            verbose=verbose,
            timeout=timeout,
            **kwargs,
        )
        self._nat_llm = llm
        self._workflow_tools = workflow_tools or []
        self.config = Config()
        self.default_model = self.config.llm_default_model
        if model in ("unknown", "datarobot-deployed-llm"):
            self.model = self.default_model

    @property
    def workflow(self) -> StateGraph[MessagesState]:
        wf = StateGraph[MessagesState, None, MessagesState, MessagesState](
            MessagesState
        )

        # ノード登録
        wf.add_node("router_node", self.agent_router)
        wf.add_node("summary_node", self.agent_summary)
        wf.add_node("feedback_node", self.agent_feedback)
        wf.add_node("knowledge_node", self.agent_knowledge)
        wf.add_node("data_completion_node", self.agent_data_completion)
        wf.add_node("performance_node", self.agent_performance)

        # エッジ定義
        wf.add_edge(START, "router_node")
        wf.add_conditional_edges(
            "router_node",
            self._route_to_capability,
            {
                ROUTE_SUMMARY: "summary_node",
                ROUTE_FEEDBACK: "feedback_node",
                ROUTE_KNOWLEDGE: "knowledge_node",
                ROUTE_DATA_COMPLETION: "data_completion_node",
                ROUTE_PERFORMANCE: "performance_node",
            },
        )
        wf.add_edge("summary_node", END)
        wf.add_edge("feedback_node", END)
        wf.add_edge("knowledge_node", END)
        wf.add_edge("data_completion_node", END)
        wf.add_edge("performance_node", END)

        return wf  # type: ignore[return-value]

    @staticmethod
    def _route_to_capability(state: MessagesState) -> str:
        """routerノードの出力からルーティング先を決定する"""
        last_msg = state["messages"][-1]
        if isinstance(last_msg, AIMessage) and isinstance(last_msg.content, str):
            return _extract_route(last_msg.content)
        return ROUTE_SUMMARY

    @property
    def prompt_template(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "あなたはキャブ株式会社（United Athleブランド）の"
                    "フィールドセールス活動支援AIエージェントです。"
                    "営業担当者やマネージャーからの質問に対して、適切なツールを使って回答してください。"
                    "日本語で丁寧に回答してください。"
                    "チャット履歴: {chat_history}",
                ),
                ("user", "{topic}"),
            ]
        )

    def llm(
        self,
        auto_model_override: bool = True,
    ) -> BaseChatModel:
        """Returns the LLM to use for agent nodes."""
        if self._nat_llm is not None:
            return self._nat_llm

        api_base = self.litellm_api_base(self.config.llm_deployment_id)
        model = self.model or self.default_model
        if auto_model_override and not self.config.use_datarobot_llm_gateway:
            model = self.default_model
        if self.verbose:
            print(f"Using model: {model}")

        config = {
            "model": model,
            "api_base": api_base,
            "api_key": self.api_key,
            "timeout": self.timeout,
            "streaming": True,
            "max_retries": 3,
        }

        if not self.config.use_datarobot_llm_gateway and self._identity_header:
            config["model_kwargs"] = {"extra_headers": self._identity_header}  # type: ignore[assignment]

        return ChatLiteLLM(**config)

    # ================================================================
    # Router Node
    # ================================================================

    @property
    def agent_router(self) -> Any:
        return create_agent(
            self.llm(),
            tools=[],
            system_prompt=make_system_prompt(
                "あなたはユーザーのリクエストを分析し、最も適切なエージェント機能にルーティングするルーターです。\n"
                "\n"
                "以下の5つの機能があります:\n"
                "1. summary - 営業活動の要約（活動コメントの要約、キーポイント抽出）\n"
                "2. feedback - マネージャー向けフィードバック・ネクストアクション提案\n"
                "3. knowledge - ナレッジベースの検索・閲覧\n"
                "4. data_completion - 未入力商談データの検出・補完提案\n"
                "5. performance - 営業パフォーマンス分析・改善提案\n"
                "\n"
                "ユーザーのメッセージを読み、最も適切な機能を1つ選んでください。\n"
                "回答には必ず [ROUTE:機能名] タグを含めてください。\n"
                "例: [ROUTE:summary] このリクエストは活動要約に関するものです。\n"
                "例: [ROUTE:feedback] フィードバック生成のリクエストです。\n"
                "例: [ROUTE:knowledge] ナレッジ検索のリクエストです。\n"
                "例: [ROUTE:data_completion] 未入力データの確認リクエストです。\n"
                "例: [ROUTE:performance] パフォーマンス分析のリクエストです。\n"
                "\n"
                "タグの後に簡単な理由を1文で説明してください。"
            ),
            name="router_agent",
        )

    # ================================================================
    # Agent 1: 営業活動自動要約
    # ================================================================

    @property
    def agent_summary(self) -> Any:
        return create_agent(
            self.llm(),
            tools=SUMMARY_TOOLS + self.mcp_tools + self._workflow_tools,
            system_prompt=make_system_prompt(
                "あなたはキャブ株式会社（United Athle）の営業活動自動要約エージェントです。\n"
                "営業担当者のSFDC活動コメントを分析し、効率的な情報把握を支援します。\n"
                "\n"
                "## あなたの役割\n"
                "1. 活動内容の簡潔な要約（3-5行）を作成する\n"
                "2. キーポイントを箇条書きで抽出する（顧客名、商談フェーズ、商品、数量、金額等）\n"
                "3. 顧客の反応・温度感を評価する（ポジティブ/ニュートラル/ネガティブ）\n"
                "4. 次回アクションを提案する\n"
                "5. 競合情報があれば特記する\n"
                "\n"
                "## 使用するツール\n"
                "- まず担当者リスト(list_sales_reps)で担当者を確認\n"
                "- 担当者ID指定で活動取得(get_activities_by_rep)\n"
                "- 個別活動の詳細取得(get_activity_detail)\n"
                "- 顧客情報の補完(get_customer_info)\n"
                "\n"
                "## 出力フォーマット\n"
                "Markdown形式で見やすく整理してください。\n"
                "- 各活動には日付、活動タイプ、顧客名を明記\n"
                "- キーポイントは箇条書き\n"
                "- 次回アクションは具体的に"
            ),
            name="summary_agent",
        )

    # ================================================================
    # Agent 2: フィードバック・ネクストアクション提案
    # ================================================================

    @property
    def agent_feedback(self) -> Any:
        return create_agent(
            self.llm(),
            tools=FEEDBACK_TOOLS + self.mcp_tools + self._workflow_tools,
            system_prompt=make_system_prompt(
                "あなたはキャブ株式会社（United Athle）のマネージャー向けフィードバック・ネクストアクション提案エージェントです。\n"
                "営業マネージャーが部下に質の高いフィードバックとネクストアクションを提供できるよう支援します。\n"
                "\n"
                "## あなたの役割\n"
                "1. 部下の活動コメント、商談履歴、パフォーマンス指標を総合的に分析\n"
                "2. 個別最適化されたフィードバック案を生成（良い点・改善点をバランスよく）\n"
                "3. 具体的なネクストアクションを提案（期限、優先度付き）\n"
                "4. リスクのある商談や支援が必要な部下を特定\n"
                "5. 過去の成功事例やナレッジを引用したアドバイスを生成\n"
                "\n"
                "## フィードバックの構成\n"
                "1. **称賛ポイント**: 具体的な良い行動を挙げて褒める\n"
                "2. **改善提案**: 建設的な改善点を提案（否定的な表現は避ける）\n"
                "3. **ネクストアクション**: 優先度HIGH/MEDIUM/LOWで3-5個提案\n"
                "4. **注意すべき商談**: リスクのある商談と対策\n"
                "\n"
                "## 注意事項\n"
                "- マネージャーの口調で書く（丁寧だが親しみやすい）\n"
                "- データに基づいた客観的な評価\n"
                "- 部下のモチベーションを損なわない表現を心がける"
            ),
            name="feedback_agent",
        )

    # ================================================================
    # Agent 3: ナレッジ検索
    # ================================================================

    @property
    def agent_knowledge(self) -> Any:
        return create_agent(
            self.llm(),
            tools=KNOWLEDGE_TOOLS + self.mcp_tools + self._workflow_tools,
            system_prompt=make_system_prompt(
                "あなたはキャブ株式会社（United Athle）のナレッジ自動蓄積・検索エージェントです。\n"
                "営業ナレッジの検索・提供を通じて、営業担当者の活動を支援します。\n"
                "\n"
                "## あなたの役割\n"
                "1. ユーザーの質問に関連するナレッジ記事を検索・提示\n"
                "2. 商品知識（United Athle製品の特徴、提案ポイント）を提供\n"
                "3. 営業ノウハウ（価格交渉、新規開拓、業種別アプローチ）を共有\n"
                "4. 成功事例・失敗事例から学びを抽出\n"
                "5. 競合情報を整理して提供\n"
                "\n"
                "## 検索手順\n"
                "1. まずキーワードでナレッジベースを検索(search_knowledge_base)\n"
                "2. 関連性の高い記事の全文を取得(get_knowledge_article)\n"
                "3. ユーザーの質問に合わせて情報を整理・要約して回答\n"
                "\n"
                "## 回答スタイル\n"
                "- 実践的で具体的なアドバイスを心がける\n"
                "- 関連するナレッジ記事のタイトルとIDを参考として提示\n"
                "- 追加で知りたいことがないか確認する"
            ),
            name="knowledge_agent",
        )

    # ================================================================
    # Agent 4: 未入力商談データ補完
    # ================================================================

    @property
    def agent_data_completion(self) -> Any:
        return create_agent(
            self.llm(),
            tools=DATA_COMPLETION_TOOLS + self.mcp_tools + self._workflow_tools,
            system_prompt=make_system_prompt(
                "あなたはキャブ株式会社（United Athle）の未入力商談データ補完エージェントです。\n"
                "SFDCに未入力のフィールドがある商談を検出し、補完を支援します。\n"
                "\n"
                "## あなたの役割\n"
                "1. 未入力フィールドがある商談を検出(find_incomplete_deals)\n"
                "2. 活動履歴から未入力フィールドの値を推定(suggest_deal_field_values)\n"
                "3. 担当者に入力を促すリマインドメッセージを生成\n"
                "4. 補完候補の値を提案（担当者の確認・承認が必要なことを明記）\n"
                "\n"
                "## 出力フォーマット\n"
                "各未入力商談について:\n"
                "- 商談名と担当者名\n"
                "- 未入力のフィールド一覧\n"
                "- 活動履歴から推定できる値（あれば）\n"
                "- 担当者への推奨アクション\n"
                "\n"
                "## 注意事項\n"
                "- 自動入力ではなく「提案」であることを明確に\n"
                "- 推定値には根拠（どの活動から推定したか）を記載\n"
                "- 確認が必要な項目は担当者に確認を促す"
            ),
            name="data_completion_agent",
        )

    # ================================================================
    # Agent 5: パフォーマンス分析
    # ================================================================

    @property
    def agent_performance(self) -> Any:
        return create_agent(
            self.llm(),
            tools=PERFORMANCE_TOOLS + self.mcp_tools + self._workflow_tools,
            system_prompt=make_system_prompt(
                "あなたはキャブ株式会社（United Athle）の営業パフォーマンス分析・改善提案エージェントです。\n"
                "営業チーム全体のパフォーマンスを分析し、データに基づいた改善提案を行います。\n"
                "\n"
                "## あなたの役割\n"
                "1. チーム・個人のパフォーマンス指標を分析\n"
                "2. 成功パターンとボトルネックを特定\n"
                "3. パイプラインの健全性を評価\n"
                "4. 具体的な改善アクションを提案\n"
                "5. トップパフォーマーの行動パターンを抽出\n"
                "\n"
                "## 分析観点\n"
                "- 活動量（訪問数、電話数、Web会議数）\n"
                "- 商談進捗（新規作成数、受注数、失注数、コンバージョン率）\n"
                "- 売上実績 vs 目標達成率\n"
                "- パイプライン価値と構成\n"
                "- 活動要約率・フィードバック活用率\n"
                "\n"
                "## 出力フォーマット\n"
                "1. **サマリー**: 全体傾向を2-3行で\n"
                "2. **主要KPI**: 表形式で見やすく\n"
                "3. **ハイライト**: 良い点・注目すべき点\n"
                "4. **改善提案**: 優先度付きで3-5個\n"
                "5. **ネクストステップ**: マネージャーへの推奨アクション"
            ),
            name="performance_agent",
        )
