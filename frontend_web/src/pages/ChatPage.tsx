'use client';
import React, { useEffect } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import { v4 as uuid } from 'uuid';
import { Skeleton } from '@/components/ui/skeleton';
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
  StartNewChat,
} from '@/components/block/chat';
import {
  isErrorStateEvent,
  isMessageStateEvent,
  isStepStateEvent,
  isThinkingEvent,
} from '@/components/block/chat/types';
import { type MessageResponse } from '@/api/chat/types';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useMainLayout } from '@/components/block/chat/main-layout-context';

const QUICK_ACTIONS = [
  { label: '活動を要約', message: '最近の営業活動を要約してください。' },
  { label: 'FBを生成', message: 'チーム全体のフィードバックとネクストアクションを提案してください。' },
  { label: 'ナレッジ検索', message: '営業ノウハウを検索してください。' },
  { label: '未入力確認', message: '未入力の商談データを確認して補完を提案してください。' },
  { label: '分析', message: 'チームのパフォーマンスを分析して改善提案をしてください。' },
];

const initialMessages: MessageResponse[] = [
  {
    id: uuid(),
    role: 'assistant',
    content: {
      format: 2,
      parts: [
        {
          type: 'text',
          text: `こんにちは！キャブ株式会社（United Athle）のフィールドセールス活動支援AIです。\n\n以下のことをお手伝いできます：\n\n- **営業活動の要約** - 担当者の活動コメントを要約し、キーポイントを抽出\n- **フィードバック生成** - 部下への個別フィードバックとネクストアクションを提案\n- **ナレッジ検索** - 営業ノウハウ・成功事例・商品知識を検索\n- **未入力データ確認** - SFDCの未入力商談を検出し、補完を支援\n- **パフォーマンス分析** - チームの営業実績を分析し、改善策を提案\n\nどのようなお手伝いをしましょうか？`,
        },
      ],
    },
    createdAt: new Date(),
    type: 'initial',
  },
];

export interface ChatPageContentProps {
  chatId: string;
  hasChat: boolean;
  isNewChat: boolean;
  isLoadingChats: boolean;
  addChatHandler: () => void;
}

export function ChatImplementation({ chatId }: { chatId: string }) {
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

  // Example for a tool with a handler
  // useAgUiTool({
  //   name: 'alert',
  //   description: 'Action. Display an alert to the user',
  //   handler: ({ message }) => alert(message),
  //   parameters: z.object({
  //     message: z
  //       .string()
  //       .describe('The message that will be displayed to the user'),
  //   }),
  //   background: false,
  // });
  //
  // Example for a custom UI widget
  //
  // useAgUiTool({
  //   name: 'weather',
  //   description: 'Widget. Displays weather result to user',
  //   render: ({ args }) => {
  //     return <WeatherWidget {...args} />;
  //   },
  //   parameters: z.object({
  //     temperature: z.number(),
  //     feelsLike: z.number(),
  //     humidity: z.number(),
  //     windSpeed: z.number(),
  //     windGust: z.number(),
  //     conditions: z.string(),
  //     location: z.string(),
  //   }),
  // });

  const handleQuickAction = (message: string) => {
    setUserInput(message);
    setTimeout(() => sendMessage(message), 100);
  };

  return (
    <Chat initialMessages={initialMessages}>
      <ScrollArea
        className="mb-5 min-h-0 w-full flex-1"
        scrollViewportRef={scrollContainerRef}
        onWheel={onChatScroll}
      >
        <div className="w-full justify-self-center">
          <ChatMessages isLoading={isLoadingHistory} messages={combinedEvents} chatId={chatId}>
            {combinedEvents &&
              combinedEvents.map(m => {
                if (isErrorStateEvent(m)) {
                  return <ChatError key={m.value.id} {...m.value} />;
                }
                if (isMessageStateEvent(m)) {
                  return <ChatMessageMemo key={m.value.id} {...m.value} />;
                }
                if (isStepStateEvent(m)) {
                  return <StepEvent key={m.value.id} {...m.value} />;
                }
                if (isThinkingEvent(m)) {
                  return <ThinkingEvent key={m.type} />;
                }
              })}
          </ChatMessages>
          <ChatProgress progress={progress || {}} deleteProgress={deleteProgress} />
        </div>
      </ScrollArea>

      {/* Quick Actions */}
      {combinedEvents.length <= 1 && (
        <div className="flex flex-wrap gap-2 justify-center px-4 pb-2">
          {QUICK_ACTIONS.map(action => (
            <button
              key={action.label}
              onClick={() => handleQuickAction(action.message)}
              className="text-xs px-3 py-1.5 rounded-full border border-blue-200 text-blue-600 hover:bg-blue-50 transition-colors"
            >
              {action.label}
            </button>
          ))}
        </div>
      )}

      <ChatTextInput
        userInput={userInput}
        setUserInput={setUserInput}
        onSubmit={sendMessage}
        runningAgent={isAgentRunning}
      />
    </Chat>
  );
}

export const ChatPage: React.FC = () => {
  const { chatId } = useParams<{ chatId: string }>();
  const { hasChat, isNewChat, isLoadingChats, addChatHandler, refetchChats } = useMainLayout();

  if (!chatId) {
    return null;
  }

  if (isLoadingChats) {
    return (
      <div className="flex w-full flex-1 flex-col space-y-4 p-4">
        <Skeleton className="h-20 w-full" />
        <Skeleton className="h-20 w-full" />
        <Skeleton className="h-20 w-full" />
      </div>
    );
  }

  if (!hasChat) {
    return <StartNewChat createChat={addChatHandler} />;
  }

  return (
    <ChatProvider
      chatId={chatId}
      runInBackground={true}
      isNewChat={isNewChat}
      refetchChats={refetchChats}
    >
      <ChatImplementation chatId={chatId} />
    </ChatProvider>
  );
};
