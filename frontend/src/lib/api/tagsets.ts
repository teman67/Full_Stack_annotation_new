// API client for tagsets operations
import api from "@/lib/api/client";

/**
 * Upload a tagset CSV file
 * @param file - The CSV file to upload
 * @param name - The name of the tagset
 * @param description - The description of the tagset
 * @returns The created tagset
 */
export async function uploadTagsetCSV(
  file: File,
  name: string,
  description: string = ""
) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("name", name);
  formData.append("description", description);

  const response = await api.post("/tagsets/upload-csv", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

  return response.data;
}

/**
 * Get all tagsets for the current user
 * @returns Array of tagsets
 */
export async function getUserTagsets() {
  const response = await api.get("/tagsets");
  return response.data;
}

/**
 * Get a specific tagset by ID
 * @param tagsetId - The ID of the tagset to retrieve
 * @returns The tagset data
 */
export async function getTagset(tagsetId: number) {
  const response = await api.get(`/tagsets/${tagsetId}`);
  return response.data;
}

/**
 * Delete a tagset and its associated file
 * @param tagsetId - The ID of the tagset to delete
 * @returns Success message
 */
export async function deleteTagset(tagsetId: number) {
  const response = await api.delete(`/tagsets/${tagsetId}`);
  return response.data;
}
