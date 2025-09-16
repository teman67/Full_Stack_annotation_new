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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Book,
  Code2,
  Key,
  Globe,
  Download,
  Copy,
  Eye,
  Trash2,
  Activity,
  Shield,
  Zap,
  Terminal,
} from "lucide-react";

interface APIKey {
  id: string;
  name: string;
  key: string;
  permissions: string[];
  createdAt: string;
  lastUsed?: string;
  requestCount: number;
  rateLimit: number;
  status: "active" | "expired" | "revoked";
}

interface APIEndpoint {
  method: "GET" | "POST" | "PUT" | "DELETE";
  path: string;
  description: string;
  authentication: boolean;
  rateLimit: string;
  parameters?: Array<{
    name: string;
    type: string;
    required: boolean;
    description: string;
  }>;
  response: {
    schema: string;
    example: string;
  };
}

const mockAPIKeys: APIKey[] = [
  {
    id: "1",
    name: "Development Key",
    key: "ak_dev_1234567890abcdef",
    permissions: ["read", "write"],
    createdAt: "2024-01-10T10:00:00Z",
    lastUsed: "2024-01-15T14:30:00Z",
    requestCount: 1247,
    rateLimit: 1000,
    status: "active",
  },
  {
    id: "2",
    name: "Production API",
    key: "ak_prod_abcdef1234567890",
    permissions: ["read"],
    createdAt: "2024-01-05T09:15:00Z",
    lastUsed: "2024-01-15T16:45:00Z",
    requestCount: 5629,
    rateLimit: 5000,
    status: "active",
  },
  {
    id: "3",
    name: "Analytics Service",
    key: "ak_analytics_9876543210fedcba",
    permissions: ["read", "analytics"],
    createdAt: "2023-12-20T11:30:00Z",
    requestCount: 892,
    rateLimit: 2000,
    status: "expired",
  },
];

const apiEndpoints: APIEndpoint[] = [
  {
    method: "GET",
    path: "/api/documents",
    description: "Retrieve list of documents",
    authentication: true,
    rateLimit: "100/hour",
    parameters: [
      {
        name: "page",
        type: "integer",
        required: false,
        description: "Page number",
      },
      {
        name: "limit",
        type: "integer",
        required: false,
        description: "Items per page",
      },
      {
        name: "search",
        type: "string",
        required: false,
        description: "Search query",
      },
    ],
    response: {
      schema: `{
  "documents": [
    {
      "id": "string",
      "title": "string",
      "created_at": "string",
      "annotation_count": "integer"
    }
  ],
  "total": "integer",
  "page": "integer",
  "pages": "integer"
}`,
      example: `{
  "documents": [
    {
      "id": "doc123",
      "title": "Medical Research Paper",
      "created_at": "2024-01-15T10:30:00Z",
      "annotation_count": 45
    }
  ],
  "total": 1,
  "page": 1,
  "pages": 1
}`,
    },
  },
  {
    method: "POST",
    path: "/api/documents/{id}/export",
    description: "Export document annotations",
    authentication: true,
    rateLimit: "10/hour",
    parameters: [
      {
        name: "id",
        type: "string",
        required: true,
        description: "Document ID",
      },
      {
        name: "format",
        type: "string",
        required: true,
        description: "Export format (json, conll, csv)",
      },
      {
        name: "options",
        type: "object",
        required: false,
        description: "Export options",
      },
    ],
    response: {
      schema: `{
  "export_id": "string",
  "status": "string",
  "download_url": "string"
}`,
      example: `{
  "export_id": "exp_123456",
  "status": "processing",
  "download_url": null
}`,
    },
  },
  {
    method: "GET",
    path: "/api/annotations",
    description: "Retrieve annotations for a document",
    authentication: true,
    rateLimit: "200/hour",
    parameters: [
      {
        name: "document_id",
        type: "string",
        required: true,
        description: "Document ID",
      },
      {
        name: "label",
        type: "string",
        required: false,
        description: "Filter by label",
      },
    ],
    response: {
      schema: `{
  "annotations": [
    {
      "id": "string",
      "start": "integer",
      "end": "integer",
      "text": "string",
      "label": "string",
      "confidence": "number"
    }
  ]
}`,
      example: `{
  "annotations": [
    {
      "id": "ann_123",
      "start": 45,
      "end": 67,
      "text": "cardiovascular disease",
      "label": "CONDITION",
      "confidence": 0.95
    }
  ]
}`,
    },
  },
];

export function APIDocumentation() {
  const [selectedEndpoint, setSelectedEndpoint] = useState<APIEndpoint | null>(
    null
  );
  const [isKeyDialogOpen, setIsKeyDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [selectedKey, setSelectedKey] = useState<APIKey | null>(null);
  const [newKeyName, setNewKeyName] = useState("");
  const [newKeyPermissions, setNewKeyPermissions] = useState<string[]>([]);
  const [activeTab, setActiveTab] = useState("overview");

  const handleCreateAPIKey = () => {
    if (!newKeyName.trim() || newKeyPermissions.length === 0) return;

    console.log("Creating API key:", {
      name: newKeyName,
      permissions: newKeyPermissions,
    });

    setIsKeyDialogOpen(false);
    setNewKeyName("");
    setNewKeyPermissions([]);
  };

  const handleDeleteAPIKey = () => {
    if (selectedKey) {
      console.log("Deleting API key:", selectedKey.id);
      setIsDeleteDialogOpen(false);
      setSelectedKey(null);
    }
  };

  const handleCopyKey = (key: string) => {
    navigator.clipboard.writeText(key);
    console.log("Copied API key to clipboard");
  };

  const getStatusBadge = (status: APIKey["status"]) => {
    switch (status) {
      case "active":
        return <Badge className="bg-green-100 text-green-800">Active</Badge>;
      case "expired":
        return <Badge className="bg-yellow-100 text-yellow-800">Expired</Badge>;
      case "revoked":
        return <Badge className="bg-red-100 text-red-800">Revoked</Badge>;
      default:
        return <Badge variant="outline">Unknown</Badge>;
    }
  };

  const getMethodBadge = (method: APIEndpoint["method"]) => {
    const colors = {
      GET: "bg-blue-100 text-blue-800",
      POST: "bg-green-100 text-green-800",
      PUT: "bg-yellow-100 text-yellow-800",
      DELETE: "bg-red-100 text-red-800",
    };

    return <Badge className={colors[method]}>{method}</Badge>;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">
            API Documentation & Integration
          </h2>
          <p className="text-muted-foreground">
            API reference, SDK downloads, and key management
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Download SDK
          </Button>
          <Button onClick={() => setIsKeyDialogOpen(true)}>
            <Key className="h-4 w-4 mr-2" />
            New API Key
          </Button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <Globe className="h-8 w-8 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">
                  API Endpoints
                </p>
                <p className="text-2xl font-bold">{apiEndpoints.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <Key className="h-8 w-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">
                  Active Keys
                </p>
                <p className="text-2xl font-bold">
                  {mockAPIKeys.filter((k) => k.status === "active").length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <Activity className="h-8 w-8 text-purple-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">
                  Total Requests
                </p>
                <p className="text-2xl font-bold">
                  {mockAPIKeys
                    .reduce((sum, key) => sum + key.requestCount, 0)
                    .toLocaleString()}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <Zap className="h-8 w-8 text-orange-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">
                  Rate Limit
                </p>
                <p className="text-2xl font-bold">5K/hr</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <Tabs
        value={activeTab}
        onValueChange={setActiveTab}
        className="space-y-6"
      >
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="endpoints">API Reference</TabsTrigger>
          <TabsTrigger value="keys">API Keys</TabsTrigger>
          <TabsTrigger value="sdks">SDKs & Examples</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Book className="h-5 w-5 mr-2" />
                  Quick Start Guide
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <h4 className="font-medium">1. Get Your API Key</h4>
                  <p className="text-sm text-muted-foreground">
                    Create an API key from the API Keys tab to authenticate your
                    requests.
                  </p>
                </div>
                <div className="space-y-2">
                  <h4 className="font-medium">2. Make Your First Request</h4>
                  <div className="bg-muted p-3 rounded-lg">
                    <code className="text-sm">
                      curl -H &quot;Authorization: Bearer YOUR_API_KEY&quot;{" "}
                      <br />
                      https://api.annotation-app.com/api/documents
                    </code>
                  </div>
                </div>
                <div className="space-y-2">
                  <h4 className="font-medium">3. Explore the API</h4>
                  <p className="text-sm text-muted-foreground">
                    Check out the API Reference tab for detailed endpoint
                    documentation.
                  </p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Shield className="h-5 w-5 mr-2" />
                  Authentication
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm text-muted-foreground">
                  All API requests require authentication using Bearer tokens.
                  Include your API key in the Authorization header:
                </p>
                <div className="bg-muted p-3 rounded-lg">
                  <code className="text-sm">
                    Authorization: Bearer YOUR_API_KEY
                  </code>
                </div>
                <div className="space-y-2">
                  <h4 className="font-medium">Rate Limits</h4>
                  <p className="text-sm text-muted-foreground">
                    API requests are rate limited per key. Check your usage in
                    the API Keys section.
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* API Reference Tab */}
        <TabsContent value="endpoints" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>API Endpoints</CardTitle>
              <CardDescription>
                Complete reference for all available API endpoints
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {apiEndpoints.map((endpoint, index) => (
                  <div key={index} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-3">
                        {getMethodBadge(endpoint.method)}
                        <code className="text-sm font-mono">
                          {endpoint.path}
                        </code>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge variant="outline">{endpoint.rateLimit}</Badge>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setSelectedEndpoint(endpoint)}
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {endpoint.description}
                    </p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* API Keys Tab */}
        <TabsContent value="keys" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>API Key Management</CardTitle>
              <CardDescription>
                Create and manage API keys for accessing the platform
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Permissions</TableHead>
                    <TableHead>Usage</TableHead>
                    <TableHead>Last Used</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {mockAPIKeys.map((apiKey) => (
                    <TableRow key={apiKey.id}>
                      <TableCell>
                        <div>
                          <div className="font-medium">{apiKey.name}</div>
                          <div className="text-sm text-muted-foreground font-mono">
                            {apiKey.key.substring(0, 20)}...
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>{getStatusBadge(apiKey.status)}</TableCell>
                      <TableCell>
                        <div className="flex flex-wrap gap-1">
                          {apiKey.permissions.map((permission) => (
                            <Badge
                              key={permission}
                              variant="outline"
                              className="text-xs"
                            >
                              {permission}
                            </Badge>
                          ))}
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="text-sm">
                          {apiKey.requestCount.toLocaleString()} /{" "}
                          {apiKey.rateLimit.toLocaleString()}
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="text-sm">
                          {apiKey.lastUsed
                            ? formatDate(apiKey.lastUsed)
                            : "Never"}
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center space-x-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleCopyKey(apiKey.key)}
                          >
                            <Copy className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setSelectedKey(apiKey);
                              setIsDeleteDialogOpen(true);
                            }}
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

        {/* SDKs Tab */}
        <TabsContent value="sdks" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Code2 className="h-5 w-5 mr-2" />
                  JavaScript SDK
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="bg-muted p-3 rounded-lg">
                  <code className="text-sm">
                    npm install @annotation-app/sdk
                  </code>
                </div>
                <div className="bg-muted p-3 rounded-lg">
                  <pre className="text-sm">
                    {`import { AnnotationAPI } from '@annotation-app/sdk';

const client = new AnnotationAPI({
  apiKey: 'YOUR_API_KEY'
});

const documents = await client.documents.list();
console.log(documents);`}
                  </pre>
                </div>
                <Button>
                  <Download className="h-4 w-4 mr-2" />
                  Download JavaScript SDK
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Terminal className="h-5 w-5 mr-2" />
                  Python SDK
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="bg-muted p-3 rounded-lg">
                  <code className="text-sm">
                    pip install annotation-app-sdk
                  </code>
                </div>
                <div className="bg-muted p-3 rounded-lg">
                  <pre className="text-sm">
                    {`from annotation_app import AnnotationAPI

client = AnnotationAPI(api_key="YOUR_API_KEY")

documents = client.documents.list()
print(documents)`}
                  </pre>
                </div>
                <Button>
                  <Download className="h-4 w-4 mr-2" />
                  Download Python SDK
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      {/* Create API Key Dialog */}
      <Dialog open={isKeyDialogOpen} onOpenChange={setIsKeyDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create New API Key</DialogTitle>
            <DialogDescription>
              Generate a new API key for accessing the platform programmatically
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium">Key Name</label>
              <Input
                value={newKeyName}
                onChange={(e) => setNewKeyName(e.target.value)}
                placeholder="Enter a descriptive name..."
              />
            </div>
            <div>
              <label className="text-sm font-medium">Permissions</label>
              <div className="flex flex-wrap gap-2 mt-2">
                {["read", "write", "analytics", "export"].map((permission) => (
                  <Button
                    key={permission}
                    variant={
                      newKeyPermissions.includes(permission)
                        ? "default"
                        : "outline"
                    }
                    size="sm"
                    onClick={() => {
                      setNewKeyPermissions((prev) =>
                        prev.includes(permission)
                          ? prev.filter((p) => p !== permission)
                          : [...prev, permission]
                      );
                    }}
                  >
                    {permission}
                  </Button>
                ))}
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsKeyDialogOpen(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleCreateAPIKey}
              disabled={!newKeyName.trim() || newKeyPermissions.length === 0}
            >
              Create API Key
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete API Key Dialog */}
      <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete API Key</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this API key? This action cannot
              be undone.
            </DialogDescription>
          </DialogHeader>
          {selectedKey && (
            <div className="bg-muted p-3 rounded-lg">
              <p className="font-medium">{selectedKey.name}</p>
              <p className="text-sm text-muted-foreground font-mono">
                {selectedKey.key.substring(0, 20)}...
              </p>
            </div>
          )}
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setIsDeleteDialogOpen(false)}
            >
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleDeleteAPIKey}>
              Delete API Key
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Endpoint Detail Dialog */}
      <Dialog
        open={!!selectedEndpoint}
        onOpenChange={() => setSelectedEndpoint(null)}
      >
        <DialogContent className="max-w-4xl">
          <DialogHeader>
            <DialogTitle className="flex items-center space-x-2">
              {selectedEndpoint && getMethodBadge(selectedEndpoint.method)}
              <code>{selectedEndpoint?.path}</code>
            </DialogTitle>
            <DialogDescription>
              {selectedEndpoint?.description}
            </DialogDescription>
          </DialogHeader>
          {selectedEndpoint && (
            <div className="space-y-4">
              {selectedEndpoint.parameters && (
                <div>
                  <h4 className="font-medium mb-2">Parameters</h4>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Name</TableHead>
                        <TableHead>Type</TableHead>
                        <TableHead>Required</TableHead>
                        <TableHead>Description</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {selectedEndpoint.parameters.map((param) => (
                        <TableRow key={param.name}>
                          <TableCell>
                            <code>{param.name}</code>
                          </TableCell>
                          <TableCell>{param.type}</TableCell>
                          <TableCell>{param.required ? "Yes" : "No"}</TableCell>
                          <TableCell>{param.description}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              )}

              <div>
                <h4 className="font-medium mb-2">Response Schema</h4>
                <div className="bg-muted p-3 rounded-lg">
                  <pre className="text-sm">
                    {selectedEndpoint.response.schema}
                  </pre>
                </div>
              </div>

              <div>
                <h4 className="font-medium mb-2">Example Response</h4>
                <div className="bg-muted p-3 rounded-lg">
                  <pre className="text-sm">
                    {selectedEndpoint.response.example}
                  </pre>
                </div>
              </div>
            </div>
          )}
          <DialogFooter>
            <Button onClick={() => setSelectedEndpoint(null)}>Close</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
