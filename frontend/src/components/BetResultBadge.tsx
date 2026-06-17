import type { ResultadoAposta } from "@/types/bet";

const LABELS: Record<ResultadoAposta, string> = {
  pendente: "Pendente",
  ganha: "Ganha",
  perdida: "Perdida",
  anulada: "Anulada",
  cashout: "Cashout",
};

const CLASS: Record<ResultadoAposta, string> = {
  pendente: "border-gold/30 bg-gold/15 text-gold",
  ganha: "border-ev-positive/30 bg-ev-positive/15 text-ev-positive shadow-glow-positive",
  perdida: "border-ev-negative/30 bg-ev-negative/15 text-ev-negative shadow-glow-negative",
  anulada: "border-border bg-surface-hover text-muted",
  cashout: "border-primary/30 bg-primary/15 text-primary",
};

export function BetResultBadge({ resultado }: { resultado: ResultadoAposta }) {
  return (
    <span
      className={`inline-flex items-center justify-center whitespace-nowrap rounded-full border px-2.5 py-1 text-xs font-semibold ${CLASS[resultado]}`}
    >
      {LABELS[resultado]}
    </span>
  );
}
