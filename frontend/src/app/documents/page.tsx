"use client";

import { useState, useCallback, useEffect } from "react";
import { withAuth } from "@/components/auth/withAuth";
import { AppLayout } from "@/components/layout/AppLayout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
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
  DialogTrigger,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Upload,
  FileText,
  MoreVertical,
  Download,
  Eye,
  Edit,
  Trash2,
  Search,
  Filter,
  Plus,
  File,
  FileImage,
  FileVideo,
  FileAudio,
  ArrowLeft,
  RefreshCw,
} from "lucide-react";
import Link from "next/link";

// Mock data for documents
// Start with an empty list for new users
interface Document {
  id: number;
  name: string;
  originalName: string;
  size: string;
  type: string;
  uploadedAt: string;
  uploadedBy: string;
  status: string;
  annotations: number;
  description: string;
  tags: string[];
}
const mockDocuments: Document[] = [];

function DocumentsPage() {
  const [documents, setDocuments] = useState(mockDocuments);
  const [isLoadingDocuments, setIsLoadingDocuments] = useState(true);
  const [isDeleting, setIsDeleting] = useState<number | null>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [viewingDocument, setViewingDocument] = useState<any>(null);
  const [isLoadingContent, setIsLoadingContent] = useState(false);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [editingDocument, setEditingDocument] = useState<any>(null);
  const [editData, setEditData] = useState({
    name: "",
    description: "",
    tags: "",
    content: "",
  });
  const [isUpdating, setIsUpdating] = useState(false);
  const [isLoadingEditContent, setIsLoadingEditContent] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [isUploadDialogOpen, setIsUploadDialogOpen] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [uploadData, setUploadData] = useState({
    name: "",
    description: "",
    tags: "",
  });

  // Reset form when dialog closes
  useEffect(() => {
    if (!isUploadDialogOpen) {
      setSelectedFile(null);
      setUploadData({
        name: "",
        description: "",
        tags: "",
      });
      setUploadError("");
    }
  }, [isUploadDialogOpen]);

  // Fetch documents on component mount
  const fetchDocuments = async () => {
    try {
      setIsLoadingDocuments(true);
      const { getProjectDocuments } = await import("@/lib/api/documents");
      const projectId = 1; // Assuming project ID 1 for now
      const fetchedDocuments = await getProjectDocuments(projectId);

      // Transform backend response to match frontend Document interface
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const transformedDocuments = fetchedDocuments.map((doc: any) => ({
        id: doc.id,
        name: doc.name || doc.filename || "Untitled",
        originalName: doc.filename || doc.name || "Unknown",
        size: doc.size ? `${(doc.size / 1024).toFixed(1)} KB` : "Unknown size",
        type: doc.content_type || doc.type || "Unknown",
        uploadedAt:
          doc.created_at || doc.uploadedAt || new Date().toISOString(),
        uploadedBy: doc.uploaded_by || "Unknown user",
        status: "completed",
        annotations: 0,
        description: doc.description || "",
        tags: doc.tags || [],
      }));

      setDocuments(transformedDocuments);
      console.log("Documents fetched successfully:", transformedDocuments);
    } catch (error) {
      console.error("Error fetching documents:", error);
    } finally {
      setIsLoadingDocuments(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);
  const getStatusColor = (status: string) => {
    switch (status) {
      case "annotated":
        return "bg-green-100 text-green-800";
      case "in_progress":
        return "bg-yellow-100 text-yellow-800";
      case "pending":
        return "bg-gray-100 text-gray-800";
      case "reviewed":
        return "bg-purple-100 text-purple-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getFileIcon = (type: string) => {
    if (type.includes("pdf") || type.includes("document")) {
      return <FileText className="h-5 w-5" />;
    } else if (type.includes("image")) {
      return <FileImage className="h-5 w-5" />;
    } else if (type.includes("video")) {
      return <FileVideo className="h-5 w-5" />;
    } else if (type.includes("audio")) {
      return <FileAudio className="h-5 w-5" />;
    }
    return <File className="h-5 w-5" />;
  };

  const filteredDocuments = documents.filter((doc) => {
    const matchesSearch =
      doc.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      doc.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      doc.tags.some((tag) =>
        tag.toLowerCase().includes(searchTerm.toLowerCase())
      );
    const matchesStatus = statusFilter === "all" || doc.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setDragActive(false);

      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        // Set the selected file
        setSelectedFile(e.dataTransfer.files[0]);

        // Prefill name with filename if empty
        if (!uploadData.name) {
          const fileName = e.dataTransfer.files[0].name.split(".")[0]; // Remove extension
          setUploadData((prev) => ({ ...prev, name: fileName }));
        }

        // Clear any previous errors
        setUploadError("");
      }
    },
    [uploadData.name]
  );

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      // Set the selected file
      setSelectedFile(e.target.files[0]);

      // Prefill name with filename if empty
      if (!uploadData.name) {
        const fileName = e.target.files[0].name.split(".")[0]; // Remove extension
        setUploadData((prev) => ({ ...prev, name: fileName }));
      }

      // Clear any previous errors
      setUploadError("");
    }
  };

  const handleDelete = async (documentId: number, documentName: string) => {
    if (
      !confirm(
        `Are you sure you want to delete "${documentName}"? This action cannot be undone.`
      )
    ) {
      return;
    }

    try {
      setIsDeleting(documentId);
      console.log(`Deleting document ${documentId}: ${documentName}`);

      // Import the deleteDocument function
      const { deleteDocument } = await import("@/lib/api/documents");

      // Delete the document
      await deleteDocument(documentId);

      console.log(`Document ${documentId} deleted successfully`);

      // Refresh the documents list
      await fetchDocuments();
    } catch (error: unknown) {
      console.error("Error deleting document:", error);
      alert(
        error instanceof Error
          ? `Failed to delete document: ${error.message}`
          : "Failed to delete document. Please try again."
      );
    } finally {
      setIsDeleting(null);
    }
  };

  const handleView = async (documentId: number) => {
    try {
      console.log(`=== VIEWING DOCUMENT ${documentId} ===`);
      setIsLoadingContent(true);

      // Get the auth token
      const token = localStorage.getItem("auth-token");
      console.log("Auth token present:", !!token);
      if (!token) {
        alert("Please log in to view documents");
        return;
      }

      console.log(
        `Fetching content from: http://localhost:8000/api/documents/${documentId}/content`
      );

      // Fetch document content from the new content endpoint
      const response = await fetch(
        `http://localhost:8000/api/documents/${documentId}/content`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      console.log("Response status:", response.status);
      console.log("Response ok:", response.ok);

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Error response:", errorText);
        throw new Error(
          `Failed to load content: ${response.status} ${errorText}`
        );
      }

      const document = await response.json();
      console.log("Document data received:", document);
      console.log(
        "Content length:",
        document.content ? document.content.length : 0
      );

      setViewingDocument(document);
    } catch (error) {
      console.error("Error viewing document:", error);
      alert(
        error instanceof Error
          ? `Failed to load document: ${error.message}`
          : "Failed to load document content"
      );
    } finally {
      setIsLoadingContent(false);
    }
  };

  const handleEdit = async (
    documentId: number,
    currentName: string,
    currentDescription: string = "",
    currentTags: string[] = []
  ) => {
    try {
      setIsLoadingEditContent(true);

      // Set the document to edit and populate form with current values
      setEditingDocument({
        id: documentId,
        name: currentName,
        description: currentDescription,
        tags: currentTags,
      });
      setEditData({
        name: currentName,
        description: currentDescription,
        tags: currentTags.join(", "),
        content: "", // Will be loaded
      });

      // Fetch the document content for editing
      const token = localStorage.getItem("auth-token");
      if (token) {
        const response = await fetch(
          `http://localhost:8000/api/documents/${documentId}/content`,
          {
            method: "GET",
            headers: {
              Authorization: `Bearer ${token}`,
              "Content-Type": "application/json",
            },
          }
        );

        if (response.ok) {
          const document = await response.json();
          setEditData((prev) => ({
            ...prev,
            content: document.content || "",
          }));
        }
      }
    } catch (error) {
      console.error("Error loading document content for editing:", error);
    } finally {
      setIsLoadingEditContent(false);
    }
  };

  const handleUpdateDocument = async () => {
    if (!editingDocument) return;

    try {
      setIsUpdating(true);

      const { updateDocument } = await import("@/lib/api/documents");

      // Convert comma-separated tags back to array
      const tags = editData.tags
        ? editData.tags
            .split(",")
            .map((tag) => tag.trim())
            .filter((tag) => tag.length > 0)
        : [];

      await updateDocument(editingDocument.id, {
        name: editData.name,
        description: editData.description,
        tags: tags,
        content: editData.content,
      });

      console.log(`Document ${editingDocument.id} updated successfully`);

      // Close modal and reset form
      setEditingDocument(null);
      setEditData({ name: "", description: "", tags: "", content: "" });

      // Refresh the documents list
      await fetchDocuments();
    } catch (error) {
      console.error("Error updating document:", error);
      alert(
        error instanceof Error
          ? `Failed to update document: ${error.message}`
          : "Failed to update document"
      );
    } finally {
      setIsUpdating(false);
    }
  };

  const handleDownload = async (documentId: number, fileName: string) => {
    try {
      // Get the auth token from localStorage
      const token = localStorage.getItem("auth-token");
      if (!token) {
        alert("Please log in to download documents");
        return;
      }

      // Make authenticated request to download endpoint
      const response = await fetch(
        `http://localhost:8000/api/documents/${documentId}/download`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Download failed: ${errorText}`);
      }

      // Get the file blob
      const blob = await response.blob();

      // Create download URL and trigger download
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = downloadUrl;
      link.download = fileName;
      document.body.appendChild(link);
      link.click();

      // Cleanup
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);

      console.log(`Downloaded document: ${fileName}`);
    } catch (error) {
      console.error("Error downloading document:", error);
      alert(
        error instanceof Error
          ? `Failed to download: ${error.message}`
          : "Failed to download document"
      );
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadError("Please select a file to upload");
      return;
    }

    if (!uploadData.name.trim()) {
      setUploadError("Please enter a name for the document");
      return;
    }

    try {
      setIsUploading(true);
      setUploadError("");

      // Import the uploadDocument function
      const { uploadDocument } = await import("@/lib/api/documents");

      // Convert comma-separated tags to array
      const tags = uploadData.tags
        ? uploadData.tags.split(",").map((tag) => tag.trim())
        : [];

      // Upload the document (using project ID 1 for now - should be dynamic)
      const projectId = 1;
      const result = await uploadDocument(
        projectId,
        selectedFile,
        uploadData.name,
        uploadData.description,
        tags
      );

      if (result) {
        // Upload successful - refetch documents to show the new file
        console.log("Document uploaded:", result);

        // Refetch documents to update the list
        await fetchDocuments();

        // Close the dialog
        setIsUploadDialogOpen(false);

        // Reset form
        setSelectedFile(null);
        setUploadData({ name: "", description: "", tags: "" });
      }
    } catch (error: unknown) {
      console.error("Error uploading document:", error);
      setUploadError(
        error instanceof Error ? error.message : "Failed to upload document"
      );
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <AppLayout>
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link href="/projects/1">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Project
              </Button>
            </Link>
            <div>
              <h1 className="text-3xl font-bold">Documents</h1>
              <p className="text-muted-foreground">
                Manage and organize your project documents
              </p>
            </div>
          </div>
          <div className="flex space-x-2">
            <Button
              variant="outline"
              onClick={fetchDocuments}
              disabled={isLoadingDocuments}
            >
              <RefreshCw
                className={`h-4 w-4 mr-2 ${
                  isLoadingDocuments ? "animate-spin" : ""
                }`}
              />
              Refresh
            </Button>
            <Dialog
              open={isUploadDialogOpen}
              onOpenChange={setIsUploadDialogOpen}
            >
              <DialogTrigger asChild>
                <Button>
                  <Upload className="h-4 w-4 mr-2" />
                  Upload Document
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-[525px]">
                <DialogHeader>
                  <DialogTitle>Upload Document</DialogTitle>
                  <DialogDescription>
                    Upload a new document to your project for annotation.
                  </DialogDescription>
                </DialogHeader>

                {/* Drag and Drop Area */}
                <div
                  className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                    dragActive
                      ? "border-primary bg-primary/5"
                      : "border-muted-foreground/25"
                  }`}
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                >
                  {!selectedFile ? (
                    <>
                      <Upload className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
                      <p className="text-sm font-medium mb-1">
                        Drag and drop your file here, or click to browse
                      </p>
                      <p className="text-xs text-muted-foreground mb-4">
                        Supports PDF, TXT, DOC, and other document formats
                      </p>
                      <input
                        type="file"
                        onChange={handleFileInput}
                        className="hidden"
                        id="file-upload"
                        accept=".pdf,.txt,.doc,.docx"
                      />
                      <label htmlFor="file-upload">
                        <span className="inline-block">
                          <Button
                            variant="outline"
                            type="button"
                            className="cursor-pointer"
                            onClick={() =>
                              document.getElementById("file-upload")?.click()
                            }
                          >
                            Choose File
                          </Button>
                        </span>
                      </label>
                    </>
                  ) : (
                    <div className="space-y-2">
                      <div className="flex items-center justify-center">
                        {getFileIcon(selectedFile.type)}
                        <span className="text-sm font-medium ml-2">
                          {selectedFile.name}
                        </span>
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          setSelectedFile(null);
                          const fileInput = document.getElementById(
                            "file-upload"
                          ) as HTMLInputElement;
                          if (fileInput) fileInput.value = "";
                        }}
                      >
                        Change File
                      </Button>
                    </div>
                  )}
                </div>

                {uploadError && (
                  <div className="text-red-500 text-sm mt-2 p-2 bg-red-50 border border-red-200 rounded">
                    {uploadError}
                  </div>
                )}

                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium">Document Name</label>
                    <Input
                      value={uploadData.name}
                      onChange={(e) =>
                        setUploadData((prev) => ({
                          ...prev,
                          name: e.target.value,
                        }))
                      }
                      placeholder="Enter document name"
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium">Description</label>
                    <Textarea
                      value={uploadData.description}
                      onChange={(e) =>
                        setUploadData((prev) => ({
                          ...prev,
                          description: e.target.value,
                        }))
                      }
                      placeholder="Enter document description"
                      rows={3}
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium">Tags</label>
                    <Input
                      value={uploadData.tags}
                      onChange={(e) =>
                        setUploadData((prev) => ({
                          ...prev,
                          tags: e.target.value,
                        }))
                      }
                      placeholder="Enter tags separated by commas"
                    />
                  </div>
                </div>

                <DialogFooter>
                  <div className="flex space-x-2">
                    <Button
                      variant="outline"
                      onClick={() => setIsUploadDialogOpen(false)}
                      disabled={isUploading}
                    >
                      Cancel
                    </Button>
                    <Button
                      onClick={handleUpload}
                      disabled={isUploading || !selectedFile}
                    >
                      {isUploading ? (
                        <span className="flex items-center">
                          <svg
                            className="animate-spin -ml-1 mr-3 h-4 w-4 text-white"
                            xmlns="http://www.w3.org/2000/svg"
                            fill="none"
                            viewBox="0 0 24 24"
                          >
                            <circle
                              className="opacity-25"
                              cx="12"
                              cy="12"
                              r="10"
                              stroke="currentColor"
                              strokeWidth="4"
                            ></circle>
                            <path
                              className="opacity-75"
                              fill="currentColor"
                              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                            ></path>
                          </svg>
                          Uploading...
                        </span>
                      ) : (
                        "Upload Document"
                      )}
                    </Button>
                  </div>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        </div>

        {/* Filters and Search */}
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search documents..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline">
                <Filter className="h-4 w-4 mr-2" />
                Status:{" "}
                {statusFilter === "all"
                  ? "All"
                  : statusFilter.replace("_", " ")}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuItem onClick={() => setStatusFilter("all")}>
                All Status
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setStatusFilter("pending")}>
                Pending
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setStatusFilter("in_progress")}>
                In Progress
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setStatusFilter("annotated")}>
                Annotated
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setStatusFilter("reviewed")}>
                Reviewed
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        {/* Documents Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {isLoadingDocuments ? (
            <div className="col-span-full text-center py-8">
              <p className="text-gray-500">Loading documents...</p>
            </div>
          ) : (
            filteredDocuments.map((doc) => (
              <Card key={doc.id} className="hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-2">
                      {getFileIcon(doc.type)}
                      <div className="flex-1 min-w-0">
                        <CardTitle className="text-base truncate">
                          {doc.originalName}
                        </CardTitle>
                        <CardDescription className="text-sm">
                          {doc.size} • {doc.uploadedAt}
                        </CardDescription>
                      </div>
                    </div>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="sm">
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent>
                        <DropdownMenuItem asChild>
                          <Link
                            href={`/annotate/${doc.id}`}
                            className="flex items-center"
                          >
                            <Eye className="h-4 w-4 mr-2" />
                            Annotate
                          </Link>
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => handleView(doc.id)}>
                          <Eye className="h-4 w-4 mr-2" />
                          View
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          onClick={() =>
                            handleDownload(doc.id, doc.originalName)
                          }
                        >
                          <Download className="h-4 w-4 mr-2" />
                          Download
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          onClick={() =>
                            handleEdit(
                              doc.id,
                              doc.name,
                              doc.description,
                              doc.tags
                            )
                          }
                        >
                          <Edit className="h-4 w-4 mr-2" />
                          Edit
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          className="text-red-600"
                          onClick={() => handleDelete(doc.id, doc.name)}
                          disabled={isDeleting === doc.id}
                        >
                          <Trash2 className="h-4 w-4 mr-2" />
                          {isDeleting === doc.id ? "Deleting..." : "Delete"}
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <p className="text-sm text-muted-foreground line-clamp-2">
                    {doc.description}
                  </p>

                  <div className="flex items-center justify-between">
                    <Badge className={getStatusColor(doc.status)}>
                      {doc.status.replace("_", " ")}
                    </Badge>
                    <span className="text-sm text-muted-foreground">
                      {doc.annotations} annotations
                    </span>
                  </div>

                  <div className="flex flex-wrap gap-1">
                    {doc.tags.slice(0, 3).map((tag, index) => (
                      <Badge
                        key={index}
                        variant="secondary"
                        className="text-xs"
                      >
                        {tag}
                      </Badge>
                    ))}
                    {doc.tags.length > 3 && (
                      <Badge variant="secondary" className="text-xs">
                        +{doc.tags.length - 3}
                      </Badge>
                    )}
                  </div>

                  <div className="text-xs text-muted-foreground">
                    Uploaded by {doc.uploadedBy}
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>

        {filteredDocuments.length === 0 && !isLoadingDocuments && (
          <div className="text-center py-12">
            <FileText className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No documents found</h3>
            <p className="text-muted-foreground mb-4">
              {searchTerm || statusFilter !== "all"
                ? "Try adjusting your search or filter criteria."
                : "Get started by uploading your first document."}
            </p>
            <Button onClick={() => setIsUploadDialogOpen(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Upload Document
            </Button>
          </div>
        )}
      </div>

      {/* Document Viewer Modal */}
      <Dialog
        open={!!viewingDocument}
        onOpenChange={() => setViewingDocument(null)}
      >
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-hidden flex flex-col">
          <DialogHeader>
            <DialogTitle>
              {viewingDocument?.name || "Document Viewer"}
            </DialogTitle>
            <DialogDescription>
              {viewingDocument?.description || "No description available"}
            </DialogDescription>
          </DialogHeader>

          <div className="flex-1 overflow-auto">
            {isLoadingContent ? (
              <div className="flex items-center justify-center p-8">
                <p className="text-gray-500">Loading content...</p>
              </div>
            ) : viewingDocument ? (
              <div className="space-y-4">
                <div className="bg-gray-50 p-4 rounded border">
                  <h4 className="font-medium text-sm text-gray-700 mb-2">
                    Document Information
                  </h4>
                  <div className="text-sm space-y-1">
                    <p>
                      <strong>Name:</strong> {viewingDocument.name}
                    </p>
                    <p>
                      <strong>File Size:</strong>{" "}
                      {viewingDocument.file_size
                        ? `${viewingDocument.file_size} bytes`
                        : "Unknown"}
                    </p>
                    <p>
                      <strong>Path:</strong> {viewingDocument.file_path}
                    </p>
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-sm text-gray-700 mb-2">
                    Content
                  </h4>
                  <div className="bg-white border rounded p-4 font-mono text-sm whitespace-pre-wrap max-h-96 overflow-auto">
                    {viewingDocument.content || "No content available"}
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-gray-500 p-4">No document selected</p>
            )}
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setViewingDocument(null)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Document Edit Modal */}
      <Dialog
        open={!!editingDocument}
        onOpenChange={() => {
          setEditingDocument(null);
          setEditData({ name: "", description: "", tags: "", content: "" });
        }}
      >
        <DialogContent className="sm:max-w-[525px]">
          <DialogHeader>
            <DialogTitle>Edit Document</DialogTitle>
            <DialogDescription>
              Update the document information below.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div>
              <label
                htmlFor="edit-name"
                className="block text-sm font-medium mb-1"
              >
                Document Name
              </label>
              <Input
                id="edit-name"
                value={editData.name}
                onChange={(e) =>
                  setEditData((prev) => ({ ...prev, name: e.target.value }))
                }
                placeholder="Enter document name"
              />
            </div>

            <div>
              <label
                htmlFor="edit-description"
                className="block text-sm font-medium mb-1"
              >
                Description
              </label>
              <Textarea
                id="edit-description"
                value={editData.description}
                onChange={(e) =>
                  setEditData((prev) => ({
                    ...prev,
                    description: e.target.value,
                  }))
                }
                placeholder="Enter document description"
                rows={3}
              />
            </div>

            <div>
              <label
                htmlFor="edit-tags"
                className="block text-sm font-medium mb-1"
              >
                Tags
              </label>
              <Input
                id="edit-tags"
                value={editData.tags}
                onChange={(e) =>
                  setEditData((prev) => ({ ...prev, tags: e.target.value }))
                }
                placeholder="Enter tags separated by commas"
              />
              <p className="text-sm text-gray-500 mt-1">
                Separate multiple tags with commas (e.g., important, research,
                draft)
              </p>
            </div>

            <div>
              <label
                htmlFor="edit-content"
                className="block text-sm font-medium mb-1"
              >
                File Content
              </label>
              {isLoadingEditContent ? (
                <div className="border rounded-md p-3 text-center text-gray-500">
                  Loading content...
                </div>
              ) : (
                <Textarea
                  id="edit-content"
                  value={editData.content}
                  onChange={(e) =>
                    setEditData((prev) => ({
                      ...prev,
                      content: e.target.value,
                    }))
                  }
                  placeholder="File content will appear here..."
                  rows={10}
                  className="font-mono text-sm"
                />
              )}
              <p className="text-sm text-gray-500 mt-1">
                Edit the file content directly here
              </p>
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setEditingDocument(null);
                setEditData({
                  name: "",
                  description: "",
                  tags: "",
                  content: "",
                });
              }}
              disabled={isUpdating}
            >
              Cancel
            </Button>
            <Button
              onClick={handleUpdateDocument}
              disabled={isUpdating || !editData.name.trim()}
            >
              {isUpdating ? "Updating..." : "Update Document"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </AppLayout>
  );
}

// Export the component wrapped with authentication protection
export default withAuth(DocumentsPage);
