"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

/**
 * Simpler HOC for pages that need simple auth check
 * It doesn't handle the loading state internally but redirects if not authenticated
 */
export function withSimpleAuth<P extends object>(
  Component: React.ComponentType<P>
) {
  return function SimpleAuthProtected(props: P) {
    const router = useRouter();
    const [hasChecked, setHasChecked] = useState(false);

    useEffect(() => {
      // Check for authentication token
      const token = localStorage.getItem("auth-token");

      if (!token) {
        // Redirect to login if no token found
        router.push("/auth/login?message=Please log in to access this page");
        return;
      }

      // Mark auth check as complete
      setHasChecked(true);
    }, [router]);

    // Only render the protected component after auth check completes
    return hasChecked ? <Component {...props} /> : null;
  };
}
