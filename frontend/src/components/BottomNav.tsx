"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { useAuth } from "@/contexts/AuthContext";
import { useBetSlip } from "@/contexts/BetSlipContext";
import { IconBetSlip, IconDashboard, IconSettings, IconTicket } from "@/components/icons";

const LINKS = [
  { href: "/", label: "Dashboard", icon: IconDashboard },
  { href: "/bets", label: "Apostas", icon: IconTicket },
  { href: "/settings", label: "Config.", icon: IconSettings },
];

export function BottomNav() {
  const { user } = useAuth();
  const { items, toggle } = useBetSlip();
  const pathname = usePathname();

  if (!user) return null;

  return (
    <nav className="fixed inset-x-0 bottom-0 z-30 flex h-16 border-t border-border bg-surface/95 backdrop-blur lg:hidden">
      {LINKS.map((link) => {
        const active = pathname === link.href;
        const Icon = link.icon;
        return (
          <Link
            key={link.href}
            href={link.href}
            className={`relative flex min-h-[44px] flex-1 flex-col items-center justify-center gap-1 text-[11px] font-medium transition-colors ${
              active ? "text-primary" : "text-muted hover:text-foreground"
            }`}
          >
            {active && (
              <span className="absolute top-0 h-0.5 w-8 rounded-full bg-gradient-primary shadow-glow" />
            )}
            <Icon className="h-5 w-5" />
            {link.label}
          </Link>
        );
      })}

      <button
        type="button"
        onClick={toggle}
        className="relative flex min-h-[44px] flex-1 flex-col items-center justify-center gap-1 text-[11px] font-medium text-muted transition-colors hover:text-foreground"
      >
        <span className="relative">
          <IconBetSlip className="h-5 w-5" />
          {items.length > 0 && (
            <span className="absolute -right-2 -top-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-gradient-primary text-[9px] font-bold text-background">
              {items.length}
            </span>
          )}
        </span>
        Carrinho
      </button>
    </nav>
  );
}
