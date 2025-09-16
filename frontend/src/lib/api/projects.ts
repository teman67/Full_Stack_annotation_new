import { apiClient } from "./client";
import type { Project, Document, TagSet } from "@/stores/projectStore";

export interface CreateProjectRequest {
  name: string;
  description: string;
  team_id?: string;
  settings?: Record<string, unknown>;
}

export interface UpdateProjectRequest {
  name?: string;
  description?: string;
  settings?: Record<string, unknown>;
}

export interface ProjectMember {
  user_id: string;
  role: "owner" | "admin" | "member" | "viewer";
  joined_at: string;
}

export interface AddMemberRequest {
  user_id: string;
  role: "admin" | "member" | "viewer";
}

export const projectsAPI = {
  // Project Management
  getProjects: async (): Promise<Project[]> => {
    return apiClient.get("/projects");
  },

  getProject: async (projectId: string): Promise<Project> => {
    return apiClient.get(`/projects/${projectId}`);
  },

  createProject: async (data: CreateProjectRequest): Promise<Project> => {
    return apiClient.post("/projects", data);
  },

  updateProject: async (
    projectId: string,
    data: UpdateProjectRequest
  ): Promise<Project> => {
    return apiClient.put(`/projects/${projectId}`, data);
  },

  deleteProject: async (projectId: string): Promise<{ message: string }> => {
    return apiClient.delete(`/projects/${projectId}`);
  },

  // Team Member Management
  getProjectMembers: async (projectId: string): Promise<ProjectMember[]> => {
    return apiClient.get(`/projects/${projectId}/members`);
  },

  addProjectMember: async (
    projectId: string,
    data: AddMemberRequest
  ): Promise<ProjectMember> => {
    return apiClient.post(`/projects/${projectId}/members`, data);
  },

  updateMemberRole: async (
    projectId: string,
    userId: string,
    role: string
  ): Promise<ProjectMember> => {
    return apiClient.put(`/projects/${projectId}/members/${userId}`, { role });
  },

  removeProjectMember: async (
    projectId: string,
    userId: string
  ): Promise<{ message: string }> => {
    return apiClient.delete(`/projects/${projectId}/members/${userId}`);
  },
};

export interface CreateDocumentRequest {
  name: string;
  content?: string;
}

export interface UpdateDocumentRequest {
  name?: string;
  content?: string;
}

export const documentsAPI = {
  // Document Management
  getDocuments: async (projectId: string): Promise<Document[]> => {
    return apiClient.get(`/projects/${projectId}/documents`);
  },

  getDocument: async (documentId: string): Promise<Document> => {
    return apiClient.get(`/documents/${documentId}`);
  },

  createDocument: async (
    projectId: string,
    data: CreateDocumentRequest
  ): Promise<Document> => {
    return apiClient.post(`/projects/${projectId}/documents`, data);
  },

  uploadDocument: async (
    projectId: string,
    file: File,
    name?: string
  ): Promise<Document> => {
    return apiClient.upload(
      `/projects/${projectId}/documents/upload`,
      file,
      name ? { name } : undefined
    );
  },

  updateDocument: async (
    documentId: string,
    data: UpdateDocumentRequest
  ): Promise<Document> => {
    return apiClient.put(`/documents/${documentId}`, data);
  },

  deleteDocument: async (documentId: string): Promise<{ message: string }> => {
    return apiClient.delete(`/documents/${documentId}`);
  },
};

export interface CreateTagSetRequest {
  name: string;
  tags_json: Array<{
    name: string;
    definition: string;
    examples?: string[];
    color?: string;
  }>;
}

export interface UpdateTagSetRequest {
  name?: string;
  tags_json?: Array<{
    name: string;
    definition: string;
    examples?: string[];
    color?: string;
  }>;
}

export const tagSetsAPI = {
  // Tag Set Management
  getTagSets: async (projectId: string): Promise<TagSet[]> => {
    return apiClient.get(`/projects/${projectId}/tagsets`);
  },

  getTagSet: async (tagSetId: string): Promise<TagSet> => {
    return apiClient.get(`/tagsets/${tagSetId}`);
  },

  createTagSet: async (
    projectId: string,
    data: CreateTagSetRequest
  ): Promise<TagSet> => {
    return apiClient.post(`/projects/${projectId}/tagsets`, data);
  },

  updateTagSet: async (
    tagSetId: string,
    data: UpdateTagSetRequest
  ): Promise<TagSet> => {
    return apiClient.put(`/tagsets/${tagSetId}`, data);
  },

  deleteTagSet: async (tagSetId: string): Promise<{ message: string }> => {
    return apiClient.delete(`/tagsets/${tagSetId}`);
  },

  // Import/Export
  importTagSet: async (projectId: string, file: File): Promise<TagSet> => {
    return apiClient.upload(`/projects/${projectId}/tagsets/import`, file);
  },

  exportTagSet: async (
    tagSetId: string,
    format: "csv" | "json"
  ): Promise<Blob> => {
    return apiClient.get(`/tagsets/${tagSetId}/export?format=${format}`, {
      responseType: "blob",
    });
  },
};
