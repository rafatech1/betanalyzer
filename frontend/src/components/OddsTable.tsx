import type { Odds } from "@/types/odds";

const MARKET_LABELS: Record<string, string> = {
  "1x2": "Resultado final (1X2)",
  "over_under_2.5": "Mais/menos de 2.5 gols",
  ambas_marcam: "Ambas marcam",
};

export function OddsTable({ odds }: { odds: Odds[] }) {
  const latestBySelection = new Map<string, Odds>();
  for (const row of odds) {
    const key = `${row.mercado}:${row.selecao}`;
    const existing = latestBySelection.get(key);
    if (!existing || new Date(row.timestamp) > new Date(existing.timestamp)) {
      latestBySelection.set(key, row);
    }
  }

  const byMarket = new Map<string, Odds[]>();
  for (const row of latestBySelection.values()) {
    const list = byMarket.get(row.mercado) ?? [];
    list.push(row);
    byMarket.set(row.mercado, list);
  }

  if (byMarket.size === 0) {
    return <p className="text-sm text-muted">Nenhuma odd disponível ainda.</p>;
  }

  return (
    <div className="grid gap-4 lg:grid-cols-2">
      {Array.from(byMarket.entries()).map(([mercado, rows]) => (
        <div key={mercado}>
          <h3 className="mb-2 text-sm font-semibold text-foreground/80">
            {MARKET_LABELS[mercado] ?? mercado}
          </h3>
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
            {rows.map((row) => (
              <div
                key={row.id}
                className="card-gradient-border rounded-lg border border-border bg-surface p-3 text-center transition-colors hover:bg-surface-hover"
              >
                <p className="text-xs text-muted">{row.selecao}</p>
                <p className="font-mono text-lg font-semibold text-foreground">
                  {row.odd.toFixed(2)}
                </p>
                <p className="mt-0.5 text-[10px] text-muted">
                  {row.casa_de_aposta} · prob. impl. {(row.prob_implicita * 100).toFixed(1)}%
                </p>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
