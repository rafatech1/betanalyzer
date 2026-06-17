"use client";

import { motion } from "framer-motion";

interface ProbabilityArcProps {
  probEstimada: number;
  probImplicita: number;
}

const RADIUS = 54;
const STROKE = 10;
const CIRCUMFERENCE = Math.PI * RADIUS;

function arcOffset(fraction: number): number {
  return CIRCUMFERENCE * (1 - Math.min(Math.max(fraction, 0), 1));
}

export function ProbabilityArc({ probEstimada, probImplicita }: ProbabilityArcProps) {
  const diff = probEstimada - probImplicita;
  const diffColor = diff > 0 ? "text-ev-positive" : diff < 0 ? "text-ev-negative" : "text-muted";

  return (
    <div className="flex flex-col items-center">
      <svg width="160" height="92" viewBox="0 0 160 92">
        <path
          d="M 8 84 A 72 72 0 0 1 152 84"
          fill="none"
          stroke="#1E2D4A"
          strokeWidth={STROKE}
          strokeLinecap="round"
        />
        <motion.path
          d="M 8 84 A 72 72 0 0 1 152 84"
          fill="none"
          stroke="#8896B3"
          strokeWidth={STROKE}
          strokeLinecap="round"
          strokeDasharray={CIRCUMFERENCE}
          initial={{ strokeDashoffset: CIRCUMFERENCE }}
          animate={{ strokeDashoffset: arcOffset(probImplicita) }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          opacity={0.55}
        />
        <motion.path
          d="M 8 84 A 72 72 0 0 1 152 84"
          fill="none"
          stroke={diff >= 0 ? "#00D4AA" : "#FF4D6A"}
          strokeWidth={STROKE}
          strokeLinecap="round"
          strokeDasharray={CIRCUMFERENCE}
          initial={{ strokeDashoffset: CIRCUMFERENCE }}
          animate={{ strokeDashoffset: arcOffset(probEstimada) }}
          transition={{ duration: 0.8, ease: "easeOut", delay: 0.15 }}
        />
      </svg>
      <div className="-mt-10 text-center">
        <p className="font-mono text-2xl font-bold text-foreground">
          {(probEstimada * 100).toFixed(1)}%
        </p>
        <p className="text-[11px] text-muted">prob. modelo</p>
      </div>
      <p className={`mt-2 font-mono text-xs font-semibold ${diffColor}`}>
        {diff > 0 ? "+" : ""}
        {(diff * 100).toFixed(1)}pp vs. implícita ({(probImplicita * 100).toFixed(1)}%)
      </p>
    </div>
  );
}
