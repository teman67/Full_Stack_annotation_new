import { apiClient } from "./client";
import type { User } from "@/stores/userStore";

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  name: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user?: User; // Optional since some endpoints don't return user
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface RegisterResponse {
  message: string;
  user: {
    id: string;
    email: string;
    name: string;
    is_active: boolean;
    is_admin: boolean;
    email_verified: boolean;
    created_at: string;
    updated_at: string;
  };
  email_verification_required: boolean;
}

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordResetConfirm {
  token: string;
  new_password: string;
}

export const authAPI = {
  // Email/Password Authentication
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    const formData = new FormData();
    formData.append("username", data.email); // FastAPI OAuth2PasswordRequestForm expects 'username'
    formData.append("password", data.password);

    return apiClient.post("/auth/token", formData, {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    });
  },

  register: async (data: RegisterRequest): Promise<RegisterResponse> => {
    return apiClient.post("/auth/register", data);
  },

  logout: async (): Promise<void> => {
    return apiClient.post("/auth/logout");
  },

  refreshToken: async (refreshToken: string): Promise<AuthResponse> => {
    return apiClient.post("/auth/refresh", { refresh_token: refreshToken });
  },

  // Password Reset
  requestPasswordReset: async (
    data: PasswordResetRequest
  ): Promise<{ message: string }> => {
    return apiClient.post("/auth/reset-password", data);
  },

  confirmPasswordReset: async (
    data: PasswordResetConfirm
  ): Promise<{ message: string }> => {
    return apiClient.post("/auth/confirm-reset", data);
  },

  // Email Verification
  verifyEmail: async (
    token_hash: string,
    type: string = "email"
  ): Promise<{ message: string }> => {
    return apiClient.post("/auth/verify-email", { token_hash, type });
  },

  resendVerification: async (email: string): Promise<{ message: string }> => {
    return apiClient.post("/auth/resend-verification", { email });
  },

  // OAuth
  getOAuthUrl: async (
    provider: "google" | "github" | "linkedin"
  ): Promise<{ url: string }> => {
    return apiClient.get(`/auth/oauth/${provider}`);
  },

  handleOAuthCallback: async (
    provider: string,
    code: string,
    state?: string
  ): Promise<AuthResponse> => {
    return apiClient.post("/auth/oauth/callback", { provider, code, state });
  },

  // User Management
  getCurrentUser: async (): Promise<User> => {
    return apiClient.get("/auth/me");
  },

  updateProfile: async (updates: Partial<User>): Promise<User> => {
    return apiClient.put("/users/me", updates);
  },

  deleteAccount: async (): Promise<{ message: string }> => {
    return apiClient.delete("/users/me");
  },

  // OAuth Account Linking
  linkOAuthAccount: async (
    provider: string,
    code: string
  ): Promise<{ message: string }> => {
    return apiClient.post("/users/link-oauth", { provider, code });
  },

  unlinkOAuthAccount: async (
    provider: string
  ): Promise<{ message: string }> => {
    return apiClient.delete(`/users/unlink-oauth/${provider}`);
  },
};
