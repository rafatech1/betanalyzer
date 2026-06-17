import { ConfidenceBadge } from "@/components/ConfidenceBadge";
import { EvBadge } from "@/components/EvBadge";
import type { Analysis } from "@/types/analysis";

const RECOMENDACAO_LABELS: Record<Analysis["recomendacao"], string> = {
  apostar: "Apostar",
  observar: "Observar",
  evitar: "Evitar",
};

export function AnalysisResultCard({ analysis }: { analysis: Analysis }) {
  return (
    <div className="rounded-lg border border-foreground/10 bg-[#161616] p-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <span className="text-sm font-semibold">
          {analysis.mercado} · {analysis.selecao}
        </span>
        <div className="flex gap-2">
          <EvBadge ev={analysis.ev} />
          <ConfidenceBadge confianca={analysis.confianca} />
        </div>
      </div>

      <div className="mt-3 grid grid-cols-3 gap-2 text-center text-xs">
        <div>
          <p className="text-foreground/50">Prob. modelo</p>
          <p className="text-base font-semibold">{(analysis.prob_estimada * 100).toFixed(1)}%</p>
        </div>
        <div>
          <p className="text-foreground/50">Prob. implícita</p>
          <p className="text-base font-semibold">{(analysis.prob_implicita * 100).toFixed(1)}%</p>
        </div>
        <div>
          <p className="text-foreground/50">Odd referência</p>
          <p className="text-base font-semibold">{analysis.odd_referencia.toFixed(2)}</p>
        </div>
      </div>

      <div className="mt-3 flex items-center justify-between rounded-md bg-foreground/5 px-3 py-2 text-sm">
        <span className="text-foreground/70">{RECOMENDACAO_LABELS[analysis.recomendacao]}</span>
        <span className="font-semibold">
          Stake sugerido: {(analysis.stake_sugerido * 100).toFixed(2)}% da banca
        </span>
      </div>

      {analysis.resumo_ia && (
        <p className="mt-3 text-sm leading-relaxed text-foreground/80">{analysis.resumo_ia}</p>
      )}
    </div>
  );
}
