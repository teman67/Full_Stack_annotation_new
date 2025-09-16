"use client";

import { toast as sonnerToast } from "sonner";

// Simple toast utility that uses only the default Sonner behavior
// No custom styling or options - just consistent duration settings
export const toast = {
  // Wrap original toast methods without any modifications
  dismiss: sonnerToast.dismiss,
  loading: sonnerToast.loading,

  // Error toast with persistent behavior
  error: (message: string) => {
    return sonnerToast.error(message, { duration: 3000 });
  },

  // Simple success toast
  success: (message: string) => {
    return sonnerToast.success(message, { duration: 3000 });
  },

  // Simple info toast
  info: (message: string) => {
    return sonnerToast.info(message, { duration: 3000 });
  },

  // Simple warning toast
  warning: (message: string) => {
    return sonnerToast.warning(message, { duration: 3000 });
  },
};
