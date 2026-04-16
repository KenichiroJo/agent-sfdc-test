import { useEffect, useRef, useState, useCallback } from 'react';
import { v4 as uuid } from 'uuid';
import { HttpAgent } from '@ag-ui/client';
import { EventType } from '@ag-ui/core';
import { AG_UI_ENDPOINT } from '@/constants/endpoints';
import { Markdown } from '@/components/ui/markdown';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
}

function useInlineAgent(threadId: string) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const currentAssistantRef = useRef<string>('');

  const sendMessage = useCallback(
    (text: string) => {
      setError(null);
      setIsRunning(true);
      currentAssistantRef.current = '';

      const userMsg: ChatMessage = { id: uuid(), role: 'user', content: text };
      setMessages(prev => [...prev, userMsg]);

      const assistantId = uuid();
      setMessages(prev => [...prev, { id: assistantId, role: 'assistant', content: '' }]);

      const agent = new HttpAgent({
        url: AG_UI_ENDPOINT,
        threadId,
        agentId: threadId,
      });

      const runId = uuid();

      agent.on(EventType.TEXT_MESSAGE_CONTENT, (event) => {
        currentAssistantRef.current += event.delta ?? '';
        setMessages(prev =>
          prev.map(m => (m.id === assistantId ? { ...m, content: currentAssistantRef.current } : m))
        );
      });

      agent.on(EventType.RUN_ERROR, (event) => {
        setError(event.message || 'エラーが発生しました');
        setIsRunning(false);
      });

      agent.on(EventType.RUN_FINISHED, () => {
        setIsRunning(false);
      });

      agent.runAgent({
        runId,
        threadId,
        messages: [
          ...messages.map(m => ({
            id: m.id,
            role: m.role as 'user' | 'assistant',
            content: m.content,
          })),
          { id: userMsg.id, role: 'user' as const, content: text },
        ],
      }).catch((err: unknown) => {
        const msg = err instanceof Error ? err.message : 'Connection error';
        setError(msg);
        setIsRunning(false);
      });
    },
    [threadId, messages]
  );

  return { messages, isRunning, error, sendMessage };
}

interface InlineChatProps {
  initialMessage: string;
  onClose?: () => void;
}

export function InlineChat({ initialMessage, onClose }: InlineChatProps) {
  const [threadId] = useState(() => uuid());
  const { messages, isRunning, error, sendMessage } = useInlineAgent(threadId);
  const [input, setInput] = useState('');
  const sentRef = useRef(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!sentRef.current && initialMessage) {
      sentRef.current = true;
      sendMessage(initialMessage);
    }
  }, [initialMessage]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = () => {
    if (input.trim() && !isRunning) {
      sendMessage(input.trim());
      setInput('');
    }
  };

  // Hide the first user message (it's the auto-sent context message)
  const visibleMessages = messages.slice(1);

  return (
    <div className="mt-3 rounded-lg border border-blue-200 bg-blue-50/30 p-3">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <div className="w-5 h-5 rounded-full bg-blue-600 flex items-center justify-center">
            <span className="text-white text-[10px]">AI</span>
          </div>
          <span className="text-xs font-medium text-blue-800">AI分析</span>
          {isRunning && (
            <span className="text-[10px] text-blue-500 animate-pulse">処理中...</span>
          )}
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="text-xs text-muted-foreground hover:text-foreground transition-colors px-1"
          >
            ✕
          </button>
        )}
      </div>

      {/* Messages */}
      <div className="max-h-[400px] overflow-y-auto space-y-2 text-xs">
        {visibleMessages.map(msg => (
          <div key={msg.id}>
            {msg.role === 'user' ? (
              <div className="flex justify-end">
                <div className="bg-blue-600 text-white rounded-lg px-3 py-2 max-w-[85%]">
                  {msg.content}
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-lg px-3 py-2 border border-blue-100 prose prose-xs max-w-none [&_p]:my-1 [&_ul]:my-1 [&_li]:my-0.5 [&_h1]:text-sm [&_h2]:text-xs [&_h3]:text-xs [&_h4]:text-xs">
                {msg.content ? (
                  <Markdown>{msg.content}</Markdown>
                ) : (
                  <span className="text-muted-foreground animate-pulse">考え中...</span>
                )}
              </div>
            )}
          </div>
        ))}
        {error && (
          <div className="text-red-600 text-[11px] bg-red-50 rounded px-2 py-1">
            エラー: {error}
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Follow-up input */}
      <div className="flex gap-2 mt-2">
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSubmit();
            }
          }}
          placeholder="追加で質問する..."
          disabled={isRunning}
          className="flex-1 rounded-md border border-input bg-background px-3 py-2 text-xs placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:opacity-50"
        />
        <button
          onClick={handleSubmit}
          disabled={isRunning || !input.trim()}
          className="px-3 py-2 rounded-md bg-blue-600 text-white text-xs font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          送信
        </button>
      </div>
    </div>
  );
}
