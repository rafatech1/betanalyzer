export function EvBadge({ ev }: { ev: number }) {
  const isPositive = ev > 0;
  const pct = (ev * 100).toFixed(1);

  return (
    <span
      className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-semibold ${
        isPositive
          ? "bg-ev-positive/15 text-ev-positive"
          : "bg-ev-negative/15 text-ev-negative"
      }`}
    >
      EV {isPositive ? "+" : ""}
      {pct}%
    </span>
  );
}
