"use client";

import { usePathname } from "next/navigation";

import { AuthGuard } from "@/components/AuthGuard";
import { ResponsibleGamingFooter } from "@/components/ResponsibleGamingFooter";
import { Sidebar } from "@/components/Sidebar";

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isLogin = pathname === "/login";

  if (isLogin) {
    return <AuthGuard>{children}</AuthGuard>;
  }

  return (
    <div className="min-h-screen bg-gradient-radial-glow">
      <Sidebar />
      <main className="ml-60 min-h-screen px-8 pb-20 pt-8">
        <AuthGuard>
          <div className="mx-auto max-w-6xl">{children}</div>
        </AuthGuard>
      </main>
      <ResponsibleGamingFooter />
    </div>
  );
}
