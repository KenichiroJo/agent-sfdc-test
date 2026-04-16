import apiClient from '@/api/apiClient';
import type {
  Activity,
  Customer,
  DashboardSummary,
  Deal,
  KnowledgeArticle,
  PerformanceMetric,
  SalesRep,
} from './types';

export const demoApi = {
  getReps: (team?: string) =>
    apiClient.get<SalesRep[]>('/v1/demo/reps', { params: team ? { team } : {} }).then(r => r.data),

  getRep: (repId: string) =>
    apiClient.get<SalesRep>(`/v1/demo/reps/${repId}`).then(r => r.data),

  getRepActivities: (repId: string, limit = 20) =>
    apiClient.get<Activity[]>(`/v1/demo/reps/${repId}/activities`, { params: { limit } }).then(r => r.data),

  getCustomers: (segment?: string) =>
    apiClient.get<Customer[]>('/v1/demo/customers', { params: segment ? { segment } : {} }).then(r => r.data),

  getDeals: (repId?: string, stage?: string) =>
    apiClient.get<Deal[]>('/v1/demo/deals', { params: { rep_id: repId, stage } }).then(r => r.data),

  getIncompleteDeals: () =>
    apiClient.get<Deal[]>('/v1/demo/deals/incomplete').then(r => r.data),

  getKnowledge: (category?: string, q?: string) =>
    apiClient.get<KnowledgeArticle[]>('/v1/demo/knowledge', { params: { category, q } }).then(r => r.data),

  getMetrics: (team?: string, period?: string) =>
    apiClient.get<PerformanceMetric[]>('/v1/demo/metrics', { params: { team, period } }).then(r => r.data),

  getDashboardSummary: () =>
    apiClient.get<DashboardSummary>('/v1/demo/dashboard/summary').then(r => r.data),
};
