import type { NivelConfianca } from "@/types/analysis";

const LABELS: Record<NivelConfianca, string> = {
  baixa: "Confiança baixa",
  media: "Confiança média",
  alta: "Confiança alta",
};

const DOT_COLOR: Record<NivelConfianca, string> = {
  baixa: "bg-muted",
  media: "bg-gold",
  alta: "bg-ev-positive",
};

export function ConfidenceBadge({ confianca }: { confianca: NivelConfianca }) {
  return (
    <span className="inline-flex items-center gap-1.5 rounded-full border border-border bg-surface-hover px-2.5 py-1 text-xs text-foreground/80">
      <span className={`h-1.5 w-1.5 rounded-full ${DOT_COLOR[confianca]}`} />
      {LABELS[confianca]}
    </span>
  );
}
