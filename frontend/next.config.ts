import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Server external packages (moved from experimental.serverComponentsExternalPackages)
  serverExternalPackages: [],
  experimental: {
    // Other experimental features can go here
  },
  // Suppress hydration warnings for browser extensions
  compiler: {
    removeConsole: process.env.NODE_ENV === "production",
  },
  // Handle hydration issues
  onDemandEntries: {
    // period (in ms) where the server will keep pages in the buffer
    maxInactiveAge: 25 * 1000,
    // number of pages that should be kept simultaneously without being disposed
    pagesBufferLength: 2,
  },
};

export default nextConfig;
