/**
 * Annotation App JavaScript SDK
 * Provides a TypeScript-friendly interface for interacting with the Annotation API
 */

export interface APIConfig {
  apiKey: string;
  baseURL?: string;
  timeout?: number;
  retries?: number;
}

export interface APIResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface Document {
  id: string;
  title: string;
  content: string;
  created_at: string;
  updated_at: string;
  annotation_count: number;
  status: "pending" | "in_progress" | "completed";
  metadata?: Record<string, unknown>;
}

export interface Annotation {
  id: string;
  document_id: string;
  start: number;
  end: number;
  text: string;
  label: string;
  confidence?: number;
  annotator_id?: string;
  created_at: string;
  metadata?: Record<string, unknown>;
}

export interface ExportOptions {
  format: "json" | "conll" | "csv" | "standoff";
  include_metadata?: boolean;
  include_statistics?: boolean;
  filter_labels?: string[];
  encoding_scheme?: "BIO" | "BILOU" | "IO";
  csv_separator?: string;
}

export interface ExportJob {
  id: string;
  status: "pending" | "processing" | "completed" | "failed";
  document_id: string;
  format: string;
  created_at: string;
  completed_at?: string;
  download_url?: string;
  error_message?: string;
  progress?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pages: number;
  limit: number;
}

export interface ListOptions {
  page?: number;
  limit?: number;
  search?: string;
  sort_by?: string;
  sort_order?: "asc" | "desc";
  [key: string]: unknown;
}

/**
 * HTTP Client for making API requests
 */
class HTTPClient {
  private config: Required<APIConfig>;

  constructor(config: APIConfig) {
    this.config = {
      baseURL: "https://api.annotation-app.com",
      timeout: 30000,
      retries: 3,
      ...config,
    };
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<APIResponse<T>> {
    const url = `${this.config.baseURL}${endpoint}`;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${this.config.apiKey}`,
          ...options.headers,
        },
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      const data = await response.json();

      if (!response.ok) {
        return {
          success: false,
          error:
            data.error || `HTTP ${response.status}: ${response.statusText}`,
        };
      }

      return {
        success: true,
        data,
      };
    } catch (error) {
      clearTimeout(timeoutId);

      if (error instanceof Error) {
        return {
          success: false,
          error: error.message,
        };
      }

      return {
        success: false,
        error: "Unknown error occurred",
      };
    }
  }

  async get<T>(
    endpoint: string,
    params?: Record<string, unknown>
  ): Promise<APIResponse<T>> {
    const url = new URL(endpoint, this.config.baseURL);
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          url.searchParams.append(key, String(value));
        }
      });
    }

    return this.request<T>(url.pathname + url.search);
  }

  async post<T>(endpoint: string, data?: unknown): Promise<APIResponse<T>> {
    return this.request<T>(endpoint, {
      method: "POST",
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async put<T>(endpoint: string, data?: unknown): Promise<APIResponse<T>> {
    return this.request<T>(endpoint, {
      method: "PUT",
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async delete<T>(endpoint: string): Promise<APIResponse<T>> {
    return this.request<T>(endpoint, {
      method: "DELETE",
    });
  }
}

/**
 * Documents API client
 */
export class DocumentsAPI {
  constructor(private client: HTTPClient) {}

  /**
   * List all documents
   */
  async list(
    options: ListOptions = {}
  ): Promise<APIResponse<PaginatedResponse<Document>>> {
    return this.client.get<PaginatedResponse<Document>>(
      "/api/documents",
      options
    );
  }

  /**
   * Get a specific document by ID
   */
  async get(id: string): Promise<APIResponse<Document>> {
    return this.client.get<Document>(`/api/documents/${id}`);
  }

  /**
   * Create a new document
   */
  async create(document: Partial<Document>): Promise<APIResponse<Document>> {
    return this.client.post<Document>("/api/documents", document);
  }

  /**
   * Update an existing document
   */
  async update(
    id: string,
    updates: Partial<Document>
  ): Promise<APIResponse<Document>> {
    return this.client.put<Document>(`/api/documents/${id}`, updates);
  }

  /**
   * Delete a document
   */
  async delete(id: string): Promise<APIResponse<void>> {
    return this.client.delete<void>(`/api/documents/${id}`);
  }

  /**
   * Export document annotations
   */
  async export(
    id: string,
    options: ExportOptions
  ): Promise<APIResponse<ExportJob>> {
    return this.client.post<ExportJob>(`/api/documents/${id}/export`, options);
  }

  /**
   * Get export job status
   */
  async getExportJob(jobId: string): Promise<APIResponse<ExportJob>> {
    return this.client.get<ExportJob>(`/api/export-jobs/${jobId}`);
  }

  /**
   * Download export file
   */
  async downloadExport(jobId: string): Promise<APIResponse<Blob>> {
    // Special handling for file downloads
    const url = `${this.client["config"].baseURL}/api/export-jobs/${jobId}/download`;

    try {
      const response = await fetch(url, {
        headers: {
          Authorization: `Bearer ${this.client["config"].apiKey}`,
        },
      });

      if (!response.ok) {
        return {
          success: false,
          error: `HTTP ${response.status}: ${response.statusText}`,
        };
      }

      const blob = await response.blob();
      return {
        success: true,
        data: blob,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : "Download failed",
      };
    }
  }
}

/**
 * Annotations API client
 */
export class AnnotationsAPI {
  constructor(private client: HTTPClient) {}

  /**
   * List annotations for a document
   */
  async list(
    documentId: string,
    options: ListOptions & { label?: string } = {}
  ): Promise<APIResponse<PaginatedResponse<Annotation>>> {
    return this.client.get<PaginatedResponse<Annotation>>(
      `/api/documents/${documentId}/annotations`,
      options
    );
  }

  /**
   * Get a specific annotation
   */
  async get(id: string): Promise<APIResponse<Annotation>> {
    return this.client.get<Annotation>(`/api/annotations/${id}`);
  }

  /**
   * Create a new annotation
   */
  async create(
    annotation: Partial<Annotation>
  ): Promise<APIResponse<Annotation>> {
    return this.client.post<Annotation>("/api/annotations", annotation);
  }

  /**
   * Update an existing annotation
   */
  async update(
    id: string,
    updates: Partial<Annotation>
  ): Promise<APIResponse<Annotation>> {
    return this.client.put<Annotation>(`/api/annotations/${id}`, updates);
  }

  /**
   * Delete an annotation
   */
  async delete(id: string): Promise<APIResponse<void>> {
    return this.client.delete<void>(`/api/annotations/${id}`);
  }

  /**
   * Bulk create annotations
   */
  async bulkCreate(
    annotations: Partial<Annotation>[]
  ): Promise<APIResponse<Annotation[]>> {
    return this.client.post<Annotation[]>("/api/annotations/bulk", {
      annotations,
    });
  }
}

/**
 * Main SDK client
 */
export class AnnotationAPI {
  private client: HTTPClient;
  public documents: DocumentsAPI;
  public annotations: AnnotationsAPI;

  constructor(config: APIConfig) {
    this.client = new HTTPClient(config);
    this.documents = new DocumentsAPI(this.client);
    this.annotations = new AnnotationsAPI(this.client);
  }

  /**
   * Test API connection
   */
  async ping(): Promise<APIResponse<{ message: string; timestamp: string }>> {
    return this.client.get("/api/ping");
  }

  /**
   * Get API status and version
   */
  async status(): Promise<APIResponse<{ version: string; status: string }>> {
    return this.client.get("/api/status");
  }
}

/**
 * Utility functions
 */
export class AnnotationUtils {
  /**
   * Calculate annotation statistics
   */
  static calculateStats(annotations: Annotation[]) {
    const labelCounts: Record<string, number> = {};
    const annotatorCounts: Record<string, number> = {};
    let totalLength = 0;

    for (const annotation of annotations) {
      // Count labels
      labelCounts[annotation.label] = (labelCounts[annotation.label] || 0) + 1;

      // Count annotators
      if (annotation.annotator_id) {
        annotatorCounts[annotation.annotator_id] =
          (annotatorCounts[annotation.annotator_id] || 0) + 1;
      }

      // Calculate text length
      totalLength += annotation.text.length;
    }

    return {
      total: annotations.length,
      labels: labelCounts,
      annotators: annotatorCounts,
      averageLength:
        annotations.length > 0 ? totalLength / annotations.length : 0,
      totalLength,
    };
  }

  /**
   * Validate annotation overlap
   */
  static findOverlaps(annotations: Annotation[]): Array<{
    annotation1: Annotation;
    annotation2: Annotation;
    overlapStart: number;
    overlapEnd: number;
  }> {
    const overlaps = [];

    for (let i = 0; i < annotations.length; i++) {
      for (let j = i + 1; j < annotations.length; j++) {
        const ann1 = annotations[i];
        const ann2 = annotations[j];

        // Check if they're for the same document
        if (ann1.document_id !== ann2.document_id) continue;

        // Check for overlap
        const overlapStart = Math.max(ann1.start, ann2.start);
        const overlapEnd = Math.min(ann1.end, ann2.end);

        if (overlapStart < overlapEnd) {
          overlaps.push({
            annotation1: ann1,
            annotation2: ann2,
            overlapStart,
            overlapEnd,
          });
        }
      }
    }

    return overlaps;
  }

  /**
   * Convert annotations to CoNLL format
   */
  static toCoNLL(
    text: string,
    annotations: Annotation[],
    scheme: "BIO" | "BILOU" | "IO" = "BIO"
  ): string {
    const tokens = text.split(/\s+/);
    const tokenAnnotations: string[] = new Array(tokens.length).fill("O");

    let currentPos = 0;
    for (let i = 0; i < tokens.length; i++) {
      const token = tokens[i];
      const tokenStart = text.indexOf(token, currentPos);
      const tokenEnd = tokenStart + token.length;

      // Find annotations that cover this token
      for (const annotation of annotations) {
        if (annotation.start <= tokenStart && annotation.end >= tokenEnd) {
          const isFirst =
            i === 0 || !tokenAnnotations[i - 1].endsWith(annotation.label);

          if (scheme === "BIO") {
            tokenAnnotations[i] = `${isFirst ? "B" : "I"}-${annotation.label}`;
          } else if (scheme === "IO") {
            tokenAnnotations[i] = `I-${annotation.label}`;
          } else if (scheme === "BILOU") {
            const isLast =
              i === tokens.length - 1 ||
              !annotations.some(
                (a) =>
                  a.label === annotation.label &&
                  a.start <= text.indexOf(tokens[i + 1], tokenEnd) &&
                  a.end >=
                    text.indexOf(tokens[i + 1], tokenEnd) + tokens[i + 1].length
              );

            if (isFirst && isLast) {
              tokenAnnotations[i] = `U-${annotation.label}`;
            } else if (isFirst) {
              tokenAnnotations[i] = `B-${annotation.label}`;
            } else if (isLast) {
              tokenAnnotations[i] = `L-${annotation.label}`;
            } else {
              tokenAnnotations[i] = `I-${annotation.label}`;
            }
          }
          break; // Use first matching annotation
        }
      }

      currentPos = tokenEnd;
    }

    // Build CoNLL output
    const lines = [];
    for (let i = 0; i < tokens.length; i++) {
      lines.push(`${tokens[i]}\t${tokenAnnotations[i]}`);
    }

    return lines.join("\n");
  }
}

// Export default instance for convenience
export default AnnotationAPI;
