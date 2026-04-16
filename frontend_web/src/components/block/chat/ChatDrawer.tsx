import { useEffect, useRef, useState } from 'react';
import { v4 as uuid } from 'uuid';
import { Sheet, SheetContent, SheetHeader, SheetTitle } from '@/components/ui/sheet';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Chat,
  useChatScroll,
  useChatContext,
  ChatMessages,
  ChatProgress,
  ChatTextInput,
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
import { useChatDrawer } from './ChatDrawerContext';
import type { MessageResponse } from '@/api/chat/types';

const QUICK_ACTIONS = [
  { label: '活動を要約', message: '最近の営業活動を要約してください。' },
  { label: 'FBを生成', message: 'チーム全体のフィードバックとネクストアクションを提案してください。' },
  { label: 'ナレッジ検索', message: '営業ノウハウを検索してください。' },
  { label: '未入力確認', message: '未入力の商談データを確認して補完を提案してください。' },
  { label: '分析', message: 'チームのパフォーマンスを分析して改善提案をしてください。' },
];

function DrawerChatContent({ chatId }: { chatId: string }) {
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

  const { prefillMessage, clearPrefill } = useChatDrawer();
  const prefillSent = useRef(false);

  useEffect(() => {
    if (prefillMessage && !prefillSent.current) {
      prefillSent.current = true;
      setUserInput(prefillMessage);
      clearPrefill();
      setTimeout(() => sendMessage(prefillMessage), 300);
    }
  }, [prefillMessage]);

  const handleQuickAction = (message: string) => {
    setUserInput(message);
    setTimeout(() => sendMessage(message), 100);
  };

  const initialMessages: MessageResponse[] = [
    {
      id: uuid(),
      role: 'assistant',
      content: {
        format: 2,
        parts: [{ type: 'text', text: 'こんにちは！何をお手伝いしましょうか？' }],
      },
      createdAt: new Date(),
      type: 'initial',
    },
  ];

  return (
    <Chat initialMessages={initialMessages}>
      <ScrollArea
        className="min-h-0 w-full flex-1 mb-3"
        scrollViewportRef={scrollContainerRef}
        onWheel={onChatScroll}
      >
        <div className="w-full px-2">
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

      {combinedEvents.length <= 1 && (
        <div className="flex flex-wrap gap-1.5 px-3 pb-2">
          {QUICK_ACTIONS.map(action => (
            <button
              key={action.label}
              onClick={() => handleQuickAction(action.message)}
              className="text-[11px] px-2.5 py-1 rounded-full border border-blue-200 text-blue-600 hover:bg-blue-50 transition-colors"
            >
              {action.label}
            </button>
          ))}
        </div>
      )}

      <div className="px-2 pb-2">
        <ChatTextInput
          userInput={userInput}
          setUserInput={setUserInput}
          onSubmit={sendMessage}
          runningAgent={isAgentRunning}
        />
      </div>
    </Chat>
  );
}

export function ChatDrawer() {
  const { isOpen, closeDrawer } = useChatDrawer();
  const [chatId, setChatId] = useState<string>('');
  const addChatToState = useAddChat();

  useEffect(() => {
    if (isOpen && !chatId) {
      const newId = uuid();
      setChatId(newId);
      addChatToState(newId);
    }
  }, [isOpen]);

  const handleNewChat = () => {
    const newId = uuid();
    setChatId(newId);
    addChatToState(newId);
  };

  return (
    <Sheet open={isOpen} onOpenChange={open => { if (!open) closeDrawer(); }}>
      <SheetContent side="right" className="w-[480px] sm:w-[520px] p-0 flex flex-col">
        <SheetHeader className="px-4 py-3 border-b flex-shrink-0">
          <div className="flex items-center justify-between">
            <SheetTitle className="text-sm font-semibold">AI アシスタント</SheetTitle>
            <button
              onClick={handleNewChat}
              className="text-[11px] px-2.5 py-1 rounded border text-muted-foreground hover:bg-muted transition-colors"
            >
              新しい会話
            </button>
          </div>
        </SheetHeader>
        <div className="flex-1 flex flex-col min-h-0">
          {chatId && (
            <ChatProvider chatId={chatId} runInBackground={true} isNewChat={true}>
              <DrawerChatContent chatId={chatId} />
            </ChatProvider>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
}
