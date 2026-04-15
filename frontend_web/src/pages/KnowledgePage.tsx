import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { demoApi } from '@/api/demo/api-requests';
import type { KnowledgeArticle, PerformanceMetric } from '@/api/demo/types';

const CATEGORIES = ['全て', '営業ノウハウ', '商品知識', '成功事例', '業界動向', '競合情報'];

const CATEGORY_COLORS: Record<string, string> = {
  '営業ノウハウ': 'bg-blue-100 text-blue-800',
  '商品知識': 'bg-green-100 text-green-800',
  '成功事例': 'bg-yellow-100 text-yellow-800',
  '業界動向': 'bg-purple-100 text-purple-800',
  '競合情報': 'bg-red-100 text-red-800',
};

function formatYen(amount: number): string {
  if (amount >= 100000000) return `${(amount / 100000000).toFixed(1)}億円`;
  if (amount >= 10000) return `${(amount / 10000).toFixed(0)}万円`;
  return `${amount}円`;
}

export function KnowledgePage() {
  const navigate = useNavigate();
  const [articles, setArticles] = useState<KnowledgeArticle[]>([]);
  const [metrics, setMetrics] = useState<PerformanceMetric[]>([]);
  const [selectedCategory, setSelectedCategory] = useState('全て');
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedArticle, setExpandedArticle] = useState<string | null>(null);

  useEffect(() => {
    demoApi.getKnowledge().then(setArticles).catch(console.error);
    demoApi.getMetrics(undefined, '2026-Q1').then(setMetrics).catch(console.error);
  }, []);

  const filteredArticles = articles.filter(a => {
    if (selectedCategory !== '全て' && a.category !== selectedCategory) return false;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      const searchable = (a.title + ' ' + a.content + ' ' + a.tags.join(' ')).toLowerCase();
      return searchable.includes(q);
    }
    return true;
  });

  const topArticles = [...articles]
    .sort((a, b) => b.helpfulness_score - a.helpfulness_score)
    .slice(0, 5);

  const avgConversion = metrics.length > 0
    ? metrics.reduce((sum, m) => sum + m.conversion_rate, 0) / metrics.length
    : 0;
  const totalRevenue = metrics.reduce((sum, m) => sum + m.revenue_won, 0);
  const totalPipeline = metrics.reduce((sum, m) => sum + m.pipeline_value, 0);

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold">ナレッジ＆分析</h1>
        <p className="text-sm text-muted-foreground">営業ナレッジの検索とチームパフォーマンスの分析</p>
      </div>

      {/* Search & Category Filter */}
      <div className="space-y-3">
        <Input
          placeholder="ナレッジを検索（例: ドライTシャツ, 価格交渉, 入札...）"
          value={searchQuery}
          onChange={e => setSearchQuery(e.target.value)}
          className="max-w-xl"
        />
        <div className="flex gap-2 flex-wrap">
          {CATEGORIES.map(cat => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
                selectedCategory === cat
                  ? 'bg-blue-600 text-white'
                  : 'bg-muted text-muted-foreground hover:bg-muted/80'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Article List */}
        <div className="lg:col-span-2 space-y-3">
          <h2 className="text-lg font-semibold">
            ナレッジ記事
            <span className="text-sm font-normal text-muted-foreground ml-2">
              {filteredArticles.length}件
            </span>
          </h2>
          {filteredArticles.map(article => (
            <Card key={article.id} className="transition-shadow hover:shadow-sm">
              <CardContent className="p-4">
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div>
                    <Badge className={`text-[10px] px-1.5 py-0 mr-2 ${CATEGORY_COLORS[article.category] || 'bg-gray-100'}`}>
                      {article.category}
                    </Badge>
                    <span className="text-[10px] text-muted-foreground">{article.subcategory}</span>
                  </div>
                  <div className="flex items-center gap-2 text-[10px] text-muted-foreground">
                    <span>👁 {article.views}</span>
                    <span>⭐ {article.helpfulness_score}</span>
                  </div>
                </div>
                <h3 className="text-sm font-medium mb-2">{article.title}</h3>
                <p className={`text-xs text-muted-foreground ${expandedArticle === article.id ? '' : 'line-clamp-3'}`}>
                  {article.content}
                </p>
                <button
                  onClick={() => setExpandedArticle(expandedArticle === article.id ? null : article.id)}
                  className="text-xs text-blue-600 mt-1 hover:underline"
                >
                  {expandedArticle === article.id ? '折りたたむ' : '全文を表示'}
                </button>
                <div className="flex flex-wrap gap-1 mt-2">
                  {article.tags.map(tag => (
                    <span key={tag} className="text-[10px] px-1.5 py-0.5 rounded bg-muted text-muted-foreground">
                      {tag}
                    </span>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
          {filteredArticles.length === 0 && (
            <div className="text-center text-muted-foreground py-12">
              該当するナレッジ記事がありません
            </div>
          )}
        </div>

        {/* Performance Panel */}
        <div className="space-y-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">チームパフォーマンス (2026-Q1)</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <div className="text-xs text-muted-foreground">受注合計</div>
                  <div className="text-lg font-bold text-green-600">{formatYen(totalRevenue)}</div>
                </div>
                <div>
                  <div className="text-xs text-muted-foreground">パイプライン</div>
                  <div className="text-lg font-bold text-blue-600">{formatYen(totalPipeline)}</div>
                </div>
                <div>
                  <div className="text-xs text-muted-foreground">平均受注率</div>
                  <div className="text-lg font-bold">{Math.round(avgConversion * 100)}%</div>
                </div>
                <div>
                  <div className="text-xs text-muted-foreground">総活動数</div>
                  <div className="text-lg font-bold">{metrics.reduce((s, m) => s + m.activities_count, 0)}件</div>
                </div>
              </div>
              <button
                onClick={() => {
                  navigate('/chat');
                }}
                className="w-full text-xs text-center py-2 rounded-md bg-blue-50 text-blue-600 hover:bg-blue-100 transition-colors font-medium"
              >
                AIに詳しい分析を依頼 →
              </button>
            </CardContent>
          </Card>

          {/* Top Articles */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">おすすめナレッジ</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {topArticles.map(article => (
                <button
                  key={article.id}
                  onClick={() => {
                    setSelectedCategory('全て');
                    setSearchQuery('');
                    setExpandedArticle(article.id);
                    document.getElementById(article.id)?.scrollIntoView({ behavior: 'smooth' });
                  }}
                  className="w-full text-left p-2 rounded hover:bg-muted transition-colors"
                >
                  <div className="text-xs font-medium line-clamp-1">{article.title}</div>
                  <div className="flex items-center gap-2 text-[10px] text-muted-foreground">
                    <Badge className={`text-[9px] px-1 py-0 ${CATEGORY_COLORS[article.category] || ''}`}>
                      {article.category}
                    </Badge>
                    <span>⭐ {article.helpfulness_score}</span>
                  </div>
                </button>
              ))}
            </CardContent>
          </Card>

          {/* Quick AI Actions */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">AIナレッジアシスト</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {[
                { label: 'ドライTシャツの提案ポイントを教えて', icon: '👕' },
                { label: '価格交渉のコツを教えて', icon: '💰' },
                { label: '新規開拓のスクリプトを見せて', icon: '📞' },
              ].map(item => (
                <button
                  key={item.label}
                  onClick={() => {
                    navigate('/chat');
                  }}
                  className="w-full text-left text-xs p-2 rounded hover:bg-muted transition-colors flex items-center gap-2"
                >
                  <span>{item.icon}</span>
                  <span>{item.label}</span>
                </button>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
