import axios, { AxiosInstance } from 'axios';
import {
  APIRequest,
  APIResponse,
  DatasetListResponse,
  DatasetMetadata,
  DatasetUploadResponse,
} from '@/types';

class APIClient {
  private client: AxiosInstance;
  private baseURL: string;
  private streamingURL: string;

  constructor() {
    this.baseURL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';
    this.streamingURL = process.env.NEXT_PUBLIC_API_STREAMING_URL || `${this.baseURL}/ask/question/stream`;
    
    this.client = axios.create({
      baseURL: this.baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  // Set authentication token/API key
  setAuth(token?: string, apiKey?: string) {
    if (token) {
      this.client.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else if (apiKey) {
      this.client.defaults.headers.common['X-API-Key'] = apiKey;
    } else {
      delete this.client.defaults.headers.common['Authorization'];
      delete this.client.defaults.headers.common['X-API-Key'];
    }
  }

  // Non-streaming request
  async askQuestion(request: APIRequest): Promise<APIResponse> {
    try {
      const response = await this.client.post<APIResponse>('/ask/question', request);
      return response.data;
    } catch (error: any) {
      if (error.response) {
        throw new Error(error.response.data?.error || error.response.data?.message || 'API request failed');
      } else if (error.request) {
        throw new Error('Unable to connect to the server. Please check your connection.');
      } else {
        throw new Error(error.message || 'An unexpected error occurred');
      }
    }
  }

  // Streaming request using Server-Sent Events
  async askQuestionStream(
    request: APIRequest,
    onChunk: (chunk: string) => void,
    onComplete: (response: APIResponse) => void,
    onError: (error: Error) => void
  ) {
    const token = this.client.defaults.headers.common['Authorization']?.toString().replace('Bearer ', '');
    const apiKey = this.client.defaults.headers.common['X-API-Key']?.toString();

    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      Accept: 'text/event-stream',
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    } else if (apiKey) {
      headers['X-API-Key'] = apiKey;
    }

    try {
      const response = await fetch(this.streamingURL, {
        method: 'POST',
        headers,
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const message = await response.text();
        throw new Error(message || `HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder('utf-8');

      if (!reader) {
        throw new Error('No response body');
      }

      let buffer = '';
      let accumulatedText = '';
      let completed = false;
      let metaColumns: string[] | undefined;
      let metaRows: any[][] | undefined;
      let metaVisualization: APIResponse['visualization'];
      let metaSuccess = false;

      try {
        while (true) {
          const { done, value } = await reader.read();

          if (done) {
            break;
          }

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const rawLine of lines) {
            const line = rawLine.trim();
            if (!line.startsWith('data:')) {
              continue;
            }

            const payload = line.slice(5).trim();
            if (!payload) {
              continue;
            }

            let event: any;
            try {
              event = JSON.parse(payload);
            } catch {
              continue;
            }

            const eventType = event.type as string | undefined;

            switch (eventType) {
              case 'status':
                // Ignore backend status updates for end users
                break;
              case 'metadata':
                metaColumns = event.columns ?? metaColumns;
                metaRows = event.rows ?? metaRows;
                metaVisualization = event.visualization ?? metaVisualization;
                metaSuccess = event.success ?? metaSuccess;
                break;
              case 'chunk': {
                const chunkText: string =
                  (typeof event.accumulated === 'string' && event.accumulated) ||
                  (typeof event.text === 'string' ? event.text : '');
                if (chunkText) {
                  accumulatedText = chunkText;
                  onChunk(accumulatedText);
                }
                break;
              }
              case 'complete': {
                const finalText: string =
                  (typeof event.text === 'string' && event.text) || accumulatedText;
                accumulatedText = finalText;
                onComplete({
                  success: metaSuccess || true,
                  response: finalText,
                  data:
                    metaColumns && metaRows
                      ? {
                          columns: metaColumns,
                          rows: metaRows,
                        }
                      : undefined,
                  visualization: metaVisualization,
                });
                completed = true;
                break;
              }
              case 'error': {
                completed = true;
                throw new Error(
                  event.message ||
                    'The assistant could not find relevant information for this question.'
                );
              }
              default:
                break;
            }

            if (completed) {
              break;
            }
          }

          if (completed) {
            break;
          }
        }
      } finally {
        reader.releaseLock();
      }

      if (!completed) {
        onComplete({
          success: metaSuccess || Boolean(accumulatedText),
          response: accumulatedText,
          data:
            metaColumns && metaRows
              ? {
                  columns: metaColumns,
                  rows: metaRows,
                }
              : undefined,
          visualization: metaVisualization,
        });
      }
    } catch (error: any) {
      onError(new Error(error?.message || 'Streaming request failed'));
    }
  }

  // Health check
  async healthCheck(): Promise<boolean> {
    try {
      const response = await this.client.get('/health');
      return response.status === 200;
    } catch {
      return false;
    }
  }

  async listDatasets(): Promise<DatasetMetadata[]> {
    try {
      const response = await this.client.get<DatasetListResponse>('/datasets');
      return response.data.datasets;
    } catch (error: any) {
      if (error.response) {
        throw new Error(error.response.data?.detail || 'Failed to load datasets');
      }
      throw new Error('Unable to load datasets. Please check your connection.');
    }
  }

  async uploadDataset(
    file: File,
    datasetType: string,
    options?: {
      name?: string;
      storeId?: string;
      columnDescriptions?: Record<string, string>;
    }
  ): Promise<DatasetMetadata> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('dataset_type', datasetType);
    if (options?.name) {
      formData.append('name', options.name);
    }
    if (options?.storeId) {
      formData.append('store_id', options.storeId);
    }
    if (options?.columnDescriptions) {
      formData.append(
        'column_descriptions',
        JSON.stringify(options.columnDescriptions)
      );
    }

    try {
      const response = await this.client.post<DatasetUploadResponse>(
        '/datasets/upload',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      return response.data.dataset;
    } catch (error: any) {
      if (error.response) {
        throw new Error(error.response.data?.detail || 'Failed to upload dataset');
      }
      throw new Error('Unable to upload dataset. Please check your connection.');
    }
  }
}

export const apiClient = new APIClient();

