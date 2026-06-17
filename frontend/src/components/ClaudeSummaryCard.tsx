"use client";

import { motion } from "framer-motion";
import { useState } from "react";

import { IconSparkles } from "@/components/icons";

const COLLAPSE_THRESHOLD = 220;

export function ClaudeSummaryCard({ resumo }: { resumo: string }) {
  const [expanded, setExpanded] = useState(false);
  const canCollapse = resumo.length > COLLAPSE_THRESHOLD;

  return (
    <motion.div
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      className="card-gradient-border rounded-xl border border-primary/30 bg-primary/5 p-4 sm:p-5"
    >
      <div className="flex items-center gap-2.5">
        <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-gradient-primary text-background shadow-glow">
          <IconSparkles className="h-5 w-5" />
        </span>
        <h3 className="text-sm font-semibold uppercase tracking-wide text-muted">
          Resumo da análise (IA)
        </h3>
      </div>

      <p
        className={`mt-3 text-[15px] leading-relaxed text-foreground/80 ${
          expanded || !canCollapse ? "" : "line-clamp-3"
        }`}
      >
        {resumo}
      </p>

      {canCollapse && (
        <button
          type="button"
          onClick={() => setExpanded((value) => !value)}
          className="mt-1.5 text-xs font-semibold text-primary hover:underline"
        >
          {expanded ? "ver menos" : "ver mais"}
        </button>
      )}
    </motion.div>
  );
}
