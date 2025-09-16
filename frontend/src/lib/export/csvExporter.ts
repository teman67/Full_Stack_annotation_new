// CSV Export Utility for Spreadsheet Analysis

interface CSVExportOptions {
  includeMetadata: boolean;
  includeStatistics: boolean;
  separator: string;
  encoding: "utf-8" | "utf-16" | "ascii";
  includeHeaders: boolean;
  flattenNestedData: boolean;
}

interface CSVAnnotation {
  document_id: string;
  document_title: string;
  annotation_id: string;
  text: string;
  label: string;
  start_position: number;
  end_position: number;
  length: number;
  confidence?: number;
  annotator_name?: string;
  annotator_email?: string;
  created_at: string;
  updated_at?: string;
  comment_count?: number;
  has_relations?: boolean;
  relation_count?: number;
}

interface CSVDocument {
  document_id: string;
  title: string;
  text_length: number;
  annotation_count: number;
  unique_labels: number;
  annotation_density: number;
  created_at: string;
  updated_at?: string;
  language?: string;
}

interface CSVLabelStatistics {
  label: string;
  total_count: number;
  document_count: number;
  average_confidence?: number;
  average_length: number;
  frequency_percentage: number;
}

interface CSVAnnotatorStatistics {
  annotator_name: string;
  annotator_email?: string;
  annotation_count: number;
  document_count: number;
  average_confidence?: number;
  unique_labels: number;
  productivity_score: number;
}

/**
 * CSV Export utility for spreadsheet-friendly annotation data
 */
export class CSVExporter {
  private options: CSVExportOptions;

  constructor(options: Partial<CSVExportOptions> = {}) {
    this.options = {
      includeMetadata: true,
      includeStatistics: true,
      separator: ",",
      encoding: "utf-8",
      includeHeaders: true,
      flattenNestedData: true,
      ...options,
    };
  }

  /**
   * Export annotations to CSV format
   */
  public exportAnnotations(annotations: CSVAnnotation[]): string {
    const headers = [
      "document_id",
      "document_title",
      "annotation_id",
      "text",
      "label",
      "start_position",
      "end_position",
      "length",
      "confidence",
      "annotator_name",
      "annotator_email",
      "created_at",
      "updated_at",
      "comment_count",
      "has_relations",
      "relation_count",
    ];

    const rows = annotations.map((annotation) => [
      this.escapeCSVField(annotation.document_id),
      this.escapeCSVField(annotation.document_title),
      this.escapeCSVField(annotation.annotation_id),
      this.escapeCSVField(annotation.text),
      this.escapeCSVField(annotation.label),
      annotation.start_position.toString(),
      annotation.end_position.toString(),
      annotation.length.toString(),
      annotation.confidence?.toString() || "",
      this.escapeCSVField(annotation.annotator_name || ""),
      this.escapeCSVField(annotation.annotator_email || ""),
      annotation.created_at,
      annotation.updated_at || "",
      annotation.comment_count?.toString() || "0",
      annotation.has_relations ? "true" : "false",
      annotation.relation_count?.toString() || "0",
    ]);

    const lines = this.options.includeHeaders ? [headers, ...rows] : rows;
    return lines.map((row) => row.join(this.options.separator)).join("\n");
  }

  /**
   * Export document statistics to CSV format
   */
  public exportDocuments(documents: CSVDocument[]): string {
    const headers = [
      "document_id",
      "title",
      "text_length",
      "annotation_count",
      "unique_labels",
      "annotation_density",
      "created_at",
      "updated_at",
      "language",
    ];

    const rows = documents.map((doc) => [
      this.escapeCSVField(doc.document_id),
      this.escapeCSVField(doc.title),
      doc.text_length.toString(),
      doc.annotation_count.toString(),
      doc.unique_labels.toString(),
      doc.annotation_density.toFixed(6),
      doc.created_at,
      doc.updated_at || "",
      this.escapeCSVField(doc.language || ""),
    ]);

    const lines = this.options.includeHeaders ? [headers, ...rows] : rows;
    return lines.map((row) => row.join(this.options.separator)).join("\n");
  }

  /**
   * Export label statistics to CSV format
   */
  public exportLabelStatistics(statistics: CSVLabelStatistics[]): string {
    const headers = [
      "label",
      "total_count",
      "document_count",
      "average_confidence",
      "average_length",
      "frequency_percentage",
    ];

    const rows = statistics.map((stat) => [
      this.escapeCSVField(stat.label),
      stat.total_count.toString(),
      stat.document_count.toString(),
      stat.average_confidence?.toFixed(3) || "",
      stat.average_length.toFixed(2),
      stat.frequency_percentage.toFixed(2),
    ]);

    const lines = this.options.includeHeaders ? [headers, ...rows] : rows;
    return lines.map((row) => row.join(this.options.separator)).join("\n");
  }

  /**
   * Export annotator statistics to CSV format
   */
  public exportAnnotatorStatistics(
    statistics: CSVAnnotatorStatistics[]
  ): string {
    const headers = [
      "annotator_name",
      "annotator_email",
      "annotation_count",
      "document_count",
      "average_confidence",
      "unique_labels",
      "productivity_score",
    ];

    const rows = statistics.map((stat) => [
      this.escapeCSVField(stat.annotator_name),
      this.escapeCSVField(stat.annotator_email || ""),
      stat.annotation_count.toString(),
      stat.document_count.toString(),
      stat.average_confidence?.toFixed(3) || "",
      stat.unique_labels.toString(),
      stat.productivity_score.toFixed(3),
    ]);

    const lines = this.options.includeHeaders ? [headers, ...rows] : rows;
    return lines.map((row) => row.join(this.options.separator)).join("\n");
  }

  /**
   * Export comprehensive dataset with multiple sheets
   */
  public exportDataset(data: {
    annotations: CSVAnnotation[];
    documents: CSVDocument[];
    labelStatistics: CSVLabelStatistics[];
    annotatorStatistics: CSVAnnotatorStatistics[];
  }): string {
    const sections = [];

    // Annotations section
    sections.push("# ANNOTATIONS");
    sections.push(this.exportAnnotations(data.annotations));
    sections.push("");

    // Documents section
    sections.push("# DOCUMENTS");
    sections.push(this.exportDocuments(data.documents));
    sections.push("");

    // Label statistics section
    sections.push("# LABEL_STATISTICS");
    sections.push(this.exportLabelStatistics(data.labelStatistics));
    sections.push("");

    // Annotator statistics section
    sections.push("# ANNOTATOR_STATISTICS");
    sections.push(this.exportAnnotatorStatistics(data.annotatorStatistics));

    return sections.join("\n");
  }

  /**
   * Generate label statistics from raw annotation data
   */
  public generateLabelStatistics(
    annotations: CSVAnnotation[]
  ): CSVLabelStatistics[] {
    const labelGroups = new Map<string, CSVAnnotation[]>();

    // Group annotations by label
    for (const annotation of annotations) {
      if (!labelGroups.has(annotation.label)) {
        labelGroups.set(annotation.label, []);
      }
      labelGroups.get(annotation.label)!.push(annotation);
    }

    const totalAnnotations = annotations.length;
    const statistics: CSVLabelStatistics[] = [];

    for (const [label, labelAnnotations] of labelGroups) {
      const documentIds = new Set(labelAnnotations.map((a) => a.document_id));
      const confidenceValues = labelAnnotations
        .map((a) => a.confidence)
        .filter((c): c is number => c !== undefined);

      const averageConfidence =
        confidenceValues.length > 0
          ? confidenceValues.reduce((sum, c) => sum + c, 0) /
            confidenceValues.length
          : undefined;

      const averageLength =
        labelAnnotations.reduce((sum, a) => sum + a.length, 0) /
        labelAnnotations.length;

      statistics.push({
        label,
        total_count: labelAnnotations.length,
        document_count: documentIds.size,
        average_confidence: averageConfidence,
        average_length: averageLength,
        frequency_percentage:
          (labelAnnotations.length / totalAnnotations) * 100,
      });
    }

    return statistics.sort((a, b) => b.total_count - a.total_count);
  }

  /**
   * Generate annotator statistics from raw annotation data
   */
  public generateAnnotatorStatistics(
    annotations: CSVAnnotation[]
  ): CSVAnnotatorStatistics[] {
    const annotatorGroups = new Map<string, CSVAnnotation[]>();

    // Group annotations by annotator
    for (const annotation of annotations) {
      const key = annotation.annotator_name || "Unknown";
      if (!annotatorGroups.has(key)) {
        annotatorGroups.set(key, []);
      }
      annotatorGroups.get(key)!.push(annotation);
    }

    const statistics: CSVAnnotatorStatistics[] = [];

    for (const [annotatorName, annotatorAnnotations] of annotatorGroups) {
      const documentIds = new Set(
        annotatorAnnotations.map((a) => a.document_id)
      );
      const uniqueLabels = new Set(annotatorAnnotations.map((a) => a.label));
      const confidenceValues = annotatorAnnotations
        .map((a) => a.confidence)
        .filter((c): c is number => c !== undefined);

      const averageConfidence =
        confidenceValues.length > 0
          ? confidenceValues.reduce((sum, c) => sum + c, 0) /
            confidenceValues.length
          : undefined;

      // Calculate productivity score (annotations per document)
      const productivityScore = annotatorAnnotations.length / documentIds.size;

      // Get email from first annotation (assuming consistent)
      const annotatorEmail = annotatorAnnotations[0]?.annotator_email;

      statistics.push({
        annotator_name: annotatorName,
        annotator_email: annotatorEmail,
        annotation_count: annotatorAnnotations.length,
        document_count: documentIds.size,
        average_confidence: averageConfidence,
        unique_labels: uniqueLabels.size,
        productivity_score: productivityScore,
      });
    }

    return statistics.sort((a, b) => b.annotation_count - a.annotation_count);
  }

  /**
   * Escape CSV field to handle commas, quotes, and newlines
   */
  private escapeCSVField(field: string): string {
    if (
      field.includes(this.options.separator) ||
      field.includes('"') ||
      field.includes("\n")
    ) {
      return `"${field.replace(/"/g, '""')}"`;
    }
    return field;
  }

  /**
   * Convert annotations to CSV-friendly format
   */
  public convertAnnotationsToCSV(
    documents: Array<{
      id: string;
      title: string;
      text: string;
      annotations: Array<{
        id: string;
        start: number;
        end: number;
        text: string;
        label: string;
        confidence?: number;
        annotator?: {
          name: string;
          email?: string;
        };
        created_at: string;
        updated_at?: string;
        comments?: string[];
        relations?: unknown[];
      }>;
    }>
  ): CSVAnnotation[] {
    const csvAnnotations: CSVAnnotation[] = [];

    for (const document of documents) {
      for (const annotation of document.annotations) {
        csvAnnotations.push({
          document_id: document.id,
          document_title: document.title,
          annotation_id: annotation.id,
          text: annotation.text,
          label: annotation.label,
          start_position: annotation.start,
          end_position: annotation.end,
          length: annotation.end - annotation.start,
          confidence: annotation.confidence,
          annotator_name: annotation.annotator?.name,
          annotator_email: annotation.annotator?.email,
          created_at: annotation.created_at,
          updated_at: annotation.updated_at,
          comment_count: annotation.comments?.length || 0,
          has_relations: (annotation.relations?.length || 0) > 0,
          relation_count: annotation.relations?.length || 0,
        });
      }
    }

    return csvAnnotations;
  }

  /**
   * Convert documents to CSV-friendly format
   */
  public convertDocumentsToCSV(
    documents: Array<{
      id: string;
      title: string;
      text: string;
      language?: string;
      created_at: string;
      updated_at?: string;
      annotations: Array<{
        label: string;
      }>;
    }>
  ): CSVDocument[] {
    return documents.map((document) => {
      const uniqueLabels = new Set(document.annotations.map((a) => a.label));

      return {
        document_id: document.id,
        title: document.title,
        text_length: document.text.length,
        annotation_count: document.annotations.length,
        unique_labels: uniqueLabels.size,
        annotation_density: document.annotations.length / document.text.length,
        created_at: document.created_at,
        updated_at: document.updated_at,
        language: document.language,
      };
    });
  }

  /**
   * Validate CSV export format
   */
  public validateCSV(csvText: string): {
    isValid: boolean;
    errors: string[];
    warnings: string[];
    rowCount: number;
    columnCount: number;
  } {
    const errors: string[] = [];
    const warnings: string[] = [];
    const lines = csvText
      .split("\n")
      .filter((line) => line.trim() !== "" && !line.startsWith("#"));

    if (lines.length === 0) {
      errors.push("Empty CSV content");
      return { isValid: false, errors, warnings, rowCount: 0, columnCount: 0 };
    }

    const headerLine = lines[0];
    const expectedColumns = headerLine.split(this.options.separator).length;
    let rowCount = 0;

    for (let i = 1; i < lines.length; i++) {
      const line = lines[i];
      const columns = line.split(this.options.separator);

      if (columns.length !== expectedColumns) {
        errors.push(
          `Row ${i + 1}: Expected ${expectedColumns} columns, got ${
            columns.length
          }`
        );
      }

      rowCount++;
    }

    if (rowCount === 0) {
      warnings.push("CSV contains only headers, no data rows");
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings,
      rowCount: rowCount,
      columnCount: expectedColumns,
    };
  }
}
