import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useChatDrawer } from '@/components/block/chat/ChatDrawerContext';
import { demoApi } from '@/api/demo/api-requests';
import type { DashboardSummary, SalesRep, Activity, PerformanceMetric } from '@/api/demo/types';

function formatYen(amount: number): string {
  if (amount >= 100000000) return `${(amount / 100000000).toFixed(1)}億円`;
  if (amount >= 10000) return `${(amount / 10000).toFixed(0)}万円`;
  return `${amount}円`;
}

function KpiCard({ title, value, subtitle, color }: { title: string; value: string; subtitle: string; color: string }) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className={`text-2xl font-bold ${color}`}>{value}</div>
        <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>
      </CardContent>
    </Card>
  );
}

export function DashboardPage() {
  const navigate = useNavigate();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const { openDrawer } = useChatDrawer();
  const [reps, setReps] = useState<SalesRep[]>([]);
  const [recentActivities, setRecentActivities] = useState<Record<string, Activity[]>>({});
  const [metrics, setMetrics] = useState<PerformanceMetric[]>([]);

  useEffect(() => {
    demoApi.getDashboardSummary().then(setSummary).catch(console.error);
    demoApi.getReps().then(data => {
      setReps(data.filter(r => r.role !== 'マネージャー'));
      data.filter(r => r.role !== 'マネージャー').forEach(rep => {
        demoApi.getRepActivities(rep.id, 3).then(acts => {
          setRecentActivities(prev => ({ ...prev, [rep.id]: acts }));
        });
      });
    }).catch(console.error);
    demoApi.getMetrics(undefined, '2026-Q1').then(setMetrics).catch(console.error);
  }, []);

  if (!summary) {
    return <div className="flex items-center justify-center h-full text-muted-foreground">読み込み中...</div>;
  }

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">マネージャーダッシュボード</h1>
        <p className="text-sm text-muted-foreground">{summary.period} | チーム全体の活動状況とAIエージェントの貢献度</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          title="活動要約率"
          value={`${Math.round(summary.avg_activity_summary_rate * 100)}%`}
          subtitle="AI要約の活用率"
          color="text-blue-600"
        />
        <KpiCard
          title="FB活用率"
          value={`${Math.round(summary.avg_feedback_utilization_rate * 100)}%`}
          subtitle="AIフィードバックの採用率"
          color="text-green-600"
        />
        <KpiCard
          title="未入力商談"
          value={`${summary.incomplete_deals_count}件`}
          subtitle="要補完の商談データ"
          color="text-orange-600"
        />
        <KpiCard
          title="パイプライン"
          value={formatYen(summary.total_pipeline)}
          subtitle={`受注済: ${formatYen(summary.total_revenue_won)}`}
          color="text-purple-600"
        />
      </div>

      {/* Team Activity + Feedback */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Team Activity List */}
        <div className="lg:col-span-2 space-y-3">
          <h2 className="text-lg font-semibold">チーム活動状況</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {reps.map(rep => {
              const repMetric = metrics.find(m => m.rep_id === rep.id);
              const acts = recentActivities[rep.id] || [];
              return (
                <Card
                  key={rep.id}
                  className="cursor-pointer hover:shadow-md transition-shadow"
                  onClick={() => navigate(`/review/${rep.id}`)}
                >
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3 mb-3">
                      <div
                        className="w-10 h-10 rounded-full flex items-center justify-center text-white text-sm font-bold"
                        style={{ backgroundColor: rep.avatar_color }}
                      >
                        {rep.name.charAt(0)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-sm">{rep.name}</div>
                        <div className="text-xs text-muted-foreground">{rep.team} | {rep.territory}</div>
                      </div>
                      {repMetric && (
                        <Badge variant="secondary" className="text-xs">
                          {repMetric.activities_count}件
                        </Badge>
                      )}
                    </div>
                    {acts.length > 0 && (
                      <div className="space-y-1">
                        {acts.slice(0, 2).map(act => (
                          <div key={act.id} className="text-xs text-muted-foreground truncate">
                            <span className="text-foreground font-medium">{act.date}</span>{' '}
                            <Badge variant="outline" className="text-[10px] px-1 py-0">
                              {act.activity_type}
                            </Badge>{' '}
                            {act.subject}
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>

        {/* AI Insights Panel */}
        <div className="space-y-3">
          <h2 className="text-lg font-semibold">AI分析ハイライト</h2>
          <Card>
            <CardContent className="p-4 space-y-4">
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-sm">🏆</span>
                  <span className="text-sm font-medium">トップパフォーマー</span>
                </div>
                {metrics
                  .filter(m => m.revenue_won > 0)
                  .sort((a, b) => b.revenue_won - a.revenue_won)
                  .slice(0, 3)
                  .map((m, i) => (
                    <div key={m.rep_id} className="flex items-center justify-between text-xs py-1">
                      <span>{i + 1}. {m.rep_name}</span>
                      <span className="font-medium">{formatYen(m.revenue_won)}</span>
                    </div>
                  ))}
              </div>
              <div className="border-t pt-3">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-sm">⚠️</span>
                  <span className="text-sm font-medium">要注目</span>
                </div>
                <div className="text-xs text-muted-foreground space-y-1">
                  <p>・未入力商談が{summary.incomplete_deals_count}件あります</p>
                  <p>・活動要約率が80%未満の担当者がいます</p>
                  <p>・パイプラインに大口案件が複数件入っています</p>
                </div>
              </div>
              <button
                onClick={() => openDrawer('チーム全体のパフォーマンスを分析して改善提案をしてください。')}
                className="w-full text-xs text-center py-2 rounded-md bg-blue-50 text-blue-600 hover:bg-blue-100 transition-colors font-medium"
              >
                AIに詳しく分析を依頼する →
              </button>
            </CardContent>
          </Card>

          {/* Team Summary */}
          {Object.entries(summary.teams).map(([team, data]) => (
            <Card key={team}>
              <CardContent className="p-4">
                <div className="text-sm font-medium mb-2">{team}</div>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <span className="text-muted-foreground">受注</span>
                    <div className="font-medium">{formatYen(data.revenue_won)}</div>
                  </div>
                  <div>
                    <span className="text-muted-foreground">パイプライン</span>
                    <div className="font-medium">{formatYen(data.pipeline_value)}</div>
                  </div>
                  <div>
                    <span className="text-muted-foreground">活動数</span>
                    <div className="font-medium">{data.activities}件</div>
                  </div>
                  <div>
                    <span className="text-muted-foreground">担当者</span>
                    <div className="font-medium">{data.reps}名</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
