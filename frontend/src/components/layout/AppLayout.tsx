"use client";

import { AppHeader } from "./AppHeader";

interface AppLayoutProps {
  children: React.ReactNode;
}

export function AppLayout({ children }: AppLayoutProps) {
  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-b from-white via-blue-50/50 to-blue-100/70">
      <AppHeader />
      <main className="flex-1 flex flex-col">{children}</main>
    </div>
  );
}
