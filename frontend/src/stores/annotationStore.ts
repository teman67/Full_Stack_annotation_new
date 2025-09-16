import { create } from "zustand";

export interface Annotation {
  id: string;
  document_id: string;
  user_id: string;
  tag_id: string;
  text: string;
  start_pos: number;
  end_pos: number;
  confidence: number;
  source: "manual" | "llm" | "auto";
  created_at: string;
  updated_at: string;
}

export interface AnnotationJob {
  id: string;
  document_id: string;
  status: "pending" | "running" | "completed" | "failed" | "cancelled";
  progress: number;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

interface AnnotationState {
  // Current annotations
  annotations: Annotation[];
  selectedAnnotation: Annotation | null;

  // Job management
  currentJob: AnnotationJob | null;
  jobHistory: AnnotationJob[];

  // UI state
  isAnnotating: boolean;
  showValidationPanel: boolean;
  selectedText: string;
  selectionRange: { start: number; end: number } | null;

  // Loading states
  isLoading: boolean;
  isJobRunning: boolean;

  // Error state
  error: string | null;

  // Actions
  setAnnotations: (annotations: Annotation[]) => void;
  setSelectedAnnotation: (annotation: Annotation | null) => void;
  setCurrentJob: (job: AnnotationJob | null) => void;
  setJobHistory: (jobs: AnnotationJob[]) => void;
  setIsAnnotating: (isAnnotating: boolean) => void;
  setShowValidationPanel: (show: boolean) => void;
  setSelectedText: (text: string) => void;
  setSelectionRange: (range: { start: number; end: number } | null) => void;
  setLoading: (isLoading: boolean) => void;
  setJobRunning: (isRunning: boolean) => void;
  setError: (error: string | null) => void;

  // Annotation management
  addAnnotation: (annotation: Annotation) => void;
  updateAnnotation: (id: string, updates: Partial<Annotation>) => void;
  removeAnnotation: (id: string) => void;

  // Job management
  addJob: (job: AnnotationJob) => void;
  updateJob: (id: string, updates: Partial<AnnotationJob>) => void;

  // Clear actions
  clearAnnotations: () => void;
  clearSelection: () => void;
  clearAll: () => void;
}

export const useAnnotationStore = create<AnnotationState>((set, get) => ({
  // Initial state
  annotations: [],
  selectedAnnotation: null,
  currentJob: null,
  jobHistory: [],
  isAnnotating: false,
  showValidationPanel: false,
  selectedText: "",
  selectionRange: null,
  isLoading: false,
  isJobRunning: false,
  error: null,

  // Basic setters
  setAnnotations: (annotations) => set({ annotations }),
  setSelectedAnnotation: (selectedAnnotation) => set({ selectedAnnotation }),
  setCurrentJob: (currentJob) => set({ currentJob }),
  setJobHistory: (jobHistory) => set({ jobHistory }),
  setIsAnnotating: (isAnnotating) => set({ isAnnotating }),
  setShowValidationPanel: (showValidationPanel) => set({ showValidationPanel }),
  setSelectedText: (selectedText) => set({ selectedText }),
  setSelectionRange: (selectionRange) => set({ selectionRange }),
  setLoading: (isLoading) => set({ isLoading }),
  setJobRunning: (isJobRunning) => set({ isJobRunning }),
  setError: (error) => set({ error }),

  // Annotation management
  addAnnotation: (annotation) => {
    const { annotations } = get();
    set({ annotations: [...annotations, annotation] });
  },
  updateAnnotation: (id, updates) => {
    const { annotations, selectedAnnotation } = get();
    const updatedAnnotations = annotations.map((a) =>
      a.id === id ? { ...a, ...updates } : a
    );
    set({
      annotations: updatedAnnotations,
      selectedAnnotation:
        selectedAnnotation?.id === id
          ? { ...selectedAnnotation, ...updates }
          : selectedAnnotation,
    });
  },
  removeAnnotation: (id) => {
    const { annotations, selectedAnnotation } = get();
    set({
      annotations: annotations.filter((a) => a.id !== id),
      selectedAnnotation:
        selectedAnnotation?.id === id ? null : selectedAnnotation,
    });
  },

  // Job management
  addJob: (job) => {
    const { jobHistory } = get();
    set({
      currentJob: job,
      jobHistory: [job, ...jobHistory],
    });
  },
  updateJob: (id, updates) => {
    const { currentJob, jobHistory } = get();
    const updatedHistory = jobHistory.map((j) =>
      j.id === id ? { ...j, ...updates } : j
    );
    set({
      jobHistory: updatedHistory,
      currentJob:
        currentJob?.id === id ? { ...currentJob, ...updates } : currentJob,
    });
  },

  // Clear actions
  clearAnnotations: () =>
    set({
      annotations: [],
      selectedAnnotation: null,
    }),
  clearSelection: () =>
    set({
      selectedText: "",
      selectionRange: null,
      selectedAnnotation: null,
    }),
  clearAll: () =>
    set({
      annotations: [],
      selectedAnnotation: null,
      currentJob: null,
      jobHistory: [],
      isAnnotating: false,
      showValidationPanel: false,
      selectedText: "",
      selectionRange: null,
      isLoading: false,
      isJobRunning: false,
      error: null,
    }),
}));
