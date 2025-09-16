"use client";

import { useEffect, useState } from "react";

/**
 * Custom hook to handle hydration mismatches
 * Useful for components that might differ between server and client
 */
export function useHydration() {
  const [isHydrated, setIsHydrated] = useState(false);

  useEffect(() => {
    setIsHydrated(true);
  }, []);

  return isHydrated;
}

/**
 * Custom hook to suppress specific hydration warnings
 * Useful for dealing with browser extensions that modify the DOM
 */
export function useSuppressHydrationWarning() {
  useEffect(() => {
    if (
      typeof window !== "undefined" &&
      process.env.NODE_ENV === "development"
    ) {
      // Create a more targeted suppression for browser extension warnings
      const originalWarn = console.warn;
      const originalError = console.error;

      const shouldSuppress = (message: string) => {
        return (
          message.includes("data-new-gr-c-s-check-loaded") ||
          message.includes("data-gr-ext-installed") ||
          message.includes("data-new-gr-c-s-loaded") ||
          (message.includes("Hydration") &&
            (message.includes("server rendered HTML") ||
              message.includes("client properties")))
        );
      };

      console.warn = (...args: unknown[]) => {
        const message = String(args[0] || "");
        if (!shouldSuppress(message)) {
          originalWarn(...args);
        }
      };

      console.error = (...args: unknown[]) => {
        const message = String(args[0] || "");
        if (!shouldSuppress(message)) {
          originalError(...args);
        }
      };

      return () => {
        console.warn = originalWarn;
        console.error = originalError;
      };
    }
  }, []);
}
