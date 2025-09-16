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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  AlertTriangle,
  CheckCircle,
  Code2,
  Copy,
  ExternalLink,
  Play,
  Terminal,
  X,
} from "lucide-react";

interface CodeExample {
  id: string;
  title: string;
  description: string;
  language: "javascript" | "python" | "curl";
  code: string;
  category: "authentication" | "documents" | "annotations" | "export";
}

const codeExamples: CodeExample[] = [
  {
    id: "js-init",
    title: "Initialize SDK",
    description: "Set up the JavaScript SDK client",
    language: "javascript",
    category: "authentication",
    code: `import { AnnotationAPI } from '@annotation-app/sdk';

const client = new AnnotationAPI({
  apiKey: 'YOUR_API_KEY',
  baseURL: 'https://api.annotation-app.com'
});

// Test connection
const result = await client.ping();
console.log(result);`,
  },
  {
    id: "py-init",
    title: "Initialize Python SDK",
    description: "Set up the Python SDK client",
    language: "python",
    category: "authentication",
    code: `from annotation_app import AnnotationAPI

client = AnnotationAPI(api_key="YOUR_API_KEY")

# Test connection
result = client.ping()
print(result)`,
  },
  {
    id: "curl-auth",
    title: "cURL Authentication",
    description: "Make authenticated requests with cURL",
    language: "curl",
    category: "authentication",
    code: `# Test API connection
curl -H "Authorization: Bearer YOUR_API_KEY" \\
     https://api.annotation-app.com/api/ping

# Get API status
curl -H "Authorization: Bearer YOUR_API_KEY" \\
     https://api.annotation-app.com/api/status`,
  },
  {
    id: "js-list-docs",
    title: "List Documents",
    description: "Retrieve paginated list of documents",
    language: "javascript",
    category: "documents",
    code: `// List documents with pagination
const response = await client.documents.list({
  page: 1,
  limit: 20,
  search: "medical research"
});

if (response.success) {
  console.log(\`Found \${response.data.total} documents\`);
  response.data.items.forEach(doc => {
    console.log(\`- \${doc.title} (\${doc.annotation_count} annotations)\`);
  });
} else {
  console.error('Error:', response.error);
}`,
  },
  {
    id: "py-create-doc",
    title: "Create Document",
    description: "Create a new document for annotation",
    language: "python",
    category: "documents",
    code: `# Create a new document
document_data = {
    "title": "Medical Research Paper",
    "content": "This is the full text of the research paper...",
    "metadata": {
        "source": "PubMed",
        "journal": "Nature Medicine",
        "year": 2024
    }
}

result = client.documents.create(document_data)
if result.success:
    doc_id = result.data["id"]
    print(f"Created document: {doc_id}")
else:
    print(f"Error: {result.error}")`,
  },
  {
    id: "js-annotations",
    title: "Work with Annotations",
    description: "Create and manage annotations",
    language: "javascript",
    category: "annotations",
    code: `// Create an annotation
const annotation = {
  document_id: "doc_123",
  start: 45,
  end: 67,
  text: "cardiovascular disease",
  label: "CONDITION",
  confidence: 0.95
};

const result = await client.annotations.create(annotation);
console.log('Created annotation:', result);

// List annotations for a document
const annotations = await client.annotations.list("doc_123", {
  label: "CONDITION",
  limit: 50
});

console.log(\`Found \${annotations.data.total} annotations\`);`,
  },
  {
    id: "py-bulk-annotations",
    title: "Bulk Create Annotations",
    description: "Create multiple annotations at once",
    language: "python",
    category: "annotations",
    code: `# Bulk create annotations
annotations = [
    {
        "document_id": "doc_123",
        "start": 10,
        "end": 20,
        "text": "hypertension",
        "label": "CONDITION"
    },
    {
        "document_id": "doc_123", 
        "start": 45,
        "end": 67,
        "text": "cardiovascular disease",
        "label": "CONDITION"
    }
]

result = client.annotations.bulk_create(annotations)
if result.success:
    print(f"Created {len(result.data)} annotations")
else:
    print(f"Error: {result.error}")`,
  },
  {
    id: "js-export",
    title: "Export Annotations",
    description: "Export document annotations in various formats",
    language: "javascript",
    category: "export",
    code: `// Start export job
const exportJob = await client.documents.export("doc_123", {
  format: "conll",
  encoding_scheme: "BIO",
  include_metadata: true,
  include_statistics: true
});

if (exportJob.success) {
  const jobId = exportJob.data.export_id;
  
  // Poll for completion
  let status = await client.documents.getExportJob(jobId);
  while (status.data.status === "processing") {
    await new Promise(resolve => setTimeout(resolve, 1000));
    status = await client.documents.getExportJob(jobId);
  }
  
  if (status.data.status === "completed") {
    // Download the file
    const file = await client.documents.downloadExport(jobId);
    console.log("Export completed");
  }
}`,
  },
  {
    id: "curl-export",
    title: "Export with cURL",
    description: "Export annotations using cURL commands",
    language: "curl",
    category: "export",
    code: `# Start export job
curl -X POST \\
     -H "Authorization: Bearer YOUR_API_KEY" \\
     -H "Content-Type: application/json" \\
     -d '{
       "format": "json",
       "include_metadata": true,
       "include_statistics": true
     }' \\
     https://api.annotation-app.com/api/documents/doc_123/export

# Check export status
curl -H "Authorization: Bearer YOUR_API_KEY" \\
     https://api.annotation-app.com/api/export-jobs/exp_456

# Download export file
curl -H "Authorization: Bearer YOUR_API_KEY" \\
     https://api.annotation-app.com/api/export-jobs/exp_456/download \\
     -o annotations.json`,
  },
];

export function SDKExamples() {
  const [selectedExample, setSelectedExample] = useState<CodeExample | null>(
    null
  );
  const [activeCategory, setActiveCategory] =
    useState<string>("authentication");
  const [testResults, setTestResults] = useState<
    Record<string, { success: boolean; message: string }>
  >({});
  const [isTestDialogOpen, setIsTestDialogOpen] = useState(false);
  const [testApiKey, setTestApiKey] = useState("");
  const [testEndpoint, setTestEndpoint] = useState("ping");

  const categories = [
    { id: "authentication", name: "Authentication" },
    { id: "documents", name: "Documents" },
    { id: "annotations", name: "Annotations" },
    { id: "export", name: "Export" },
  ];

  const filteredExamples = codeExamples.filter(
    (example) => example.category === activeCategory
  );

  const handleCopyCode = (code: string) => {
    navigator.clipboard.writeText(code);
    console.log("Code copied to clipboard");
  };

  const handleRunTest = async () => {
    if (!testApiKey.trim()) return;

    setTestResults((prev) => ({
      ...prev,
      [testEndpoint]: { success: false, message: "Testing..." },
    }));

    try {
      // Simulate API test
      await new Promise((resolve) => setTimeout(resolve, 1000));

      const success = Math.random() > 0.3; // 70% success rate for demo

      setTestResults((prev) => ({
        ...prev,
        [testEndpoint]: {
          success,
          message: success
            ? "API call successful"
            : "Authentication failed - please check your API key",
        },
      }));
    } catch {
      setTestResults((prev) => ({
        ...prev,
        [testEndpoint]: {
          success: false,
          message: "Network error occurred",
        },
      }));
    }
  };

  const getLanguageIcon = (language: string) => {
    switch (language) {
      case "javascript":
        return <Code2 className="h-4 w-4 text-yellow-600" />;
      case "python":
        return <Terminal className="h-4 w-4 text-blue-600" />;
      case "curl":
        return <Terminal className="h-4 w-4 text-green-600" />;
      default:
        return <Code2 className="h-4 w-4" />;
    }
  };

  const getLanguageBadge = (language: string) => {
    const colors = {
      javascript: "bg-yellow-100 text-yellow-800",
      python: "bg-blue-100 text-blue-800",
      curl: "bg-green-100 text-green-800",
    };

    return (
      <Badge
        className={
          colors[language as keyof typeof colors] || "bg-gray-100 text-gray-800"
        }
      >
        {language.toUpperCase()}
      </Badge>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">SDK Examples & Integration</h2>
          <p className="text-muted-foreground">
            Code examples and interactive testing for API integration
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" onClick={() => setIsTestDialogOpen(true)}>
            <Play className="h-4 w-4 mr-2" />
            Test API
          </Button>
          <Button>
            <ExternalLink className="h-4 w-4 mr-2" />
            View Full Docs
          </Button>
        </div>
      </div>

      {/* Category Tabs */}
      <div className="border-b">
        <nav className="flex space-x-8">
          {categories.map((category) => (
            <button
              key={category.id}
              onClick={() => setActiveCategory(category.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeCategory === category.id
                  ? "border-primary text-primary"
                  : "border-transparent text-muted-foreground hover:text-foreground"
              }`}
            >
              {category.name}
            </button>
          ))}
        </nav>
      </div>

      {/* Code Examples Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredExamples.map((example) => (
          <Card
            key={example.id}
            className="cursor-pointer hover:shadow-md transition-shadow"
          >
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  {getLanguageIcon(example.language)}
                  <CardTitle className="text-lg">{example.title}</CardTitle>
                </div>
                {getLanguageBadge(example.language)}
              </div>
              <CardDescription>{example.description}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="bg-muted p-4 rounded-lg relative">
                <pre className="text-sm overflow-x-auto">
                  <code>{example.code.substring(0, 200)}...</code>
                </pre>
                <div className="absolute top-2 right-2 flex space-x-1">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleCopyCode(example.code)}
                  >
                    <Copy className="h-3 w-3" />
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setSelectedExample(example)}
                  >
                    <ExternalLink className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Test Results */}
      {Object.keys(testResults).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Test Results</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {Object.entries(testResults).map(([endpoint, result]) => (
                <div
                  key={endpoint}
                  className="flex items-center justify-between p-3 bg-muted rounded-lg"
                >
                  <div className="flex items-center space-x-3">
                    {result.success ? (
                      <CheckCircle className="h-5 w-5 text-green-600" />
                    ) : (
                      <AlertTriangle className="h-5 w-5 text-red-600" />
                    )}
                    <div>
                      <div className="font-medium">/{endpoint}</div>
                      <div className="text-sm text-muted-foreground">
                        {result.message}
                      </div>
                    </div>
                  </div>
                  <Badge variant={result.success ? "default" : "destructive"}>
                    {result.success ? "Success" : "Failed"}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Code Detail Dialog */}
      <Dialog
        open={!!selectedExample}
        onOpenChange={() => setSelectedExample(null)}
      >
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center space-x-2">
              {selectedExample && getLanguageIcon(selectedExample.language)}
              <span>{selectedExample?.title}</span>
              {selectedExample && getLanguageBadge(selectedExample.language)}
            </DialogTitle>
            <DialogDescription>
              {selectedExample?.description}
            </DialogDescription>
          </DialogHeader>
          {selectedExample && (
            <div className="space-y-4">
              <div className="bg-muted p-4 rounded-lg relative">
                <pre className="text-sm overflow-x-auto whitespace-pre-wrap">
                  <code>{selectedExample.code}</code>
                </pre>
                <Button
                  variant="outline"
                  size="sm"
                  className="absolute top-2 right-2"
                  onClick={() => handleCopyCode(selectedExample.code)}
                >
                  <Copy className="h-4 w-4 mr-2" />
                  Copy
                </Button>
              </div>
            </div>
          )}
          <DialogFooter>
            <Button onClick={() => setSelectedExample(null)}>Close</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* API Test Dialog */}
      <Dialog open={isTestDialogOpen} onOpenChange={setIsTestDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Test API Connection</DialogTitle>
            <DialogDescription>
              Test your API key and connection to the platform
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium">API Key</label>
              <Input
                type="password"
                value={testApiKey}
                onChange={(e) => setTestApiKey(e.target.value)}
                placeholder="Enter your API key"
              />
            </div>
            <div>
              <label className="text-sm font-medium">Test Endpoint</label>
              <Select value={testEndpoint} onValueChange={setTestEndpoint}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="ping">Ping</SelectItem>
                  <SelectItem value="status">Status</SelectItem>
                  <SelectItem value="documents">List Documents</SelectItem>
                  <SelectItem value="annotations">List Annotations</SelectItem>
                </SelectContent>
              </Select>
            </div>
            {testResults[testEndpoint] && (
              <div
                className={`p-3 rounded-lg ${
                  testResults[testEndpoint].success
                    ? "bg-green-100 text-green-800"
                    : "bg-red-100 text-red-800"
                }`}
              >
                <div className="flex items-center space-x-2">
                  {testResults[testEndpoint].success ? (
                    <CheckCircle className="h-4 w-4" />
                  ) : (
                    <X className="h-4 w-4" />
                  )}
                  <span className="text-sm">
                    {testResults[testEndpoint].message}
                  </span>
                </div>
              </div>
            )}
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setIsTestDialogOpen(false)}
            >
              Cancel
            </Button>
            <Button onClick={handleRunTest} disabled={!testApiKey.trim()}>
              <Play className="h-4 w-4 mr-2" />
              Run Test
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
