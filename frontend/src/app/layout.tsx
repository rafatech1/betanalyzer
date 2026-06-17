import type { Metadata } from "next";
import "./globals.css";

import { AuthGuard } from "@/components/AuthGuard";
import { NavBar } from "@/components/NavBar";
import { ResponsibleGamingFooter } from "@/components/ResponsibleGamingFooter";
import { AuthProvider } from "@/contexts/AuthContext";

export const metadata: Metadata = {
  title: "BetAnalyzer",
  description: "Análise de apostas de futebol orientada a valor (EV+)",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR">
      <body className="bg-background text-foreground min-h-screen">
        <AuthProvider>
          <NavBar />
          <main className="mx-auto max-w-6xl px-4 pb-16 pt-6">
            <AuthGuard>{children}</AuthGuard>
          </main>
          <ResponsibleGamingFooter />
        </AuthProvider>
      </body>
    </html>
  );
}
