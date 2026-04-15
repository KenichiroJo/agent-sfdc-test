import { Outlet } from 'react-router-dom';
import { AppSidebar } from '@/components/block/nav/AppSidebar';

export function AppLayout() {
  return (
    <div className="flex h-full w-full">
      <AppSidebar />
      <main className="flex-1 overflow-auto bg-background">
        <Outlet />
      </main>
    </div>
  );
}
