"use client";

import { useState } from "react";
import { AppLayout } from "@/components/layout/AppLayout";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  ArrowLeft,
  Users,
  FileText,
  Upload,
  Download,
  Settings,
  Plus,
  MoreVertical,
  Calendar,
  Activity,
} from "lucide-react";
import Link from "next/link";

// Mock data for project details
const mockProject = {
  id: 1,
  name: "Medical Research Corpus",
  description:
    "Annotation project for medical literature analysis focusing on identifying key medical entities, symptoms, and treatments in research papers.",
  owner: "Dr. Sarah Johnson",
  status: "active",
  createdAt: "2024-01-15",
  updatedAt: "2024-03-10",
  tags: ["Medical", "Research", "NLP"],
  statistics: {
    totalDocuments: 25,
    annotatedDocuments: 18,
    totalAnnotations: 1247,
    teamMembers: 5,
  },
  teamMembers: [
    {
      id: 1,
      name: "Dr. Sarah Johnson",
      email: "sarah@university.edu",
      role: "Owner",
      avatar: "",
    },
    {
      id: 2,
      name: "Michael Chen",
      email: "michael@university.edu",
      role: "Annotator",
      avatar: "",
    },
    {
      id: 3,
      name: "Emma Rodriguez",
      email: "emma@university.edu",
      role: "Annotator",
      avatar: "",
    },
    {
      id: 4,
      name: "James Wilson",
      email: "james@university.edu",
      role: "Reviewer",
      avatar: "",
    },
    {
      id: 5,
      name: "Lisa Thompson",
      email: "lisa@university.edu",
      role: "Annotator",
      avatar: "",
    },
  ],
  documents: [
    {
      id: 1,
      name: "research_paper_001.pdf",
      size: "2.3 MB",
      uploadedAt: "2024-03-01",
      status: "annotated",
      annotations: 45,
    },
    {
      id: 2,
      name: "medical_journal_002.pdf",
      size: "1.8 MB",
      uploadedAt: "2024-03-02",
      status: "in_progress",
      annotations: 23,
    },
    {
      id: 3,
      name: "clinical_study_003.pdf",
      size: "3.1 MB",
      uploadedAt: "2024-03-03",
      status: "pending",
      annotations: 0,
    },
    {
      id: 4,
      name: "research_abstract_004.txt",
      size: "15 KB",
      uploadedAt: "2024-03-04",
      status: "annotated",
      annotations: 67,
    },
    {
      id: 5,
      name: "medical_review_005.pdf",
      size: "2.7 MB",
      uploadedAt: "2024-03-05",
      status: "reviewed",
      annotations: 89,
    },
  ],
  recentActivity: [
    {
      id: 1,
      user: "Michael Chen",
      action: "completed annotation of",
      target: "research_paper_001.pdf",
      timestamp: "2 hours ago",
    },
    {
      id: 2,
      user: "Emma Rodriguez",
      action: "started annotating",
      target: "medical_journal_002.pdf",
      timestamp: "4 hours ago",
    },
    {
      id: 3,
      user: "James Wilson",
      action: "reviewed",
      target: "medical_review_005.pdf",
      timestamp: "1 day ago",
    },
    {
      id: 4,
      user: "Lisa Thompson",
      action: "uploaded",
      target: "clinical_study_003.pdf",
      timestamp: "2 days ago",
    },
  ],
};

export default function ProjectDetailPage() {
  const [project] = useState(mockProject);
  const [activeTab, setActiveTab] = useState("overview");

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-green-100 text-green-800";
      case "completed":
        return "bg-blue-100 text-blue-800";
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

  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase();
  };

  return (
    <AppLayout>
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link href="/projects">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Projects
              </Button>
            </Link>
            <div>
              <div className="flex items-center space-x-3">
                <h1 className="text-3xl font-bold">{project.name}</h1>
                <Badge className={getStatusColor(project.status)}>
                  {project.status}
                </Badge>
              </div>
              <p className="text-muted-foreground">{project.description}</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
            <Button variant="outline">
              <Settings className="h-4 w-4 mr-2" />
              Settings
            </Button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <FileText className="h-5 w-5 text-primary" />
                <div>
                  <p className="text-2xl font-bold">
                    {project.statistics.totalDocuments}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Total Documents
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Activity className="h-5 w-5 text-green-600" />
                <div>
                  <p className="text-2xl font-bold">
                    {project.statistics.annotatedDocuments}
                  </p>
                  <p className="text-sm text-muted-foreground">Annotated</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <FileText className="h-5 w-5 text-blue-600" />
                <div>
                  <p className="text-2xl font-bold">
                    {project.statistics.totalAnnotations}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Total Annotations
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Users className="h-5 w-5 text-purple-600" />
                <div>
                  <p className="text-2xl font-bold">
                    {project.statistics.teamMembers}
                  </p>
                  <p className="text-sm text-muted-foreground">Team Members</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="documents">Documents</TabsTrigger>
            <TabsTrigger value="team">Team</TabsTrigger>
            <TabsTrigger value="activity">Activity</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Project Info */}
              <Card>
                <CardHeader>
                  <CardTitle>Project Information</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label className="text-sm font-medium">Owner</label>
                    <p className="text-sm text-muted-foreground">
                      {project.owner}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium">Created</label>
                    <p className="text-sm text-muted-foreground">
                      {project.createdAt}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium">Last Updated</label>
                    <p className="text-sm text-muted-foreground">
                      {project.updatedAt}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium">Tags</label>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {project.tags.map((tag, index) => (
                        <Badge key={index} variant="secondary">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Recent Activity */}
              <Card>
                <CardHeader>
                  <CardTitle>Recent Activity</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {project.recentActivity.map((activity) => (
                      <div
                        key={activity.id}
                        className="flex items-start space-x-3"
                      >
                        <Avatar className="h-8 w-8">
                          <AvatarFallback className="text-xs">
                            {getInitials(activity.user)}
                          </AvatarFallback>
                        </Avatar>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm">
                            <span className="font-medium">{activity.user}</span>{" "}
                            {activity.action}{" "}
                            <span className="font-medium">
                              {activity.target}
                            </span>
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {activity.timestamp}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="documents" className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">Documents</h3>
              <Button>
                <Upload className="h-4 w-4 mr-2" />
                Upload Document
              </Button>
            </div>

            <Card>
              <CardContent className="p-0">
                <div className="space-y-0">
                  {project.documents.map((doc, index) => (
                    <div
                      key={doc.id}
                      className={`flex items-center justify-between p-4 hover:bg-muted/50 ${
                        index !== project.documents.length - 1 ? "border-b" : ""
                      }`}
                    >
                      <div className="flex items-center space-x-3">
                        <FileText className="h-5 w-5 text-muted-foreground" />
                        <div>
                          <p className="font-medium">{doc.name}</p>
                          <p className="text-sm text-muted-foreground">
                            {doc.size} • Uploaded {doc.uploadedAt}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-3">
                        <Badge className={getStatusColor(doc.status)}>
                          {doc.status.replace("_", " ")}
                        </Badge>
                        <span className="text-sm text-muted-foreground">
                          {doc.annotations} annotations
                        </span>
                        <Button variant="ghost" size="sm">
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="team" className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">Team Members</h3>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Add Member
              </Button>
            </div>

            <Card>
              <CardContent className="p-0">
                <div className="space-y-0">
                  {project.teamMembers.map((member, index) => (
                    <div
                      key={member.id}
                      className={`flex items-center justify-between p-4 hover:bg-muted/50 ${
                        index !== project.teamMembers.length - 1
                          ? "border-b"
                          : ""
                      }`}
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
                        </div>
                      </div>
                      <div className="flex items-center space-x-3">
                        <Badge variant="secondary">{member.role}</Badge>
                        <Button variant="ghost" size="sm">
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="activity" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Project Activity</CardTitle>
                <CardDescription>
                  Recent actions and changes in this project
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {project.recentActivity.map((activity) => (
                    <div
                      key={activity.id}
                      className="flex items-start space-x-4"
                    >
                      <Avatar className="h-10 w-10">
                        <AvatarFallback>
                          {getInitials(activity.user)}
                        </AvatarFallback>
                      </Avatar>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm">
                          <span className="font-medium">{activity.user}</span>{" "}
                          {activity.action}{" "}
                          <span className="font-medium">{activity.target}</span>
                        </p>
                        <div className="flex items-center mt-1 text-xs text-muted-foreground">
                          <Calendar className="h-3 w-3 mr-1" />
                          {activity.timestamp}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </AppLayout>
  );
}
