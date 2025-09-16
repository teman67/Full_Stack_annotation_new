"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { FileText, Users, Settings, LogOut, User } from "lucide-react";
import { toast } from "@/lib/utils/toast";

interface User {
  id: string;
  email: string;
  name: string;
  is_admin?: boolean;
}

export function AppHeader() {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    // Check authentication state
    const token = localStorage.getItem("auth-token");
    const userInfo = localStorage.getItem("user-info");

    if (token && userInfo) {
      try {
        setUser(JSON.parse(userInfo));
      } catch (error) {
        console.error("Error parsing user info:", error);
        // Clear invalid data
        localStorage.removeItem("auth-token");
        localStorage.removeItem("user-info");
      }
    }
    setIsLoading(false);
  }, []);

  const handleLogout = () => {
    // Clear localStorage
    localStorage.removeItem("auth-token");
    localStorage.removeItem("user-info");

    // Show success message
    toast.success("Logged out successfully!");

    // Reset user state
    setUser(null);

    // Redirect to home page
    router.push("/");
  };

  const getFirstName = (name: string, email: string) => {
    if (name && name !== email) {
      return name.split(" ")[0];
    }
    // If name is same as email or doesn't exist, extract from email
    return email?.split("@")[0]?.split(".")[0] || "User";
  };

  const getUserInitials = (name: string, email: string) => {
    const firstName = getFirstName(name, email);
    return firstName.charAt(0).toUpperCase();
  };

  if (isLoading) {
    return (
      <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-white/80 backdrop-blur supports-[backdrop-filter]:bg-white/60">
        <div className="w-full flex h-16 items-center justify-between px-4 md:px-6">
          <div className="flex items-center">
            <Link href="/" className="flex items-center space-x-3 group">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-primary to-accent text-white group-hover:scale-110 transition-transform duration-300">
                <FileText className="h-4 w-4" />
              </div>
              <span className="hidden font-bold sm:inline-block bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                Scientific Annotator
              </span>
            </Link>
          </div>
          <div className="flex items-center">{/* Loading placeholder */}</div>
        </div>
      </header>
    );
  }

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-white/80 backdrop-blur supports-[backdrop-filter]:bg-white/60 shadow-sm">
      <div className="w-full flex h-16 items-center justify-between px-4 md:px-6">
        <div className="flex items-center">
          <Link href="/" className="flex items-center space-x-3 group">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-primary to-accent text-white group-hover:scale-110 transition-transform duration-300">
              <FileText className="h-4 w-4" />
            </div>
            <span className="hidden font-bold sm:inline-block bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Scientific Annotator
            </span>
          </Link>
        </div>

        {user && (
          <nav className="hidden md:flex items-center space-x-1 absolute left-1/2 transform -translate-x-1/2">
            <Link
              href="/dashboard"
              className="px-3 py-2 text-sm font-medium rounded-lg transition-all duration-200 hover:bg-primary/5 hover:text-primary"
            >
              Dashboard
            </Link>
            <Link
              href="/projects"
              className="px-3 py-2 text-sm font-medium rounded-lg transition-all duration-200 hover:bg-primary/5 hover:text-primary"
            >
              Projects
            </Link>
            <Link
              href="/documents"
              className="px-3 py-2 text-sm font-medium rounded-lg transition-all duration-200 hover:bg-primary/5 hover:text-primary"
            >
              Documents
            </Link>
            <Link
              href="/tagsets"
              className="px-3 py-2 text-sm font-medium rounded-lg transition-all duration-200 hover:bg-primary/5 hover:text-primary"
            >
              Tag Sets
            </Link>
            {user.is_admin && (
              <Link
                href="/admin"
                className="px-3 py-2 text-sm font-medium rounded-lg transition-all duration-200 hover:bg-primary/5 hover:text-primary"
              >
                Admin
              </Link>
            )}
          </nav>
        )}

        <div className="flex items-center space-x-3">
          {!user ? (
            <div className="flex items-center space-x-3">
              <Button variant="ghost" asChild className="hover:bg-primary/5">
                <Link href="/auth/login">Sign In</Link>
              </Button>
              <Button
                asChild
                className="bg-gradient-to-r from-primary to-accent hover:from-primary/90 hover:to-accent/90 text-white shadow-lg shadow-primary/25"
              >
                <Link href="/auth/register">Sign Up</Link>
              </Button>
            </div>
          ) : (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  className="relative h-10 w-10 rounded-full hover:bg-primary/5"
                >
                  <Avatar className="h-9 w-9 ring-2 ring-primary/10 hover:ring-primary/20 transition-all">
                    <AvatarImage src="" alt={user.name || ""} />
                    <AvatarFallback className="bg-gradient-to-br from-primary to-accent text-white font-semibold">
                      {getUserInitials(user.name, user.email)}
                    </AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent
                className="w-56 border-border/50 shadow-lg"
                align="end"
                forceMount
              >
                <DropdownMenuLabel className="font-normal">
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-semibold leading-none">
                      {getFirstName(user.name, user.email)}
                    </p>
                    <p className="text-xs leading-none text-muted-foreground">
                      {user.email}
                    </p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem asChild className="hover:bg-primary/5">
                  <Link href="/profile" className="flex items-center">
                    <User className="mr-2 h-4 w-4" />
                    <span>Profile</span>
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild className="hover:bg-primary/5">
                  <Link href="/settings" className="flex items-center">
                    <Settings className="mr-2 h-4 w-4" />
                    <span>Settings</span>
                  </Link>
                </DropdownMenuItem>
                {user.is_admin && (
                  <DropdownMenuItem asChild className="hover:bg-primary/5">
                    <Link href="/admin" className="flex items-center">
                      <Users className="mr-2 h-4 w-4" />
                      <span>Admin Panel</span>
                    </Link>
                  </DropdownMenuItem>
                )}
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  className="flex items-center hover:bg-destructive/5 hover:text-destructive"
                  onClick={handleLogout}
                >
                  <LogOut className="mr-2 h-4 w-4" />
                  <span>Log out</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          )}
        </div>
      </div>
    </header>
  );
}
