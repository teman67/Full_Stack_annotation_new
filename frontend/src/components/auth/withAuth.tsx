"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

/**
 * Higher Order Component to protect routes that require authentication
 * It checks for the auth token and redirects to login if not authenticated
 */
export function withAuth<P extends object>(Component: React.ComponentType<P>) {
  return function AuthProtected(props: P) {
    const router = useRouter();
    const [isLoading, setIsLoading] = useState(true);
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    useEffect(() => {
      // Check for authentication token
      const token = localStorage.getItem("auth-token");

      if (!token) {
        // Redirect to login if no token found
        router.push("/auth/login?message=Please log in to access this page");
        return;
      }

      // Set authenticated state
      setIsAuthenticated(true);
      setIsLoading(false);
    }, [router]);

    // Show loading state
    if (isLoading) {
      return (
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
            <p className="mt-4 text-lg">Loading...</p>
          </div>
        </div>
      );
    }

    // Only render the protected component if authenticated
    return isAuthenticated ? <Component {...props} /> : null;
  };
}
