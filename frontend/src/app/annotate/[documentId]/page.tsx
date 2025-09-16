"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import { useParams } from "next/navigation";
import { useSession } from "next-auth/react";
import { withAuth } from "@/components/auth/withAuth";
import { AppLayout } from "@/components/layout/AppLayout";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import {
  ArrowLeft,
  Save,
  Pause,
  Eye,
  EyeOff,
  Zap,
  Bot,
  User,
  Tag,
  Trash2,
  Edit,
  CheckCircle,
  AlertCircle,
  Keyboard,
  TrendingUp,
  Award,
} from "lucide-react";
import Link from "next/link";
import { useDocumentCollaboration } from "@/contexts/CollaborationContext";
import {
  CollaborationUI,
  useCursorTracking,
  CollaborationNotifications,
} from "@/components/collaboration/CollaborationUI";

// Mock data for annotation
const mockDocument = {
  id: 1,
  name: "research_paper_001.pdf",
  content: `Artificial intelligence (AI) has revolutionized medical diagnosis and treatment planning in recent years. Machine learning algorithms can now analyze medical images with accuracy comparable to experienced radiologists. Deep learning models have been successfully applied to detect cancer in mammograms, identify diabetic retinopathy in retinal photographs, and classify skin lesions.

The implementation of AI in healthcare faces several challenges including data privacy concerns, regulatory approval processes, and the need for extensive clinical validation. Healthcare providers must ensure that AI systems are transparent, explainable, and free from bias.

Recent studies have shown that AI-powered diagnostic tools can reduce misdiagnosis rates by up to 30% while improving efficiency in clinical workflows. The integration of natural language processing (NLP) with electronic health records enables automated extraction of clinical insights from unstructured medical notes.

Looking forward, the combination of AI with precision medicine promises personalized treatment recommendations based on individual patient characteristics, genetic profiles, and historical treatment outcomes. This paradigm shift towards data-driven healthcare delivery has the potential to improve patient outcomes while reducing costs.`,
  projectId: 1,
  uploadedAt: "2024-03-01",
  status: "pending",
};

const mockTagSets = [
  {
    id: 1,
    name: "Medical Entities",
    tags: [
      {
        id: 1,
        name: "TECHNOLOGY",
        color: "#3B82F6",
        description: "Technology terms",
      },
      {
        id: 2,
        name: "MEDICAL_CONDITION",
        color: "#10B981",
        description: "Medical conditions",
      },
      {
        id: 3,
        name: "PROCEDURE",
        color: "#F59E0B",
        description: "Medical procedures",
      },
      {
        id: 4,
        name: "ORGANIZATION",
        color: "#8B5CF6",
        description: "Organizations",
      },
      {
        id: 5,
        name: "METRIC",
        color: "#EF4444",
        description: "Measurements and statistics",
      },
    ],
  },
];

interface Annotation {
  id: string;
  text: string;
  start: number;
  end: number;
  tagId: number;
  tagName: string;
  tagColor: string;
  confidence?: number;
  source: "manual" | "llm";
  createdAt: string;
  createdBy: string;
}

function AnnotationEditorPage() {
  const params = useParams();
  const { data: session } = useSession();
  const documentId = params.documentId as string;

  // Collaboration integration
  const collaboration = useDocumentCollaboration(
    documentId,
    session?.user?.id || "anonymous",
    session?.user?.name || "Anonymous User"
  );

  const [documentData] = useState(mockDocument);
  const [tagSets] = useState(mockTagSets);
  const [selectedTagSet, setSelectedTagSet] = useState(mockTagSets[0]);
  const [annotations, setAnnotations] = useState<Annotation[]>([]);
  const [selectedText, setSelectedText] = useState("");
  const [selectedRange, setSelectedRange] = useState<{
    start: number;
    end: number;
  } | null>(null);
  const [isAnnotationDialogOpen, setIsAnnotationDialogOpen] = useState(false);
  const [selectedTag, setSelectedTag] = useState<number | null>(null);
  const [isLLMRunning, setIsLLMRunning] = useState(false);
  const [llmProgress, setLLMProgress] = useState(0);
  const [showAnnotations, setShowAnnotations] = useState(true);
  const [activeTab, setActiveTab] = useState("annotate");
  const [editingAnnotation, setEditingAnnotation] = useState<string | null>(
    null
  );
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [editingTag, setEditingTag] = useState<number | null>(null);
  const [showKeyboardHelp, setShowKeyboardHelp] = useState(false);

  const textContentRef = useRef<HTMLDivElement>(null);

  // Enable cursor tracking for collaboration
  useCursorTracking(textContentRef as React.RefObject<HTMLElement>);

  // Set up real-time collaboration for annotations
  useEffect(() => {
    collaboration.onAnnotationUpdate((update) => {
      if (update.action === "create" && update.annotation) {
        setAnnotations((prev) => [
          ...prev,
          {
            id: update.annotation!.id,
            text: update.annotation!.text,
            start: update.annotation!.start,
            end: update.annotation!.end,
            tagId: update.annotation!.tagId,
            tagName: update.annotation!.tagName,
            tagColor: update.annotation!.tagColor,
            source: "manual",
            createdAt: update.timestamp,
            createdBy: update.annotation!.userName,
          },
        ]);
      } else if (update.action === "delete") {
        setAnnotations((prev) =>
          prev.filter((a) => a.id !== update.annotation?.id)
        );
      } else if (update.action === "update" && update.annotation) {
        setAnnotations((prev) =>
          prev.map((a) =>
            a.id === update.annotation!.id
              ? {
                  ...a,
                  tagId: update.annotation!.tagId,
                  tagName: update.annotation!.tagName,
                  tagColor: update.annotation!.tagColor,
                }
              : a
          )
        );
      }
    });
  }, [collaboration]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl/Cmd + S to save
      if ((e.ctrlKey || e.metaKey) && e.key === "s") {
        e.preventDefault();
        // Auto-save functionality would go here
        console.log("Auto-save triggered");
      }

      // Ctrl/Cmd + H to toggle annotation visibility
      if ((e.ctrlKey || e.metaKey) && e.key === "h") {
        e.preventDefault();
        setShowAnnotations((prev) => !prev);
      }

      // Escape to close dialogs
      if (e.key === "Escape") {
        setIsAnnotationDialogOpen(false);
        setIsEditDialogOpen(false);
        setShowKeyboardHelp(false);
      }

      // Delete key to delete selected annotation
      if (e.key === "Delete" && editingAnnotation) {
        handleDeleteAnnotation(editingAnnotation);
        setEditingAnnotation(null);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [editingAnnotation]); // handleDeleteAnnotation is stable due to useCallback

  // Handle text selection
  const handleTextSelection = useCallback(() => {
    const selection = window.getSelection();
    if (!selection || selection.rangeCount === 0) return;

    const range = selection.getRangeAt(0);
    const selectedText = range.toString().trim();

    if (selectedText.length === 0) return;

    // Calculate start and end positions relative to the document content
    const startOffset = range.startOffset;
    const endOffset = range.endOffset;

    // Find the actual positions in the full text
    let actualStart = 0;
    let actualEnd = 0;

    if (textContentRef.current) {
      const walker = window.document.createTreeWalker(
        textContentRef.current,
        NodeFilter.SHOW_TEXT,
        null
      );

      let currentOffset = 0;
      let node;

      while ((node = walker.nextNode())) {
        const nodeText = node.textContent || "";
        if (node === range.startContainer) {
          actualStart = currentOffset + startOffset;
        }
        if (node === range.endContainer) {
          actualEnd = currentOffset + endOffset;
          break;
        }
        currentOffset += nodeText.length;
      }
    }

    setSelectedText(selectedText);
    setSelectedRange({ start: actualStart, end: actualEnd });
    setIsAnnotationDialogOpen(true);
  }, []);

  // Create annotation
  const handleCreateAnnotation = () => {
    if (!selectedRange || !selectedTag) return;

    const tag = selectedTagSet.tags.find((t) => t.id === selectedTag);
    if (!tag) return;

    const newAnnotation: Annotation = {
      id: Date.now().toString(),
      text: selectedText,
      start: selectedRange.start,
      end: selectedRange.end,
      tagId: selectedTag,
      tagName: tag.name,
      tagColor: tag.color,
      source: "manual",
      createdAt: new Date().toISOString(),
      createdBy: "Current User",
    };

    setAnnotations((prev) => [...prev, newAnnotation]);

    // Send collaboration update
    collaboration.sendAnnotationUpdate({
      id: Date.now().toString(),
      documentId,
      action: "create",
      annotation: {
        id: newAnnotation.id,
        text: newAnnotation.text,
        start: newAnnotation.start,
        end: newAnnotation.end,
        tagId: newAnnotation.tagId,
        tagName: newAnnotation.tagName,
        tagColor: newAnnotation.tagColor,
        userId: session?.user?.id || "anonymous",
        userName: session?.user?.name || "Anonymous User",
      },
      userId: session?.user?.id || "anonymous",
      timestamp: new Date().toISOString(),
    });

    setIsAnnotationDialogOpen(false);
    setSelectedText("");
    setSelectedRange(null);
    setSelectedTag(null);

    // Clear selection
    window.getSelection()?.removeAllRanges();
  };

  // Delete annotation
  const handleDeleteAnnotation = useCallback(
    (annotationId: string) => {
      setAnnotations((prev) => prev.filter((a) => a.id !== annotationId));

      // Send collaboration update
      collaboration.sendAnnotationUpdate({
        id: Date.now().toString(),
        documentId,
        action: "delete",
        annotation: {
          id: annotationId,
          text: "",
          start: 0,
          end: 0,
          tagId: 0,
          tagName: "",
          tagColor: "",
          userId: session?.user?.id || "anonymous",
          userName: session?.user?.name || "Anonymous User",
        },
        userId: session?.user?.id || "anonymous",
        timestamp: new Date().toISOString(),
      });
    },
    [collaboration, documentId, session]
  );

  // Edit annotation
  const handleEditAnnotation = (annotationId: string) => {
    const annotation = annotations.find((a) => a.id === annotationId);
    if (annotation) {
      setEditingAnnotation(annotationId);
      setEditingTag(annotation.tagId);
      setIsEditDialogOpen(true);
    }
  };

  // Save annotation edit
  const handleSaveAnnotationEdit = () => {
    if (editingAnnotation && editingTag) {
      const tag = selectedTagSet.tags.find((t) => t.id === editingTag);
      if (tag) {
        setAnnotations((prev) =>
          prev.map((a) =>
            a.id === editingAnnotation
              ? { ...a, tagId: tag.id, tagName: tag.name, tagColor: tag.color }
              : a
          )
        );
      }
    }
    setIsEditDialogOpen(false);
    setEditingAnnotation(null);
    setEditingTag(null);
  };

  // Simulate LLM annotation process
  const handleRunLLMAnnotation = async () => {
    setIsLLMRunning(true);
    setLLMProgress(0);

    // Simulate progress
    const progressInterval = setInterval(() => {
      setLLMProgress((prev) => {
        const newProgress = prev + Math.random() * 20;
        if (newProgress >= 100) {
          clearInterval(progressInterval);

          // Add some mock LLM annotations
          setTimeout(() => {
            const llmAnnotations: Annotation[] = [
              {
                id: "llm-1",
                text: "Artificial intelligence",
                start: 0,
                end: 25,
                tagId: 1,
                tagName: "TECHNOLOGY",
                tagColor: "#3B82F6",
                confidence: 0.95,
                source: "llm",
                createdAt: new Date().toISOString(),
                createdBy: "LLM Assistant",
              },
              {
                id: "llm-2",
                text: "medical diagnosis",
                start: 42,
                end: 58,
                tagId: 3,
                tagName: "PROCEDURE",
                tagColor: "#F59E0B",
                confidence: 0.87,
                source: "llm",
                createdAt: new Date().toISOString(),
                createdBy: "LLM Assistant",
              },
              {
                id: "llm-3",
                text: "cancer",
                start: 345,
                end: 351,
                tagId: 2,
                tagName: "MEDICAL_CONDITION",
                tagColor: "#10B981",
                confidence: 0.92,
                source: "llm",
                createdAt: new Date().toISOString(),
                createdBy: "LLM Assistant",
              },
            ];

            setAnnotations((prev) => [...prev, ...llmAnnotations]);
            setIsLLMRunning(false);
          }, 500);

          return 100;
        }
        return newProgress;
      });
    }, 200);
  };

  // Render text with annotations
  const renderAnnotatedText = () => {
    if (!showAnnotations || annotations.length === 0) {
      return documentData.content;
    }

    // Sort annotations by start position
    const sortedAnnotations = [...annotations].sort(
      (a, b) => a.start - b.start
    );

    const result = [];
    let lastIndex = 0;

    sortedAnnotations.forEach((annotation, index) => {
      // Add text before annotation
      if (annotation.start > lastIndex) {
        result.push(
          <span key={`text-${index}`}>
            {documentData.content.slice(lastIndex, annotation.start)}
          </span>
        );
      }

      // Add annotated text
      result.push(
        <span
          key={annotation.id}
          className="relative inline-block cursor-pointer group"
          style={{
            backgroundColor: annotation.tagColor + "20",
            borderBottom: `2px solid ${annotation.tagColor}`,
          }}
        >
          {annotation.text}
          <div className="absolute bottom-full left-0 mb-2 p-2 bg-black text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10">
            <div className="font-semibold">{annotation.tagName}</div>
            <div>Source: {annotation.source}</div>
            {annotation.confidence && (
              <div>Confidence: {(annotation.confidence * 100).toFixed(1)}%</div>
            )}
          </div>
        </span>
      );

      lastIndex = annotation.end;
    });

    // Add remaining text
    if (lastIndex < documentData.content.length) {
      result.push(
        <span key="text-end">{documentData.content.slice(lastIndex)}</span>
      );
    }

    return result;
  };

  return (
    <AppLayout>
      {/* Collaboration UI Components */}
      <CollaborationUI documentId={documentId} />
      <CollaborationNotifications />

      <div className="flex h-[calc(100vh-4rem)]">
        {/* Main Content */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b bg-white">
            <div className="flex items-center space-x-4">
              <Link href="/documents">
                <Button variant="ghost" size="sm">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to Documents
                </Button>
              </Link>
              <div>
                <h1 className="text-xl font-bold">{documentData.name}</h1>
                <p className="text-sm text-muted-foreground">
                  Project: Medical Research Corpus • {annotations.length}{" "}
                  annotations
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowKeyboardHelp(true)}
              >
                <Keyboard className="h-4 w-4 mr-2" />
                Shortcuts
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowAnnotations(!showAnnotations)}
              >
                {showAnnotations ? (
                  <EyeOff className="h-4 w-4 mr-2" />
                ) : (
                  <Eye className="h-4 w-4 mr-2" />
                )}
                {showAnnotations ? "Hide" : "Show"} Annotations
              </Button>
              <Button variant="outline" size="sm">
                <Save className="h-4 w-4 mr-2" />
                Save
              </Button>
            </div>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-hidden">
            <Tabs
              value={activeTab}
              onValueChange={setActiveTab}
              className="h-full flex flex-col"
            >
              <TabsList className="mx-4 mt-4">
                <TabsTrigger value="annotate">Annotate</TabsTrigger>
                <TabsTrigger value="llm">LLM Runner</TabsTrigger>
                <TabsTrigger value="validate">Validate</TabsTrigger>
              </TabsList>

              <TabsContent
                value="annotate"
                className="flex-1 p-4 overflow-auto"
              >
                <Card className="h-full">
                  <CardContent className="p-6 h-full overflow-auto">
                    <div
                      ref={textContentRef}
                      className="prose max-w-none leading-relaxed text-justify select-text"
                      onMouseUp={handleTextSelection}
                      style={{ userSelect: "text" }}
                    >
                      {renderAnnotatedText()}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="llm" className="flex-1 p-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Bot className="h-5 w-5 mr-2" />
                      LLM Annotation Runner
                    </CardTitle>
                    <CardDescription>
                      Automatically annotate this document using AI
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="text-sm font-medium">Tag Set</label>
                        <Select
                          value={selectedTagSet.id.toString()}
                          onValueChange={(value) => {
                            const tagSet = tagSets.find(
                              (ts) => ts.id === parseInt(value)
                            );
                            if (tagSet) setSelectedTagSet(tagSet);
                          }}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {tagSets.map((tagSet) => (
                              <SelectItem
                                key={tagSet.id}
                                value={tagSet.id.toString()}
                              >
                                {tagSet.name}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      <div>
                        <label className="text-sm font-medium">LLM Model</label>
                        <Select>
                          <SelectTrigger>
                            <SelectValue placeholder="Select a model" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="gpt-4">GPT-4</SelectItem>
                            <SelectItem value="claude-3">Claude 3</SelectItem>
                            <SelectItem value="groq">Groq</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>

                    {isLLMRunning && (
                      <div className="space-y-2">
                        <div className="flex items-center justify-between text-sm">
                          <span>Processing document...</span>
                          <span>{Math.round(llmProgress)}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-primary h-2 rounded-full transition-all duration-300"
                            style={{ width: `${llmProgress}%` }}
                          />
                        </div>
                      </div>
                    )}

                    <div className="flex space-x-2">
                      <Button
                        onClick={handleRunLLMAnnotation}
                        disabled={isLLMRunning}
                        className="flex-1"
                      >
                        {isLLMRunning ? (
                          <>
                            <Pause className="h-4 w-4 mr-2" />
                            Running...
                          </>
                        ) : (
                          <>
                            <Zap className="h-4 w-4 mr-2" />
                            Run LLM Annotation
                          </>
                        )}
                      </Button>
                      {isLLMRunning && (
                        <Button
                          variant="outline"
                          onClick={() => setIsLLMRunning(false)}
                        >
                          Cancel
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="validate" className="flex-1 p-4">
                <div className="space-y-4">
                  {/* Quality Metrics */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center">
                        <Award className="h-5 w-5 mr-2" />
                        Annotation Quality Metrics
                      </CardTitle>
                      <CardDescription>
                        Overall annotation quality and statistics
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="text-sm">Coverage</span>
                            <span className="text-sm font-medium">
                              {annotations.length > 0
                                ? `${(
                                    (annotations.reduce(
                                      (acc, a) => acc + (a.end - a.start),
                                      0
                                    ) /
                                      documentData.content.length) *
                                    100
                                  ).toFixed(1)}%`
                                : "0%"}
                            </span>
                          </div>
                          <Progress
                            value={
                              annotations.length > 0
                                ? (annotations.reduce(
                                    (acc, a) => acc + (a.end - a.start),
                                    0
                                  ) /
                                    documentData.content.length) *
                                  100
                                : 0
                            }
                          />
                        </div>
                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="text-sm">Avg. Confidence</span>
                            <span className="text-sm font-medium">
                              {annotations.filter((a) => a.confidence).length >
                              0
                                ? `${(
                                    (annotations
                                      .filter((a) => a.confidence)
                                      .reduce(
                                        (acc, a) => acc + (a.confidence || 0),
                                        0
                                      ) /
                                      annotations.filter((a) => a.confidence)
                                        .length) *
                                    100
                                  ).toFixed(1)}%`
                                : "N/A"}
                            </span>
                          </div>
                          <Progress
                            value={
                              annotations.filter((a) => a.confidence).length > 0
                                ? (annotations
                                    .filter((a) => a.confidence)
                                    .reduce(
                                      (acc, a) => acc + (a.confidence || 0),
                                      0
                                    ) /
                                    annotations.filter((a) => a.confidence)
                                      .length) *
                                  100
                                : 0
                            }
                          />
                        </div>
                        <div className="text-center p-3 border rounded-lg">
                          <div className="text-2xl font-bold text-primary">
                            {annotations.length}
                          </div>
                          <div className="text-sm text-muted-foreground">
                            Total Annotations
                          </div>
                        </div>
                        <div className="text-center p-3 border rounded-lg">
                          <div className="text-2xl font-bold text-green-600">
                            {
                              selectedTagSet.tags.filter((tag) =>
                                annotations.some((a) => a.tagId === tag.id)
                              ).length
                            }
                          </div>
                          <div className="text-sm text-muted-foreground">
                            Tags Used
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Validation Tools */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center">
                        <CheckCircle className="h-5 w-5 mr-2" />
                        Validation Tools
                      </CardTitle>
                      <CardDescription>
                        Review and validate annotation quality
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        <div className="flex items-center justify-between p-4 border rounded-lg">
                          <div>
                            <h4 className="font-medium">Position Validation</h4>
                            <p className="text-sm text-muted-foreground">
                              Check for overlapping or invalid annotation
                              positions
                            </p>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Badge variant="outline" className="text-green-600">
                              {
                                annotations.filter(
                                  (a, i) =>
                                    !annotations.some(
                                      (b, j) =>
                                        i !== j &&
                                        ((a.start >= b.start &&
                                          a.start < b.end) ||
                                          (a.end > b.start && a.end <= b.end))
                                    )
                                ).length
                              }{" "}
                              Valid
                            </Badge>
                            <Button variant="outline" size="sm">
                              <CheckCircle className="h-4 w-4 mr-2" />
                              Validate
                            </Button>
                          </div>
                        </div>
                        <div className="flex items-center justify-between p-4 border rounded-lg">
                          <div>
                            <h4 className="font-medium">Duplicate Detection</h4>
                            <p className="text-sm text-muted-foreground">
                              Find and merge duplicate annotations
                            </p>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Badge
                              variant="outline"
                              className="text-orange-600"
                            >
                              {annotations.filter((a, i) =>
                                annotations.some(
                                  (b, j) =>
                                    i !== j &&
                                    a.text.toLowerCase() ===
                                      b.text.toLowerCase() &&
                                    a.tagId === b.tagId
                                )
                              ).length / 2}{" "}
                              Duplicates
                            </Badge>
                            <Button variant="outline" size="sm">
                              <AlertCircle className="h-4 w-4 mr-2" />
                              Check Duplicates
                            </Button>
                          </div>
                        </div>
                        <div className="flex items-center justify-between p-4 border rounded-lg">
                          <div>
                            <h4 className="font-medium">Quality Assessment</h4>
                            <p className="text-sm text-muted-foreground">
                              Analyze annotation consistency and quality
                            </p>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Badge variant="outline" className="text-blue-600">
                              {
                                annotations.filter(
                                  (a) => (a.confidence || 0) >= 0.8
                                ).length
                              }{" "}
                              High Quality
                            </Badge>
                            <Button variant="outline" size="sm">
                              <TrendingUp className="h-4 w-4 mr-2" />
                              Analyze
                            </Button>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>
            </Tabs>
          </div>
        </div>

        {/* Annotation Sidebar */}
        <div className="w-80 border-l bg-muted/10 flex flex-col">
          <div className="p-4 border-b bg-white">
            <h3 className="font-semibold">
              Annotations ({annotations.length})
            </h3>
            <p className="text-sm text-muted-foreground">
              {annotations.filter((a) => a.source === "manual").length} manual,
              {annotations.filter((a) => a.source === "llm").length} AI
              generated
            </p>
          </div>

          <div className="flex-1 overflow-auto p-4 space-y-3">
            {annotations.map((annotation) => (
              <div
                key={annotation.id}
                className="p-3 border rounded-lg bg-white"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <Badge
                        style={{
                          backgroundColor: annotation.tagColor + "20",
                          color: annotation.tagColor,
                          borderColor: annotation.tagColor + "40",
                        }}
                      >
                        {annotation.tagName}
                      </Badge>
                      {annotation.source === "llm" ? (
                        <Bot className="h-3 w-3 text-muted-foreground" />
                      ) : (
                        <User className="h-3 w-3 text-muted-foreground" />
                      )}
                      {annotation.confidence && (
                        <Badge
                          variant="outline"
                          className={`text-xs ${
                            annotation.confidence >= 0.9
                              ? "border-green-500 text-green-700"
                              : annotation.confidence >= 0.7
                              ? "border-yellow-500 text-yellow-700"
                              : "border-red-500 text-red-700"
                          }`}
                        >
                          {(annotation.confidence * 100).toFixed(0)}%
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm font-medium mb-1">
                      &quot;{annotation.text}&quot;
                    </p>
                    <div className="space-y-1">
                      <p className="text-xs text-muted-foreground">
                        Position: {annotation.start}-{annotation.end} • Length:{" "}
                        {annotation.end - annotation.start}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {annotation.source === "llm"
                          ? "AI Generated"
                          : "Manual"}{" "}
                        • {new Date(annotation.createdAt).toLocaleTimeString()}
                      </p>
                      {annotation.confidence && (
                        <div className="flex items-center space-x-2">
                          <span className="text-xs text-muted-foreground">
                            Quality:
                          </span>
                          <Progress
                            value={annotation.confidence * 100}
                            className="flex-1 h-1"
                          />
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="flex space-x-1">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleEditAnnotation(annotation.id)}
                      className="h-8 w-8 p-0"
                    >
                      <Edit className="h-3 w-3" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDeleteAnnotation(annotation.id)}
                      className="h-8 w-8 p-0 text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}

            {annotations.length === 0 && (
              <div className="text-center py-8 text-muted-foreground">
                <Tag className="h-8 w-8 mx-auto mb-2" />
                <p className="text-sm">No annotations yet</p>
                <p className="text-xs">Select text to create annotations</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Annotation Creation Dialog */}
      <Dialog
        open={isAnnotationDialogOpen}
        onOpenChange={setIsAnnotationDialogOpen}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create Annotation</DialogTitle>
            <DialogDescription>
              Selected text: &quot;{selectedText}&quot;
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium">Tag</label>
              <Select
                value={selectedTag?.toString()}
                onValueChange={(value) => setSelectedTag(parseInt(value))}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select a tag..." />
                </SelectTrigger>
                <SelectContent>
                  {selectedTagSet.tags.map((tag) => (
                    <SelectItem key={tag.id} value={tag.id.toString()}>
                      <div className="flex items-center space-x-2">
                        <div
                          className="w-3 h-3 rounded"
                          style={{ backgroundColor: tag.color }}
                        />
                        <span>{tag.name}</span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setIsAnnotationDialogOpen(false)}
            >
              Cancel
            </Button>
            <Button onClick={handleCreateAnnotation} disabled={!selectedTag}>
              Create Annotation
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Annotation Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Edit Annotation</DialogTitle>
            <DialogDescription>
              {editingAnnotation && (
                <>
                  Editing annotation: &quot;
                  {annotations.find((a) => a.id === editingAnnotation)?.text}
                  &quot;
                </>
              )}
            </DialogDescription>
          </DialogHeader>

          <div className="grid gap-4 py-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Tag</label>
              <Select
                value={editingTag?.toString()}
                onValueChange={(value) => setEditingTag(parseInt(value))}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select a tag" />
                </SelectTrigger>
                <SelectContent>
                  {selectedTagSet.tags.map((tag) => (
                    <SelectItem key={tag.id} value={tag.id.toString()}>
                      <div className="flex items-center space-x-2">
                        <div
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: tag.color }}
                        />
                        <span>{tag.name}</span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setIsEditDialogOpen(false)}
            >
              Cancel
            </Button>
            <Button onClick={handleSaveAnnotationEdit} disabled={!editingTag}>
              Save Changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Keyboard Shortcuts Help Dialog */}
      <Dialog open={showKeyboardHelp} onOpenChange={setShowKeyboardHelp}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle className="flex items-center">
              <Keyboard className="h-5 w-5 mr-2" />
              Keyboard Shortcuts
            </DialogTitle>
            <DialogDescription>
              Speed up your annotation workflow with these shortcuts
            </DialogDescription>
          </DialogHeader>

          <div className="grid gap-4 py-4">
            <div className="space-y-3">
              <div className="flex justify-between items-center p-2 border rounded">
                <span className="text-sm">Save annotations</span>
                <Badge variant="outline">Ctrl + S</Badge>
              </div>
              <div className="flex justify-between items-center p-2 border rounded">
                <span className="text-sm">Close dialogs</span>
                <Badge variant="outline">Escape</Badge>
              </div>
              <div className="flex justify-between items-center p-2 border rounded">
                <span className="text-sm">Delete selected annotation</span>
                <Badge variant="outline">Delete</Badge>
              </div>
              <div className="flex justify-between items-center p-2 border rounded">
                <span className="text-sm">Toggle annotation visibility</span>
                <Badge variant="outline">Ctrl + H</Badge>
              </div>
              <div className="flex justify-between items-center p-2 border rounded">
                <span className="text-sm">
                  Create annotation from selection
                </span>
                <Badge variant="outline">Select text</Badge>
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button onClick={() => setShowKeyboardHelp(false)}>Got it</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </AppLayout>
  );
}

// Export the component wrapped with authentication protection
export default withAuth(AnnotationEditorPage);
