"use client";

import { IconBan, IconCheck, IconX } from "@/components/icons";
import type { ResultadoAposta } from "@/types/bet";

export function BetResultQuickActions({
  onSelect,
}: {
  onSelect: (resultado: ResultadoAposta) => void;
}) {
  return (
    <div className="flex items-center gap-1.5">
      <button
        type="button"
        title="Marcar como ganha"
        onClick={() => onSelect("ganha")}
        className="flex h-8 w-8 items-center justify-center rounded-lg border border-ev-positive/30 bg-ev-positive/10 text-ev-positive transition-colors hover:bg-ev-positive/20"
      >
        <IconCheck className="h-4 w-4" />
      </button>
      <button
        type="button"
        title="Marcar como perdida"
        onClick={() => onSelect("perdida")}
        className="flex h-8 w-8 items-center justify-center rounded-lg border border-ev-negative/30 bg-ev-negative/10 text-ev-negative transition-colors hover:bg-ev-negative/20"
      >
        <IconX className="h-4 w-4" />
      </button>
      <button
        type="button"
        title="Anular aposta"
        onClick={() => onSelect("anulada")}
        className="flex h-8 w-8 items-center justify-center rounded-lg border border-border bg-surface-hover text-muted transition-colors hover:text-foreground"
      >
        <IconBan className="h-4 w-4" />
      </button>
    </div>
  );
}
