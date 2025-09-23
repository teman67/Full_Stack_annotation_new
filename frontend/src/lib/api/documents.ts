// API client for document operations
import api from "@/lib/api/client";

/**
 * Upload a document file
 * @param projectId - The ID of the project to upload to
 * @param file - The file to upload
 * @param name - Optional custom name for the document
 * @param description - Optional document description
 * @param tags - Optional tags for the document
 * @returns The created document
 */
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

/**
 * Get all documents for a project
 * @param projectId - The ID of the project to get documents for
 * @returns Array of documents
 */
export async function getProjectDocuments(projectId: number) {
  const response = await api.get(`/documents/project/${projectId}`);
  return response.data;
}

/**
 * Get a specific document by ID
 * @param documentId - The ID of the document to retrieve
 * @returns The document data
 */
export async function getDocument(documentId: number) {
  const response = await api.get(`/documents/${documentId}`);
  return response.data;
}

/**
 * Update a document
 * @param documentId - The ID of the document to update
 * @param documentData - The updated document data
 * @returns The updated document
 */
export async function updateDocument(
  documentId: number,
  documentData: { name?: string; description?: string; tags?: string[] }
) {
  const response = await api.put(`/documents/${documentId}`, documentData);
  return response.data;
}

/**
 * Delete a document
 * @param documentId - The ID of the document to delete
 * @returns Success message
 */
export async function deleteDocument(documentId: number) {
  const response = await api.delete(`/documents/${documentId}`);
  return response.data;
}
