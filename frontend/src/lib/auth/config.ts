import { NextAuthOptions } from "next-auth";
import GoogleProvider from "next-auth/providers/google";
import GitHubProvider from "next-auth/providers/github";
import CredentialsProvider from "next-auth/providers/credentials";
import { authAPI } from "@/lib/api/auth";

export const authOptions: NextAuthOptions = {
  providers: [
    // Credentials Provider for email/password login
    CredentialsProvider({
      name: "credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          throw new Error("Email and password are required");
        }

        try {
          const loginResponse = await authAPI.login({
            email: credentials.email,
            password: credentials.password,
          });

          // Now get user info with the token
          if (loginResponse.access_token) {
            // Store token temporarily for user info request
            const tempHeaders = {
              Authorization: `Bearer ${loginResponse.access_token}`,
            };

            try {
              const userResponse = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL}/auth/me`,
                {
                  headers: tempHeaders,
                }
              );

              if (userResponse.ok) {
                const user = await userResponse.json();
                return {
                  id: user.id,
                  email: user.email,
                  name: user.name,
                  image: user.avatar_url,
                  accessToken: loginResponse.access_token,
                  isAdmin: user.is_admin,
                };
              }
            } catch (userError) {
              console.error("Failed to fetch user info:", userError);
            }
          }
          return null;
        } catch (error) {
          console.error("Authentication error:", error);
          throw new Error("Invalid credentials");
        }
      },
    }),

    // Google OAuth Provider
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),

    // GitHub OAuth Provider
    GitHubProvider({
      clientId: process.env.GITHUB_ID!,
      clientSecret: process.env.GITHUB_SECRET!,
    }),
  ],

  callbacks: {
    async jwt({ token, user, account }) {
      // Handle OAuth sign-in
      if (account && user) {
        if (account.provider === "google" || account.provider === "github") {
          try {
            // Exchange OAuth code for our backend token
            const response = await authAPI.handleOAuthCallback(
              account.provider,
              account.access_token || "",
              account.id_token
            );

            token.accessToken = response.access_token;
            if (response.user) {
              token.user = response.user;
              token.isAdmin = response.user.is_admin;
            }
          } catch (error) {
            console.error("OAuth callback error:", error);
            // Handle OAuth error
          }
        } else if (account.provider === "credentials") {
          // Handle credentials login
          const credUser = user as { accessToken?: string; isAdmin?: boolean };
          token.accessToken = credUser.accessToken;
          token.isAdmin = credUser.isAdmin;
        }
      }

      return token;
    },

    async session({ session, token }) {
      // Send properties to the client
      if (token.accessToken && session.user) {
        session.accessToken = token.accessToken as string;
        session.user.isAdmin = token.isAdmin as boolean;

        // Store token in localStorage for API calls
        if (typeof window !== "undefined") {
          localStorage.setItem("auth-token", token.accessToken as string);
        }
      }

      return session;
    },

    async signIn() {
      // Allow sign in for all providers
      return true;
    },

    async redirect({ url, baseUrl }) {
      // Redirect to dashboard after successful login
      if (url.startsWith("/")) return `${baseUrl}${url}`;
      if (new URL(url).origin === baseUrl) return url;
      return `${baseUrl}/dashboard`;
    },
  },

  pages: {
    signIn: "/auth/login",
    error: "/auth/error",
  },

  session: {
    strategy: "jwt",
    maxAge: 24 * 60 * 60, // 24 hours
  },

  secret: process.env.NEXTAUTH_SECRET,
};
