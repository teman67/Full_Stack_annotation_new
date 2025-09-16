import { NextResponse } from "next/server";

export function middleware() {
  // Temporarily disable NextAuth middleware to use localStorage-based auth
  // TODO: Re-enable and integrate with custom auth system later
  return NextResponse.next();
}

export const config = {
  matcher: [
    "/dashboard/:path*",
    "/projects/:path*",
    "/admin/:path*",
    "/settings/:path*",
  ],
};
