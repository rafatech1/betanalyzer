import type { NivelConfianca } from "@/types/analysis";

const LABELS: Record<NivelConfianca, string> = {
  baixa: "Confiança baixa",
  media: "Confiança média",
  alta: "Confiança alta",
};

export function ConfidenceBadge({ confianca }: { confianca: NivelConfianca }) {
  return (
    <span className="inline-flex items-center rounded-full border border-foreground/20 bg-foreground/5 px-2 py-0.5 text-xs text-foreground/80">
      {LABELS[confianca]}
    </span>
  );
}
