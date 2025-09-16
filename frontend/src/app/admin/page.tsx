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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
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
  Users,
  BarChart3,
  Shield,
  Activity,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Clock,
  FileText,
  Database,
  Bell,
  Mail,
  UserPlus,
  UserMinus,
  Crown,
  Eye,
  Edit,
  Trash2,
  Download,
  Upload,
} from "lucide-react";

import { AnalyticsDashboard } from "@/components/analytics/AnalyticsDashboard";
import { APIDocumentation } from "@/components/api/APIDocumentation";
import { SDKExamples } from "@/components/api/SDKExamples";

// Mock data for admin dashboard
const mockStats = {
  totalUsers: 1247,
  activeUsers: 892,
  totalProjects: 156,
  totalAnnotations: 45692,
  storageUsed: "12.4 GB",
  apiCalls: 125430,
};

interface User {
  id: string;
  name: string;
  email: string;
  role: "admin" | "user";
  status: "active" | "inactive";
  lastLogin: string;
  projects: number;
  annotations: number;
}

const mockUsers: User[] = [
  {
    id: "1",
    name: "Dr. Sarah Johnson",
    email: "sarah.johnson@university.edu",
    role: "admin",
    status: "active",
    lastLogin: "2024-01-15T10:30:00Z",
    projects: 12,
    annotations: 1523,
  },
  {
    id: "2",
    name: "Prof. Michael Chen",
    email: "m.chen@research.org",
    role: "user",
    status: "active",
    lastLogin: "2024-01-14T16:45:00Z",
    projects: 8,
    annotations: 2104,
  },
  {
    id: "3",
    name: "Dr. Emily Rodriguez",
    email: "e.rodriguez@lab.edu",
    role: "user",
    status: "inactive",
    lastLogin: "2024-01-10T09:15:00Z",
    projects: 3,
    annotations: 456,
  },
  {
    id: "4",
    name: "Alex Thompson",
    email: "alex.t@biotech.com",
    role: "user",
    status: "active",
    lastLogin: "2024-01-15T14:20:00Z",
    projects: 5,
    annotations: 789,
  },
];

const mockAuditLogs = [
  {
    id: "1",
    action: "User promoted to admin",
    user: "admin@system.com",
    target: "sarah.johnson@university.edu",
    timestamp: "2024-01-15T10:30:00Z",
    details: "Promoted to admin role",
  },
  {
    id: "2",
    action: "Project deleted",
    user: "admin@system.com",
    target: "Medical Research Project #45",
    timestamp: "2024-01-14T16:45:00Z",
    details: "Project and all annotations removed",
  },
  {
    id: "3",
    action: "Bulk user import",
    user: "admin@system.com",
    target: "25 new users",
    timestamp: "2024-01-14T14:20:00Z",
    details: "Imported from CSV file",
  },
];

export default function AdminDashboardPage() {
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [isUserDialogOpen, setIsUserDialogOpen] = useState(false);
  const [isAnnouncementDialogOpen, setIsAnnouncementDialogOpen] =
    useState(false);
  const [userAction, setUserAction] = useState<
    "view" | "edit" | "delete" | null
  >(null);
  const [announcement, setAnnouncement] = useState({
    title: "",
    content: "",
    type: "info" as "info" | "warning" | "success",
  });

  const handleUserAction = (user: User, action: "view" | "edit" | "delete") => {
    setSelectedUser(user);
    setUserAction(action);
    setIsUserDialogOpen(true);
  };

  const handlePromoteUser = (userId: string) => {
    console.log("Promoting user:", userId);
    // Implementation would update user role
  };

  const handleDemoteUser = (userId: string) => {
    console.log("Demoting user:", userId);
    // Implementation would update user role
  };

  const handleCreateAnnouncement = () => {
    console.log("Creating announcement:", announcement);
    setIsAnnouncementDialogOpen(false);
    setAnnouncement({ title: "", content: "", type: "info" });
  };

  return (
    <AppLayout>
      <div className="container mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold flex items-center">
            <Crown className="h-8 w-8 mr-3 text-yellow-600" />
            Admin Dashboard
          </h1>
          <p className="text-muted-foreground mt-2">
            Platform overview, user management, and system administration
          </p>
        </div>

        {/* Overview Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <Users className="h-8 w-8 text-blue-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-muted-foreground">
                    Total Users
                  </p>
                  <p className="text-2xl font-bold">
                    {mockStats.totalUsers.toLocaleString()}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <Activity className="h-8 w-8 text-green-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-muted-foreground">
                    Active Users
                  </p>
                  <p className="text-2xl font-bold">
                    {mockStats.activeUsers.toLocaleString()}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <FileText className="h-8 w-8 text-purple-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-muted-foreground">
                    Projects
                  </p>
                  <p className="text-2xl font-bold">
                    {mockStats.totalProjects.toLocaleString()}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <BarChart3 className="h-8 w-8 text-orange-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-muted-foreground">
                    Annotations
                  </p>
                  <p className="text-2xl font-bold">
                    {mockStats.totalAnnotations.toLocaleString()}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <Database className="h-8 w-8 text-red-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-muted-foreground">
                    Storage
                  </p>
                  <p className="text-2xl font-bold">{mockStats.storageUsed}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <TrendingUp className="h-8 w-8 text-indigo-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-muted-foreground">
                    API Calls
                  </p>
                  <p className="text-2xl font-bold">
                    {mockStats.apiCalls.toLocaleString()}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Admin Tabs */}
        <Tabs defaultValue="users" className="space-y-6">
          <TabsList className="grid w-full grid-cols-6">
            <TabsTrigger value="users">User Management</TabsTrigger>
            <TabsTrigger value="system">System Health</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
            <TabsTrigger value="api">API & SDK</TabsTrigger>
            <TabsTrigger value="announcements">Announcements</TabsTrigger>
            <TabsTrigger value="audit">Audit Logs</TabsTrigger>
          </TabsList>

          {/* User Management Tab */}
          <TabsContent value="users" className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="flex items-center">
                      <Users className="h-5 w-5 mr-2" />
                      User Management
                    </CardTitle>
                    <CardDescription>
                      Manage users, roles, and permissions across the platform
                    </CardDescription>
                  </div>
                  <div className="flex space-x-2">
                    <Button variant="outline" size="sm">
                      <Upload className="h-4 w-4 mr-2" />
                      Import Users
                    </Button>
                    <Button variant="outline" size="sm">
                      <Download className="h-4 w-4 mr-2" />
                      Export Users
                    </Button>
                    <Button size="sm">
                      <UserPlus className="h-4 w-4 mr-2" />
                      Add User
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>User</TableHead>
                      <TableHead>Role</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Last Login</TableHead>
                      <TableHead>Projects</TableHead>
                      <TableHead>Annotations</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {mockUsers.map((user) => (
                      <TableRow key={user.id}>
                        <TableCell>
                          <div>
                            <div className="font-medium">{user.name}</div>
                            <div className="text-sm text-muted-foreground">
                              {user.email}
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge
                            variant={
                              user.role === "admin" ? "default" : "secondary"
                            }
                          >
                            {user.role}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge
                            variant={
                              user.status === "active" ? "default" : "secondary"
                            }
                            className={
                              user.status === "active"
                                ? "bg-green-100 text-green-800"
                                : ""
                            }
                          >
                            {user.status}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-sm">
                          {new Date(user.lastLogin).toLocaleDateString()}
                        </TableCell>
                        <TableCell>{user.projects}</TableCell>
                        <TableCell>
                          {user.annotations.toLocaleString()}
                        </TableCell>
                        <TableCell>
                          <div className="flex space-x-1">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleUserAction(user, "view")}
                            >
                              <Eye className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleUserAction(user, "edit")}
                            >
                              <Edit className="h-4 w-4" />
                            </Button>
                            {user.role === "user" && (
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handlePromoteUser(user.id)}
                              >
                                <Crown className="h-4 w-4" />
                              </Button>
                            )}
                            {user.role === "admin" && (
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleDemoteUser(user.id)}
                              >
                                <UserMinus className="h-4 w-4" />
                              </Button>
                            )}
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleUserAction(user, "delete")}
                              className="text-red-600 hover:text-red-700"
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          {/* System Health Tab */}
          <TabsContent value="system" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Activity className="h-5 w-5 mr-2" />
                    System Status
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span>Database Connection</span>
                    <Badge className="bg-green-100 text-green-800">
                      <CheckCircle className="h-3 w-3 mr-1" />
                      Healthy
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>API Response Time</span>
                    <Badge className="bg-green-100 text-green-800">
                      <Clock className="h-3 w-3 mr-1" />
                      124ms
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Memory Usage</span>
                    <Badge className="bg-yellow-100 text-yellow-800">
                      <AlertTriangle className="h-3 w-3 mr-1" />
                      78%
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Storage Usage</span>
                    <Badge className="bg-green-100 text-green-800">
                      <Database className="h-3 w-3 mr-1" />
                      45%
                    </Badge>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Shield className="h-5 w-5 mr-2" />
                    Security Monitor
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span>Failed Login Attempts (24h)</span>
                    <Badge variant="outline">23</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Active Sessions</span>
                    <Badge variant="outline">156</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>SSL Certificate</span>
                    <Badge className="bg-green-100 text-green-800">Valid</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Rate Limit Violations</span>
                    <Badge variant="outline">2</Badge>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Analytics Tab */}
          <TabsContent value="analytics" className="space-y-6">
            <AnalyticsDashboard />
          </TabsContent>

          {/* API & SDK Tab */}
          <TabsContent value="api" className="space-y-6">
            <Tabs defaultValue="documentation" className="space-y-6">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="documentation">
                  API Documentation
                </TabsTrigger>
                <TabsTrigger value="examples">SDK Examples</TabsTrigger>
              </TabsList>

              <TabsContent value="documentation">
                <APIDocumentation />
              </TabsContent>

              <TabsContent value="examples">
                <SDKExamples />
              </TabsContent>
            </Tabs>
          </TabsContent>

          {/* Announcements Tab */}
          <TabsContent value="announcements" className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="flex items-center">
                      <Bell className="h-5 w-5 mr-2" />
                      Platform Announcements
                    </CardTitle>
                    <CardDescription>
                      Create and manage platform-wide announcements
                    </CardDescription>
                  </div>
                  <Button onClick={() => setIsAnnouncementDialogOpen(true)}>
                    <Mail className="h-4 w-4 mr-2" />
                    New Announcement
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8 text-muted-foreground">
                  No announcements yet. Create your first announcement to
                  communicate with users.
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Audit Logs Tab */}
          <TabsContent value="audit" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <FileText className="h-5 w-5 mr-2" />
                  Audit Logs
                </CardTitle>
                <CardDescription>
                  Track admin actions and system changes
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Action</TableHead>
                      <TableHead>User</TableHead>
                      <TableHead>Target</TableHead>
                      <TableHead>Timestamp</TableHead>
                      <TableHead>Details</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {mockAuditLogs.map((log) => (
                      <TableRow key={log.id}>
                        <TableCell className="font-medium">
                          {log.action}
                        </TableCell>
                        <TableCell>{log.user}</TableCell>
                        <TableCell>{log.target}</TableCell>
                        <TableCell>
                          {new Date(log.timestamp).toLocaleString()}
                        </TableCell>
                        <TableCell className="text-sm text-muted-foreground">
                          {log.details}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* User Management Dialog */}
        <Dialog open={isUserDialogOpen} onOpenChange={setIsUserDialogOpen}>
          <DialogContent className="sm:max-w-[600px]">
            <DialogHeader>
              <DialogTitle>
                {userAction === "view" && "View User Details"}
                {userAction === "edit" && "Edit User"}
                {userAction === "delete" && "Delete User"}
              </DialogTitle>
              <DialogDescription>
                {selectedUser &&
                  userAction === "view" &&
                  `Viewing details for ${selectedUser.name}`}
                {selectedUser &&
                  userAction === "edit" &&
                  `Edit user information for ${selectedUser.name}`}
                {selectedUser &&
                  userAction === "delete" &&
                  `Are you sure you want to delete ${selectedUser.name}?`}
              </DialogDescription>
            </DialogHeader>

            {selectedUser && userAction !== "delete" && (
              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium">Name</label>
                    <Input
                      value={selectedUser.name}
                      disabled={userAction === "view"}
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium">Email</label>
                    <Input
                      value={selectedUser.email}
                      disabled={userAction === "view"}
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium">Role</label>
                    <Select
                      value={selectedUser.role}
                      disabled={userAction === "view"}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="user">User</SelectItem>
                        <SelectItem value="admin">Admin</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <label className="text-sm font-medium">Status</label>
                    <Select
                      value={selectedUser.status}
                      disabled={userAction === "view"}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="active">Active</SelectItem>
                        <SelectItem value="inactive">Inactive</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </div>
            )}

            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setIsUserDialogOpen(false)}
              >
                {userAction === "delete" ? "Cancel" : "Close"}
              </Button>
              {userAction === "edit" && <Button>Save Changes</Button>}
              {userAction === "delete" && (
                <Button variant="destructive">Delete User</Button>
              )}
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Announcement Dialog */}
        <Dialog
          open={isAnnouncementDialogOpen}
          onOpenChange={setIsAnnouncementDialogOpen}
        >
          <DialogContent className="sm:max-w-[600px]">
            <DialogHeader>
              <DialogTitle>Create Platform Announcement</DialogTitle>
              <DialogDescription>
                Send a message to all platform users
              </DialogDescription>
            </DialogHeader>

            <div className="grid gap-4 py-4">
              <div>
                <label className="text-sm font-medium">Title</label>
                <Input
                  value={announcement.title}
                  onChange={(e) =>
                    setAnnouncement((prev) => ({
                      ...prev,
                      title: e.target.value,
                    }))
                  }
                  placeholder="Announcement title"
                />
              </div>
              <div>
                <label className="text-sm font-medium">Type</label>
                <Select
                  value={announcement.type}
                  onValueChange={(value: "info" | "warning" | "success") =>
                    setAnnouncement((prev) => ({ ...prev, type: value }))
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="info">Information</SelectItem>
                    <SelectItem value="warning">Warning</SelectItem>
                    <SelectItem value="success">Success</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="text-sm font-medium">Content</label>
                <Textarea
                  value={announcement.content}
                  onChange={(e) =>
                    setAnnouncement((prev) => ({
                      ...prev,
                      content: e.target.value,
                    }))
                  }
                  placeholder="Announcement content..."
                  rows={4}
                />
              </div>
            </div>

            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setIsAnnouncementDialogOpen(false)}
              >
                Cancel
              </Button>
              <Button onClick={handleCreateAnnouncement}>
                Send Announcement
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </AppLayout>
  );
}
