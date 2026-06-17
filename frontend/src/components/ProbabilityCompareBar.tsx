"use client";

import { motion } from "framer-motion";

interface ProbabilityCompareBarProps {
  probModelo: number;
  probImplicita: number;
}

export function ProbabilityCompareBar({ probModelo, probImplicita }: ProbabilityCompareBarProps) {
  const modeloPct = probModelo * 100;
  const implicitaPct = probImplicita * 100;

  return (
    <div className="w-full space-y-2">
      <div className="flex items-center gap-2">
        <span className="w-16 shrink-0 text-[11px] text-muted">Modelo</span>
        <div className="relative h-2.5 flex-1 overflow-hidden rounded-full bg-surface-hover">
          <motion.div
            className="h-full rounded-full bg-gradient-primary"
            initial={{ width: 0 }}
            animate={{ width: `${modeloPct}%` }}
            transition={{ duration: 0.7, ease: "easeOut" }}
          />
        </div>
        <span className="w-12 shrink-0 text-right font-mono text-xs font-semibold text-primary">
          {modeloPct.toFixed(1)}%
        </span>
      </div>
      <div className="flex items-center gap-2">
        <span className="w-16 shrink-0 text-[11px] text-muted">Implícita</span>
        <div className="relative h-2.5 flex-1 overflow-hidden rounded-full bg-surface-hover">
          <motion.div
            className="h-full rounded-full bg-muted"
            initial={{ width: 0 }}
            animate={{ width: `${implicitaPct}%` }}
            transition={{ duration: 0.7, ease: "easeOut", delay: 0.1 }}
          />
        </div>
        <span className="w-12 shrink-0 text-right font-mono text-xs font-semibold text-muted">
          {implicitaPct.toFixed(1)}%
        </span>
      </div>
    </div>
  );
}
