"use client";

import { useState } from "react";
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
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Link2,
  Lightbulb,
  Star,
  Target,
  Layers,
  Bookmark,
  ArrowRight,
} from "lucide-react";

// Mock data for advanced features
const annotationTemplates = [
  {
    id: 1,
    name: "Medical Procedure",
    description: "Standard template for medical procedures",
    tags: [
      { name: "PROCEDURE", color: "#3B82F6" },
      { name: "LOCATION", color: "#10B981" },
      { name: "DURATION", color: "#F59E0B" },
    ],
    pattern: "Procedure: {PROCEDURE} at {LOCATION} for {DURATION}",
  },
  {
    id: 2,
    name: "Research Finding",
    description: "Template for research findings and results",
    tags: [
      { name: "FINDING", color: "#EF4444" },
      { name: "EVIDENCE", color: "#8B5CF6" },
      { name: "SIGNIFICANCE", color: "#F97316" },
    ],
    pattern:
      "Finding: {FINDING} supported by {EVIDENCE} with {SIGNIFICANCE} significance",
  },
  {
    id: 3,
    name: "Drug Information",
    description: "Template for medication and drug annotations",
    tags: [
      { name: "DRUG_NAME", color: "#06B6D4" },
      { name: "DOSAGE", color: "#84CC16" },
      { name: "SIDE_EFFECT", color: "#F59E0B" },
    ],
    pattern: "Drug: {DRUG_NAME} at {DOSAGE} may cause {SIDE_EFFECT}",
  },
];

const smartSuggestions = [
  {
    text: "artificial intelligence",
    confidence: 0.95,
    suggestedTag: "TECHNOLOGY",
    reason: "Pattern match with technology terms",
  },
  {
    text: "clinical trial",
    confidence: 0.89,
    suggestedTag: "RESEARCH_METHOD",
    reason: "Context analysis from surrounding medical terms",
  },
  {
    text: "machine learning",
    confidence: 0.92,
    suggestedTag: "TECHNOLOGY",
    reason: "Semantic similarity to existing annotations",
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
}

interface NestedAnnotationData {
  text: string;
  tag: string;
}

interface SelectionData {
  start: number;
  end: number;
}

interface AdvancedAnnotationFeaturesProps {
  annotations: Annotation[];
  onCreateNestedAnnotation: (
    parentId: string,
    childData: NestedAnnotationData
  ) => void;
  onCreateAnnotationRelationship: (
    sourceId: string,
    targetId: string,
    type: string
  ) => void;
  onApplyTemplate: (templateId: number, selection: SelectionData) => void;
}

export function AdvancedAnnotationFeatures({
  annotations,
  onCreateNestedAnnotation,
  onCreateAnnotationRelationship,
  onApplyTemplate,
}: AdvancedAnnotationFeaturesProps) {
  const [isNestedDialogOpen, setIsNestedDialogOpen] = useState(false);
  const [isRelationshipDialogOpen, setIsRelationshipDialogOpen] =
    useState(false);
  const [isTemplateDialogOpen, setIsTemplateDialogOpen] = useState(false);
  const [selectedParentAnnotation, setSelectedParentAnnotation] = useState<
    string | null
  >(null);
  const [selectedTemplate, setSelectedTemplate] = useState<number | null>(null);
  const [relationshipData, setRelationshipData] = useState({
    source: "",
    target: "",
    type: "dependency",
  });

  const handleCreateNested = () => {
    if (selectedParentAnnotation) {
      onCreateNestedAnnotation(selectedParentAnnotation, {
        text: "Nested annotation text",
        tag: "NESTED_TAG",
      });
      setIsNestedDialogOpen(false);
    }
  };

  const handleCreateRelationship = () => {
    if (relationshipData.source && relationshipData.target) {
      onCreateAnnotationRelationship(
        relationshipData.source,
        relationshipData.target,
        relationshipData.type
      );
      setIsRelationshipDialogOpen(false);
      setRelationshipData({ source: "", target: "", type: "dependency" });
    }
  };

  const handleApplyTemplate = () => {
    if (selectedTemplate) {
      onApplyTemplate(selectedTemplate, { start: 0, end: 10 }); // Mock selection
      setIsTemplateDialogOpen(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Star className="h-5 w-5 mr-2" />
            Advanced Annotation Tools
          </CardTitle>
          <CardDescription>
            Enhanced features for complex annotation workflows
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button
              variant="outline"
              className="h-20 flex flex-col items-center justify-center space-y-2"
              onClick={() => setIsNestedDialogOpen(true)}
            >
              <Layers className="h-6 w-6" />
              <span className="text-sm">Nested Annotations</span>
            </Button>
            <Button
              variant="outline"
              className="h-20 flex flex-col items-center justify-center space-y-2"
              onClick={() => setIsRelationshipDialogOpen(true)}
            >
              <Link2 className="h-6 w-6" />
              <span className="text-sm">Link Annotations</span>
            </Button>
            <Button
              variant="outline"
              className="h-20 flex flex-col items-center justify-center space-y-2"
              onClick={() => setIsTemplateDialogOpen(true)}
            >
              <Bookmark className="h-6 w-6" />
              <span className="text-sm">Apply Template</span>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Smart Suggestions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Lightbulb className="h-5 w-5 mr-2" />
            Smart Suggestions
          </CardTitle>
          <CardDescription>
            AI-powered annotation recommendations based on context
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {smartSuggestions.map((suggestion, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50"
              >
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <span className="font-medium">
                      &ldquo;{suggestion.text}&rdquo;
                    </span>
                    <Badge variant="outline">{suggestion.suggestedTag}</Badge>
                    <Badge variant="secondary" className="text-xs">
                      {(suggestion.confidence * 100).toFixed(0)}%
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground mt-1">
                    {suggestion.reason}
                  </p>
                </div>
                <div className="flex space-x-2">
                  <Button size="sm" variant="outline">
                    Accept
                  </Button>
                  <Button size="sm" variant="ghost">
                    Dismiss
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Annotation Quality Scoring */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Target className="h-5 w-5 mr-2" />
            Quality Scoring
          </CardTitle>
          <CardDescription>
            Automatic quality assessment for annotations
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center p-4 border rounded-lg">
                <div className="text-2xl font-bold text-green-600">8.7</div>
                <div className="text-sm text-muted-foreground">
                  Overall Quality Score
                </div>
              </div>
              <div className="text-center p-4 border rounded-lg">
                <div className="text-2xl font-bold text-blue-600">94%</div>
                <div className="text-sm text-muted-foreground">
                  Consistency Rate
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Precision</span>
                <span className="font-medium">92%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-green-600 h-2 rounded-full"
                  style={{ width: "92%" }}
                ></div>
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Coverage</span>
                <span className="font-medium">78%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full"
                  style={{ width: "78%" }}
                ></div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Nested Annotation Dialog */}
      <Dialog open={isNestedDialogOpen} onOpenChange={setIsNestedDialogOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Create Nested Annotation</DialogTitle>
            <DialogDescription>
              Add a sub-annotation within an existing annotation
            </DialogDescription>
          </DialogHeader>

          <div className="grid gap-4 py-4">
            <div>
              <label className="text-sm font-medium">Parent Annotation</label>
              <Select
                value={selectedParentAnnotation || ""}
                onValueChange={setSelectedParentAnnotation}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select parent annotation" />
                </SelectTrigger>
                <SelectContent>
                  {annotations.map((annotation) => (
                    <SelectItem key={annotation.id} value={annotation.id}>
                      {annotation.text.substring(0, 50)}...
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-medium">Nested Text</label>
              <Input placeholder="Text for nested annotation" />
            </div>
            <div>
              <label className="text-sm font-medium">Tag</label>
              <Select>
                <SelectTrigger>
                  <SelectValue placeholder="Select tag" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="detail">DETAIL</SelectItem>
                  <SelectItem value="example">EXAMPLE</SelectItem>
                  <SelectItem value="specification">SPECIFICATION</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setIsNestedDialogOpen(false)}
            >
              Cancel
            </Button>
            <Button onClick={handleCreateNested}>Create Nested</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Relationship Dialog */}
      <Dialog
        open={isRelationshipDialogOpen}
        onOpenChange={setIsRelationshipDialogOpen}
      >
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Create Annotation Relationship</DialogTitle>
            <DialogDescription>
              Link two annotations with a relationship type
            </DialogDescription>
          </DialogHeader>

          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium">Source Annotation</label>
                <Select
                  value={relationshipData.source}
                  onValueChange={(value) =>
                    setRelationshipData((prev) => ({ ...prev, source: value }))
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select source" />
                  </SelectTrigger>
                  <SelectContent>
                    {annotations.map((annotation) => (
                      <SelectItem key={annotation.id} value={annotation.id}>
                        {annotation.text.substring(0, 30)}...
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="text-sm font-medium">Target Annotation</label>
                <Select
                  value={relationshipData.target}
                  onValueChange={(value) =>
                    setRelationshipData((prev) => ({ ...prev, target: value }))
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select target" />
                  </SelectTrigger>
                  <SelectContent>
                    {annotations.map((annotation) => (
                      <SelectItem key={annotation.id} value={annotation.id}>
                        {annotation.text.substring(0, 30)}...
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="flex items-center justify-center">
              <ArrowRight className="h-4 w-4 text-muted-foreground" />
            </div>

            <div>
              <label className="text-sm font-medium">Relationship Type</label>
              <Select
                value={relationshipData.type}
                onValueChange={(value) =>
                  setRelationshipData((prev) => ({ ...prev, type: value }))
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="dependency">Dependency</SelectItem>
                  <SelectItem value="similarity">Similarity</SelectItem>
                  <SelectItem value="causation">Causation</SelectItem>
                  <SelectItem value="contrast">Contrast</SelectItem>
                  <SelectItem value="elaboration">Elaboration</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setIsRelationshipDialogOpen(false)}
            >
              Cancel
            </Button>
            <Button onClick={handleCreateRelationship}>Create Link</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Template Dialog */}
      <Dialog
        open={isTemplateDialogOpen}
        onOpenChange={setIsTemplateDialogOpen}
      >
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle>Apply Annotation Template</DialogTitle>
            <DialogDescription>
              Use predefined templates for structured annotations
            </DialogDescription>
          </DialogHeader>

          <Tabs defaultValue="select" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="select">Select Template</TabsTrigger>
              <TabsTrigger value="create">Create Template</TabsTrigger>
            </TabsList>

            <TabsContent value="select" className="space-y-4">
              <div className="grid gap-3">
                {annotationTemplates.map((template) => (
                  <div
                    key={template.id}
                    className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                      selectedTemplate === template.id
                        ? "border-primary bg-primary/5"
                        : "hover:bg-muted/50"
                    }`}
                    onClick={() => setSelectedTemplate(template.id)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4 className="font-medium">{template.name}</h4>
                        <p className="text-sm text-muted-foreground mt-1">
                          {template.description}
                        </p>
                        <div className="flex flex-wrap gap-1 mt-2">
                          {template.tags.map((tag, index) => (
                            <Badge
                              key={index}
                              variant="outline"
                              style={{
                                borderColor: tag.color,
                                color: tag.color,
                              }}
                            >
                              {tag.name}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    </div>
                    <div className="mt-3 p-2 bg-muted rounded text-sm font-mono">
                      {template.pattern}
                    </div>
                  </div>
                ))}
              </div>
            </TabsContent>

            <TabsContent value="create" className="space-y-4">
              <div className="grid gap-4">
                <div>
                  <label className="text-sm font-medium">Template Name</label>
                  <Input placeholder="Enter template name" />
                </div>
                <div>
                  <label className="text-sm font-medium">Description</label>
                  <Textarea placeholder="Describe the template purpose" />
                </div>
                <div>
                  <label className="text-sm font-medium">Pattern</label>
                  <Input placeholder="e.g., {TAG1} causes {TAG2} in {LOCATION}" />
                </div>
              </div>
            </TabsContent>
          </Tabs>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setIsTemplateDialogOpen(false)}
            >
              Cancel
            </Button>
            <Button onClick={handleApplyTemplate} disabled={!selectedTemplate}>
              Apply Template
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
