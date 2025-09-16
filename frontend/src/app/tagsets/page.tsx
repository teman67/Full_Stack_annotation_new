"use client";

import { useState } from "react";
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
  Plus,
  Search,
  MoreVertical,
  Edit,
  Trash2,
  Download,
  Upload,
  Eye,
  Copy,
  Tag,
  ArrowLeft,
} from "lucide-react";
import Link from "next/link";

// Start with an empty list for new users
const mockTagSets: TagSet[] = [];

function TagSetsPage() {
  const [tagSets, setTagSets] = useState(mockTagSets);
  const [searchTerm, setSearchTerm] = useState("");
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isImportDialogOpen, setIsImportDialogOpen] = useState(false);
  const [selectedTagSet, setSelectedTagSet] = useState<TagSet | null>(null);
  const [newTagSet, setNewTagSet] = useState({
    name: "",
    description: "",
    tags: [] as Tag[],
  });
  const [newTag, setNewTag] = useState({
    name: "",
    color: "#3B82F6",
    description: "",
  });

  const filteredTagSets = tagSets.filter(
    (tagSet) =>
      tagSet.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      tagSet.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      tagSet.tags.some((tag) =>
        tag.name.toLowerCase().includes(searchTerm.toLowerCase())
      )
  );

  const handleCreateTagSet = () => {
    const newId = Math.max(...tagSets.map((ts) => ts.id)) + 1;
    const tagSet = {
      ...newTagSet,
      id: newId,
      createdAt: new Date().toISOString().split("T")[0],
      updatedAt: new Date().toISOString().split("T")[0],
      createdBy: "Current User",
      usageCount: 0,
      isDefault: false,
    };
    setTagSets([...tagSets, tagSet]);
    setNewTagSet({ name: "", description: "", tags: [] });
    setIsCreateDialogOpen(false);
  };

  const handleAddTag = () => {
    if (newTag.name.trim()) {
      setNewTagSet((prev) => ({
        ...prev,
        tags: [...prev.tags, { ...newTag, name: newTag.name.toUpperCase() }],
      }));
      setNewTag({ name: "", color: "#3B82F6", description: "" });
    }
  };

  const handleRemoveTag = (index: number) => {
    setNewTagSet((prev) => ({
      ...prev,
      tags: prev.tags.filter((_, i) => i !== index),
    }));
  };

  const exportTagSet = (tagSet: TagSet) => {
    const csvContent = [
      "tag_name,color,description",
      ...tagSet.tags.map(
        (tag: Tag) => `${tag.name},${tag.color},"${tag.description}"`
      ),
    ].join("\n");

    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.style.display = "none";
    a.href = url;
    a.download = `${tagSet.name.replace(/\s+/g, "_")}_tags.csv`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const handleFileImport = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        const csv = event.target?.result as string;
        // Parse CSV and create tag set
        console.log("Importing CSV:", csv);
        setIsImportDialogOpen(false);
      };
      reader.readAsText(file);
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
              <h1 className="text-3xl font-bold">Tag Sets</h1>
              <p className="text-muted-foreground">
                Manage annotation tag sets and entity types
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Dialog
              open={isImportDialogOpen}
              onOpenChange={setIsImportDialogOpen}
            >
              <DialogTrigger asChild>
                <Button variant="outline">
                  <Upload className="h-4 w-4 mr-2" />
                  Import CSV
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Import Tag Set from CSV</DialogTitle>
                  <DialogDescription>
                    Upload a CSV file with tag definitions. Format:
                    tag_name,color,description
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <input
                    type="file"
                    accept=".csv"
                    onChange={handleFileImport}
                    className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary file:text-primary-foreground hover:file:bg-primary/80"
                  />
                </div>
                <DialogFooter>
                  <Button
                    variant="outline"
                    onClick={() => setIsImportDialogOpen(false)}
                  >
                    Cancel
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>

            <Dialog
              open={isCreateDialogOpen}
              onOpenChange={setIsCreateDialogOpen}
            >
              <DialogTrigger asChild>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Create Tag Set
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-[600px]">
                <DialogHeader>
                  <DialogTitle>Create New Tag Set</DialogTitle>
                  <DialogDescription>
                    Define a new set of annotation tags for your project.
                  </DialogDescription>
                </DialogHeader>

                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium">Name</label>
                    <Input
                      value={newTagSet.name}
                      onChange={(e) =>
                        setNewTagSet((prev) => ({
                          ...prev,
                          name: e.target.value,
                        }))
                      }
                      placeholder="Enter tag set name"
                    />
                  </div>

                  <div>
                    <label className="text-sm font-medium">Description</label>
                    <Textarea
                      value={newTagSet.description}
                      onChange={(e) =>
                        setNewTagSet((prev) => ({
                          ...prev,
                          description: e.target.value,
                        }))
                      }
                      placeholder="Enter tag set description"
                      rows={2}
                    />
                  </div>

                  <div>
                    <label className="text-sm font-medium">Tags</label>
                    <div className="space-y-2">
                      {/* Add new tag form */}
                      <div className="flex space-x-2">
                        <Input
                          value={newTag.name}
                          onChange={(e) =>
                            setNewTag((prev) => ({
                              ...prev,
                              name: e.target.value,
                            }))
                          }
                          placeholder="Tag name"
                          className="flex-1"
                        />
                        <input
                          type="color"
                          value={newTag.color}
                          onChange={(e) =>
                            setNewTag((prev) => ({
                              ...prev,
                              color: e.target.value,
                            }))
                          }
                          className="w-12 h-10 border rounded"
                        />
                        <Input
                          value={newTag.description}
                          onChange={(e) =>
                            setNewTag((prev) => ({
                              ...prev,
                              description: e.target.value,
                            }))
                          }
                          placeholder="Description"
                          className="flex-1"
                        />
                        <Button onClick={handleAddTag}>Add</Button>
                      </div>

                      {/* Existing tags */}
                      <div className="space-y-1 max-h-32 overflow-y-auto">
                        {newTagSet.tags.map((tag, index) => (
                          <div
                            key={index}
                            className="flex items-center justify-between p-2 bg-muted rounded"
                          >
                            <div className="flex items-center space-x-2">
                              <div
                                className="w-4 h-4 rounded"
                                style={{ backgroundColor: tag.color }}
                              />
                              <span className="font-medium">{tag.name}</span>
                              <span className="text-sm text-muted-foreground">
                                {tag.description}
                              </span>
                            </div>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleRemoveTag(index)}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                <DialogFooter>
                  <Button
                    variant="outline"
                    onClick={() => setIsCreateDialogOpen(false)}
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={handleCreateTagSet}
                    disabled={!newTagSet.name || newTagSet.tags.length === 0}
                  >
                    Create Tag Set
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        </div>

        {/* Search */}
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search tag sets..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>

        {/* Tag Sets Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredTagSets.map((tagSet) => (
            <Card key={tagSet.id} className="hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <CardTitle className="text-lg">{tagSet.name}</CardTitle>
                      {tagSet.isDefault && (
                        <Badge variant="secondary">Default</Badge>
                      )}
                    </div>
                    <CardDescription className="mt-1">
                      {tagSet.description}
                    </CardDescription>
                  </div>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="sm">
                        <MoreVertical className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent>
                      <DropdownMenuItem
                        onClick={() => setSelectedTagSet(tagSet)}
                      >
                        <Eye className="h-4 w-4 mr-2" />
                        View Details
                      </DropdownMenuItem>
                      <DropdownMenuItem>
                        <Edit className="h-4 w-4 mr-2" />
                        Edit
                      </DropdownMenuItem>
                      <DropdownMenuItem>
                        <Copy className="h-4 w-4 mr-2" />
                        Duplicate
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => exportTagSet(tagSet)}>
                        <Download className="h-4 w-4 mr-2" />
                        Export CSV
                      </DropdownMenuItem>
                      {!tagSet.isDefault && (
                        <DropdownMenuItem className="text-red-600">
                          <Trash2 className="h-4 w-4 mr-2" />
                          Delete
                        </DropdownMenuItem>
                      )}
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Tag Preview */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">
                      Tags ({tagSet.tags.length})
                    </span>
                    <span className="text-xs text-muted-foreground">
                      Used in {tagSet.usageCount} projects
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {tagSet.tags.slice(0, 6).map((tag, index) => (
                      <Badge
                        key={index}
                        variant="secondary"
                        className="text-xs"
                        style={{
                          backgroundColor: tag.color + "20",
                          color: tag.color,
                          borderColor: tag.color + "40",
                        }}
                      >
                        {tag.name}
                      </Badge>
                    ))}
                    {tagSet.tags.length > 6 && (
                      <Badge variant="secondary" className="text-xs">
                        +{tagSet.tags.length - 6}
                      </Badge>
                    )}
                  </div>
                </div>

                <div className="text-xs text-muted-foreground">
                  Created by {tagSet.createdBy} • {tagSet.createdAt}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {filteredTagSets.length === 0 && (
          <div className="text-center py-12">
            <Tag className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No tag sets found</h3>
            <p className="text-muted-foreground mb-4">
              {searchTerm
                ? "Try adjusting your search criteria."
                : "Get started by creating your first tag set."}
            </p>
            <Button onClick={() => setIsCreateDialogOpen(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Create Tag Set
            </Button>
          </div>
        )}

        {/* Tag Set Details Modal */}
        {selectedTagSet && (
          <Dialog
            open={!!selectedTagSet}
            onOpenChange={() => setSelectedTagSet(null)}
          >
            <DialogContent className="sm:max-w-[600px]">
              <DialogHeader>
                <DialogTitle>{selectedTagSet.name}</DialogTitle>
                <DialogDescription>
                  {selectedTagSet.description}
                </DialogDescription>
              </DialogHeader>

              <div className="space-y-4">
                <div>
                  <h4 className="font-medium mb-2">
                    Tags ({selectedTagSet.tags.length})
                  </h4>
                  <div className="space-y-2 max-h-60 overflow-y-auto">
                    {selectedTagSet.tags.map((tag: Tag, index: number) => (
                      <div
                        key={index}
                        className="flex items-center space-x-3 p-2 border rounded"
                      >
                        <div
                          className="w-4 h-4 rounded"
                          style={{ backgroundColor: tag.color }}
                        />
                        <div className="flex-1">
                          <div className="font-medium">{tag.name}</div>
                          <div className="text-sm text-muted-foreground">
                            {tag.description}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="text-sm text-muted-foreground">
                  Created by {selectedTagSet.createdBy} on{" "}
                  {selectedTagSet.createdAt}
                  <br />
                  Last updated: {selectedTagSet.updatedAt}
                  <br />
                  Used in {selectedTagSet.usageCount} projects
                </div>
              </div>

              <DialogFooter>
                <Button
                  variant="outline"
                  onClick={() => setSelectedTagSet(null)}
                >
                  Close
                </Button>
                <Button onClick={() => exportTagSet(selectedTagSet)}>
                  <Download className="h-4 w-4 mr-2" />
                  Export CSV
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        )}
      </div>
    </AppLayout>
  );
}

// Export the component wrapped with authentication protection
export default withAuth(TagSetsPage);
