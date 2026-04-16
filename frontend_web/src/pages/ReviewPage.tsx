import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { InlineChat } from '@/components/block/chat/InlineChat';
import { demoApi } from '@/api/demo/api-requests';
import type { SalesRep, Activity } from '@/api/demo/types';

const SENTIMENT_MAP: Record<string, { label: string; color: string }> = {
  positive: { label: 'ポジティブ', color: 'bg-green-100 text-green-800' },
  neutral: { label: 'ニュートラル', color: 'bg-gray-100 text-gray-800' },
  negative: { label: 'ネガティブ', color: 'bg-red-100 text-red-800' },
};

const TYPE_COLORS: Record<string, string> = {
  '訪問': 'bg-blue-100 text-blue-800',
  '電話': 'bg-yellow-100 text-yellow-800',
  'Web会議': 'bg-purple-100 text-purple-800',
  'メール': 'bg-gray-100 text-gray-800',
  '展示会': 'bg-pink-100 text-pink-800',
};

function ActivityCard({ activity }: { activity: Activity }) {
  const [expanded, setExpanded] = useState(false);
  const [chatOpen, setChatOpen] = useState(false);
  const [chatMessage, setChatMessage] = useState('');
  const sentiment = SENTIMENT_MAP[activity.sentiment] || SENTIMENT_MAP.neutral;

  const handleAskAI = () => {
    setChatMessage(
      `活動ID ${activity.id}（${activity.subject}）の内容を要約して、キーポイントとネクストアクションを提案してください。\n\n活動詳細:\n- 日付: ${activity.date}\n- タイプ: ${activity.activity_type}\n- 顧客: ${activity.customer_name || '不明'}\n- コメント: ${activity.comment}`
    );
    setChatOpen(true);
  };

  return (
    <Card className="transition-shadow hover:shadow-sm">
      <CardContent className="p-4">
        <div className="flex items-start justify-between gap-2 mb-2">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-sm font-medium">{activity.date}</span>
            <Badge className={`text-[10px] px-1.5 py-0 ${TYPE_COLORS[activity.activity_type] || 'bg-gray-100'}`}>
              {activity.activity_type}
            </Badge>
            <Badge className={`text-[10px] px-1.5 py-0 ${sentiment.color}`}>
              {sentiment.label}
            </Badge>
          </div>
          <span className="text-xs text-muted-foreground whitespace-nowrap">{activity.duration_minutes}分</span>
        </div>

        {activity.customer_name && (
          <div className="text-xs text-muted-foreground mb-1">{activity.customer_name}</div>
        )}
        <div className="text-sm font-medium mb-2">{activity.subject}</div>

        <div className={`text-xs text-muted-foreground ${expanded ? '' : 'line-clamp-3'}`}>
          {activity.comment}
        </div>
        {activity.comment.length > 150 && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-xs text-blue-600 mt-1 hover:underline"
          >
            {expanded ? '折りたたむ' : '全文を表示'}
          </button>
        )}

        {activity.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-2">
            {activity.tags.map(tag => (
              <span key={tag} className="text-[10px] px-1.5 py-0.5 rounded bg-muted text-muted-foreground">
                {tag}
              </span>
            ))}
          </div>
        )}

        <div className="flex items-center gap-2 mt-3 pt-2 border-t">
          <button
            onClick={handleAskAI}
            disabled={chatOpen}
            className="text-xs px-3 py-1.5 rounded-md bg-blue-50 text-blue-600 hover:bg-blue-100 transition-colors font-medium disabled:opacity-50"
          >
            {chatOpen ? 'AI分析中' : 'AIに要約を依頼'}
          </button>
          {activity.follow_up_date && (
            <span className="text-[10px] text-muted-foreground ml-auto">
              次回: {activity.follow_up_date}
            </span>
          )}
        </div>

        {/* Inline Chat */}
        {chatOpen && (
          <InlineChat
            initialMessage={chatMessage}
            onClose={() => setChatOpen(false)}
          />
        )}
      </CardContent>
    </Card>
  );
}

export function ReviewPage() {
  const { repId } = useParams<{ repId?: string }>();
  const navigate = useNavigate();
  const [reps, setReps] = useState<SalesRep[]>([]);
  const [activities, setActivities] = useState<Activity[]>([]);
  const [selectedRep, setSelectedRep] = useState<SalesRep | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [repChatOpen, setRepChatOpen] = useState(false);
  const [repChatMessage, setRepChatMessage] = useState('');

  useEffect(() => {
    demoApi.getReps().then(data => {
      const filtered = data.filter(r => r.role !== 'マネージャー');
      setReps(filtered);
      if (repId) {
        const rep = filtered.find(r => r.id === repId);
        if (rep) setSelectedRep(rep);
      } else if (filtered.length > 0) {
        setSelectedRep(filtered[0]);
        navigate(`/review/${filtered[0].id}`, { replace: true });
      }
    }).catch(console.error);
  }, []);

  useEffect(() => {
    if (selectedRep) {
      setRepChatOpen(false);
      demoApi.getRepActivities(selectedRep.id, 30).then(setActivities).catch(console.error);
    }
  }, [selectedRep]);

  const handleSelectRep = (rep: SalesRep) => {
    setSelectedRep(rep);
    navigate(`/review/${rep.id}`);
  };

  const handleRepFeedback = () => {
    if (!selectedRep) return;
    setRepChatMessage(
      `${selectedRep.name}さん（${selectedRep.team} / ${selectedRep.territory}）の最近の活動についてフィードバックとネクストアクションを提案してください。`
    );
    setRepChatOpen(true);
  };

  const filteredReps = reps.filter(r =>
    searchQuery === '' || r.name.includes(searchQuery) || r.territory.includes(searchQuery)
  );

  return (
    <div className="flex h-full">
      {/* Left Panel - Rep Selector */}
      <div className="w-72 border-r bg-muted/30 flex flex-col">
        <div className="p-3 border-b">
          <h2 className="text-sm font-semibold mb-2">営業担当者</h2>
          <Input
            placeholder="名前・テリトリーで検索..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            className="h-8 text-xs"
          />
        </div>
        <div className="flex-1 overflow-auto p-2 space-y-1">
          {filteredReps.map(rep => (
            <button
              key={rep.id}
              onClick={() => handleSelectRep(rep)}
              className={`w-full text-left rounded-md p-2.5 transition-colors ${
                selectedRep?.id === rep.id
                  ? 'bg-blue-50 border border-blue-200'
                  : 'hover:bg-muted'
              }`}
            >
              <div className="flex items-center gap-2.5">
                <div
                  className="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold flex-shrink-0"
                  style={{ backgroundColor: rep.avatar_color }}
                >
                  {rep.name.charAt(0)}
                </div>
                <div className="min-w-0">
                  <div className="text-sm font-medium truncate">{rep.name}</div>
                  <div className="text-[10px] text-muted-foreground truncate">{rep.territory}</div>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Right Panel - Activity Timeline */}
      <div className="flex-1 overflow-auto">
        {selectedRep ? (
          <div className="p-6 max-w-3xl">
            <div className="flex items-center gap-3 mb-4">
              <div
                className="w-12 h-12 rounded-full flex items-center justify-center text-white font-bold"
                style={{ backgroundColor: selectedRep.avatar_color }}
              >
                {selectedRep.name.charAt(0)}
              </div>
              <div>
                <h1 className="text-xl font-bold">{selectedRep.name}</h1>
                <p className="text-sm text-muted-foreground">
                  {selectedRep.team} | {selectedRep.territory}
                </p>
              </div>
              <button
                onClick={handleRepFeedback}
                disabled={repChatOpen}
                className="ml-auto text-xs px-4 py-2 rounded-md bg-blue-600 text-white hover:bg-blue-700 transition-colors font-medium disabled:opacity-50"
              >
                {repChatOpen ? 'フィードバック生成中' : 'AIフィードバックを生成'}
              </button>
            </div>

            {/* Rep-level inline chat */}
            {repChatOpen && (
              <div className="mb-4">
                <InlineChat
                  initialMessage={repChatMessage}
                  onClose={() => setRepChatOpen(false)}
                />
              </div>
            )}

            <div className="space-y-3">
              {activities.map(act => (
                <ActivityCard key={act.id} activity={act} />
              ))}
              {activities.length === 0 && (
                <div className="text-center text-muted-foreground py-12">活動データがありません</div>
              )}
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-center h-full text-muted-foreground">
            担当者を選択してください
          </div>
        )}
      </div>
    </div>
  );
}
