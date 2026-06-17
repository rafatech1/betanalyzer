"use client";

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";

import { useAuth } from "@/contexts/AuthContext";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user && pathname !== "/login") {
      router.replace("/login");
    }
  }, [loading, user, pathname, router]);

  if (pathname === "/login") {
    return <>{children}</>;
  }

  if (loading) {
    return <p className="p-4 text-sm text-foreground/50">Carregando...</p>;
  }

  if (!user) {
    return null;
  }

  return <>{children}</>;
}
