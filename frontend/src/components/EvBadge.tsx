export function EvBadge({ ev }: { ev: number }) {
  const isPositive = ev > 0;
  const pct = (ev * 100).toFixed(1);

  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-1 font-mono text-xs font-semibold ${
        isPositive
          ? "bg-ev-positive/15 text-ev-positive shadow-glow-positive"
          : "bg-ev-negative/15 text-ev-negative shadow-glow-negative"
      }`}
    >
      EV {isPositive ? "+" : ""}
      {pct}%
    </span>
  );
}
