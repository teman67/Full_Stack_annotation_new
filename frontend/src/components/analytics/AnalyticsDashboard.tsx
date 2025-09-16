"use client";

import { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  BarChart3,
  TrendingUp,
  Users,
  FileText,
  Target,
  Activity,
  Clock,
  Download,
} from "lucide-react";

// Mock analytics data
const projectAnalytics = {
  totalProjects: 156,
  activeProjects: 89,
  completedProjects: 45,
  totalAnnotations: 45692,
  avgAnnotationsPerProject: 293,
  totalUsers: 234,
  activeUsers: 156,
  avgSessionTime: "24m 30s",
};

const qualityMetrics = {
  overallQuality: 8.7,
  precision: 92,
  recall: 87,
  consistency: 94,
  interAnnotatorAgreement: 89,
};

// Activity data for charts (used by chart components)
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const activityData = [
  { date: "2024-01-01", annotations: 245, users: 23, projects: 8 },
  { date: "2024-01-02", annotations: 312, users: 28, projects: 12 },
  { date: "2024-01-03", annotations: 189, users: 19, projects: 6 },
  { date: "2024-01-04", annotations: 456, users: 34, projects: 15 },
  { date: "2024-01-05", annotations: 389, users: 31, projects: 11 },
  { date: "2024-01-06", annotations: 287, users: 25, projects: 9 },
  { date: "2024-01-07", annotations: 356, users: 29, projects: 13 },
];

const topProjects = [
  {
    name: "Medical Research Corpus",
    annotations: 3456,
    users: 12,
    quality: 9.1,
  },
  {
    name: "Clinical Trial Analysis",
    annotations: 2890,
    users: 8,
    quality: 8.8,
  },
  {
    name: "Drug Discovery Dataset",
    annotations: 2341,
    users: 15,
    quality: 8.5,
  },
  { name: "Genomics Research", annotations: 1987, users: 6, quality: 9.3 },
  { name: "Biomarker Studies", annotations: 1765, users: 9, quality: 8.2 },
];

const userActivity = [
  {
    name: "Dr. Sarah Johnson",
    annotations: 1234,
    quality: 9.2,
    lastActive: "2 hours ago",
  },
  {
    name: "Prof. Michael Chen",
    annotations: 987,
    quality: 8.9,
    lastActive: "4 hours ago",
  },
  {
    name: "Dr. Emily Rodriguez",
    annotations: 856,
    quality: 9.0,
    lastActive: "1 day ago",
  },
  {
    name: "Alex Thompson",
    annotations: 743,
    quality: 8.7,
    lastActive: "3 hours ago",
  },
  {
    name: "Dr. James Wilson",
    annotations: 692,
    quality: 8.8,
    lastActive: "6 hours ago",
  },
];

export function AnalyticsDashboard() {
  const [timeRange, setTimeRange] = useState("7d");
  const [selectedMetric, setSelectedMetric] = useState("annotations");

  const handleExportReport = () => {
    console.log("Exporting analytics report...");
    // Implementation would generate and download report
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Analytics Dashboard</h2>
          <p className="text-muted-foreground">
            Platform insights and performance metrics
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1d">Last 24h</SelectItem>
              <SelectItem value="7d">Last 7 days</SelectItem>
              <SelectItem value="30d">Last 30 days</SelectItem>
              <SelectItem value="90d">Last 90 days</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline" onClick={handleExportReport}>
            <Download className="h-4 w-4 mr-2" />
            Export Report
          </Button>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <FileText className="h-8 w-8 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">
                  Total Annotations
                </p>
                <p className="text-2xl font-bold">
                  {projectAnalytics.totalAnnotations.toLocaleString()}
                </p>
                <p className="text-xs text-green-600 flex items-center">
                  <TrendingUp className="h-3 w-3 mr-1" />
                  +12% from last week
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <Users className="h-8 w-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">
                  Active Users
                </p>
                <p className="text-2xl font-bold">
                  {projectAnalytics.activeUsers}
                </p>
                <p className="text-xs text-green-600 flex items-center">
                  <TrendingUp className="h-3 w-3 mr-1" />
                  +8% from last week
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <Target className="h-8 w-8 text-purple-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">
                  Quality Score
                </p>
                <p className="text-2xl font-bold">
                  {qualityMetrics.overallQuality}
                </p>
                <p className="text-xs text-green-600 flex items-center">
                  <TrendingUp className="h-3 w-3 mr-1" />
                  +0.2 from last week
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <Clock className="h-8 w-8 text-orange-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">
                  Avg Session
                </p>
                <p className="text-2xl font-bold">
                  {projectAnalytics.avgSessionTime}
                </p>
                <p className="text-xs text-red-600 flex items-center">
                  <TrendingUp className="h-3 w-3 mr-1 rotate-180" />
                  -5% from last week
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Analytics */}
      <Tabs defaultValue="activity" className="space-y-6">
        <TabsList>
          <TabsTrigger value="activity">Activity Trends</TabsTrigger>
          <TabsTrigger value="quality">Quality Metrics</TabsTrigger>
          <TabsTrigger value="projects">Project Performance</TabsTrigger>
          <TabsTrigger value="users">User Analytics</TabsTrigger>
        </TabsList>

        {/* Activity Trends */}
        <TabsContent value="activity" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center">
                    <Activity className="h-5 w-5 mr-2" />
                    Activity Overview
                  </CardTitle>
                  <CardDescription>
                    Platform usage trends over time
                  </CardDescription>
                </div>
                <Select
                  value={selectedMetric}
                  onValueChange={setSelectedMetric}
                >
                  <SelectTrigger className="w-40">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="annotations">Annotations</SelectItem>
                    <SelectItem value="users">Active Users</SelectItem>
                    <SelectItem value="projects">Projects</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardHeader>
            <CardContent>
              {/* Mock Chart - In real app this would be a proper chart component */}
              <div className="h-64 border rounded-lg flex items-center justify-center bg-muted/10">
                <div className="text-center">
                  <BarChart3 className="h-12 w-12 text-muted-foreground mx-auto mb-2" />
                  <p className="text-muted-foreground">
                    Chart showing {selectedMetric} trends
                  </p>
                  <p className="text-sm text-muted-foreground mt-1">
                    Integration with Chart.js or Recharts would go here
                  </p>
                </div>
              </div>

              {/* Activity Summary */}
              <div className="grid grid-cols-3 gap-4 mt-6">
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">2,834</div>
                  <div className="text-sm text-muted-foreground">
                    Annotations This Week
                  </div>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-green-600">189</div>
                  <div className="text-sm text-muted-foreground">
                    Peak Daily Users
                  </div>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">23</div>
                  <div className="text-sm text-muted-foreground">
                    Active Projects
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Quality Metrics */}
        <TabsContent value="quality" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Quality Metrics</CardTitle>
                <CardDescription>
                  Annotation quality and accuracy measures
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Precision</span>
                    <span className="font-medium">
                      {qualityMetrics.precision}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-green-600 h-2 rounded-full"
                      style={{ width: `${qualityMetrics.precision}%` }}
                    ></div>
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Recall</span>
                    <span className="font-medium">
                      {qualityMetrics.recall}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${qualityMetrics.recall}%` }}
                    ></div>
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Consistency</span>
                    <span className="font-medium">
                      {qualityMetrics.consistency}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-purple-600 h-2 rounded-full"
                      style={{ width: `${qualityMetrics.consistency}%` }}
                    ></div>
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Inter-Annotator Agreement</span>
                    <span className="font-medium">
                      {qualityMetrics.interAnnotatorAgreement}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-orange-600 h-2 rounded-full"
                      style={{
                        width: `${qualityMetrics.interAnnotatorAgreement}%`,
                      }}
                    ></div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Quality Trends</CardTitle>
                <CardDescription>
                  Quality score evolution over time
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-48 border rounded-lg flex items-center justify-center bg-muted/10">
                  <div className="text-center">
                    <TrendingUp className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                    <p className="text-muted-foreground">Quality trend chart</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Project Performance */}
        <TabsContent value="projects" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Top Performing Projects</CardTitle>
              <CardDescription>
                Projects ranked by annotation volume and quality
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {topProjects.map((project, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-4 border rounded-lg"
                  >
                    <div className="flex-1">
                      <h4 className="font-medium">{project.name}</h4>
                      <div className="flex items-center space-x-4 mt-1">
                        <span className="text-sm text-muted-foreground">
                          {project.annotations.toLocaleString()} annotations
                        </span>
                        <span className="text-sm text-muted-foreground">
                          {project.users} users
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge
                        variant="outline"
                        className={`${
                          project.quality >= 9
                            ? "border-green-500 text-green-700"
                            : project.quality >= 8.5
                            ? "border-blue-500 text-blue-700"
                            : "border-yellow-500 text-yellow-700"
                        }`}
                      >
                        {project.quality} Quality
                      </Badge>
                      <Button variant="ghost" size="sm">
                        View Details
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* User Analytics */}
        <TabsContent value="users" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Top Contributors</CardTitle>
              <CardDescription>
                Most active users by annotation count and quality
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {userActivity.map((user, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-4 border rounded-lg"
                  >
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center text-white font-medium">
                        {user.name
                          .split(" ")
                          .map((n) => n[0])
                          .join("")}
                      </div>
                      <div>
                        <h4 className="font-medium">{user.name}</h4>
                        <p className="text-sm text-muted-foreground">
                          {user.annotations.toLocaleString()} annotations •
                          Quality: {user.quality}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge variant="outline">{user.lastActive}</Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
