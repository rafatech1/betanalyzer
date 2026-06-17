"use client";

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";

import { useAuth } from "@/contexts/AuthContext";

const PUBLIC_PATHS = ["/login", "/register", "/forgot-password", "/reset-password"];

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const pathname = usePathname();
  const router = useRouter();
  const isPublicPath = PUBLIC_PATHS.includes(pathname);

  useEffect(() => {
    if (!loading && !user && !isPublicPath) {
      router.replace("/login");
    }
  }, [loading, user, isPublicPath, router]);

  if (isPublicPath) {
    return <>{children}</>;
  }

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-border border-t-primary" />
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return <>{children}</>;
}
