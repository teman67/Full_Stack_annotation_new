"use client";

import { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Icons } from "@/components/ui/icons";
import { toast } from "@/lib/utils/toast";
import { authAPI } from "@/lib/api/auth";
import { AppLayout } from "@/components/layout/AppLayout";

function LoginPageContent() {
  const [isLoading, setIsLoading] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const searchParams = useSearchParams();

  useEffect(() => {
    // Handle URL parameters for messages
    const message = searchParams.get("message");
    const verified = searchParams.get("verified");

    // Don't automatically dismiss toasts - let them expire naturally
    // This preserves any error messages from login attempts

    if (message) {
      toast.info(message);
    } else if (verified === "true") {
      toast.success("Email verified successfully! You can now log in.");
    }
  }, [searchParams]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      // Use direct authAPI call
      const response = await authAPI.login({
        email,
        password,
      });

      if (response.access_token) {
        // Store the access token
        localStorage.setItem("auth-token", response.access_token);

        // Also get user info to store in localStorage for consistency
        try {
          const userResponse = await authAPI.getCurrentUser();
          localStorage.setItem("user-info", JSON.stringify(userResponse));
        } catch (userError) {
          console.warn("Could not fetch user info:", userError);
        }

        toast.success("Login successful!");

        // Force a page reload to ensure all components recognize the new auth state
        window.location.href = "/dashboard";
      }
    } catch (error: unknown) {
      console.error("Login error:", error);

      // Simple error handling - just show the backend error message directly
      let errorMessage = "Incorrect username or password";

      if (
        error &&
        typeof error === "object" &&
        "message" in error &&
        typeof error.message === "string"
      ) {
        errorMessage = error.message;
      }

      // Check if the error is about email verification
      if (
        errorMessage.toLowerCase().includes("verify") ||
        errorMessage.toLowerCase().includes("verification") ||
        errorMessage.toLowerCase().includes("not verified")
      ) {
        toast.error(
          "⚠️ Please verify your email before logging in. Check your inbox for a verification link."
        );
        setIsLoading(false);
        return;
      }

      // Show error message with same simplicity as success message
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleOAuthSignIn = async (provider: "google" | "github") => {
    setIsLoading(true);
    try {
      toast.info(
        `OAuth with ${provider} will be available soon. Please use email/password login.`
      );
    } catch (error) {
      console.error("OAuth error:", error);
      toast.error(`Failed to sign in with ${provider}. Please try again.`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AppLayout>
      <div className="flex items-center justify-center bg-gradient-to-br from-primary/5 via-background to-accent/5 relative overflow-hidden py-16 min-h-[calc(100vh-4rem)]">
        {/* Background decoration */}
        <div className="absolute inset-0 bg-grid-white/[0.02] bg-[size:50px_50px]" />
        <div className="absolute inset-0">
          <div className="absolute top-20 left-20 w-32 h-32 bg-primary/10 rounded-full blur-3xl" />
          <div className="absolute bottom-20 right-20 w-40 h-40 bg-accent/10 rounded-full blur-3xl" />
        </div>

        <Card className="w-full max-w-md relative z-10 border-border/50 shadow-xl shadow-primary/10 backdrop-blur-sm">
          <CardHeader className="space-y-3 text-center">
            <CardTitle className="text-3xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Welcome Back
            </CardTitle>
            <CardDescription className="text-muted-foreground">
              Enter your credentials to access your research workspace
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  disabled={isLoading}
                />
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="password">Password</Label>
                  <Link
                    href="/auth/forgot-password"
                    className="text-sm text-primary hover:underline"
                  >
                    Forgot password?
                  </Link>
                </div>
                <Input
                  id="password"
                  type="password"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  disabled={isLoading}
                />
              </div>
              <Button
                type="submit"
                className="w-full bg-gradient-to-r from-primary to-accent hover:from-primary/90 hover:to-accent/90 text-white shadow-lg shadow-primary/25"
                disabled={isLoading}
              >
                {isLoading && (
                  <Icons.spinner className="mr-2 h-4 w-4 animate-spin" />
                )}
                Sign In
              </Button>
            </form>

            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-background px-2 text-muted-foreground">
                  Or continue with
                </span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <Button
                variant="outline"
                onClick={() => handleOAuthSignIn("google")}
                disabled={isLoading}
              >
                {isLoading ? (
                  <Icons.spinner className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Icons.google className="mr-2 h-4 w-4" />
                )}
                Google
              </Button>
              <Button
                variant="outline"
                onClick={() => handleOAuthSignIn("github")}
                disabled={isLoading}
              >
                {isLoading ? (
                  <Icons.spinner className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Icons.gitHub className="mr-2 h-4 w-4" />
                )}
                GitHub
              </Button>
            </div>

            <div className="text-center text-sm">
              Don&apos;t have an account?{" "}
              <Link
                href="/auth/register"
                className="text-primary hover:underline"
              >
                Sign up
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}

export default function LoginPage() {
  return (
    <Suspense
      fallback={
        <AppLayout>
          <div className="flex items-center justify-center min-h-screen">
            <Icons.spinner className="h-8 w-8 animate-spin" />
          </div>
        </AppLayout>
      }
    >
      <LoginPageContent />
    </Suspense>
  );
}
