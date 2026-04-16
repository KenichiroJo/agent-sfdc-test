import { Outlet } from 'react-router-dom';
import { AppSidebar } from '@/components/block/nav/AppSidebar';
import { ChatDrawerProvider } from '@/components/block/chat/ChatDrawerContext';
import { ChatDrawer } from '@/components/block/chat/ChatDrawer';

export function AppLayout() {
  return (
    <ChatDrawerProvider>
      <div className="flex h-full w-full">
        <AppSidebar />
        <main className="flex-1 overflow-auto bg-background">
          <Outlet />
        </main>
        <ChatDrawer />
      </div>
    </ChatDrawerProvider>
  );
}
