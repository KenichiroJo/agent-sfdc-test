import { createContext, useContext, useState, useCallback, type PropsWithChildren } from 'react';

interface ChatDrawerState {
  isOpen: boolean;
  prefillMessage: string | null;
  openDrawer: (message?: string) => void;
  closeDrawer: () => void;
  clearPrefill: () => void;
}

const ChatDrawerContext = createContext<ChatDrawerState | null>(null);

export function ChatDrawerProvider({ children }: PropsWithChildren) {
  const [isOpen, setIsOpen] = useState(false);
  const [prefillMessage, setPrefillMessage] = useState<string | null>(null);

  const openDrawer = useCallback((message?: string) => {
    if (message) {
      setPrefillMessage(message);
    }
    setIsOpen(true);
  }, []);

  const closeDrawer = useCallback(() => {
    setIsOpen(false);
  }, []);

  const clearPrefill = useCallback(() => {
    setPrefillMessage(null);
  }, []);

  return (
    <ChatDrawerContext.Provider value={{ isOpen, prefillMessage, openDrawer, closeDrawer, clearPrefill }}>
      {children}
    </ChatDrawerContext.Provider>
  );
}

export function useChatDrawer() {
  const ctx = useContext(ChatDrawerContext);
  if (!ctx) throw new Error('useChatDrawer must be inside ChatDrawerProvider');
  return ctx;
}
