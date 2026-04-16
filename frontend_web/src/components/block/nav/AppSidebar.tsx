import { useNavigate, useLocation } from 'react-router-dom';
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarFooter,
} from '@/components/ui/sidebar';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { useChatDrawer } from '@/components/block/chat/ChatDrawerContext';
import { PATHS } from '@/constants/path';

const NAV_ITEMS = [
  { label: 'ダッシュボード', path: PATHS.DASHBOARD, icon: '📊' },
  { label: '活動レビュー＆FB', path: PATHS.REVIEW, icon: '📋' },
  { label: 'ナレッジ＆分析', path: PATHS.KNOWLEDGE, icon: '📚' },
];

export function AppSidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { openDrawer } = useChatDrawer();

  return (
    <Sidebar>
      <SidebarHeader className="border-b border-sidebar-border px-4 py-4">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600 text-white text-sm font-bold">
            SW
          </div>
          <div>
            <div className="text-sm font-semibold">StyleWorks</div>
            <div className="text-xs text-muted-foreground">営業活動支援AI</div>
          </div>
        </div>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>メニュー</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {NAV_ITEMS.map(item => {
                const isActive = location.pathname.startsWith(item.path.replace(':repId', ''));
                return (
                  <SidebarMenuItem key={item.path}>
                    <SidebarMenuButton
                      isActive={isActive}
                      onClick={() => navigate(item.path)}
                      className="gap-3"
                    >
                      <span className="text-base">{item.icon}</span>
                      <span>{item.label}</span>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                );
              })}
              <SidebarMenuItem>
                <SidebarMenuButton onClick={() => openDrawer()} className="gap-3">
                  <span className="text-base">💬</span>
                  <span>AIチャット</span>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter className="border-t border-sidebar-border p-4">
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <button
                disabled
                className="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm text-muted-foreground opacity-60 cursor-not-allowed hover:bg-transparent"
              >
                <span className="text-base">☁️</span>
                <span>Salesforce連携</span>
                <span className="ml-auto rounded bg-muted px-1.5 py-0.5 text-[10px] font-medium">
                  未接続
                </span>
              </button>
            </TooltipTrigger>
            <TooltipContent side="right">
              <p>デモ版では無効です。本番環境ではSalesforceに接続します。</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </SidebarFooter>
    </Sidebar>
  );
}
