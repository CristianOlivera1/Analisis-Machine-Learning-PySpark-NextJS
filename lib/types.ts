// Dataset Types
export interface Dataset {
  id: string;
  name: string;
  file_path: string;
  rows: number;
  columns: number;
  column_names: string[];
  column_types: Record<string, string>;
  created_at: string;
}

export interface DatasetPreview {
  columns: string[];
  data: Record<string, any>[];
  total_rows: number;
}

export interface DatasetStatistics {
  column: string;
  count: number;
  mean?: number;
  std?: number;
  min?: number;
  max?: number;
  percentile_25?: number;
  percentile_50?: number;
  percentile_75?: number;
  unique?: number;
  top?: string;
  freq?: number;
}

// Model Types
export interface Model {
  id: string;
  name: string;
  model_type: 'classification' | 'regression' | 'clustering';
  algorithm: string;
  dataset_id: string;
  target_column: string;
  feature_columns: string[];
  metrics: Record<string, number>;
  created_at: string;
}

export interface ModelType {
  type: string;
  algorithms: Algorithm[];
}

export interface Algorithm {
  name: string;
  displayName?: string;
  params: AlgorithmParam[];
}

export interface AlgorithmParam {
  name: string;
  type: 'int' | 'float' | 'bool' | 'string';
  default: any;
  min?: number;
  max?: number;
  options?: string[];
}

export interface TrainingRequest {
  dataset_id: string;
  model_type: 'classification' | 'regression' | 'clustering';
  algorithm: string;
  target_column?: string;
  feature_columns: string[];
  test_size?: number;
  params?: Record<string, any>;
  model_name?: string;
}

// Chart Types
export interface HistogramData {
  column: string;
  bins: number;
  data: { bin: string; count: number; min: number; max: number }[];
}
