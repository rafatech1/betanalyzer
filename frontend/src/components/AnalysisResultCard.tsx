"use client";

import { motion } from "framer-motion";

import { ConfidenceBadge } from "@/components/ConfidenceBadge";
import { EvBadge } from "@/components/EvBadge";
import { ProbabilityArc } from "@/components/ProbabilityArc";
import { ProbabilityCompareBar } from "@/components/ProbabilityCompareBar";
import { RecommendationBadge } from "@/components/RecommendationBadge";
import type { Analysis } from "@/types/analysis";

export function AnalysisResultCard({
  analysis,
  index = 0,
}: {
  analysis: Analysis;
  index?: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay: index * 0.06 }}
      className="card-gradient-border flex flex-col rounded-xl border border-border bg-surface p-5"
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

      <div className="mt-4 flex justify-center">
        <ProbabilityArc
          probEstimada={analysis.prob_estimada}
          probImplicita={analysis.prob_implicita}
        />
      </div>

      <div className="mt-2">
        <ProbabilityCompareBar
          probModelo={analysis.prob_estimada}
          probImplicita={analysis.prob_implicita}
        />
      </div>

      <div className="mt-5 grid grid-cols-3 items-end gap-3 border-t border-border pt-4 text-center">
        <div>
          <p className="text-xs text-muted">Odd referência</p>
          <p className="font-mono text-2xl font-bold text-foreground">
            {analysis.odd_referencia.toFixed(2)}
          </p>
        </div>
        <div>
          <p className="mb-1.5 text-xs text-muted">Recomendação</p>
          <RecommendationBadge recomendacao={analysis.recomendacao} />
        </div>
        <div>
          <p className="text-xs text-muted">Stake sugerido</p>
          <p className="font-mono text-lg font-semibold text-primary">
            {(analysis.stake_sugerido * 100).toFixed(2)}%
          </p>
        </div>
      </div>
    </motion.div>
  );
}
