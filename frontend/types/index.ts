// API Types
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sql?: string;
  data?: {
    columns: string[];
    rows: any[][];
  };
  visualization?: 'bar' | 'line' | 'pie' | 'table';
  error?: string;
}

export interface APIRequest {
  question: string;
  org_id?: number;
  session_id?: string;
  store_id?: string;
  dataset_type?: string;
  intent?: string;
}

export interface APIResponse {
  success: boolean;
  response: string;
  sql?: string;
  data?: {
    columns: string[];
    rows: any[][];
  };
  visualization?: 'bar' | 'line' | 'pie' | 'table';
  error?: string;
}

export interface DatasetColumn {
  name: string;
  original_name: string;
  dtype: string;
  sample_values: Array<string | number | null>;
}

export interface DatasetMetadata {
  id: string;
  name: string;
  table_name: string;
  row_count: number;
  created_at: string;
  updated_at: string;
  columns: DatasetColumn[];
}

export interface DatasetUploadResponse {
  dataset: DatasetMetadata;
}

export interface DatasetListResponse {
  datasets: DatasetMetadata[];
}

export interface AuthState {
  isAuthenticated: boolean;
  token?: string;
  apiKey?: string;
  user?: {
    email?: string;
    name?: string;
  };
}

export interface QueryExample {
  id: string;
  text: string;
  category: string;
}

