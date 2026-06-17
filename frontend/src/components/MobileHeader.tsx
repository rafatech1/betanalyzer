"use client";

import { useRouter } from "next/navigation";

import { useAuth } from "@/contexts/AuthContext";
import { IconLogout } from "@/components/icons";
import { Logo } from "@/components/Logo";

export function MobileHeader() {
  const { user, logout } = useAuth();
  const router = useRouter();

  if (!user) return null;

  async function handleLogout() {
    await logout();
    router.replace("/login");
  }

  return (
    <header className="fixed inset-x-0 top-0 z-30 flex h-14 items-center justify-between border-b border-border bg-surface/95 px-4 backdrop-blur lg:hidden">
      <Logo size={26} />
      <div className="flex items-center gap-1.5">
        <span className="max-w-[110px] truncate text-xs font-medium text-foreground">
          {user.nome}
        </span>
        <button
          onClick={handleLogout}
          title="Sair"
          className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md text-muted transition-colors hover:bg-surface-hover hover:text-ev-negative"
        >
          <IconLogout className="h-4 w-4" />
        </button>
      </div>
    </header>
  );
}
