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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import {
  ArrowLeft,
  Settings,
  Tag,
  Trash2,
  Plus,
  UserPlus,
  Mail,
  Shield,
  Save,
  AlertTriangle,
} from "lucide-react";
import Link from "next/link";

// Mock data for project settings
const mockProject = {
  id: 1,
  name: "Medical Research Corpus",
  description:
    "Annotation project for medical literature analysis focusing on identifying key medical entities, symptoms, and treatments in research papers.",
  visibility: "private",
  allowGuestAccess: false,
  requireReviewApproval: true,
  annotationGuidelines:
    "Please follow the medical entity annotation guidelines...",
  owner: "Dr. Sarah Johnson",
  createdAt: "2024-01-15",
  tagSets: [
    { id: 1, name: "Medical Entities", isDefault: true },
    { id: 2, name: "Clinical Terms", isDefault: false },
  ],
};

const mockTeamMembers = [
  {
    id: 1,
    name: "Dr. Sarah Johnson",
    email: "sarah@university.edu",
    role: "owner",
    avatar: "",
    joinedAt: "2024-01-15",
  },
  {
    id: 2,
    name: "Michael Chen",
    email: "michael@university.edu",
    role: "annotator",
    avatar: "",
    joinedAt: "2024-01-20",
  },
  {
    id: 3,
    name: "Emma Rodriguez",
    email: "emma@university.edu",
    role: "annotator",
    avatar: "",
    joinedAt: "2024-01-25",
  },
  {
    id: 4,
    name: "James Wilson",
    email: "james@university.edu",
    role: "reviewer",
    avatar: "",
    joinedAt: "2024-02-01",
  },
  {
    id: 5,
    name: "Lisa Thompson",
    email: "lisa@university.edu",
    role: "annotator",
    avatar: "",
    joinedAt: "2024-02-10",
  },
];

function ProjectSettingsPage() {
  const [project, setProject] = useState(mockProject);
  const [teamMembers, setTeamMembers] = useState(mockTeamMembers);
  const [isInviteDialogOpen, setIsInviteDialogOpen] = useState(false);
  const [inviteData, setInviteData] = useState({
    email: "",
    role: "annotator",
  });
  const [activeTab, setActiveTab] = useState("general");

  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase();
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case "owner":
        return "bg-purple-100 text-purple-800";
      case "reviewer":
        return "bg-blue-100 text-blue-800";
      case "annotator":
        return "bg-green-100 text-green-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const handleSaveSettings = () => {
    // Save project settings
    console.log("Saving project settings:", project);
  };

  const handleInviteMember = () => {
    // Send invitation
    console.log("Inviting member:", inviteData);
    setIsInviteDialogOpen(false);
    setInviteData({ email: "", role: "annotator" });
  };

  const handleRemoveMember = (memberId: number) => {
    setTeamMembers((prev) => prev.filter((member) => member.id !== memberId));
  };

  const handleRoleChange = (memberId: number, newRole: string) => {
    setTeamMembers((prev) =>
      prev.map((member) =>
        member.id === memberId ? { ...member, role: newRole } : member
      )
    );
  };

  return (
    <AppLayout>
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link href={`/projects/${project.id}`}>
              <Button variant="ghost" size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Project
              </Button>
            </Link>
            <div>
              <h1 className="text-3xl font-bold">Project Settings</h1>
              <p className="text-muted-foreground">{project.name}</p>
            </div>
          </div>
          <Button onClick={handleSaveSettings}>
            <Save className="h-4 w-4 mr-2" />
            Save Changes
          </Button>
        </div>

        {/* Settings Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="general">General</TabsTrigger>
            <TabsTrigger value="team">Team</TabsTrigger>
            <TabsTrigger value="annotations">Annotations</TabsTrigger>
            <TabsTrigger value="danger">Danger Zone</TabsTrigger>
          </TabsList>

          <TabsContent value="general" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Project Information</CardTitle>
                <CardDescription>
                  Basic information about your project
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Project Name</Label>
                  <Input
                    id="name"
                    value={project.name}
                    onChange={(e) =>
                      setProject((prev) => ({ ...prev, name: e.target.value }))
                    }
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    value={project.description}
                    onChange={(e) =>
                      setProject((prev) => ({
                        ...prev,
                        description: e.target.value,
                      }))
                    }
                    rows={3}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="visibility">Visibility</Label>
                  <Select
                    value={project.visibility}
                    onValueChange={(value: string) =>
                      setProject((prev) => ({ ...prev, visibility: value }))
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="private">Private</SelectItem>
                      <SelectItem value="internal">Internal</SelectItem>
                      <SelectItem value="public">Public</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Access Settings</CardTitle>
                <CardDescription>
                  Control who can access and interact with your project
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Allow Guest Access</Label>
                    <p className="text-sm text-muted-foreground">
                      Allow non-members to view project documents
                    </p>
                  </div>
                  <Switch
                    checked={project.allowGuestAccess}
                    onCheckedChange={(checked: boolean) =>
                      setProject((prev) => ({
                        ...prev,
                        allowGuestAccess: checked,
                      }))
                    }
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Require Review Approval</Label>
                    <p className="text-sm text-muted-foreground">
                      All annotations must be reviewed before finalization
                    </p>
                  </div>
                  <Switch
                    checked={project.requireReviewApproval}
                    onCheckedChange={(checked: boolean) =>
                      setProject((prev) => ({
                        ...prev,
                        requireReviewApproval: checked,
                      }))
                    }
                  />
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="team" className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Team Members</CardTitle>
                    <CardDescription>
                      Manage who has access to this project
                    </CardDescription>
                  </div>
                  <Dialog
                    open={isInviteDialogOpen}
                    onOpenChange={setIsInviteDialogOpen}
                  >
                    <DialogTrigger asChild>
                      <Button>
                        <UserPlus className="h-4 w-4 mr-2" />
                        Invite Member
                      </Button>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>Invite Team Member</DialogTitle>
                        <DialogDescription>
                          Send an invitation to join this project
                        </DialogDescription>
                      </DialogHeader>
                      <div className="space-y-4">
                        <div className="space-y-2">
                          <Label htmlFor="email">Email Address</Label>
                          <Input
                            id="email"
                            type="email"
                            value={inviteData.email}
                            onChange={(e) =>
                              setInviteData((prev) => ({
                                ...prev,
                                email: e.target.value,
                              }))
                            }
                            placeholder="Enter email address"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="role">Role</Label>
                          <Select
                            value={inviteData.role}
                            onValueChange={(value: string) =>
                              setInviteData((prev) => ({
                                ...prev,
                                role: value,
                              }))
                            }
                          >
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="annotator">
                                Annotator
                              </SelectItem>
                              <SelectItem value="reviewer">Reviewer</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      </div>
                      <DialogFooter>
                        <Button
                          variant="outline"
                          onClick={() => setIsInviteDialogOpen(false)}
                        >
                          Cancel
                        </Button>
                        <Button onClick={handleInviteMember}>
                          <Mail className="h-4 w-4 mr-2" />
                          Send Invitation
                        </Button>
                      </DialogFooter>
                    </DialogContent>
                  </Dialog>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {teamMembers.map((member) => (
                    <div
                      key={member.id}
                      className="flex items-center justify-between p-4 border rounded-lg"
                    >
                      <div className="flex items-center space-x-3">
                        <Avatar>
                          <AvatarImage src={member.avatar} />
                          <AvatarFallback>
                            {getInitials(member.name)}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <p className="font-medium">{member.name}</p>
                          <p className="text-sm text-muted-foreground">
                            {member.email}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            Joined {member.joinedAt}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        {member.role === "owner" ? (
                          <Badge className={getRoleColor(member.role)}>
                            <Shield className="h-3 w-3 mr-1" />
                            {member.role}
                          </Badge>
                        ) : (
                          <Select
                            value={member.role}
                            onValueChange={(value: string) =>
                              handleRoleChange(member.id, value)
                            }
                          >
                            <SelectTrigger className="w-32">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="annotator">
                                Annotator
                              </SelectItem>
                              <SelectItem value="reviewer">Reviewer</SelectItem>
                            </SelectContent>
                          </Select>
                        )}
                        {member.role !== "owner" && (
                          <AlertDialog>
                            <AlertDialogTrigger asChild>
                              <Button
                                variant="ghost"
                                size="sm"
                                className="text-destructive hover:text-destructive"
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </AlertDialogTrigger>
                            <AlertDialogContent>
                              <AlertDialogHeader>
                                <AlertDialogTitle>
                                  Remove Team Member
                                </AlertDialogTitle>
                                <AlertDialogDescription>
                                  Are you sure you want to remove {member.name}{" "}
                                  from this project? This action cannot be
                                  undone.
                                </AlertDialogDescription>
                              </AlertDialogHeader>
                              <AlertDialogFooter>
                                <AlertDialogCancel>Cancel</AlertDialogCancel>
                                <AlertDialogAction
                                  onClick={() => handleRemoveMember(member.id)}
                                >
                                  Remove
                                </AlertDialogAction>
                              </AlertDialogFooter>
                            </AlertDialogContent>
                          </AlertDialog>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="annotations" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Annotation Guidelines</CardTitle>
                <CardDescription>
                  Provide instructions for annotators working on this project
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Textarea
                  value={project.annotationGuidelines}
                  onChange={(e) =>
                    setProject((prev) => ({
                      ...prev,
                      annotationGuidelines: e.target.value,
                    }))
                  }
                  rows={6}
                  placeholder="Enter annotation guidelines..."
                />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Tag Sets</CardTitle>
                <CardDescription>
                  Manage the tag sets used in this project
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {project.tagSets.map((tagSet) => (
                    <div
                      key={tagSet.id}
                      className="flex items-center justify-between p-3 border rounded-lg"
                    >
                      <div className="flex items-center space-x-3">
                        <Tag className="h-4 w-4 text-muted-foreground" />
                        <div>
                          <p className="font-medium">{tagSet.name}</p>
                          {tagSet.isDefault && (
                            <Badge variant="secondary" className="mt-1">
                              Default
                            </Badge>
                          )}
                        </div>
                      </div>
                      <Button variant="ghost" size="sm">
                        <Settings className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                  <Button variant="outline" className="w-full">
                    <Plus className="h-4 w-4 mr-2" />
                    Add Tag Set
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="danger" className="space-y-6">
            <Card className="border-destructive">
              <CardHeader>
                <CardTitle className="text-destructive flex items-center">
                  <AlertTriangle className="h-5 w-5 mr-2" />
                  Danger Zone
                </CardTitle>
                <CardDescription>
                  Irreversible and destructive actions
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="border border-destructive/20 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium text-destructive">
                        Delete Project
                      </h4>
                      <p className="text-sm text-muted-foreground">
                        Permanently delete this project and all its data. This
                        cannot be undone.
                      </p>
                    </div>
                    <AlertDialog>
                      <AlertDialogTrigger asChild>
                        <Button variant="destructive">
                          <Trash2 className="h-4 w-4 mr-2" />
                          Delete Project
                        </Button>
                      </AlertDialogTrigger>
                      <AlertDialogContent>
                        <AlertDialogHeader>
                          <AlertDialogTitle>Delete Project</AlertDialogTitle>
                          <AlertDialogDescription>
                            This action cannot be undone. This will permanently
                            delete the &quot;{project.name}&quot; project and
                            remove all data including documents, annotations,
                            and team members.
                          </AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                          <AlertDialogCancel>Cancel</AlertDialogCancel>
                          <AlertDialogAction className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
                            Yes, delete project
                          </AlertDialogAction>
                        </AlertDialogFooter>
                      </AlertDialogContent>
                    </AlertDialog>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </AppLayout>
  );
}

// Export the component wrapped with authentication protection
export default withAuth(ProjectSettingsPage);
