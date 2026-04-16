#!/usr/bin/env python3
"""デモデータ生成スクリプト - JSON + CSV 両方を出力"""

import csv
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)
OUTPUT_DIR = Path(__file__).parent

# ============================================================
# 1. 営業担当者（既存のまま - 10名）
# ============================================================
SALES_REPS = [
    {"id": "MGR001", "name": "佐藤 健一", "name_kana": "サトウ ケンイチ", "email": "sato.kenichi@styleworks.co.jp", "role": "マネージャー", "team": "東日本営業部", "manager_id": None, "hire_date": "2010-04-01", "territory": "東日本エリア統括", "target_quarterly_revenue": 50000000, "avatar_color": "#3B82F6"},
    {"id": "MGR002", "name": "山本 直子", "name_kana": "ヤマモト ナオコ", "email": "yamamoto.naoko@styleworks.co.jp", "role": "マネージャー", "team": "西日本営業部", "manager_id": None, "hire_date": "2012-04-01", "territory": "西日本エリア統括", "target_quarterly_revenue": 45000000, "avatar_color": "#8B5CF6"},
    {"id": "REP001", "name": "田中 太郎", "name_kana": "タナカ タロウ", "email": "tanaka.taro@styleworks.co.jp", "role": "フィールドセールス", "team": "東日本営業部", "manager_id": "MGR001", "hire_date": "2018-04-01", "territory": "東京都・神奈川県", "target_quarterly_revenue": 12000000, "avatar_color": "#10B981"},
    {"id": "REP002", "name": "鈴木 美咲", "name_kana": "スズキ ミサキ", "email": "suzuki.misaki@styleworks.co.jp", "role": "フィールドセールス", "team": "東日本営業部", "manager_id": "MGR001", "hire_date": "2020-04-01", "territory": "埼玉県・千葉県", "target_quarterly_revenue": 10000000, "avatar_color": "#F59E0B"},
    {"id": "REP003", "name": "高橋 翔太", "name_kana": "タカハシ ショウタ", "email": "takahashi.shota@styleworks.co.jp", "role": "フィールドセールス", "team": "東日本営業部", "manager_id": "MGR001", "hire_date": "2019-10-01", "territory": "北関東・東北", "target_quarterly_revenue": 10000000, "avatar_color": "#EF4444"},
    {"id": "REP004", "name": "渡辺 陽介", "name_kana": "ワタナベ ヨウスケ", "email": "watanabe.yosuke@styleworks.co.jp", "role": "フィールドセールス", "team": "東日本営業部", "manager_id": "MGR001", "hire_date": "2022-04-01", "territory": "北海道・甲信越", "target_quarterly_revenue": 8000000, "avatar_color": "#06B6D4"},
    {"id": "REP005", "name": "中村 愛", "name_kana": "ナカムラ アイ", "email": "nakamura.ai@styleworks.co.jp", "role": "フィールドセールス", "team": "西日本営業部", "manager_id": "MGR002", "hire_date": "2017-04-01", "territory": "大阪府・兵庫県", "target_quarterly_revenue": 12000000, "avatar_color": "#EC4899"},
    {"id": "REP006", "name": "伊藤 大輔", "name_kana": "イトウ ダイスケ", "email": "ito.daisuke@styleworks.co.jp", "role": "フィールドセールス", "team": "西日本営業部", "manager_id": "MGR002", "hire_date": "2021-04-01", "territory": "京都府・滋賀県・奈良県", "target_quarterly_revenue": 9000000, "avatar_color": "#14B8A6"},
    {"id": "REP007", "name": "小林 誠", "name_kana": "コバヤシ マコト", "email": "kobayashi.makoto@styleworks.co.jp", "role": "フィールドセールス", "team": "西日本営業部", "manager_id": "MGR002", "hire_date": "2019-04-01", "territory": "中国・四国地方", "target_quarterly_revenue": 9000000, "avatar_color": "#F97316"},
    {"id": "REP008", "name": "加藤 結衣", "name_kana": "カトウ ユイ", "email": "kato.yui@styleworks.co.jp", "role": "フィールドセールス", "team": "西日本営業部", "manager_id": "MGR002", "hire_date": "2023-04-01", "territory": "九州・沖縄", "target_quarterly_revenue": 8000000, "avatar_color": "#A855F7"},
]

# ============================================================
# 2. 顧客企業（15→30社に増量）
# ============================================================
CUSTOMERS = [
    {"id": "CUST001", "company_name": "株式会社東京ユニフォームサービス", "industry": "ユニフォーム・制服", "segment": "企業制服", "region": "東京都", "annual_revenue_estimate": 85000000, "primary_contact": "森田 浩二", "primary_contact_title": "購買部長", "relationship_since": "2019-06-15", "notes": "大手企業の社員制服を一括納入。年間10万枚以上の発注実績あり。"},
    {"id": "CUST002", "company_name": "プロモーションワークス株式会社", "industry": "イベント・販促", "segment": "イベント・プロモーション", "region": "東京都", "annual_revenue_estimate": 42000000, "primary_contact": "石川 真理", "primary_contact_title": "営業企画部マネージャー", "relationship_since": "2020-03-01", "notes": "企業イベント・展示会向けのオリジナルTシャツ制作を多数手掛ける。"},
    {"id": "CUST003", "company_name": "湘南スポーツクラブ", "industry": "スポーツ", "segment": "スポーツチーム", "region": "神奈川県", "annual_revenue_estimate": 15000000, "primary_contact": "藤井 健太", "primary_contact_title": "運営部長", "relationship_since": "2021-01-10", "notes": "地域密着型スポーツクラブ。約30チームのウェア供給。"},
    {"id": "CUST004", "company_name": "セレクトショップ URBAN STYLE", "industry": "小売", "segment": "小売・セレクトショップ", "region": "東京都", "annual_revenue_estimate": 28000000, "primary_contact": "西村 彩香", "primary_contact_title": "バイヤー", "relationship_since": "2022-05-20", "notes": "トレンド感のある無地Tシャツ中心のセレクト。ヘビーウェイト人気。"},
    {"id": "CUST005", "company_name": "埼玉県立総合教育センター", "industry": "教育", "segment": "官公庁・学校", "region": "埼玉県", "annual_revenue_estimate": 12000000, "primary_contact": "木村 正", "primary_contact_title": "事務局長", "relationship_since": "2020-09-01", "notes": "県内複数校向けに体操服・イベントTシャツを供給。入札案件が多い。"},
    {"id": "CUST006", "company_name": "プリントスター株式会社", "industry": "プリント・EC", "segment": "EC・プリント事業者", "region": "千葉県", "annual_revenue_estimate": 65000000, "primary_contact": "松本 大地", "primary_contact_title": "代表取締役", "relationship_since": "2018-04-01", "notes": "オンデマンドプリント事業者。無地ボディの大量仕入れが主。"},
    {"id": "CUST007", "company_name": "関西フードサービス株式会社", "industry": "飲食・サービス", "segment": "企業制服", "region": "大阪府", "annual_revenue_estimate": 38000000, "primary_contact": "吉田 裕子", "primary_contact_title": "総務部課長", "relationship_since": "2019-11-15", "notes": "飲食チェーン約80店舗のスタッフユニフォーム。"},
    {"id": "CUST008", "company_name": "大阪プロモーションセンター", "industry": "イベント・販促", "segment": "イベント・プロモーション", "region": "大阪府", "annual_revenue_estimate": 32000000, "primary_contact": "岡田 智也", "primary_contact_title": "企画ディレクター", "relationship_since": "2021-07-01", "notes": "関西圏の大型イベント・フェスのグッズ制作。"},
    {"id": "CUST009", "company_name": "京都織物工業株式会社", "industry": "繊維・製造", "segment": "小売・セレクトショップ", "region": "京都府", "annual_revenue_estimate": 22000000, "primary_contact": "井上 和夫", "primary_contact_title": "商品企画部長", "relationship_since": "2020-02-15", "notes": "和テイスト×ストリートのアパレルブランド展開。"},
    {"id": "CUST010", "company_name": "中国地方建設業協同組合", "industry": "建設", "segment": "企業制服", "region": "広島県", "annual_revenue_estimate": 18000000, "primary_contact": "山田 勝", "primary_contact_title": "事務局次長", "relationship_since": "2022-01-10", "notes": "組合加盟企業向け作業着・安全ベスト・Tシャツ供給。"},
    {"id": "CUST011", "company_name": "九州スポーツアカデミー", "industry": "スポーツ・教育", "segment": "スポーツチーム", "region": "福岡県", "annual_revenue_estimate": 20000000, "primary_contact": "原田 大介", "primary_contact_title": "アカデミー長", "relationship_since": "2021-04-01", "notes": "サッカー・野球・バスケのアカデミー。年間契約。"},
    {"id": "CUST012", "company_name": "デジタルプリントジャパン株式会社", "industry": "プリント・EC", "segment": "EC・プリント事業者", "region": "大阪府", "annual_revenue_estimate": 55000000, "primary_contact": "村上 恵美", "primary_contact_title": "仕入部長", "relationship_since": "2019-08-01", "notes": "DTF・DTGプリント専門。全国のクリエイター向けサービス。"},
    {"id": "CUST013", "company_name": "北海道観光振興機構", "industry": "観光・自治体", "segment": "官公庁・学校", "region": "北海道", "annual_revenue_estimate": 8000000, "primary_contact": "佐々木 誠一", "primary_contact_title": "企画課主任", "relationship_since": "2023-03-01", "notes": "観光プロモーション用オリジナルグッズ制作。"},
    {"id": "CUST014", "company_name": "株式会社横浜クリエイティブ", "industry": "デザイン・クリエイティブ", "segment": "EC・プリント事業者", "region": "神奈川県", "annual_revenue_estimate": 18000000, "primary_contact": "川口 美穂", "primary_contact_title": "プロダクションマネージャー", "relationship_since": "2022-09-15", "notes": "アーティスト・バンドのオフィシャルグッズ制作。"},
    {"id": "CUST015", "company_name": "四国メディカルサプライ株式会社", "industry": "医療・介護", "segment": "企業制服", "region": "愛媛県", "annual_revenue_estimate": 25000000, "primary_contact": "三浦 健二", "primary_contact_title": "営業部長", "relationship_since": "2021-06-01", "notes": "病院・介護施設のスタッフウェア。"},
    # 追加顧客（16-30）
    {"id": "CUST016", "company_name": "株式会社名古屋テキスタイル", "industry": "アパレル", "segment": "小売・セレクトショップ", "region": "愛知県", "annual_revenue_estimate": 35000000, "primary_contact": "近藤 裕也", "primary_contact_title": "MD部長", "relationship_since": "2020-08-01", "notes": "名古屋圏のセレクトショップ5店舗を展開。無地ボディのPB展開に積極的。"},
    {"id": "CUST017", "company_name": "株式会社アスリートワン", "industry": "スポーツ", "segment": "スポーツチーム", "region": "東京都", "annual_revenue_estimate": 30000000, "primary_contact": "谷口 翔", "primary_contact_title": "商品企画リーダー", "relationship_since": "2019-05-15", "notes": "実業団・社会人スポーツチーム向けウェアの企画販売。年間5万枚。"},
    {"id": "CUST018", "company_name": "グラフィックプリント北関東", "industry": "プリント・EC", "segment": "EC・プリント事業者", "region": "群馬県", "annual_revenue_estimate": 20000000, "primary_contact": "関根 太一", "primary_contact_title": "工場長", "relationship_since": "2021-11-01", "notes": "シルクスクリーンプリント中心。地元企業のノベルティ制作。"},
    {"id": "CUST019", "company_name": "東北自動車販売協会", "industry": "自動車", "segment": "企業制服", "region": "宮城県", "annual_revenue_estimate": 15000000, "primary_contact": "阿部 和彦", "primary_contact_title": "総務委員長", "relationship_since": "2023-01-15", "notes": "加盟ディーラーのスタッフポロシャツ統一化プロジェクト。"},
    {"id": "CUST020", "company_name": "株式会社沖縄リゾートマネジメント", "industry": "ホテル・観光", "segment": "企業制服", "region": "沖縄県", "annual_revenue_estimate": 12000000, "primary_contact": "上原 明", "primary_contact_title": "購買担当", "relationship_since": "2024-02-01", "notes": "リゾートホテル3施設のスタッフカジュアルユニフォーム。"},
    {"id": "CUST021", "company_name": "新潟県温泉旅館組合", "industry": "観光・宿泊", "segment": "官公庁・学校", "region": "新潟県", "annual_revenue_estimate": 6000000, "primary_contact": "斎藤 正夫", "primary_contact_title": "事務局長", "relationship_since": "2024-04-01", "notes": "組合加盟旅館のお土産・スタッフTシャツ。"},
    {"id": "CUST022", "company_name": "宇都宮フットサルリーグ", "industry": "スポーツ", "segment": "スポーツチーム", "region": "栃木県", "annual_revenue_estimate": 5000000, "primary_contact": "石原 拓也", "primary_contact_title": "事務局長", "relationship_since": "2024-05-01", "notes": "リーグ統一ウェア導入検討中。20チーム参加。"},
    {"id": "CUST023", "company_name": "テクノロジーパーク株式会社", "industry": "IT", "segment": "企業制服", "region": "東京都", "annual_revenue_estimate": 45000000, "primary_contact": "橋本 隆", "primary_contact_title": "人事総務部長", "relationship_since": "2022-07-01", "notes": "IT企業のカジュアルオフィスウェア。社員2000名規模。"},
    {"id": "CUST024", "company_name": "札幌ラーメン街道協会", "industry": "飲食", "segment": "企業制服", "region": "北海道", "annual_revenue_estimate": 8000000, "primary_contact": "田村 誠", "primary_contact_title": "会長", "relationship_since": "2023-09-01", "notes": "加盟ラーメン店50店舗のスタッフTシャツ。"},
    {"id": "CUST025", "company_name": "関東学生陸上競技連盟", "industry": "スポーツ・教育", "segment": "スポーツチーム", "region": "東京都", "annual_revenue_estimate": 10000000, "primary_contact": "久保田 修", "primary_contact_title": "事務局次長", "relationship_since": "2021-03-01", "notes": "大学駅伝・陸上大会の公式ウェア。ドライ素材必須。"},
    {"id": "CUST026", "company_name": "西日本物流株式会社", "industry": "物流", "segment": "企業制服", "region": "兵庫県", "annual_revenue_estimate": 22000000, "primary_contact": "佐野 正義", "primary_contact_title": "管理部長", "relationship_since": "2020-06-15", "notes": "物流センタースタッフ約500名のユニフォーム。蛍光ベスト含む。"},
    {"id": "CUST027", "company_name": "クリエイティブラボ東京", "industry": "デザイン", "segment": "EC・プリント事業者", "region": "東京都", "annual_revenue_estimate": 25000000, "primary_contact": "松田 あゆみ", "primary_contact_title": "クリエイティブディレクター", "relationship_since": "2022-04-01", "notes": "アパレルブランドのOEM・ODM。デザイナーズブランド複数展開。"},
    {"id": "CUST028", "company_name": "神戸市スポーツ振興協会", "industry": "自治体", "segment": "官公庁・学校", "region": "兵庫県", "annual_revenue_estimate": 9000000, "primary_contact": "遠藤 健次", "primary_contact_title": "事業課長", "relationship_since": "2023-04-01", "notes": "市民スポーツ大会、マラソン大会の参加者Tシャツ。"},
    {"id": "CUST029", "company_name": "株式会社福岡ワーカーズ", "industry": "人材・派遣", "segment": "企業制服", "region": "福岡県", "annual_revenue_estimate": 16000000, "primary_contact": "中島 大樹", "primary_contact_title": "業務管理部長", "relationship_since": "2022-10-01", "notes": "派遣スタッフ向けユニフォーム。多業種対応で色分け必要。"},
    {"id": "CUST030", "company_name": "岡山デニムストリート", "industry": "アパレル", "segment": "小売・セレクトショップ", "region": "岡山県", "annual_revenue_estimate": 14000000, "primary_contact": "武田 一郎", "primary_contact_title": "店長", "relationship_since": "2023-06-01", "notes": "岡山デニムとのコラボ商品を展開。無地ボディへのプリント加工。"},
]

# ============================================================
# ヘルパー関数
# ============================================================

PRODUCTS = [
    "5001-01 ヘビーウェイトTシャツ", "5900-01 ドライアスレチックTシャツ",
    "5214-01 スウェットプルオーバーパーカー", "2020-01 ドライカノコポロシャツ",
    "5004-01 ポケット付きTシャツ", "5942-01 ドライアスレチックロングスリーブTシャツ",
    "5029-01 ヘビーウェイトロングスリーブTシャツ", "5044-01 10.0オンス スウェットパンツ",
    "1520-01 キャンバストートバッグ", "9660-01 フラットバイザーキャップ",
]
COLORS = ["ホワイト", "ブラック", "ネイビー", "ロイヤルブルー", "レッド", "ミックスグレー", "ナチュラル", "バーガンディ", "フォレストグリーン", "ターコイズブルー", "蛍光イエロー", "蛍光オレンジ", "サンドカーキ", "スモーキーグリーン", "パステルピンク", "チャコール"]
COMPETITORS = ["トムス", "ギルダン", "プリントスター社", "Hanes", "地元業者", "ジャージーズ", None, None, None]
ACTIVITY_TYPES = ["訪問", "電話", "Web会議", "メール", "展示会"]
SENTIMENTS = ["positive", "positive", "positive", "neutral", "neutral", "neutral", "negative"]
STAGES = ["リード", "初回提案", "提案中", "見積提出", "交渉中", "受注", "失注"]
STAGE_WEIGHTS = [15, 10, 15, 10, 10, 25, 15]
DEAL_PRODUCT_CATS = ["ヘビーウェイトTシャツ", "ドライTシャツ", "ポロシャツ", "スウェット・パーカー", "Tシャツ・ポロシャツ", "ドライTシャツ・ヘビーウェイトTシャツ"]
LOSS_REASONS = [
    "価格で劣後。競合の見積りが当社より約8%安かった。",
    "納期が合わなかった。先方の希望納期に対して2週間遅れの回答だった。",
    "先方の予算縮小により案件自体が中止。",
    "競合が先行してサンプル提出済みで、品質確認も完了していたため逆転困難。",
    "顧客の担当者異動により、新担当が既存取引先を優先。",
    "カラーバリエーションが先方の要望に合わなかった。",
]

COMMENT_TEMPLATES = {
    "訪問": [
        "{contact}を訪問。{subject_detail}。{product}の提案を実施。{reaction}。{next_action}。",
        "{contact}を訪問。{subject_detail}について打ち合わせ。{detail}。{follow_up}。",
        "{contact}訪問。{subject_detail}。先方からは{reaction}。競合は{competitor}が入っているとの情報。{next_action}。",
        "{contact}を訪問し、{subject_detail}について協議。{product}への関心が高い。サンプル{colors}を送付予定。見積りは{quantity}枚規模で依頼あり。{next_action}。",
        "{contact}を訪問。年間契約の更新交渉。昨年度は{product}を中心に約{prev_quantity}枚の実績。今年度は{growth}。{pricing}。{next_action}。",
    ],
    "電話": [
        "{contact}より電話。{subject_detail}について。{detail}。{follow_up}。",
        "{contact}に架電。{subject_detail}の確認。{reaction}。{next_action}。",
        "{contact}より問い合わせ電話。{product}の{detail}。{quantity}枚の見込み。{follow_up}。",
        "{contact}に定期フォロー電話。{subject_detail}。{reaction}。次回は{next_action}。",
    ],
    "Web会議": [
        "{contact}とWeb会議。{subject_detail}について。{detail}。{follow_up}。",
        "{contact}とオンライン打ち合わせ。{subject_detail}の詳細を確認。{product}の{detail}。{next_action}。",
        "{contact}とWeb会議で{subject_detail}について協議。{reaction}。見積り{quantity}枚ベースで作成予定。{follow_up}。",
    ],
    "メール": [
        "{contact}宛に{subject_detail}のメールを送付。{detail}。{follow_up}。",
        "{contact}からメール返信。{subject_detail}について。{reaction}。{next_action}。",
        "{contact}にカタログ・サンプル({product} {colors})を送付完了。{follow_up}。",
    ],
    "展示会": [
        "{event_name}に出展。{contact}を含む{visitor_count}名と名刺交換。{product}への関心が高い来場者多数。{detail}。{follow_up}。",
    ],
}

REACTIONS = [
    "好感触で前向きな反応", "興味を示されたが価格面で慎重", "予算確保が課題とのこと",
    "品質に満足いただけた", "競合比較中で返答待ち", "即決には至らず検討中",
    "非常に前向きで早期発注を検討中", "現行品との比較を希望",
    "サンプル確認後に正式検討とのこと", "担当者変更の可能性あり注意",
]
NEXT_ACTIONS = [
    "来週サンプル送付予定", "見積り作成後に再訪問", "GW明けに再度連絡",
    "社内で価格承認を取得後回答", "次回訪問時にプレゼン資料持参",
    "倉庫に在庫状況を確認して回答", "1週間以内にフォローアップ電話",
    "来月の定期訪問で進捗確認", "上長承認後に正式提案",
]

REP_IDS = [f"REP{i:03d}" for i in range(1, 9)]
CUST_IDS = [c["id"] for c in CUSTOMERS]
CUST_BY_ID = {c["id"]: c for c in CUSTOMERS}
REP_BY_ID = {r["id"]: r for r in SALES_REPS}

# 担当者ごとの主要顧客マッピング
REP_CUSTOMER_MAP = {
    "REP001": ["CUST001", "CUST002", "CUST004", "CUST023", "CUST027"],
    "REP002": ["CUST005", "CUST006", "CUST018", "CUST025"],
    "REP003": ["CUST003", "CUST013", "CUST017", "CUST022"],
    "REP004": ["CUST014", "CUST021", "CUST024", "CUST019"],
    "REP005": ["CUST007", "CUST008", "CUST026", "CUST028"],
    "REP006": ["CUST009", "CUST012", "CUST016"],
    "REP007": ["CUST010", "CUST015", "CUST030"],
    "REP008": ["CUST011", "CUST020", "CUST029"],
}


def gen_date(start: str, end: str) -> str:
    s = datetime.strptime(start, "%Y-%m-%d")
    e = datetime.strptime(end, "%Y-%m-%d")
    d = s + timedelta(days=random.randint(0, (e - s).days))
    return d.strftime("%Y-%m-%d")


def gen_comment(act_type: str, cust: dict, product: str) -> str:
    templates = COMMENT_TEMPLATES.get(act_type, COMMENT_TEMPLATES["電話"])
    tpl = random.choice(templates)
    return tpl.format(
        contact=f"{cust['company_name']}{cust['primary_contact']}{cust['primary_contact_title']}",
        subject_detail=random.choice([
            f"{product}の新規提案", f"年間契約更新交渉", f"追加発注の打ち合わせ",
            f"サンプル評価フィードバック", f"来期の発注計画確認", f"新商品ラインナップ提案",
            f"在庫状況の確認と発注調整", f"価格改定の協議",
        ]),
        product=product,
        detail=random.choice([
            "吸汗速乾素材のニーズが高まっているとのこと",
            f"サンプル3色を来週送付予定",
            "現行品との比較テストを実施中",
            "刺繍・プリント加工の仕様を詳細確認",
            "納期は来月末を希望",
            "新色の追加を検討中",
        ]),
        reaction=random.choice(REACTIONS),
        next_action=random.choice(NEXT_ACTIONS),
        follow_up=random.choice(NEXT_ACTIONS),
        competitor=random.choice([c for c in COMPETITORS if c]) if random.random() > 0.5 else "不明",
        colors=f"{random.choice(COLORS)}・{random.choice(COLORS)}",
        quantity=random.choice([500, 1000, 2000, 3000, 5000, 8000, 10000, 15000, 20000]),
        prev_quantity=random.choice([1000, 2000, 3000, 5000]),
        growth=random.choice(["10%増の見込み", "20%増の見込み", "横ばいの見込み", "拡大予定"]),
        pricing=random.choice(["単価交渉が必要", "価格据え置きで合意", "ボリュームディスカウントを提案"]),
        event_name=random.choice(["東京ビジネスEXPO", "関西プリントフェア", "スポーツ用品展示会"]),
        visitor_count=random.randint(5, 30),
    )


# ============================================================
# 3. 商談データ生成（60件）
# ============================================================
DEALS = []
deal_counter = 0

for rep_id in REP_IDS:
    custs = REP_CUSTOMER_MAP.get(rep_id, [])
    # 各担当者あたり6-9件の商談
    n_deals = random.randint(6, 9)
    for i in range(n_deals):
        deal_counter += 1
        cust_id = random.choice(custs) if custs and random.random() > 0.15 else None
        stage = random.choices(STAGES, weights=STAGE_WEIGHTS, k=1)[0]

        if stage == "受注":
            amount = random.choice([1500000, 2800000, 5000000, 8000000, 12000000, 18000000, 22000000, 35000000])
            prob = 100
            close = gen_date("2025-01-01", "2026-03-31")
            loss = None
        elif stage == "失注":
            amount = random.choice([1200000, 3000000, 4500000, 6000000, 9000000])
            prob = 0
            close = gen_date("2025-01-01", "2026-03-31")
            loss = random.choice(LOSS_REASONS)
        else:
            amount = random.choice([500000, 800000, 1500000, 2400000, 3500000, 5000000, 8000000, 12000000, 18000000, 25000000, 45000000])
            prob = random.choice([20, 30, 35, 40, 50, 60, 65, 70, 75, 80, 90])
            close = gen_date("2026-04-01", "2026-12-31")
            loss = None

        # 意図的に一部フィールドをNullにする（未入力テスト用）
        if stage not in ("受注", "失注") and random.random() < 0.2:
            amount = None
            prob = None
        if stage not in ("受注", "失注") and random.random() < 0.15:
            close = None
        prod_cat = random.choice(DEAL_PRODUCT_CATS) if random.random() > 0.1 else None
        qty = random.choice([200, 500, 1000, 1500, 2000, 3000, 5000, 8000, 10000, 15000, 20000, 50000]) if random.random() > 0.12 else None

        cust_name = CUST_BY_ID[cust_id]["company_name"] if cust_id else "未登録顧客"
        deal_suffix = random.choice([
            "年間契約", "追加発注", "新規提案", "リニューアル案件", "入札案件",
            "季節商品", "イベント案件", "スポーツウェア", "ユニフォーム", "PB商品",
            "下期ユニフォーム", "定期発注Q2", "夏季キャンペーン", "秋冬コレクション",
        ])

        deal = {
            "id": f"DEAL{deal_counter:03d}",
            "rep_id": rep_id,
            "customer_id": cust_id,
            "deal_name": f"{cust_name} {deal_suffix}",
            "stage": stage,
            "amount": amount,
            "probability": prob,
            "expected_close_date": close,
            "product_category": prod_cat,
            "quantity_estimate": qty,
            "competitor": random.choice(COMPETITORS),
            "loss_reason": loss,
            "notes": f"{cust_name}との{deal_suffix}。{'大口案件。' if (amount or 0) > 10000000 else ''}",
        }
        DEALS.append(deal)

# ============================================================
# 4. 活動データ生成（100件）
# ============================================================
ACTIVITIES = []
act_counter = 0
DEAL_BY_ID = {d["id"]: d for d in DEALS}

for rep_id in REP_IDS:
    custs = REP_CUSTOMER_MAP.get(rep_id, [])
    rep_deals = [d for d in DEALS if d["rep_id"] == rep_id and d["stage"] not in ("受注", "失注")]
    # 各担当者12-15件の活動
    n_acts = random.randint(12, 15)
    for i in range(n_acts):
        act_counter += 1
        cust_id = random.choice(custs) if custs and random.random() > 0.1 else None
        act_type = random.choices(ACTIVITY_TYPES, weights=[30, 25, 15, 20, 10] if act_counter % 10 != 0 else [5, 5, 5, 5, 80], k=1)[0]
        if act_type == "展示会":
            act_type = random.choice(["訪問", "電話", "Web会議"])  # 展示会は稀

        cust = CUST_BY_ID.get(cust_id, {"company_name": "新規見込み客", "primary_contact": "担当者", "primary_contact_title": ""})
        product = random.choice(PRODUCTS)
        date = gen_date("2026-01-15", "2026-04-14")

        # 関連商談
        deal_id = None
        if cust_id and rep_deals:
            matching = [d for d in rep_deals if d["customer_id"] == cust_id]
            if matching:
                deal_id = random.choice(matching)["id"]

        comment = gen_comment(act_type, cust, product)
        subject_options = [
            f"{cust['company_name']}への{product.split(' ')[1] if ' ' in product else product}提案",
            f"{cust['company_name']} 定期フォロー",
            f"{cust['company_name']} 追加発注確認",
            f"サンプル送付・フィードバック確認",
            f"来期発注計画のすり合わせ",
            f"新商品ラインナップ提案",
            f"在庫状況確認と納期調整",
            f"価格改定の相談",
            f"年間契約更新交渉",
            f"新規案件ヒアリング",
        ]

        tags = []
        for kw in ["ドライ", "ヘビーウェイト", "ポロシャツ", "スウェット", "パーカー"]:
            if kw in product or kw in comment:
                tags.append(kw)
        if (amount or 0) > 10000000 or "大口" in comment:
            tags.append("大口案件")
        for comp in ["トムス", "ギルダン", "プリントスター"]:
            if comp in comment:
                tags.append(f"競合{comp}")
        for kw in ["入札", "新規", "サンプル", "納期", "価格", "契約更新"]:
            if kw in comment:
                tags.append(kw)
        tags = list(set(tags))[:5]

        activity = {
            "id": f"ACT{act_counter:03d}",
            "rep_id": rep_id,
            "customer_id": cust_id,
            "activity_type": act_type,
            "date": date,
            "duration_minutes": random.choice([10, 15, 20, 25, 30, 40, 45, 50, 60, 75, 90, 120]),
            "subject": random.choice(subject_options),
            "comment": comment,
            "sentiment": random.choice(SENTIMENTS),
            "deal_id": deal_id,
            "follow_up_date": (datetime.strptime(date, "%Y-%m-%d") + timedelta(days=random.randint(3, 14))).strftime("%Y-%m-%d") if random.random() > 0.2 else None,
            "tags": tags,
        }
        ACTIVITIES.append(activity)

# Sort activities by date descending
ACTIVITIES.sort(key=lambda x: x["date"], reverse=True)

# ============================================================
# 5. ナレッジ記事（既存15件を維持 - 手書きの方が品質が高い）
# ============================================================
# loader.pyから既存データを読み込む
with open(OUTPUT_DIR / "knowledge_articles.json", "r", encoding="utf-8") as f:
    KNOWLEDGE_ARTICLES = json.load(f)

# ============================================================
# 6. パフォーマンス指標（4四半期分に拡大）
# ============================================================
PERFORMANCE_METRICS = []
for rep_id in REP_IDS:
    for period in ["2025-Q2", "2025-Q3", "2025-Q4", "2026-Q1"]:
        base_activity = random.randint(28, 55)
        visits = int(base_activity * random.uniform(0.28, 0.40))
        calls = int(base_activity * random.uniform(0.22, 0.35))
        web = int(base_activity * random.uniform(0.10, 0.22))
        emails = base_activity - visits - calls - web

        deals_created = random.randint(1, 5)
        deals_won = random.randint(0, min(deals_created, 3))
        deals_lost = random.randint(0, min(deals_created - deals_won, 2))
        conv_rate = round(deals_won / deals_created, 2) if deals_created > 0 else 0

        rev_won = deals_won * random.choice([2000000, 3500000, 5000000, 8000000, 12000000, 15000000]) if deals_won > 0 else 0
        pipeline = random.choice([2000000, 5000000, 8000000, 12000000, 18000000, 25000000, 35000000, 48000000])

        metric = {
            "rep_id": rep_id,
            "period": period,
            "activities_count": base_activity,
            "visits_count": visits,
            "calls_count": calls,
            "web_meetings_count": web,
            "emails_count": emails,
            "deals_created": deals_created,
            "deals_won": deals_won,
            "deals_lost": deals_lost,
            "revenue_won": rev_won,
            "pipeline_value": pipeline,
            "conversion_rate": conv_rate,
            "avg_deal_cycle_days": random.randint(25, 65) if deals_won > 0 else 0,
            "activity_summary_rate": round(random.uniform(0.65, 0.98), 2),
            "feedback_utilization_rate": round(random.uniform(0.45, 0.90), 2),
            "knowledge_contributions": random.randint(0, 5),
        }
        PERFORMANCE_METRICS.append(metric)


# ============================================================
# 書き出し
# ============================================================

def write_json(data: list, filename: str):
    with open(OUTPUT_DIR / filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  JSON: {filename} ({len(data)}件)")


def write_csv(data: list, filename: str):
    if not data:
        return
    csv_dir = OUTPUT_DIR / "csv"
    csv_dir.mkdir(exist_ok=True)
    keys = list(data[0].keys())
    with open(csv_dir / filename, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for row in data:
            flat = {}
            for k, v in row.items():
                if isinstance(v, list):
                    flat[k] = "; ".join(str(x) for x in v)
                elif v is None:
                    flat[k] = ""
                else:
                    flat[k] = v
            writer.writerow(flat)
    print(f"  CSV:  csv/{filename} ({len(data)}件)")


if __name__ == "__main__":
    print("デモデータを生成中...")
    print()

    write_json(SALES_REPS, "sales_reps.json")
    write_csv(SALES_REPS, "sales_reps.csv")

    write_json(CUSTOMERS, "customers.json")
    write_csv(CUSTOMERS, "customers.csv")

    write_json(ACTIVITIES, "activities.json")
    write_csv(ACTIVITIES, "activities.csv")

    write_json(DEALS, "deals.json")
    write_csv(DEALS, "deals.csv")

    # ナレッジは既存を維持
    write_csv(KNOWLEDGE_ARTICLES, "knowledge_articles.csv")

    write_json(PERFORMANCE_METRICS, "performance_metrics.json")
    write_csv(PERFORMANCE_METRICS, "performance_metrics.csv")

    print()
    print("完了！")
    print(f"  営業担当者: {len(SALES_REPS)}名")
    print(f"  顧客企業:   {len(CUSTOMERS)}社")
    print(f"  活動記録:   {len(ACTIVITIES)}件")
    print(f"  商談データ: {len(DEALS)}件")
    print(f"  ナレッジ:   {len(KNOWLEDGE_ARTICLES)}件")
    print(f"  KPI指標:    {len(PERFORMANCE_METRICS)}件 ({len(PERFORMANCE_METRICS)//8}四半期)")
