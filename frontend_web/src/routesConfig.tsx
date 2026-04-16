import { PATHS } from '@/constants/path.ts';
import { lazy } from 'react';
import { Navigate } from 'react-router-dom';
import { SettingsLayout } from './pages/SettingsLayout';
import { AppLayout } from './pages/AppLayout';
import { DashboardPage } from './pages/DashboardPage';
import { ReviewPage } from './pages/ReviewPage';
import { KnowledgePage } from './pages/KnowledgePage';

const OAuthCallback = lazy(() => import('./pages/OAuthCallback'));

export const appRoutes = [
  { path: PATHS.OAUTH_CB, element: <OAuthCallback /> },
  {
    element: <AppLayout />,
    children: [
      { path: PATHS.DASHBOARD, element: <DashboardPage /> },
      { path: PATHS.REVIEW, element: <ReviewPage /> },
      { path: PATHS.REVIEW_REP, element: <ReviewPage /> },
      { path: PATHS.KNOWLEDGE, element: <KnowledgePage /> },
      {
        path: PATHS.SETTINGS.ROOT,
        element: <SettingsLayout />,
        children: [{ path: 'sources', element: <Navigate to={PATHS.SETTINGS.ROOT} replace /> }],
      },
      { path: '/', element: <Navigate to={PATHS.DASHBOARD} replace /> },
      { path: '*', element: <Navigate to={PATHS.DASHBOARD} replace /> },
    ],
  },
];
