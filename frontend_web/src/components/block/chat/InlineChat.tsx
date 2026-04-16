import { useEffect, useRef, useState, useCallback } from 'react';
import { v4 as uuid } from 'uuid';
import { getApiUrl } from '@/lib/url-utils';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
}

/**
 * Sends a message to the chat API via SSE and streams the response.
 * Uses native fetch - no ag-ui dependency.
 */
async function streamChat(
  threadId: string,
  messages: Array<{ role: string; content: string }>,
  onDelta: (text: string) => void,
  onDone: () => void,
  onError: (err: string) => void,
) {
  const apiBase = getApiUrl();
  const url = `${apiBase}/v1/chat`;

  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
      },
      credentials: 'include',
      body: JSON.stringify({
        threadId: threadId,
        runId: uuid(),
        messages: messages.map(m => ({
          id: uuid(),
          role: m.role,
          content: m.content,
        })),
      }),
    });

    if (!res.ok) {
      onError(`API error: ${res.status}`);
      return;
    }

    const reader = res.body?.getReader();
    if (!reader) {
      onError('No response body');
      return;
    }

    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue;
        const data = line.slice(6).trim();
        if (data === '[DONE]') continue;

        try {
          const event = JSON.parse(data);
          // Handle different event formats from the DataRobot AG-UI backend
          if (event.type === 'TEXT_MESSAGE_CONTENT' && event.delta) {
            onDelta(event.delta);
          } else if (event.type === 'RUN_FINISHED') {
            // Stream complete
          } else if (event.type === 'RUN_ERROR') {
            onError(event.message || 'Agent error');
          }
          // Also handle nested events format
          if (event.events) {
            for (const e of event.events) {
              if (e.content?.parts) {
                for (const part of e.content.parts) {
                  if (part.type === 'text' && part.text) {
                    onDelta(part.text);
                  }
                }
              }
            }
          }
        } catch {
          // Not valid JSON, skip
        }
      }
    }

    onDone();
  } catch (err) {
    onError(err instanceof Error ? err.message : 'Connection error');
  }
}

interface InlineChatProps {
  initialMessage: string;
  onClose?: () => void;
}

export function InlineChat({ initialMessage, onClose }: InlineChatProps) {
  const [threadId] = useState(() => uuid());
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [input, setInput] = useState('');
  const sentRef = useRef(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const assistantTextRef = useRef('');

  const sendMessage = useCallback(
    (text: string) => {
      setError(null);
      setIsRunning(true);
      assistantTextRef.current = '';

      const userMsg: ChatMessage = { id: uuid(), role: 'user', content: text };
      const assistantId = uuid();

      setMessages(prev => [
        ...prev,
        userMsg,
        { id: assistantId, role: 'assistant', content: '' },
      ]);

      const history = [
        ...messages.map(m => ({ role: m.role, content: m.content })),
        { role: 'user', content: text },
      ];

      streamChat(
        threadId,
        history,
        (delta) => {
          assistantTextRef.current += delta;
          setMessages(prev =>
            prev.map(m =>
              m.id === assistantId
                ? { ...m, content: assistantTextRef.current }
                : m
            )
          );
        },
        () => setIsRunning(false),
        (err) => {
          setError(err);
          setIsRunning(false);
        },
      );
    },
    [threadId, messages],
  );

  // Auto-send initial message
  useEffect(() => {
    if (!sentRef.current && initialMessage) {
      sentRef.current = true;
      sendMessage(initialMessage);
    }
  }, [initialMessage, sendMessage]);

  // Auto-scroll
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = () => {
    if (input.trim() && !isRunning) {
      sendMessage(input.trim());
      setInput('');
    }
  };

  // Don't show the first user message (auto-sent context)
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
                <div className="bg-blue-600 text-white rounded-lg px-3 py-2 max-w-[85%] whitespace-pre-wrap">
                  {msg.content}
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-lg px-3 py-2 border border-blue-100 whitespace-pre-wrap">
                {msg.content || (
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
