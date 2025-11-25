// Core API response types

export interface Session {
  id: string;
  user_id?: string;
  created_at: string;
  last_accessed_at: string;
  preferences: UserPreferences;
  sites: Site[];
}

export interface UserPreferences {
  default_color_scheme?: string;
  default_site_type?: string;
  favorite_features?: string[];
  design_style?: string;
  framework_preference?: string;
}

export interface Site {
  id: string;
  session_id: string;
  name: string;
  description?: string;
  framework: string;
  design_style: string;
  created_at: string;
  updated_at: string;
  versions: SiteVersion[];
  audits: Audit[];
  deployments: Deployment[];
}

export interface SiteVersion {
  id: string;
  version_number: number;
  html_code: string;
  css_code?: string;
  js_code?: string;
  created_at: string;
  change_description?: string;
}

export interface Audit {
  id: string;
  site_id: string;
  timestamp: string;
  seo: CategoryScore;
  accessibility: CategoryScore;
  performance: CategoryScore;
  overall_score: number;
}

export interface CategoryScore {
  score: number;
  issues: Issue[];
  passed_checks: number;
  total_checks: number;
}

export interface Issue {
  severity: 'critical' | 'high' | 'medium' | 'low';
  description: string;
  fix_suggestion?: string;
  affected_elements?: string[];
}

export interface Deployment {
  id: string;
  site_id: string;
  url: string;
  status: 'pending' | 'deploying' | 'success' | 'failed';
  platform: 'vercel';
  created_at: string;
  deployed_at?: string;
  error_message?: string;
}

// API Error types
export enum ErrorType {
  NETWORK_ERROR = 'network_error',
  VALIDATION_ERROR = 'validation_error',
  API_ERROR = 'api_error',
  WEBSOCKET_ERROR = 'websocket_error',
  UNKNOWN_ERROR = 'unknown_error',
}

export interface AppError {
  type: ErrorType;
  message: string;
  details?: any;
  recoverable: boolean;
  retryable: boolean;
}
