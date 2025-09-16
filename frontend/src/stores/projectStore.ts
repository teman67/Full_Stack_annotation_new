import { create } from "zustand";

export interface Project {
  id: string;
  name: string;
  description: string;
  owner_id: string;
  team_id?: string;
  settings: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface Document {
  id: string;
  project_id: string;
  name: string;
  content: string;
  file_path?: string;
  uploaded_by: string;
  created_at: string;
  updated_at: string;
}

export interface TagSet {
  id: string;
  project_id: string;
  name: string;
  tags_json: unknown[];
  created_by: string;
  created_at: string;
}

interface ProjectState {
  // Current project data
  currentProject: Project | null;
  projects: Project[];
  documents: Document[];
  tagSets: TagSet[];

  // Loading states
  isLoading: boolean;
  isDocumentsLoading: boolean;
  isTagSetsLoading: boolean;

  // Error states
  error: string | null;

  // Actions
  setCurrentProject: (project: Project | null) => void;
  setProjects: (projects: Project[]) => void;
  setDocuments: (documents: Document[]) => void;
  setTagSets: (tagSets: TagSet[]) => void;
  setLoading: (isLoading: boolean) => void;
  setDocumentsLoading: (isLoading: boolean) => void;
  setTagSetsLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;

  // Project actions
  addProject: (project: Project) => void;
  updateProject: (id: string, updates: Partial<Project>) => void;
  removeProject: (id: string) => void;

  // Document actions
  addDocument: (document: Document) => void;
  updateDocument: (id: string, updates: Partial<Document>) => void;
  removeDocument: (id: string) => void;

  // Tag set actions
  addTagSet: (tagSet: TagSet) => void;
  updateTagSet: (id: string, updates: Partial<TagSet>) => void;
  removeTagSet: (id: string) => void;

  // Clear actions
  clearAll: () => void;
}

export const useProjectStore = create<ProjectState>((set, get) => ({
  // Initial state
  currentProject: null,
  projects: [],
  documents: [],
  tagSets: [],
  isLoading: false,
  isDocumentsLoading: false,
  isTagSetsLoading: false,
  error: null,

  // Basic setters
  setCurrentProject: (project) => set({ currentProject: project }),
  setProjects: (projects) => set({ projects }),
  setDocuments: (documents) => set({ documents }),
  setTagSets: (tagSets) => set({ tagSets }),
  setLoading: (isLoading) => set({ isLoading }),
  setDocumentsLoading: (isDocumentsLoading) => set({ isDocumentsLoading }),
  setTagSetsLoading: (isTagSetsLoading) => set({ isTagSetsLoading }),
  setError: (error) => set({ error }),

  // Project actions
  addProject: (project) => {
    const { projects } = get();
    set({ projects: [...projects, project] });
  },
  updateProject: (id, updates) => {
    const { projects, currentProject } = get();
    const updatedProjects = projects.map((p) =>
      p.id === id ? { ...p, ...updates } : p
    );
    set({
      projects: updatedProjects,
      currentProject:
        currentProject?.id === id
          ? { ...currentProject, ...updates }
          : currentProject,
    });
  },
  removeProject: (id) => {
    const { projects, currentProject } = get();
    set({
      projects: projects.filter((p) => p.id !== id),
      currentProject: currentProject?.id === id ? null : currentProject,
    });
  },

  // Document actions
  addDocument: (document) => {
    const { documents } = get();
    set({ documents: [...documents, document] });
  },
  updateDocument: (id, updates) => {
    const { documents } = get();
    const updatedDocuments = documents.map((d) =>
      d.id === id ? { ...d, ...updates } : d
    );
    set({ documents: updatedDocuments });
  },
  removeDocument: (id) => {
    const { documents } = get();
    set({ documents: documents.filter((d) => d.id !== id) });
  },

  // Tag set actions
  addTagSet: (tagSet) => {
    const { tagSets } = get();
    set({ tagSets: [...tagSets, tagSet] });
  },
  updateTagSet: (id, updates) => {
    const { tagSets } = get();
    const updatedTagSets = tagSets.map((t) =>
      t.id === id ? { ...t, ...updates } : t
    );
    set({ tagSets: updatedTagSets });
  },
  removeTagSet: (id) => {
    const { tagSets } = get();
    set({ tagSets: tagSets.filter((t) => t.id !== id) });
  },

  // Clear all data
  clearAll: () =>
    set({
      currentProject: null,
      projects: [],
      documents: [],
      tagSets: [],
      error: null,
      isLoading: false,
      isDocumentsLoading: false,
      isTagSetsLoading: false,
    }),
}));
