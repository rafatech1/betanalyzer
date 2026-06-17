"use client";

import { motion } from "framer-motion";

import { IconSparkles } from "@/components/icons";

export function ClaudeSummaryCard({ resumo }: { resumo: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      className="card-gradient-border rounded-xl border border-primary/30 bg-primary/5 p-4 sm:p-5"
    >
      <div className="flex items-center gap-2">
        <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-gradient-primary text-background shadow-glow">
          <IconSparkles className="h-3.5 w-3.5" />
        </span>
        <h3 className="text-xs font-semibold uppercase tracking-wide text-muted">
          Resumo da análise (IA)
        </h3>
      </div>
      <p className="mt-2.5 text-sm leading-relaxed text-foreground/80">{resumo}</p>
    </motion.div>
  );
}
