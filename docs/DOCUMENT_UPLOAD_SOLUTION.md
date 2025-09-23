# Document Upload Solution

This document explains how we implemented a two-step document upload process for the Full Stack Annotation application and fixed UUID issues with document uploads.

## Problem Statement

The original document upload process had the following issues:

1. The document was automatically uploaded as soon as a file was selected, without giving users a chance to review or add metadata
2. There was no clear indication of upload status or progress
3. Error handling was limited, without providing clear feedback to users
4. The UI didn't display the selected file before upload

## Solution Overview

We implemented a two-step document upload process similar to the tagset CSV upload solution:

1. **Step 1**: User selects a file (drag & drop or file browser)
2. **Step 2**: User adds metadata (name, description, tags) and clicks "Upload" button

This approach gives users more control over the upload process and provides better visual feedback.

## Implementation Details

### 1. Frontend State Management

Added new state variables to track the document upload process:

```typescript
const [selectedFile, setSelectedFile] = useState<File | null>(null);
const [isUploading, setIsUploading] = useState(false);
const [uploadError, setUploadError] = useState("");
```

Added an effect to reset form state when the dialog closes:

```typescript
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
```

### 2. File Selection Handlers

Updated the file selection handlers to set the selected file state:

```typescript
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
```

### 3. Upload Dialog UI

Updated the upload dialog UI to show the selected file and provide better feedback:

```jsx
{!selectedFile ? (
  // Original file input UI
  <>
    <Upload className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
    <p className="text-sm font-medium mb-1">
      Drag and drop your file here, or click to browse
    </p>
    {/* ... */}
  </>
) : (
  // Selected file display
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
        const fileInput = document.getElementById('file-upload') as HTMLInputElement;
        if (fileInput) fileInput.value = '';
      }}
    >
      Change File
    </Button>
  </div>
)}

{uploadError && (
  <div className="text-red-500 text-sm mt-2 p-2 bg-red-50 border border-red-200 rounded">
    {uploadError}
  </div>
)}
```

### 4. Upload Button

Added a dedicated upload button with loading state:

```jsx
<DialogFooter>
  <div className="flex space-x-2">
    <Button
      variant="outline"
      onClick={() => setIsUploadDialogOpen(false)}
      disabled={isUploading}
    >
      Cancel
    </Button>
    <Button onClick={handleUpload} disabled={isUploading || !selectedFile}>
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
```

### 5. Upload Handler

Created a dedicated upload handler function that sends the file to the server with metadata:

```typescript
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

    // Upload the document
    const projectId = 1; // Should be dynamic in a real implementation
    const result = await uploadDocument(
      projectId,
      selectedFile,
      uploadData.name,
      uploadData.description,
      tags
    );

    if (result) {
      // Add the new document to the list
      console.log("Document uploaded:", result);

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
```

### 6. API Integration

Created a dedicated API client function for document uploads:

```typescript
export async function uploadDocument(
  projectId: number,
  file: File,
  name?: string,
  description?: string,
  tags?: string[]
) {
  const formData = new FormData();
  formData.append("file", file);

  if (name) formData.append("name", name);
  if (description) formData.append("description", description);
  if (tags && tags.length > 0) formData.append("tags", JSON.stringify(tags));

  const response = await api.post(
    `/documents/project/${projectId}/upload`,
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );

  return response.data;
}
```

## Benefits of the Solution

1. **Better User Experience**: Users can review and modify document details before uploading
2. **Improved Error Handling**: Clear error messages for validation and upload failures
3. **Visual Feedback**: Loading indicators and file preview for better user interaction
4. **Separation of Concerns**: File selection and upload are separate operations
5. **Metadata Control**: Users can add relevant metadata (name, description, tags) before uploading

## Future Improvements

1. **Progress Indicators**: Add upload progress bar for large files
2. **File Type Validation**: More robust validation of file types and sizes
3. **Multi-file Upload**: Support for uploading multiple files at once
4. **Preview Generation**: Generate document previews when appropriate
5. **Integration with Backend Services**: Connect with document processing pipelines for analysis

## UUID Handling Fix

After implementing the two-step document upload process, we encountered an issue with UUID handling in the document upload API:

```
Get user by ID error: {'message': 'invalid input syntax for type integer: "5adb01e4-e12a-4b90-8830-7ce4e0ed69d8"', 'code': '22P02', 'hint': None, 'details': None}
```

This error occurred because the database was expecting an integer for the user ID, but Supabase uses UUID strings for user IDs.

### Solution for UUID Handling

1. **Database Schema Fixes**:

```sql
-- Modify documents table if needed
ALTER TABLE documents
DROP CONSTRAINT IF EXISTS documents_uploaded_by_fkey,
ALTER COLUMN uploaded_by TYPE TEXT,  -- or UUID if your Supabase uses UUID type
ADD CONSTRAINT documents_uploaded_by_fkey
    FOREIGN KEY (uploaded_by)
    REFERENCES auth.users(id);

-- Update project owner_id to use proper UUID type
ALTER TABLE projects
DROP CONSTRAINT IF EXISTS projects_owner_id_fkey,
ALTER COLUMN owner_id TYPE TEXT,  -- or UUID if your Supabase uses UUID type
ADD CONSTRAINT projects_owner_id_fkey
    FOREIGN KEY (owner_id)
    REFERENCES auth.users(id);

-- Update project collaborator user_id to use proper UUID type
ALTER TABLE project_collaborators
DROP CONSTRAINT IF EXISTS project_collaborators_user_id_fkey,
ALTER COLUMN user_id TYPE TEXT,  -- or UUID if your Supabase uses UUID type
ADD CONSTRAINT project_collaborators_user_id_fkey
    FOREIGN KEY (user_id)
    REFERENCES auth.users(id);
```

2. **Code Fixes**:

```python
# Ensure UUIDs are treated as strings
def get_user_by_id(self, user_id: str) -> Optional[Dict]:
    """Get user by ID"""
    try:
        # Ensure user_id is a string to handle UUID correctly
        user_id_str = str(user_id)
        response = self.client.table('users').select('*').eq('id', user_id_str).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Get user by ID error: {e}")
        return None
```

3. **Document Creation**:

```python
# Create document record in database
document_data = {
    "name": document_name,
    "content": content,
    "description": description,
    "tags": tag_list,
    "project_id": project_id,
    "uploaded_by": str(current_user.get("id")),  # Ensure UUID is stored as string
    "file_path": storage_path,
    "file_size": len(file_content),
    "file_type": file_extension,
    "created_at": datetime.utcnow().isoformat(),
}
```

4. **Storage Setup**:

   Used the setup_storage.py script to create a "documents" bucket in Supabase Storage with appropriate RLS policies.

## Conclusion

By implementing a two-step document upload process and fixing the UUID handling issues, we've significantly improved the user experience for uploading documents. This approach gives users more control over the upload process, provides better feedback, and ensures that documents are properly tagged and described before being added to the system.

Additionally, the UUID fix ensures proper compatibility between Supabase's authentication system (which uses UUIDs) and our database schema, making document uploads work correctly for all users.
