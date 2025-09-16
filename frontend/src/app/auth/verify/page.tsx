"use client";

import { Suspense } from "react";
import { useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Icons } from "@/components/ui/icons";
import { toast } from "@/lib/utils/toast";
import { authAPI } from "@/lib/api/auth";

function VerifyEmailContent() {
  const [status, setStatus] = useState<
    "loading" | "success" | "error" | "expired"
  >("loading");
  const [isLoading, setIsLoading] = useState(true);
  const searchParams = useSearchParams();
  const router = useRouter();

  useEffect(() => {
    const verifyEmail = async () => {
      setIsLoading(true);

      try {
        // Get parameters from URL hash (after #) since Supabase uses hash fragments
        const hash = window.location.hash.substring(1); // Remove the # symbol
        const hashParams = new URLSearchParams(hash);

        // Also check search params (after ?) as backup
        const token_hash =
          searchParams.get("token_hash") || hashParams.get("token_hash");
        const access_token =
          searchParams.get("access_token") || hashParams.get("access_token");
        const refresh_token =
          searchParams.get("refresh_token") || hashParams.get("refresh_token");
        const expires_in =
          searchParams.get("expires_in") || hashParams.get("expires_in");
        const token_type =
          searchParams.get("token_type") || hashParams.get("token_type");
        const type =
          searchParams.get("type") || hashParams.get("type") || "signup";

        // Debug logging - check ALL parameters
        console.log("Verification page loaded with ALL params:");
        console.log("- URL hash:", hash);
        console.log("- token_hash:", token_hash);
        console.log(
          "- access_token:",
          access_token ? "Found (hidden for security)" : null
        );
        console.log(
          "- refresh_token:",
          refresh_token ? "Found (hidden for security)" : null
        );
        console.log("- expires_in:", expires_in);
        console.log("- token_type:", token_type);
        console.log("- type:", type);
        console.log("- Hash params:", Object.fromEntries(hashParams.entries()));
        console.log(
          "- Search params:",
          Object.fromEntries(searchParams.entries())
        );
        console.log("- Full URL:", window.location.href);

        // Check if this is a successful redirect with access token (automatic verification)
        if (access_token && refresh_token) {
          console.log(
            "Found access_token and refresh_token - automatic verification successful"
          );
          setStatus("success");
          // Don't show toast here - let the login page handle the message
          // This prevents duplicate messages

          // Redirect to login page after 3 seconds
          setTimeout(() => {
            router.push("/auth/login?verified=true");
          }, 3000);
          return;
        }

        // Check if we have a token_hash for manual verification
        if (token_hash) {
          console.log("Found token_hash - attempting manual verification");
          console.log(
            "Calling authAPI.verifyEmail with token_hash and type:",
            type
          );

          // Call backend verification endpoint using authAPI
          await authAPI.verifyEmail(token_hash, type);

          setStatus("success");
          // Don't show toast here - let the login page handle the message
          // This prevents duplicate messages

          // Redirect to login page after 3 seconds
          setTimeout(() => {
            router.push("/auth/login?verified=true");
          }, 3000);
          return;
        }

        // If no tokens found, this might be an error or direct access
        console.log("No verification tokens found in URL or hash");
        setStatus("error");
        toast.error("Invalid verification link. No token found.");
        return;
      } catch (error: unknown) {
        setStatus("error");
        let errorMessage =
          "Email verification failed. The link may be expired or invalid.";

        if (error && typeof error === "object" && "response" in error) {
          const apiError = error as {
            response?: { data?: { detail?: string } };
          };
          errorMessage = apiError.response?.data?.detail || errorMessage;
        }

        toast.error(errorMessage);
      } finally {
        setIsLoading(false);
      }
    };

    verifyEmail();
  }, [searchParams, router]);

  const handleResendEmail = async () => {
    try {
      const email = localStorage.getItem("pendingVerificationEmail");

      if (!email) {
        toast.error(
          "Please go back to registration and enter your email again."
        );
        return;
      }

      await authAPI.resendVerification(email);
      toast.success("New verification email sent! Please check your inbox.");
    } catch (error: unknown) {
      let errorMessage =
        "Failed to resend verification email. Please try again later.";

      if (error && typeof error === "object" && "response" in error) {
        const apiError = error as { response?: { data?: { detail?: string } } };
        errorMessage = apiError.response?.data?.detail || errorMessage;
      }

      toast.error(errorMessage);
    }
  };

  const getStatusMessage = () => {
    switch (status) {
      case "loading":
        return {
          title: "Verifying Your Email...",
          description: "Please wait while we verify your email address...",
          showSpinner: true,
        };
      case "success":
        return {
          title: "Email Verified Successfully!",
          description:
            "Your email has been verified and your account is now active. Redirecting to login...",
          showSpinner: false,
        };
      case "error":
        return {
          title: "Verification Failed",
          description:
            "There was a problem verifying your email address. The link may be expired or invalid.",
          showSpinner: false,
        };
      case "expired":
        return {
          title: "Verification Link Expired",
          description:
            "The verification link has expired. Please request a new one.",
          showSpinner: false,
        };
      default:
        return {
          title: "Email Verification",
          description: "Verifying your email address...",
          showSpinner: false,
        };
    }
  };

  const statusInfo = getStatusMessage();

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="flex justify-center mb-4">
            {statusInfo.showSpinner ? (
              <Icons.spinner className="h-12 w-12 text-blue-500 animate-spin" />
            ) : (
              <div
                className={`h-12 w-12 rounded-full flex items-center justify-center ${
                  status === "success"
                    ? "bg-green-100 text-green-600"
                    : "bg-red-100 text-red-600"
                }`}
              >
                {status === "success" ? "✓" : "✗"}
              </div>
            )}
          </div>
          <CardTitle className="text-2xl font-bold">
            {statusInfo.title}
          </CardTitle>
          <CardDescription>{statusInfo.description}</CardDescription>
        </CardHeader>

        <CardContent className="space-y-4">
          <div className="flex flex-col space-y-3">
            {status === "success" && (
              <Button
                onClick={() => router.push("/auth/login?verified=true")}
                className="w-full"
                disabled={isLoading}
              >
                Continue to Login
              </Button>
            )}

            {(status === "error" || status === "expired") && (
              <>
                <Button
                  onClick={handleResendEmail}
                  variant="outline"
                  className="w-full"
                  disabled={isLoading}
                >
                  📧 Resend Verification Email
                </Button>

                <Button
                  onClick={() => router.push("/auth/register")}
                  variant="outline"
                  className="w-full"
                  disabled={isLoading}
                >
                  Back to Registration
                </Button>
              </>
            )}

            {status === "loading" && (
              <Button
                onClick={() => router.push("/auth/login")}
                variant="outline"
                className="w-full"
                disabled={isLoading}
              >
                Back to Login
              </Button>
            )}
          </div>

          <div className="text-center text-sm text-gray-600">
            <p>
              Need help? Contact{" "}
              <a
                href="mailto:support@yourapp.com"
                className="text-blue-600 hover:underline"
              >
                support
              </a>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense
      fallback={
        <div className="flex items-center justify-center min-h-screen">
          <Icons.spinner className="h-8 w-8 animate-spin" />
        </div>
      }
    >
      <VerifyEmailContent />
    </Suspense>
  );
}
