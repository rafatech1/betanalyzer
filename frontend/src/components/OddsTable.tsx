"use client";

import { useState } from "react";

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

function buildBookmakerRows(
  marketRows: Odds[],
  selections: string[]
): { casa_de_aposta: string; odds: Map<string, number | undefined> }[] {
  const latestByBookmaker = new Map<string, Map<string, Odds>>();
  for (const row of marketRows) {
    let bySelecao = latestByBookmaker.get(row.casa_de_aposta);
    if (!bySelecao) {
      bySelecao = new Map();
      latestByBookmaker.set(row.casa_de_aposta, bySelecao);
    }
    const existing = bySelecao.get(row.selecao);
    if (!existing || new Date(row.timestamp) > new Date(existing.timestamp)) {
      bySelecao.set(row.selecao, row);
    }
  }

  return Array.from(latestByBookmaker.entries())
    .map(([casa_de_aposta, bySelecao]) => ({
      casa_de_aposta,
      odds: new Map(selections.map((s) => [s, bySelecao.get(s)?.odd] as const)),
    }))
    .filter((entry) => Array.from(entry.odds.values()).some((v) => v !== undefined))
    .sort((a, b) => a.casa_de_aposta.localeCompare(b.casa_de_aposta));
}

function BookmakerComparisonTable({
  marketRows,
  selections,
}: {
  marketRows: Odds[];
  selections: string[];
}) {
  const bookmakerRows = buildBookmakerRows(marketRows, selections);
  if (bookmakerRows.length === 0) return null;

  const bestBySelection = new Map<string, number>();
  for (const selecao of selections) {
    const values = bookmakerRows
      .map((row) => row.odds.get(selecao))
      .filter((v): v is number => v !== undefined);
    if (values.length > 0) bestBySelection.set(selecao, Math.max(...values));
  }

  return (
    <div className="mt-3 overflow-x-auto rounded-xl border border-border">
      <table className="w-full text-sm">
        <thead className="bg-surface-hover text-left text-xs text-muted">
          <tr>
            <th className="px-3 py-2 font-medium">Casa de aposta</th>
            {selections.map((selecao) => (
              <th key={selecao} className="px-3 py-2 text-center font-medium">
                {SELECTION_LABELS[selecao] ?? selecao}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {bookmakerRows.map((row) => (
            <tr key={row.casa_de_aposta} className="border-t border-border">
              <td className="px-3 py-2 text-foreground">{row.casa_de_aposta}</td>
              {selections.map((selecao) => {
                const value = row.odds.get(selecao);
                const isBest = value !== undefined && value === bestBySelection.get(selecao);
                return (
                  <td
                    key={selecao}
                    className={`px-3 py-2 text-center font-mono ${
                      isBest ? "font-bold text-ev-positive" : "text-foreground"
                    }`}
                  >
                    {value !== undefined ? value.toFixed(2) : "—"}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function MarketGroup({
  title,
  rows,
  gridClassName,
  flashKeys,
  marketRows,
  selections,
}: {
  title: string;
  rows: Odds[];
  gridClassName: string;
  flashKeys: Set<string>;
  marketRows: Odds[];
  selections: string[];
}) {
  const [expanded, setExpanded] = useState(false);
  if (rows.length === 0) return null;
  const minOdd = Math.min(...rows.map((row) => row.odd));
  const bookmakerCount = new Set(marketRows.map((row) => row.casa_de_aposta)).size;

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

      {bookmakerCount > 1 && (
        <button
          type="button"
          onClick={() => setExpanded((prev) => !prev)}
          className="mt-3 text-xs font-medium text-primary hover:underline"
        >
          {expanded ? "Ocultar casas de aposta" : "Ver todas as casas"}
        </button>
      )}

      {expanded && <BookmakerComparisonTable marketRows={marketRows} selections={selections} />}
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

  const rawByMarket = new Map<string, Odds[]>();
  for (const row of odds) {
    const list = rawByMarket.get(row.mercado) ?? [];
    list.push(row);
    rawByMarket.set(row.mercado, list);
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
            marketRows={rawByMarket.get("1x2") ?? []}
            selections={ORDER_1X2}
          />
        )}
        {marketOverUnder && (
          <MarketGroup
            title={MARKET_LABELS["over_under_2.5"]}
            rows={sortBySelectionOrder(marketOverUnder, ORDER_OVER_UNDER)}
            gridClassName="grid grid-cols-2 gap-2 sm:gap-3"
            flashKeys={flashKeys}
            marketRows={rawByMarket.get("over_under_2.5") ?? []}
            selections={ORDER_OVER_UNDER}
          />
        )}
        {otherMarkets.map(([mercado, rows]) => (
          <MarketGroup
            key={mercado}
            title={MARKET_LABELS[mercado] ?? mercado}
            rows={rows}
            gridClassName="grid grid-cols-2 gap-2 sm:grid-cols-3 sm:gap-3"
            flashKeys={flashKeys}
            marketRows={rawByMarket.get(mercado) ?? []}
            selections={Array.from(new Set(rows.map((r) => r.selecao)))}
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
