"use client";

import { usePathname } from "next/navigation";

import { AuthGuard } from "@/components/AuthGuard";
import { BetSlip } from "@/components/BetSlip";
import { BottomNav } from "@/components/BottomNav";
import { MobileHeader } from "@/components/MobileHeader";
import { ResponsibleGamingFooter } from "@/components/ResponsibleGamingFooter";
import { Sidebar } from "@/components/Sidebar";

const STANDALONE_PATHS = ["/login", "/register", "/forgot-password", "/reset-password"];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isStandalone = STANDALONE_PATHS.includes(pathname);

  if (isStandalone) {
    return <AuthGuard>{children}</AuthGuard>;
  }

  return (
    <div className="min-h-screen bg-gradient-radial-glow">
      <Sidebar />
      <MobileHeader />
      <main className="min-h-screen px-4 pb-6 pt-20 sm:px-6 lg:ml-60 lg:px-8 lg:pb-20 lg:pt-8">
        <AuthGuard>
          <div className="mx-auto max-w-6xl">{children}</div>
        </AuthGuard>
      </main>
      <ResponsibleGamingFooter />
      <div aria-hidden className="h-16 lg:hidden" />
      <BottomNav />
      <BetSlip />
    </div>
  );
}
