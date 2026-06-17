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
    return <p className="text-sm text-foreground/50">Nenhuma odd disponível ainda.</p>;
  }

  return (
    <div className="space-y-4">
      {Array.from(byMarket.entries()).map(([mercado, rows]) => (
        <div key={mercado}>
          <h3 className="mb-2 text-sm font-semibold text-foreground/80">
            {MARKET_LABELS[mercado] ?? mercado}
          </h3>
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
            {rows.map((row) => (
              <div
                key={row.id}
                className="rounded-md border border-foreground/10 bg-[#161616] p-2 text-center"
              >
                <p className="text-xs text-foreground/50">{row.selecao}</p>
                <p className="text-lg font-semibold">{row.odd.toFixed(2)}</p>
                <p className="text-[10px] text-foreground/40">
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
