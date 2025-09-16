"use client";

import { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
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
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Download,
  FileText,
  Settings,
  Calendar,
  Clock,
  CheckCircle,
  AlertCircle,
  RefreshCw,
  Search,
  FileDown,
  Code,
  Table,
  FileJson,
} from "lucide-react";

interface ExportFormat {
  id: string;
  name: string;
  description: string;
  extension: string;
  icon: React.ReactNode;
  supportedFeatures: string[];
}

interface ExportJob {
  id: string;
  name: string;
  format: string;
  status: "pending" | "processing" | "completed" | "failed";
  createdAt: string;
  completedAt?: string;
  fileSize?: string;
  downloadUrl?: string;
  projectId: string;
  projectName: string;
  filters: ExportFilters;
}

interface ExportFilters {
  includeMetadata: boolean;
  includeComments: boolean;
  includeAnnotationHistory: boolean;
  dateRange?: {
    start: string;
    end: string;
  };
  annotationTypes?: string[];
  users?: string[];
}

const exportFormats: ExportFormat[] = [
  {
    id: "conll",
    name: "CoNLL Format",
    description:
      "Standard CoNLL format for NLP tasks with token-level annotations",
    extension: "conllu",
    icon: <Code className="h-4 w-4" />,
    supportedFeatures: ["tokens", "pos_tags", "ner_tags", "dependencies"],
  },
  {
    id: "json",
    name: "JSON Export",
    description:
      "Complete JSON export with all metadata and annotation details",
    extension: "json",
    icon: <FileJson className="h-4 w-4" />,
    supportedFeatures: [
      "metadata",
      "annotations",
      "history",
      "comments",
      "relationships",
    ],
  },
  {
    id: "csv",
    name: "CSV Export",
    description: "Spreadsheet-friendly format for data analysis",
    extension: "csv",
    icon: <Table className="h-4 w-4" />,
    supportedFeatures: ["annotations", "metadata", "statistics"],
  },
  {
    id: "standoff",
    name: "Standoff Format",
    description: "Brat-style standoff annotation format",
    extension: "ann",
    icon: <FileText className="h-4 w-4" />,
    supportedFeatures: ["entities", "relations", "events", "attributes"],
  },
];

const mockExportJobs: ExportJob[] = [
  {
    id: "1",
    name: "Medical Corpus - CoNLL Export",
    format: "conll",
    status: "completed",
    createdAt: "2024-01-15T10:30:00Z",
    completedAt: "2024-01-15T10:32:15Z",
    fileSize: "2.4 MB",
    downloadUrl: "/downloads/medical-corpus-conll.zip",
    projectId: "proj1",
    projectName: "Medical Research Corpus",
    filters: {
      includeMetadata: true,
      includeComments: false,
      includeAnnotationHistory: false,
    },
  },
  {
    id: "2",
    name: "Clinical Trials - JSON Export",
    format: "json",
    status: "processing",
    createdAt: "2024-01-15T11:45:00Z",
    projectId: "proj2",
    projectName: "Clinical Trial Analysis",
    filters: {
      includeMetadata: true,
      includeComments: true,
      includeAnnotationHistory: true,
      dateRange: {
        start: "2024-01-01",
        end: "2024-01-15",
      },
    },
  },
  {
    id: "3",
    name: "Drug Discovery - CSV Export",
    format: "csv",
    status: "failed",
    createdAt: "2024-01-14T16:20:00Z",
    projectId: "proj3",
    projectName: "Drug Discovery Dataset",
    filters: {
      includeMetadata: true,
      includeComments: false,
      includeAnnotationHistory: false,
    },
  },
];

export function ExportSystem() {
  const [isExportDialogOpen, setIsExportDialogOpen] = useState(false);
  const [isCustomFormatDialogOpen, setIsCustomFormatDialogOpen] =
    useState(false);
  const [selectedFormat, setSelectedFormat] = useState<ExportFormat | null>(
    null
  );
  const [exportFilters, setExportFilters] = useState<ExportFilters>({
    includeMetadata: true,
    includeComments: true,
    includeAnnotationHistory: false,
  });
  const [exportName, setExportName] = useState("");
  const [selectedProject, setSelectedProject] = useState("");
  const [customFormatTemplate, setCustomFormatTemplate] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");

  const handleStartExport = () => {
    if (!selectedFormat || !selectedProject || !exportName) return;

    console.log("Starting export:", {
      format: selectedFormat.id,
      project: selectedProject,
      name: exportName,
      filters: exportFilters,
    });

    setIsExportDialogOpen(false);
    resetExportForm();
  };

  const resetExportForm = () => {
    setSelectedFormat(null);
    setExportName("");
    setSelectedProject("");
    setExportFilters({
      includeMetadata: true,
      includeComments: true,
      includeAnnotationHistory: false,
    });
  };

  const handleDownloadExport = (job: ExportJob) => {
    if (job.downloadUrl) {
      console.log("Downloading export:", job.downloadUrl);
      // Implementation would trigger actual download
    }
  };

  const handleRetryExport = (jobId: string) => {
    console.log("Retrying export:", jobId);
    // Implementation would retry the failed export
  };

  const getStatusBadge = (status: ExportJob["status"]) => {
    switch (status) {
      case "completed":
        return (
          <Badge className="bg-green-100 text-green-800">
            <CheckCircle className="h-3 w-3 mr-1" />
            Completed
          </Badge>
        );
      case "processing":
        return (
          <Badge className="bg-blue-100 text-blue-800">
            <RefreshCw className="h-3 w-3 mr-1 animate-spin" />
            Processing
          </Badge>
        );
      case "pending":
        return (
          <Badge className="bg-yellow-100 text-yellow-800">
            <Clock className="h-3 w-3 mr-1" />
            Pending
          </Badge>
        );
      case "failed":
        return (
          <Badge className="bg-red-100 text-red-800">
            <AlertCircle className="h-3 w-3 mr-1" />
            Failed
          </Badge>
        );
      default:
        return <Badge variant="outline">Unknown</Badge>;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const filteredJobs = mockExportJobs.filter((job) => {
    const matchesStatus = statusFilter === "all" || job.status === statusFilter;
    const matchesSearch =
      searchQuery === "" ||
      job.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      job.projectName.toLowerCase().includes(searchQuery.toLowerCase());

    return matchesStatus && matchesSearch;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Export System</h2>
          <p className="text-muted-foreground">
            Export annotations in various formats for analysis and integration
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            onClick={() => setIsCustomFormatDialogOpen(true)}
          >
            <Settings className="h-4 w-4 mr-2" />
            Custom Format
          </Button>
          <Button onClick={() => setIsExportDialogOpen(true)}>
            <Download className="h-4 w-4 mr-2" />
            New Export
          </Button>
        </div>
      </div>

      {/* Export Formats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {exportFormats.map((format) => (
          <Card
            key={format.id}
            className="cursor-pointer hover:shadow-md transition-shadow"
          >
            <CardContent className="p-6">
              <div className="flex items-center space-x-3 mb-3">
                {format.icon}
                <div>
                  <h3 className="font-medium">{format.name}</h3>
                  <p className="text-sm text-muted-foreground">
                    .{format.extension}
                  </p>
                </div>
              </div>
              <p className="text-sm text-muted-foreground mb-3">
                {format.description}
              </p>
              <div className="flex flex-wrap gap-1">
                {format.supportedFeatures.slice(0, 3).map((feature) => (
                  <Badge key={feature} variant="outline" className="text-xs">
                    {feature}
                  </Badge>
                ))}
                {format.supportedFeatures.length > 3 && (
                  <Badge variant="outline" className="text-xs">
                    +{format.supportedFeatures.length - 3}
                  </Badge>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Export Jobs */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center">
                <FileDown className="h-5 w-5 mr-2" />
                Export Jobs
              </CardTitle>
              <CardDescription>
                Track and manage your export operations
              </CardDescription>
            </div>
            <div className="flex items-center space-x-2">
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search exports..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 w-64"
                />
              </div>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-32">
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="completed">Completed</SelectItem>
                  <SelectItem value="processing">Processing</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="failed">Failed</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {filteredJobs.map((job) => (
              <div key={job.id} className="border rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h3 className="font-medium">{job.name}</h3>
                      {getStatusBadge(job.status)}
                      <Badge variant="outline">
                        {exportFormats.find((f) => f.id === job.format)?.name}
                      </Badge>
                    </div>
                    <div className="flex items-center space-x-4 text-sm text-muted-foreground mb-2">
                      <span>Project: {job.projectName}</span>
                      <span className="flex items-center">
                        <Calendar className="h-3 w-3 mr-1" />
                        {formatDate(job.createdAt)}
                      </span>
                      {job.fileSize && <span>Size: {job.fileSize}</span>}
                    </div>
                    <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                      {job.filters.includeMetadata && (
                        <Badge variant="outline" className="text-xs">
                          Metadata
                        </Badge>
                      )}
                      {job.filters.includeComments && (
                        <Badge variant="outline" className="text-xs">
                          Comments
                        </Badge>
                      )}
                      {job.filters.includeAnnotationHistory && (
                        <Badge variant="outline" className="text-xs">
                          History
                        </Badge>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center space-x-2 ml-4">
                    {job.status === "completed" && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDownloadExport(job)}
                      >
                        <Download className="h-4 w-4 mr-1" />
                        Download
                      </Button>
                    )}
                    {job.status === "failed" && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleRetryExport(job.id)}
                      >
                        <RefreshCw className="h-4 w-4 mr-1" />
                        Retry
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            ))}

            {filteredJobs.length === 0 && (
              <div className="text-center py-8 text-muted-foreground">
                No export jobs found matching your criteria.
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* New Export Dialog */}
      <Dialog open={isExportDialogOpen} onOpenChange={setIsExportDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Create New Export</DialogTitle>
            <DialogDescription>
              Configure and start a new export job for your annotation data
            </DialogDescription>
          </DialogHeader>

          <Tabs defaultValue="format" className="space-y-4">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="format">Format</TabsTrigger>
              <TabsTrigger value="options">Options</TabsTrigger>
              <TabsTrigger value="filters">Filters</TabsTrigger>
            </TabsList>

            <TabsContent value="format" className="space-y-4">
              <div>
                <label className="text-sm font-medium">Export Name</label>
                <Input
                  value={exportName}
                  onChange={(e) => setExportName(e.target.value)}
                  placeholder="Enter export name..."
                />
              </div>

              <div>
                <label className="text-sm font-medium">Project</label>
                <Select
                  value={selectedProject}
                  onValueChange={setSelectedProject}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select project..." />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="proj1">
                      Medical Research Corpus
                    </SelectItem>
                    <SelectItem value="proj2">
                      Clinical Trial Analysis
                    </SelectItem>
                    <SelectItem value="proj3">
                      Drug Discovery Dataset
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="text-sm font-medium mb-3 block">
                  Export Format
                </label>
                <div className="grid grid-cols-2 gap-3">
                  {exportFormats.map((format) => (
                    <div
                      key={format.id}
                      className={`border rounded-lg p-3 cursor-pointer transition-all ${
                        selectedFormat?.id === format.id
                          ? "border-blue-500 bg-blue-50"
                          : "hover:border-gray-300"
                      }`}
                      onClick={() => setSelectedFormat(format)}
                    >
                      <div className="flex items-center space-x-2 mb-2">
                        {format.icon}
                        <span className="font-medium">{format.name}</span>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        {format.description}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </TabsContent>

            <TabsContent value="options" className="space-y-4">
              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <Checkbox
                    checked={exportFilters.includeMetadata}
                    onCheckedChange={(checked: boolean) =>
                      setExportFilters((prev) => ({
                        ...prev,
                        includeMetadata: !!checked,
                      }))
                    }
                  />
                  <label className="text-sm">
                    Include metadata and document information
                  </label>
                </div>

                <div className="flex items-center space-x-2">
                  <Checkbox
                    checked={exportFilters.includeComments}
                    onCheckedChange={(checked: boolean) =>
                      setExportFilters((prev) => ({
                        ...prev,
                        includeComments: !!checked,
                      }))
                    }
                  />
                  <label className="text-sm">
                    Include annotation comments and notes
                  </label>
                </div>

                <div className="flex items-center space-x-2">
                  <Checkbox
                    checked={exportFilters.includeAnnotationHistory}
                    onCheckedChange={(checked: boolean) =>
                      setExportFilters((prev) => ({
                        ...prev,
                        includeAnnotationHistory: !!checked,
                      }))
                    }
                  />
                  <label className="text-sm">
                    Include annotation edit history
                  </label>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="filters" className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">Start Date</label>
                  <Input type="date" />
                </div>
                <div>
                  <label className="text-sm font-medium">End Date</label>
                  <Input type="date" />
                </div>
              </div>

              <div>
                <label className="text-sm font-medium">Annotation Types</label>
                <Select>
                  <SelectTrigger>
                    <SelectValue placeholder="All types" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Types</SelectItem>
                    <SelectItem value="entities">Named Entities</SelectItem>
                    <SelectItem value="relations">Relations</SelectItem>
                    <SelectItem value="events">Events</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="text-sm font-medium">Annotators</label>
                <Select>
                  <SelectTrigger>
                    <SelectValue placeholder="All annotators" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Annotators</SelectItem>
                    <SelectItem value="user1">Dr. Sarah Johnson</SelectItem>
                    <SelectItem value="user2">Prof. Michael Chen</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </TabsContent>
          </Tabs>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setIsExportDialogOpen(false)}
            >
              Cancel
            </Button>
            <Button
              onClick={handleStartExport}
              disabled={!selectedFormat || !selectedProject || !exportName}
            >
              Start Export
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Custom Format Dialog */}
      <Dialog
        open={isCustomFormatDialogOpen}
        onOpenChange={setIsCustomFormatDialogOpen}
      >
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Custom Export Format</DialogTitle>
            <DialogDescription>
              Create a custom export template using template variables
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium">Template Format</label>
              <Textarea
                value={customFormatTemplate}
                onChange={(e) => setCustomFormatTemplate(e.target.value)}
                placeholder={`// Custom format template example:
{
  "document": "{{document.name}}",
  "annotations": [
    {{#each annotations}}
    {
      "text": "{{text}}",
      "label": "{{label}}",
      "start": {{start}},
      "end": {{end}},
      "annotator": "{{annotator.name}}"
    }{{#unless @last}},{{/unless}}
    {{/each}}
  ]
}`}
                rows={12}
                className="font-mono text-sm"
              />
            </div>

            <div className="bg-muted p-3 rounded-lg">
              <h4 className="text-sm font-medium mb-2">Available Variables:</h4>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <span>
                  <code>{"{{document.name}}"}</code> - Document name
                </span>
                <span>
                  <code>{"{{document.text}}"}</code> - Document content
                </span>
                <span>
                  <code>{"{{annotations}}"}</code> - Annotation array
                </span>
                <span>
                  <code>{"{{annotation.text}}"}</code> - Annotation text
                </span>
                <span>
                  <code>{"{{annotation.label}}"}</code> - Annotation label
                </span>
                <span>
                  <code>{"{{annotation.start}}"}</code> - Start position
                </span>
                <span>
                  <code>{"{{annotation.end}}"}</code> - End position
                </span>
                <span>
                  <code>{"{{annotator.name}}"}</code> - Annotator name
                </span>
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setIsCustomFormatDialogOpen(false)}
            >
              Cancel
            </Button>
            <Button onClick={() => setIsCustomFormatDialogOpen(false)}>
              Save Template
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
