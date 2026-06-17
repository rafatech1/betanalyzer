"use client";

import { motion } from "framer-motion";

import { ConfidenceBadge } from "@/components/ConfidenceBadge";
import { EvBadge } from "@/components/EvBadge";
import { ProbabilityArc } from "@/components/ProbabilityArc";
import type { Analysis } from "@/types/analysis";

const RECOMENDACAO_LABELS: Record<Analysis["recomendacao"], string> = {
  apostar: "Apostar",
  observar: "Observar",
  evitar: "Evitar",
};

const RECOMENDACAO_CLASS: Record<Analysis["recomendacao"], string> = {
  apostar: "text-ev-positive",
  observar: "text-gold",
  evitar: "text-ev-negative",
};

export function AnalysisResultCard({ analysis }: { analysis: Analysis }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="card-gradient-border rounded-xl border border-border bg-surface p-5"
    >
      <div className="flex flex-wrap items-center justify-between gap-2">
        <span className="text-sm font-semibold">
          {analysis.mercado} · {analysis.selecao}
        </span>
        <div className="flex gap-2">
          <EvBadge ev={analysis.ev} />
          <ConfidenceBadge confianca={analysis.confianca} />
        </div>
      </div>

      <div className="mt-4 flex flex-col items-center gap-4 sm:flex-row sm:justify-between">
        <ProbabilityArc
          probEstimada={analysis.prob_estimada}
          probImplicita={analysis.prob_implicita}
        />

        <div className="grid w-full grid-cols-3 gap-2 text-center sm:w-auto sm:grid-cols-1 sm:gap-3 sm:text-right">
          <div>
            <p className="text-xs text-muted">Odd referência</p>
            <p className="font-mono text-base font-semibold">
              {analysis.odd_referencia.toFixed(2)}
            </p>
          </div>
          <div>
            <p className="text-xs text-muted">Recomendação</p>
            <p className={`text-base font-semibold ${RECOMENDACAO_CLASS[analysis.recomendacao]}`}>
              {RECOMENDACAO_LABELS[analysis.recomendacao]}
            </p>
          </div>
          <div>
            <p className="text-xs text-muted">Stake sugerido</p>
            <p className="font-mono text-base font-semibold text-primary">
              {(analysis.stake_sugerido * 100).toFixed(2)}%
            </p>
          </div>
        </div>
      </div>

      {analysis.resumo_ia && (
        <p className="mt-4 border-t border-border pt-3 text-sm leading-relaxed text-foreground/80">
          {analysis.resumo_ia}
        </p>
      )}
    </motion.div>
  );
}
