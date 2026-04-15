export interface SalesRep {
  id: string;
  name: string;
  name_kana: string;
  email: string;
  role: string;
  team: string;
  manager_id: string | null;
  hire_date: string;
  territory: string;
  target_quarterly_revenue: number;
  avatar_color: string;
}

export interface Customer {
  id: string;
  company_name: string;
  industry: string;
  segment: string;
  region: string;
  annual_revenue_estimate: number;
  primary_contact: string;
  primary_contact_title: string;
  relationship_since: string;
  notes: string;
}

export interface Activity {
  id: string;
  rep_id: string;
  customer_id: string | null;
  customer_name?: string;
  activity_type: string;
  date: string;
  duration_minutes: number;
  subject: string;
  comment: string;
  sentiment: string;
  deal_id: string | null;
  follow_up_date: string | null;
  tags: string[];
}

export interface Deal {
  id: string;
  rep_id: string;
  customer_id: string | null;
  deal_name: string;
  stage: string;
  amount: number | null;
  probability: number | null;
  expected_close_date: string | null;
  product_category: string | null;
  quantity_estimate: number | null;
  competitor: string | null;
  loss_reason: string | null;
  notes: string;
  missing_fields?: string[];
  rep_name?: string;
}

export interface KnowledgeArticle {
  id: string;
  title: string;
  category: string;
  subcategory: string;
  content: string;
  author_rep_id: string;
  source_activity_ids: string[];
  tags: string[];
  created_date: string;
  views: number;
  helpfulness_score: number;
  product_categories: string[];
}

export interface PerformanceMetric {
  rep_id: string;
  rep_name?: string;
  period: string;
  activities_count: number;
  visits_count: number;
  calls_count: number;
  web_meetings_count: number;
  emails_count: number;
  deals_created: number;
  deals_won: number;
  deals_lost: number;
  revenue_won: number;
  pipeline_value: number;
  conversion_rate: number;
  avg_deal_cycle_days: number;
  activity_summary_rate: number;
  feedback_utilization_rate: number;
  knowledge_contributions: number;
}

export interface DashboardSummary {
  period: string;
  total_reps: number;
  total_activities: number;
  total_revenue_won: number;
  total_pipeline: number;
  avg_activity_summary_rate: number;
  avg_feedback_utilization_rate: number;
  incomplete_deals_count: number;
  active_deals_count: number;
  teams: Record<string, {
    revenue_won: number;
    pipeline_value: number;
    activities: number;
    reps: number;
  }>;
}
