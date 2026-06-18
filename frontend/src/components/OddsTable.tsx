"use client";

import type { Odds } from "@/types/odds";

const MARKET_LABELS: Record<string, string> = {
  "1x2": "Resultado final (1X2)",
  "over_under_2.5": "Mais/menos de 2.5 gols",
  ambas_marcam: "Ambas marcam",
};

const SELECTION_LABELS: Record<string, string> = {
  casa: "Casa",
  empate: "Empate",
  fora: "Fora",
  "mais_2.5": "Mais de 2.5",
  "menos_2.5": "Menos de 2.5",
};

const ORDER_1X2 = ["casa", "empate", "fora"];
const ORDER_OVER_UNDER = ["mais_2.5", "menos_2.5"];

function sortBySelectionOrder(rows: Odds[], order: string[]): Odds[] {
  return [...rows].sort((a, b) => order.indexOf(a.selecao) - order.indexOf(b.selecao));
}

export function oddKey(row: Odds): string {
  return `${row.mercado}:${row.selecao}`;
}

function OddCard({ row, highlighted, flash }: { row: Odds; highlighted: boolean; flash: boolean }) {
  return (
    <div
      className={`card-gradient-border relative rounded-xl border p-3 text-center transition-colors duration-300 sm:p-4 ${
        flash
          ? "border-primary bg-primary/20 shadow-glow"
          : highlighted
            ? "border-primary/50 bg-primary/10 shadow-glow"
            : "border-border bg-surface hover:bg-surface-hover"
      }`}
    >
      <p className="truncate text-xs font-medium text-muted">
        {SELECTION_LABELS[row.selecao] ?? row.selecao}
      </p>
      <p
        className={`mt-1 font-mono text-2xl font-bold sm:text-3xl ${
          highlighted ? "text-primary" : "text-foreground"
        }`}
      >
        {row.odd.toFixed(2)}
      </p>
      <div className="mt-2 flex flex-wrap items-center justify-center gap-1.5">
        <span className="truncate rounded-full border border-border bg-background/60 px-2 py-0.5 text-[10px] text-muted">
          {row.casa_de_aposta}
        </span>
        <span className="rounded-full bg-surface-hover px-2 py-0.5 text-[10px] font-mono text-muted">
          {(row.prob_implicita * 100).toFixed(1)}%
        </span>
      </div>
    </div>
  );
}

function MarketGroup({
  title,
  rows,
  gridClassName,
  flashKeys,
}: {
  title: string;
  rows: Odds[];
  gridClassName: string;
  flashKeys: Set<string>;
}) {
  if (rows.length === 0) return null;
  const minOdd = Math.min(...rows.map((row) => row.odd));

  return (
    <div>
      <h3 className="mb-3 text-sm font-semibold text-foreground/80">{title}</h3>
      <div className={gridClassName}>
        {rows.map((row) => (
          <OddCard
            key={row.id}
            row={row}
            highlighted={row.odd === minOdd}
            flash={flashKeys.has(oddKey(row))}
          />
        ))}
      </div>
    </div>
  );
}

export function OddsTable({
  odds,
  updatedAt,
  flashKeys = new Set(),
}: {
  odds: Odds[];
  updatedAt?: Date | null;
  flashKeys?: Set<string>;
}) {
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
    return (
      <p className="rounded-xl border border-border bg-surface p-6 text-center text-sm text-muted">
        Nenhuma odd disponível ainda.
      </p>
    );
  }

  const market1x2 = byMarket.get("1x2");
  const marketOverUnder = byMarket.get("over_under_2.5");
  const otherMarkets = Array.from(byMarket.entries()).filter(
    ([mercado]) => mercado !== "1x2" && mercado !== "over_under_2.5"
  );

  return (
    <div className="space-y-3">
      <div className="space-y-6">
        {market1x2 && (
          <MarketGroup
            title={MARKET_LABELS["1x2"]}
            rows={sortBySelectionOrder(market1x2, ORDER_1X2)}
            gridClassName="grid grid-cols-3 gap-2 sm:gap-3"
            flashKeys={flashKeys}
          />
        )}
        {marketOverUnder && (
          <MarketGroup
            title={MARKET_LABELS["over_under_2.5"]}
            rows={sortBySelectionOrder(marketOverUnder, ORDER_OVER_UNDER)}
            gridClassName="grid grid-cols-2 gap-2 sm:gap-3"
            flashKeys={flashKeys}
          />
        )}
        {otherMarkets.map(([mercado, rows]) => (
          <MarketGroup
            key={mercado}
            title={MARKET_LABELS[mercado] ?? mercado}
            rows={rows}
            gridClassName="grid grid-cols-2 gap-2 sm:grid-cols-3 sm:gap-3"
            flashKeys={flashKeys}
          />
        ))}
      </div>

      {updatedAt && (
        <p className="text-right text-[11px] text-muted">
          Atualizado às{" "}
          {updatedAt.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })}
        </p>
      )}
    </div>
  );
}
