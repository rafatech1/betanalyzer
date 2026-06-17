import type { Analysis } from "@/types/analysis";

const LABELS: Record<Analysis["recomendacao"], string> = {
  apostar: "Apostar",
  observar: "Observar",
  evitar: "Evitar",
};

const CLASS: Record<Analysis["recomendacao"], string> = {
  apostar: "border-ev-positive/30 bg-ev-positive/15 text-ev-positive shadow-glow-positive",
  observar: "border-gold/30 bg-gold/15 text-gold shadow-glow-gold",
  evitar: "border-ev-negative/30 bg-ev-negative/15 text-ev-negative shadow-glow-negative",
};

export function RecommendationBadge({
  recomendacao,
}: {
  recomendacao: Analysis["recomendacao"];
}) {
  return (
    <span
      className={`inline-flex items-center justify-center rounded-full border px-3 py-1 text-xs font-semibold ${CLASS[recomendacao]}`}
    >
      {LABELS[recomendacao]}
    </span>
  );
}
