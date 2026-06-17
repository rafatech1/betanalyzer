"use client";

import { motion } from "framer-motion";

export function ClaudeSummaryCard({ resumo }: { resumo: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      className="card-gradient-border rounded-xl border border-border bg-surface p-4"
    >
      <h3 className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-muted">
        Resumo da análise (IA)
      </h3>
      <p className="text-sm leading-relaxed text-foreground/80">{resumo}</p>
    </motion.div>
  );
}
