// CoNLL Format Export Utility
// Migrated from original Streamlit app functionality

interface Token {
  id: number;
  text: string;
  start: number;
  end: number;
  whitespace?: string;
  pos?: string;
  lemma?: string;
}

interface Annotation {
  id: string;
  start: number;
  end: number;
  label: string;
  text: string;
  confidence?: number;
  annotator?: string;
  created_at?: string;
}

interface Document {
  id: string;
  title: string;
  text: string;
  tokens: Token[];
  annotations: Annotation[];
  metadata?: Record<string, unknown>;
}

interface CoNLLOptions {
  includePos: boolean;
  includeLemma: boolean;
  includeConfidence: boolean;
  encoding: "BIO" | "BILOU" | "IO";
  separator: string;
}

/**
 * Convert annotations to CoNLL format
 * Migrated from the original Streamlit app's CoNLL export functionality
 */
export class CoNLLExporter {
  private options: CoNLLOptions;

  constructor(options: Partial<CoNLLOptions> = {}) {
    this.options = {
      includePos: false,
      includeLemma: false,
      includeConfidence: false,
      encoding: "BIO",
      separator: "\t",
      ...options,
    };
  }

  /**
   * Export a document to CoNLL format
   */
  public exportDocument(document: Document): string {
    const lines: string[] = [];

    // Add document header
    lines.push(`# doc_id = ${document.id}`);
    lines.push(`# doc_title = ${document.title}`);
    lines.push("");

    // Generate token-level annotations
    const tokenAnnotations = this.generateTokenAnnotations(document);

    // Create CoNLL lines
    for (let i = 0; i < document.tokens.length; i++) {
      const token = document.tokens[i];
      const annotation = tokenAnnotations[i];

      const columns = [
        (i + 1).toString(), // Token ID
        token.text, // Token text
      ];

      if (this.options.includePos && token.pos) {
        columns.push(token.pos);
      }

      if (this.options.includeLemma && token.lemma) {
        columns.push(token.lemma);
      }

      // Add NER tag
      columns.push(annotation.tag);

      if (
        this.options.includeConfidence &&
        annotation.confidence !== undefined
      ) {
        columns.push(annotation.confidence.toFixed(3));
      }

      lines.push(columns.join(this.options.separator));
    }

    lines.push(""); // End with empty line
    return lines.join("\n");
  }

  /**
   * Export multiple documents to CoNLL format
   */
  public exportDocuments(documents: Document[]): string {
    return documents.map((doc) => this.exportDocument(doc)).join("\n");
  }

  /**
   * Generate token-level annotations using the specified encoding scheme
   */
  private generateTokenAnnotations(document: Document): Array<{
    tag: string;
    confidence?: number;
  }> {
    const tokenAnnotations = document.tokens.map(() => ({
      tag: "O",
      confidence: undefined as number | undefined,
    }));

    // Sort annotations by start position to handle overlaps
    const sortedAnnotations = [...document.annotations].sort(
      (a, b) => a.start - b.start
    );

    for (const annotation of sortedAnnotations) {
      const overlappingTokens = this.findOverlappingTokens(
        document.tokens,
        annotation
      );

      if (overlappingTokens.length === 0) continue;

      // Apply encoding scheme
      this.applyEncodingScheme(tokenAnnotations, overlappingTokens, annotation);
    }

    return tokenAnnotations;
  }

  /**
   * Find tokens that overlap with an annotation
   */
  private findOverlappingTokens(
    tokens: Token[],
    annotation: Annotation
  ): number[] {
    const overlapping: number[] = [];

    for (let i = 0; i < tokens.length; i++) {
      const token = tokens[i];

      // Check if token overlaps with annotation
      if (token.start < annotation.end && token.end > annotation.start) {
        overlapping.push(i);
      }
    }

    return overlapping;
  }

  /**
   * Apply the specified encoding scheme to tokens
   */
  private applyEncodingScheme(
    tokenAnnotations: Array<{ tag: string; confidence?: number }>,
    tokenIndices: number[],
    annotation: Annotation
  ): void {
    if (tokenIndices.length === 0) return;

    const label = annotation.label;
    const confidence = annotation.confidence;

    switch (this.options.encoding) {
      case "BIO":
        // First token gets B- prefix, rest get I- prefix
        tokenAnnotations[tokenIndices[0]] = {
          tag: `B-${label}`,
          confidence,
        };
        for (let i = 1; i < tokenIndices.length; i++) {
          tokenAnnotations[tokenIndices[i]] = {
            tag: `I-${label}`,
            confidence,
          };
        }
        break;

      case "BILOU":
        if (tokenIndices.length === 1) {
          // Single token gets U- prefix
          tokenAnnotations[tokenIndices[0]] = {
            tag: `U-${label}`,
            confidence,
          };
        } else {
          // First token gets B-, last gets L-, middle get I-
          tokenAnnotations[tokenIndices[0]] = {
            tag: `B-${label}`,
            confidence,
          };
          for (let i = 1; i < tokenIndices.length - 1; i++) {
            tokenAnnotations[tokenIndices[i]] = {
              tag: `I-${label}`,
              confidence,
            };
          }
          tokenAnnotations[tokenIndices[tokenIndices.length - 1]] = {
            tag: `L-${label}`,
            confidence,
          };
        }
        break;

      case "IO":
        // All tokens get I- prefix
        for (const tokenIndex of tokenIndices) {
          tokenAnnotations[tokenIndex] = {
            tag: `I-${label}`,
            confidence,
          };
        }
        break;
    }
  }

  /**
   * Generate statistics for the export
   */
  public generateStatistics(documents: Document[]): {
    totalDocuments: number;
    totalTokens: number;
    totalAnnotations: number;
    labelCounts: Record<string, number>;
    averageTokensPerDocument: number;
    averageAnnotationsPerDocument: number;
  } {
    const totalTokens = documents.reduce(
      (sum, doc) => sum + doc.tokens.length,
      0
    );
    const totalAnnotations = documents.reduce(
      (sum, doc) => sum + doc.annotations.length,
      0
    );

    const labelCounts: Record<string, number> = {};
    for (const document of documents) {
      for (const annotation of document.annotations) {
        labelCounts[annotation.label] =
          (labelCounts[annotation.label] || 0) + 1;
      }
    }

    return {
      totalDocuments: documents.length,
      totalTokens,
      totalAnnotations,
      labelCounts,
      averageTokensPerDocument: totalTokens / documents.length,
      averageAnnotationsPerDocument: totalAnnotations / documents.length,
    };
  }

  /**
   * Validate CoNLL format compliance
   */
  public validateExport(conllText: string): {
    isValid: boolean;
    errors: string[];
    warnings: string[];
  } {
    const errors: string[] = [];
    const warnings: string[] = [];
    const lines = conllText.split("\n");

    let lineNumber = 0;
    let expectedTokenId = 1;

    for (const line of lines) {
      lineNumber++;

      if (line.trim() === "" || line.startsWith("#")) {
        // Reset token counter for new document
        if (line.trim() === "") {
          expectedTokenId = 1;
        }
        continue;
      }

      const columns = line.split(this.options.separator);

      if (columns.length < 3) {
        errors.push(
          `Line ${lineNumber}: Insufficient columns (expected at least 3, got ${columns.length})`
        );
        continue;
      }

      const tokenId = parseInt(columns[0]);
      if (isNaN(tokenId)) {
        errors.push(`Line ${lineNumber}: Invalid token ID "${columns[0]}"`);
      } else if (tokenId !== expectedTokenId) {
        warnings.push(
          `Line ${lineNumber}: Token ID ${tokenId} expected ${expectedTokenId}`
        );
      }

      expectedTokenId = tokenId + 1;

      // Validate NER tag format
      const nerTag =
        columns[columns.length - (this.options.includeConfidence ? 2 : 1)];
      if (!this.isValidNERTag(nerTag)) {
        errors.push(`Line ${lineNumber}: Invalid NER tag format "${nerTag}"`);
      }

      // Validate confidence if included
      if (this.options.includeConfidence) {
        const confidence = parseFloat(columns[columns.length - 1]);
        if (isNaN(confidence) || confidence < 0 || confidence > 1) {
          errors.push(
            `Line ${lineNumber}: Invalid confidence value "${
              columns[columns.length - 1]
            }"`
          );
        }
      }
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings,
    };
  }

  /**
   * Check if a NER tag follows the correct format
   */
  private isValidNERTag(tag: string): boolean {
    if (tag === "O") return true;

    const prefixes =
      this.options.encoding === "BILOU"
        ? ["B", "I", "L", "O", "U"]
        : this.options.encoding === "BIO"
        ? ["B", "I", "O"]
        : ["I", "O"];

    const pattern = new RegExp(
      `^(${prefixes.filter((p) => p !== "O").join("|")})-\\w+$`
    );
    return pattern.test(tag);
  }
}
