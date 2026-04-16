import { useEffect, useRef, useState } from 'react';
import { v4 as uuid } from 'uuid';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Chat,
  useChatScroll,
  useChatContext,
  ChatMessages,
  ChatProgress,
  ChatError,
  ChatMessageMemo,
  StepEvent,
  ThinkingEvent,
  ChatProvider,
} from '@/components/block/chat';
import {
  isErrorStateEvent,
  isMessageStateEvent,
  isStepStateEvent,
  isThinkingEvent,
} from '@/components/block/chat/types';
import { useAddChat } from '@/components/block/chat/hooks/use-chats-state';
import type { MessageResponse } from '@/api/chat/types';

function InlineChatContent({
  chatId,
  initialMessage,
}: {
  chatId: string;
  initialMessage: string;
}) {
  const {
    sendMessage,
    userInput,
    setUserInput,
    combinedEvents,
    progress,
    deleteProgress,
    isLoadingHistory,
    isAgentRunning,
  } = useChatContext();

  const { scrollContainerRef, onChatScroll } = useChatScroll({
    chatId,
    events: combinedEvents,
  });

  const sentRef = useRef(false);

  useEffect(() => {
    if (!sentRef.current && initialMessage) {
      sentRef.current = true;
      setUserInput(initialMessage);
      setTimeout(() => sendMessage(initialMessage), 200);
    }
  }, [initialMessage]);

  const handleSubmit = (msg?: string) => {
    const text = msg || userInput;
    if (text.trim()) {
      sendMessage(text);
    }
  };

  const greeting: MessageResponse[] = [
    {
      id: uuid(),
      role: 'assistant',
      content: {
        format: 2,
        parts: [{ type: 'text', text: '分析中...' }],
      },
      createdAt: new Date(),
      type: 'initial',
    },
  ];

  return (
    <Chat initialMessages={greeting}>
      <ScrollArea
        className="max-h-[400px] w-full"
        scrollViewportRef={scrollContainerRef}
        onWheel={onChatScroll}
      >
        <div className="w-full px-1">
          <ChatMessages isLoading={isLoadingHistory} messages={combinedEvents} chatId={chatId}>
            {combinedEvents?.map(m => {
              if (isErrorStateEvent(m)) return <ChatError key={m.value.id} {...m.value} />;
              if (isMessageStateEvent(m)) return <ChatMessageMemo key={m.value.id} {...m.value} />;
              if (isStepStateEvent(m)) return <StepEvent key={m.value.id} {...m.value} />;
              if (isThinkingEvent(m)) return <ThinkingEvent key={m.type} />;
            })}
          </ChatMessages>
          <ChatProgress progress={progress || {}} deleteProgress={deleteProgress} />
        </div>
      </ScrollArea>

      {/* Follow-up input */}
      <div className="flex gap-2 mt-2">
        <input
          type="text"
          value={userInput}
          onChange={e => setUserInput(e.target.value)}
          onKeyDown={e => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSubmit();
            }
          }}
          placeholder="追加で質問する..."
          disabled={isAgentRunning}
          className="flex-1 rounded-md border border-input bg-background px-3 py-2 text-xs placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:opacity-50"
        />
        <button
          onClick={() => handleSubmit()}
          disabled={isAgentRunning || !userInput.trim()}
          className="px-3 py-2 rounded-md bg-blue-600 text-white text-xs font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isAgentRunning ? '処理中...' : '送信'}
        </button>
      </div>
    </Chat>
  );
}

interface InlineChatProps {
  initialMessage: string;
  onClose?: () => void;
}

export function InlineChat({ initialMessage, onClose }: InlineChatProps) {
  const [chatId] = useState(() => uuid());
  const addChatToState = useAddChat();

  useEffect(() => {
    addChatToState(chatId);
  }, [chatId]);

  return (
    <div className="mt-3 rounded-lg border border-blue-200 bg-blue-50/30 p-3">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <div className="w-5 h-5 rounded-full bg-blue-600 flex items-center justify-center">
            <span className="text-white text-[10px]">AI</span>
          </div>
          <span className="text-xs font-medium text-blue-800">AI分析</span>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="text-xs text-muted-foreground hover:text-foreground transition-colors"
          >
            閉じる
          </button>
        )}
      </div>
      <ChatProvider chatId={chatId} runInBackground={true} isNewChat={true}>
        <InlineChatContent chatId={chatId} initialMessage={initialMessage} />
      </ChatProvider>
    </div>
  );
}
