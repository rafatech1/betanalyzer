"use client";

import { motion } from "framer-motion";
import { useEffect, useRef, useState } from "react";

interface StatCardProps {
  label: string;
  value: number | null;
  format?: (value: number) => string;
  accent?: "primary" | "positive" | "negative" | "gold" | "neutral";
}

const ACCENT_CLASS: Record<NonNullable<StatCardProps["accent"]>, string> = {
  primary: "text-primary",
  positive: "text-ev-positive",
  negative: "text-ev-negative",
  gold: "text-gold",
  neutral: "text-foreground",
};

function useAnimatedNumber(target: number, durationMs = 700): number {
  const [value, setValue] = useState(0);
  const startRef = useRef<number | null>(null);
  const fromRef = useRef(0);

  useEffect(() => {
    fromRef.current = value;
    startRef.current = null;
    let rafId: number;

    function tick(timestamp: number) {
      if (startRef.current === null) startRef.current = timestamp;
      const progress = Math.min((timestamp - startRef.current) / durationMs, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setValue(fromRef.current + (target - fromRef.current) * eased);
      if (progress < 1) rafId = requestAnimationFrame(tick);
    }

    rafId = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(rafId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [target, durationMs]);

  return value;
}

export function StatCard({ label, value, format, accent = "neutral" }: StatCardProps) {
  const animated = useAnimatedNumber(value ?? 0);
  const display = value === null ? "—" : format ? format(animated) : animated.toFixed(2);

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="card-gradient-border rounded-xl border border-border bg-surface p-4"
    >
      <p className="text-xs text-muted">{label}</p>
      <p className={`mt-1 font-mono text-2xl font-semibold ${ACCENT_CLASS[accent]}`}>{display}</p>
    </motion.div>
  );
}
