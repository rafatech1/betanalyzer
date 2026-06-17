"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";

import { useAuth } from "@/contexts/AuthContext";

const LINKS = [
  { href: "/", label: "Dashboard" },
  { href: "/bets", label: "Minhas apostas" },
  { href: "/settings", label: "Configurações" },
];

export function NavBar() {
  const { user, logout } = useAuth();
  const router = useRouter();

  async function handleLogout() {
    await logout();
    router.replace("/login");
  }

  return (
    <header className="sticky top-0 z-10 border-b border-foreground/10 bg-background/95 backdrop-blur">
      <nav className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <Link href="/" className="text-lg font-bold text-primary">
          BetAnalyzer
        </Link>
        <div className="flex items-center gap-4 text-sm text-foreground/70">
          {user &&
            LINKS.map((link) => (
              <Link key={link.href} href={link.href} className="hover:text-primary">
                {link.label}
              </Link>
            ))}
          {user && (
            <div className="flex items-center gap-3 border-l border-foreground/10 pl-4">
              <span className="text-foreground/50">{user.nome}</span>
              <button onClick={handleLogout} className="hover:text-primary">
                Sair
              </button>
            </div>
          )}
        </div>
      </nav>
    </header>
  );
}
