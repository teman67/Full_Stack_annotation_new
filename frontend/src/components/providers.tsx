"use client";

import { SessionProvider } from "next-auth/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/sonner";
import { CollaborationProvider } from "@/contexts/CollaborationContext";
import { useState } from "react";
import { useSuppressHydrationWarning } from "@/hooks/useHydration";

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 minute
            retry: 1,
          },
        },
      })
  );

  // Handle hydration issues caused by browser extensions
  useSuppressHydrationWarning();

  return (
    <SessionProvider>
      <QueryClientProvider client={queryClient}>
        <CollaborationProvider>
          {children}
          <Toaster />
        </CollaborationProvider>
      </QueryClientProvider>
    </SessionProvider>
  );
}
