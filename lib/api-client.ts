import axios, { AxiosInstance, AxiosError } from 'axios';
import type {
  Dataset,
  DatasetPreview,
  DatasetStatistics,
  Model,
  ModelType,
  TrainingRequest,
  HistogramData,
} from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: `${API_BASE_URL}/api`,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 180000, 
    });

    // Interceptor para manejo de errores
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.data) {
          const errorData = error.response.data as any;
          throw new Error(errorData.error || errorData.message || 'Error en la petición');
        }
        throw new Error(error.message || 'Error de conexión');
      }
    );
  }

  // Dataset Endpoints
  async uploadDataset(file: File): Promise<Dataset> {
    const formData = new FormData();
    formData.append('file', file);
    
    const { data } = await this.client.post<Dataset>('/datasets/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 120000, 
    });
    return data;
  }

  async listDatasets(): Promise<Dataset[]> {
    const { data } = await this.client.get<{ datasets: Dataset[] }>('/datasets');
    return data.datasets;
  }

  async getDatasetPreview(datasetId: string, limit = 100): Promise<DatasetPreview> {
    const { data } = await this.client.get<DatasetPreview>(
      `/datasets/${datasetId}/preview`,
      { params: { limit } }
    );
    return data;
  }

  async deleteDataset(datasetId: string): Promise<void> {
    await this.client.delete(`/datasets/${datasetId}`);
  }

  async loadSampleDataset(sampleName: string): Promise<Dataset> {
    const { data } = await this.client.post<Dataset>(`/datasets/samples/${sampleName}/load`);
    return data;
  }

  async getStatistics(datasetId: string): Promise<DatasetStatistics> {
    const { data } = await this.client.get<{ statistics: DatasetStatistics }>(
      `/datasets/${datasetId}/statistics`
    );
    return data.statistics;
  }

  async getHistogram(datasetId: string, column: string, bins = 10): Promise<HistogramData> {
    const { data } = await this.client.get<HistogramData>(
      `/datasets/${datasetId}/histogram`,
      { params: { column, bins } }
    );
    return data;
  }

  // Model Endpoints
  async getModelTypes(): Promise<ModelType[]> {
    const { data } = await this.client.get<Record<string, Record<string, { name: string; params: string[] }>>>('/models/types');
    
    return Object.entries(data).map(([type, algorithms]) => ({
      type,
      algorithms: Object.entries(algorithms).map(([key, algo]) => ({
        name: key,
        displayName: algo.name,
        params: algo.params.map(param => ({
          name: param,
          type: 'float' as const,
          default: null
        }))
      }))
    }));
  }

  async trainModel(request: TrainingRequest): Promise<Model> {
    const backendRequest = {
      dataset_id: request.dataset_id,
      model_type: request.model_type,
      algorithm: request.algorithm,
      features: request.feature_columns, 
      target: request.target_column,      
      test_size: request.test_size,
      params: request.params,
      model_name: request.model_name
    };
    
    const { data } = await this.client.post<any>('/models/train', backendRequest, {
      timeout: 180000, // 3 minutos para entrenamiento de modelos
    });
    return {
      ...data,
      feature_columns: data.features || [],
      target_column: data.target || '',
    };
  }

  async listModels(): Promise<Model[]> {
    const { data } = await this.client.get<{ models: any[] }>('/models');
    return data.models.map(model => ({
      ...model,
      feature_columns: model.features || [],
      target_column: model.target || '',
    }));
  }

  async deleteModel(modelId: string): Promise<void> {
    await this.client.delete(`/models/${modelId}`);
  }

  // Report Endpoints
  async generateReport(
    datasetId?: string,
    modelId?: string,
    includePreview = true,
    includeStatistics = true,
    includeMetrics = true
  ): Promise<Blob> {
    const { data } = await this.client.post(
      '/reports/generate',
      {
        dataset_id: datasetId,
        model_id: modelId,
        include_preview: includePreview,
        include_statistics: includeStatistics,
        include_metrics: includeMetrics,
      },
      { 
        responseType: 'blob',
        timeout: 120000,
      }
    );
    return data;
  }
}

export const apiClient = new ApiClient();
export default apiClient;
