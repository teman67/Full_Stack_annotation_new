// JSON Export Utility for Comprehensive Annotation Data

interface JSONExportOptions {
  includeMetadata: boolean;
  includeComments: boolean;
  includeAnnotationHistory: boolean;
  includeStatistics: boolean;
  prettyFormat: boolean;
  includeSchema: boolean;
}

interface ExportedAnnotation {
  id: string;
  start: number;
  end: number;
  text: string;
  label: string;
  confidence?: number;
  annotator?: {
    id: string;
    name: string;
    email?: string;
  };
  created_at: string;
  updated_at?: string;
  comments?: string[];
  attributes?: Record<string, unknown>;
  relations?: Array<{
    type: string;
    target: string;
    direction?: "outgoing" | "incoming" | "bidirectional";
  }>;
  history?: Array<{
    action: "created" | "updated" | "deleted";
    timestamp: string;
    user: string;
    changes?: Record<string, { from: unknown; to: unknown }>;
  }>;
}

interface ExportedDocument {
  id: string;
  title: string;
  text: string;
  language?: string;
  created_at: string;
  updated_at?: string;
  metadata?: Record<string, unknown>;
  annotations: ExportedAnnotation[];
  statistics?: {
    total_annotations: number;
    annotations_by_label: Record<string, number>;
    annotations_by_annotator: Record<string, number>;
    average_confidence: number;
    text_length: number;
    annotation_density: number;
  };
  schema?: {
    labels: Array<{
      name: string;
      color?: string;
      description?: string;
      hotkey?: string;
    }>;
    relations?: Array<{
      name: string;
      source_labels: string[];
      target_labels: string[];
      symmetric: boolean;
    }>;
  };
}

interface JSONExportResult {
  export_info: {
    format: "json";
    version: string;
    created_at: string;
    created_by?: string;
    total_documents: number;
    total_annotations: number;
    export_options: JSONExportOptions;
  };
  documents: ExportedDocument[];
  global_statistics?: {
    total_documents: number;
    total_annotations: number;
    unique_labels: string[];
    unique_annotators: string[];
    label_distribution: Record<string, number>;
    annotator_contribution: Record<string, number>;
    confidence_distribution: {
      mean: number;
      median: number;
      std_dev: number;
      min: number;
      max: number;
    };
  };
  schema?: {
    $schema: string;
    type: string;
    properties: Record<string, unknown>;
  };
}

/**
 * JSON Export utility for comprehensive annotation data export
 */
export class JSONExporter {
  private options: JSONExportOptions;

  constructor(options: Partial<JSONExportOptions> = {}) {
    this.options = {
      includeMetadata: true,
      includeComments: true,
      includeAnnotationHistory: false,
      includeStatistics: true,
      prettyFormat: true,
      includeSchema: false,
      ...options,
    };
  }

  /**
   * Export documents to JSON format
   */
  public exportDocuments(documents: ExportedDocument[]): string {
    const result: JSONExportResult = {
      export_info: {
        format: "json",
        version: "1.0.0",
        created_at: new Date().toISOString(),
        total_documents: documents.length,
        total_annotations: documents.reduce(
          (sum, doc) => sum + doc.annotations.length,
          0
        ),
        export_options: this.options,
      },
      documents: this.processDocuments(documents),
    };

    if (this.options.includeStatistics) {
      result.global_statistics = this.generateGlobalStatistics(documents);
    }

    if (this.options.includeSchema) {
      result.schema = this.generateJSONSchema();
    }

    return this.options.prettyFormat
      ? JSON.stringify(result, null, 2)
      : JSON.stringify(result);
  }

  /**
   * Export a single document to JSON format
   */
  public exportDocument(document: ExportedDocument): string {
    const processedDocument = this.processDocument(document);

    return this.options.prettyFormat
      ? JSON.stringify(processedDocument, null, 2)
      : JSON.stringify(processedDocument);
  }

  /**
   * Process documents according to export options
   */
  private processDocuments(documents: ExportedDocument[]): ExportedDocument[] {
    return documents.map((doc) => this.processDocument(doc));
  }

  /**
   * Process a single document according to export options
   */
  private processDocument(document: ExportedDocument): ExportedDocument {
    const processed: ExportedDocument = {
      id: document.id,
      title: document.title,
      text: document.text,
      created_at: document.created_at,
      annotations: this.processAnnotations(document.annotations),
    };

    if (document.language) {
      processed.language = document.language;
    }

    if (document.updated_at) {
      processed.updated_at = document.updated_at;
    }

    if (this.options.includeMetadata && document.metadata) {
      processed.metadata = document.metadata;
    }

    if (this.options.includeStatistics) {
      processed.statistics = this.generateDocumentStatistics(document);
    }

    if (document.schema) {
      processed.schema = document.schema;
    }

    return processed;
  }

  /**
   * Process annotations according to export options
   */
  private processAnnotations(
    annotations: ExportedAnnotation[]
  ): ExportedAnnotation[] {
    return annotations.map((annotation) => {
      const processed: ExportedAnnotation = {
        id: annotation.id,
        start: annotation.start,
        end: annotation.end,
        text: annotation.text,
        label: annotation.label,
        created_at: annotation.created_at,
      };

      if (annotation.confidence !== undefined) {
        processed.confidence = annotation.confidence;
      }

      if (annotation.annotator) {
        processed.annotator = annotation.annotator;
      }

      if (annotation.updated_at) {
        processed.updated_at = annotation.updated_at;
      }

      if (this.options.includeComments && annotation.comments) {
        processed.comments = annotation.comments;
      }

      if (annotation.attributes) {
        processed.attributes = annotation.attributes;
      }

      if (annotation.relations) {
        processed.relations = annotation.relations;
      }

      if (this.options.includeAnnotationHistory && annotation.history) {
        processed.history = annotation.history;
      }

      return processed;
    });
  }

  /**
   * Generate document-level statistics
   */
  private generateDocumentStatistics(
    document: ExportedDocument
  ): ExportedDocument["statistics"] {
    const annotations = document.annotations;
    const labelCounts: Record<string, number> = {};
    const annotatorCounts: Record<string, number> = {};
    let totalConfidence = 0;
    let confidenceCount = 0;

    for (const annotation of annotations) {
      // Count labels
      labelCounts[annotation.label] = (labelCounts[annotation.label] || 0) + 1;

      // Count annotators
      if (annotation.annotator) {
        const annotatorName = annotation.annotator.name;
        annotatorCounts[annotatorName] =
          (annotatorCounts[annotatorName] || 0) + 1;
      }

      // Accumulate confidence
      if (annotation.confidence !== undefined) {
        totalConfidence += annotation.confidence;
        confidenceCount++;
      }
    }

    return {
      total_annotations: annotations.length,
      annotations_by_label: labelCounts,
      annotations_by_annotator: annotatorCounts,
      average_confidence:
        confidenceCount > 0 ? totalConfidence / confidenceCount : 0,
      text_length: document.text.length,
      annotation_density: annotations.length / document.text.length,
    };
  }

  /**
   * Generate global statistics across all documents
   */
  private generateGlobalStatistics(
    documents: ExportedDocument[]
  ): JSONExportResult["global_statistics"] {
    const allAnnotations = documents.flatMap((doc) => doc.annotations);
    const uniqueLabels = new Set<string>();
    const uniqueAnnotators = new Set<string>();
    const labelCounts: Record<string, number> = {};
    const annotatorCounts: Record<string, number> = {};
    const confidenceValues: number[] = [];

    for (const annotation of allAnnotations) {
      uniqueLabels.add(annotation.label);
      labelCounts[annotation.label] = (labelCounts[annotation.label] || 0) + 1;

      if (annotation.annotator) {
        uniqueAnnotators.add(annotation.annotator.name);
        annotatorCounts[annotation.annotator.name] =
          (annotatorCounts[annotation.annotator.name] || 0) + 1;
      }

      if (annotation.confidence !== undefined) {
        confidenceValues.push(annotation.confidence);
      }
    }

    const confidenceStats =
      this.calculateConfidenceStatistics(confidenceValues);

    return {
      total_documents: documents.length,
      total_annotations: allAnnotations.length,
      unique_labels: Array.from(uniqueLabels),
      unique_annotators: Array.from(uniqueAnnotators),
      label_distribution: labelCounts,
      annotator_contribution: annotatorCounts,
      confidence_distribution: confidenceStats,
    };
  }

  /**
   * Calculate confidence statistics
   */
  private calculateConfidenceStatistics(values: number[]): {
    mean: number;
    median: number;
    std_dev: number;
    min: number;
    max: number;
  } {
    if (values.length === 0) {
      return { mean: 0, median: 0, std_dev: 0, min: 0, max: 0 };
    }

    const sorted = [...values].sort((a, b) => a - b);
    const mean = values.reduce((sum, val) => sum + val, 0) / values.length;
    const variance =
      values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) /
      values.length;
    const stdDev = Math.sqrt(variance);

    const median =
      sorted.length % 2 === 0
        ? (sorted[sorted.length / 2 - 1] + sorted[sorted.length / 2]) / 2
        : sorted[Math.floor(sorted.length / 2)];

    return {
      mean: Number(mean.toFixed(3)),
      median: Number(median.toFixed(3)),
      std_dev: Number(stdDev.toFixed(3)),
      min: sorted[0],
      max: sorted[sorted.length - 1],
    };
  }

  /**
   * Generate JSON Schema for the export format
   */
  private generateJSONSchema(): JSONExportResult["schema"] {
    return {
      $schema: "http://json-schema.org/draft-07/schema#",
      type: "object",
      properties: {
        export_info: {
          type: "object",
          properties: {
            format: { type: "string", const: "json" },
            version: { type: "string" },
            created_at: { type: "string", format: "date-time" },
            total_documents: { type: "integer", minimum: 0 },
            total_annotations: { type: "integer", minimum: 0 },
          },
          required: [
            "format",
            "version",
            "created_at",
            "total_documents",
            "total_annotations",
          ],
        } as Record<string, unknown>,
        documents: {
          type: "array",
          items: {
            type: "object",
            properties: {
              id: { type: "string" },
              title: { type: "string" },
              text: { type: "string" },
              annotations: {
                type: "array",
                items: {
                  type: "object",
                  properties: {
                    id: { type: "string" },
                    start: { type: "integer", minimum: 0 },
                    end: { type: "integer", minimum: 0 },
                    text: { type: "string" },
                    label: { type: "string" },
                    confidence: { type: "number", minimum: 0, maximum: 1 },
                  },
                  required: ["id", "start", "end", "text", "label"],
                },
              },
            },
            required: ["id", "title", "text", "annotations"],
          },
        } as Record<string, unknown>,
      } as Record<string, unknown>,
    };
  }

  /**
   * Validate JSON export format
   */
  public validateExport(jsonText: string): {
    isValid: boolean;
    errors: string[];
    warnings: string[];
  } {
    const errors: string[] = [];
    const warnings: string[] = [];

    try {
      const data = JSON.parse(jsonText) as JSONExportResult;

      // Validate basic structure
      if (!data.export_info) {
        errors.push("Missing export_info section");
      } else {
        if (data.export_info.format !== "json") {
          errors.push("Invalid format in export_info");
        }
        if (!data.export_info.version) {
          errors.push("Missing version in export_info");
        }
      }

      if (!data.documents || !Array.isArray(data.documents)) {
        errors.push("Missing or invalid documents array");
      } else {
        // Validate each document
        for (let i = 0; i < data.documents.length; i++) {
          const doc = data.documents[i];
          if (!doc.id || !doc.title || !doc.text) {
            errors.push(
              `Document ${i}: Missing required fields (id, title, text)`
            );
          }

          if (!doc.annotations || !Array.isArray(doc.annotations)) {
            errors.push(`Document ${i}: Missing or invalid annotations array`);
          } else {
            // Validate annotations
            for (let j = 0; j < doc.annotations.length; j++) {
              const ann = doc.annotations[j];
              if (
                !ann.id ||
                ann.start === undefined ||
                ann.end === undefined ||
                !ann.text ||
                !ann.label
              ) {
                errors.push(
                  `Document ${i}, Annotation ${j}: Missing required fields`
                );
              }

              if (ann.start >= ann.end) {
                errors.push(
                  `Document ${i}, Annotation ${j}: Invalid span (start >= end)`
                );
              }

              if (
                ann.confidence !== undefined &&
                (ann.confidence < 0 || ann.confidence > 1)
              ) {
                warnings.push(
                  `Document ${i}, Annotation ${j}: Confidence out of range [0,1]`
                );
              }
            }
          }
        }
      }
    } catch (error) {
      errors.push(
        `Invalid JSON format: ${
          error instanceof Error ? error.message : "Unknown error"
        }`
      );
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings,
    };
  }
}
