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
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import {
  Database,
  Download,
  Upload,
  RefreshCw,
  CheckCircle,
  Settings,
  Trash2,
  Clock,
  Shield,
  Archive,
} from "lucide-react";

interface BackupRecord {
  id: string;
  name: string;
  type: "full" | "incremental" | "configuration";
  size: string;
  createdAt: string;
  status: "completed" | "failed" | "in_progress";
}

interface SystemConfig {
  key: string;
  value: string;
  description: string;
  category: "security" | "performance" | "features" | "integrations";
}

const mockBackups: BackupRecord[] = [
  {
    id: "1",
    name: "Full System Backup - 2024-01-15",
    type: "full",
    size: "2.4 GB",
    createdAt: "2024-01-15T10:30:00Z",
    status: "completed",
  },
  {
    id: "2",
    name: "Database Backup - 2024-01-14",
    type: "incremental",
    size: "145 MB",
    createdAt: "2024-01-14T22:00:00Z",
    status: "completed",
  },
  {
    id: "3",
    name: "Configuration Backup - 2024-01-13",
    type: "configuration",
    size: "2.1 MB",
    createdAt: "2024-01-13T18:15:00Z",
    status: "completed",
  },
];

const mockSystemConfig: SystemConfig[] = [
  {
    key: "max_file_upload_size",
    value: "50MB",
    description: "Maximum file size allowed for uploads",
    category: "performance",
  },
  {
    key: "session_timeout",
    value: "24h",
    description: "User session timeout duration",
    category: "security",
  },
  {
    key: "auto_save_interval",
    value: "30s",
    description: "Automatic save interval for annotations",
    category: "features",
  },
  {
    key: "email_notifications",
    value: "enabled",
    description: "Email notification system status",
    category: "integrations",
  },
];

export function SystemManagement() {
  const [isBackupDialogOpen, setIsBackupDialogOpen] = useState(false);
  const [isConfigDialogOpen, setIsConfigDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [selectedBackup, setSelectedBackup] = useState<BackupRecord | null>(
    null
  );
  const [selectedConfig, setSelectedConfig] = useState<SystemConfig | null>(
    null
  );
  const [backupType, setBackupType] = useState<
    "full" | "incremental" | "configuration"
  >("full");
  const [backupName, setBackupName] = useState("");
  const [isCreatingBackup, setIsCreatingBackup] = useState(false);

  const handleCreateBackup = async () => {
    setIsCreatingBackup(true);
    console.log("Creating backup:", { type: backupType, name: backupName });

    // Simulate backup creation
    setTimeout(() => {
      setIsCreatingBackup(false);
      setIsBackupDialogOpen(false);
      setBackupName("");
      setBackupType("full");
    }, 3000);
  };

  const handleDeleteBackup = async () => {
    if (selectedBackup) {
      console.log("Deleting backup:", selectedBackup.id);
      setIsDeleteDialogOpen(false);
      setSelectedBackup(null);
    }
  };

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const handleUpdateConfig = (config: SystemConfig, newValue: string) => {
    console.log("Updating config:", config.key, "to", newValue);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const getStatusBadge = (status: BackupRecord["status"]) => {
    switch (status) {
      case "completed":
        return <Badge className="bg-green-100 text-green-800">Completed</Badge>;
      case "failed":
        return <Badge className="bg-red-100 text-red-800">Failed</Badge>;
      case "in_progress":
        return <Badge className="bg-blue-100 text-blue-800">In Progress</Badge>;
      default:
        return <Badge variant="outline">Unknown</Badge>;
    }
  };

  const getTypeBadge = (type: BackupRecord["type"]) => {
    switch (type) {
      case "full":
        return <Badge className="bg-purple-100 text-purple-800">Full</Badge>;
      case "incremental":
        return <Badge className="bg-blue-100 text-blue-800">Incremental</Badge>;
      case "configuration":
        return <Badge className="bg-orange-100 text-orange-800">Config</Badge>;
      default:
        return <Badge variant="outline">Unknown</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold">System Management</h2>
        <p className="text-muted-foreground">
          Backup management and system configuration
        </p>
      </div>

      {/* System Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <Database className="h-8 w-8 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">
                  Database Status
                </p>
                <p className="text-2xl font-bold">Healthy</p>
                <div className="flex items-center text-xs text-green-600">
                  <CheckCircle className="h-3 w-3 mr-1" />
                  All systems operational
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <Archive className="h-8 w-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">
                  Last Backup
                </p>
                <p className="text-2xl font-bold">2 hours ago</p>
                <div className="flex items-center text-xs text-green-600">
                  <CheckCircle className="h-3 w-3 mr-1" />
                  Backup successful
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <Shield className="h-8 w-8 text-purple-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">
                  Security Status
                </p>
                <p className="text-2xl font-bold">Secure</p>
                <div className="flex items-center text-xs text-green-600">
                  <CheckCircle className="h-3 w-3 mr-1" />
                  All checks passed
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Backup Management */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center">
                <Archive className="h-5 w-5 mr-2" />
                Backup Management
              </CardTitle>
              <CardDescription>
                Create, manage, and restore system backups
              </CardDescription>
            </div>
            <Button onClick={() => setIsBackupDialogOpen(true)}>
              <Upload className="h-4 w-4 mr-2" />
              Create Backup
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {mockBackups.map((backup) => (
              <div
                key={backup.id}
                className="flex items-center justify-between p-4 border rounded-lg"
              >
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-1">
                    <h4 className="font-medium">{backup.name}</h4>
                    {getTypeBadge(backup.type)}
                    {getStatusBadge(backup.status)}
                  </div>
                  <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                    <span>Size: {backup.size}</span>
                    <span className="flex items-center">
                      <Clock className="h-3 w-3 mr-1" />
                      {formatDate(backup.createdAt)}
                    </span>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Button variant="outline" size="sm">
                    <Download className="h-4 w-4 mr-1" />
                    Download
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setSelectedBackup(backup);
                      setIsDeleteDialogOpen(true);
                    }}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* System Configuration */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Settings className="h-5 w-5 mr-2" />
            System Configuration
          </CardTitle>
          <CardDescription>
            Manage system settings and configuration parameters
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {mockSystemConfig.map((config) => (
              <div key={config.key} className="p-4 border rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <h4 className="font-medium">{config.key}</h4>
                    <Badge variant="outline" className="text-xs">
                      {config.category}
                    </Badge>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setSelectedConfig(config);
                      setIsConfigDialogOpen(true);
                    }}
                  >
                    Edit
                  </Button>
                </div>
                <p className="text-sm text-muted-foreground mb-2">
                  {config.description}
                </p>
                <p className="text-sm font-mono bg-muted px-2 py-1 rounded">
                  {config.value}
                </p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Create Backup Dialog */}
      <Dialog open={isBackupDialogOpen} onOpenChange={setIsBackupDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create System Backup</DialogTitle>
            <DialogDescription>
              Create a new backup of your system data and configurations.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium">Backup Name</label>
              <Input
                value={backupName}
                onChange={(e) => setBackupName(e.target.value)}
                placeholder="Enter backup name..."
              />
            </div>
            <div>
              <label className="text-sm font-medium">Backup Type</label>
              <Select
                value={backupType}
                onValueChange={(
                  value: "full" | "incremental" | "configuration"
                ) => setBackupType(value)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="full">Full Backup</SelectItem>
                  <SelectItem value="incremental">
                    Incremental Backup
                  </SelectItem>
                  <SelectItem value="configuration">
                    Configuration Only
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setIsBackupDialogOpen(false)}
            >
              Cancel
            </Button>
            <Button
              onClick={handleCreateBackup}
              disabled={isCreatingBackup || !backupName}
            >
              {isCreatingBackup && (
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
              )}
              Create Backup
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Configuration Dialog */}
      <Dialog open={isConfigDialogOpen} onOpenChange={setIsConfigDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Configuration</DialogTitle>
            <DialogDescription>
              Modify system configuration parameter.
            </DialogDescription>
          </DialogHeader>
          {selectedConfig && (
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium">Parameter</label>
                <Input value={selectedConfig.key} disabled />
              </div>
              <div>
                <label className="text-sm font-medium">Description</label>
                <Textarea value={selectedConfig.description} disabled />
              </div>
              <div>
                <label className="text-sm font-medium">Value</label>
                <Input defaultValue={selectedConfig.value} />
              </div>
            </div>
          )}
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setIsConfigDialogOpen(false)}
            >
              Cancel
            </Button>
            <Button onClick={() => setIsConfigDialogOpen(false)}>
              Save Changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Backup Confirmation */}
      <AlertDialog
        open={isDeleteDialogOpen}
        onOpenChange={setIsDeleteDialogOpen}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Backup</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete this backup? This action cannot be
              undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={() => setIsDeleteDialogOpen(false)}>
              Cancel
            </AlertDialogCancel>
            <AlertDialogAction onClick={handleDeleteBackup}>
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
