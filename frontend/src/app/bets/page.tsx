"use client";

import { motion } from "framer-motion";
import { useEffect, useMemo, useState } from "react";

import { fetchBetStats, fetchBets, updateBet } from "@/lib/api";
import { BankrollChart } from "@/components/BankrollChart";
import { BetResultBadge } from "@/components/BetResultBadge";
import { BetResultQuickActions } from "@/components/BetResultQuickActions";
import { StatCard } from "@/components/StatCard";
import type { Bet, BetStats, ResultadoAposta } from "@/types/bet";

type Filtro = "todas" | "pendente" | "ganha" | "perdida";

const FILTRO_LABELS: Record<Filtro, string> = {
  todas: "Todas",
  pendente: "Pendentes",
  ganha: "Ganhas",
  perdida: "Perdidas",
};

export default function BetsPage() {
  const [bets, setBets] = useState<Bet[]>([]);
  const [stats, setStats] = useState<BetStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filtro, setFiltro] = useState<Filtro>("todas");

  async function reload() {
    setLoading(true);
    try {
      const [betsData, statsData] = await Promise.all([fetchBets(), fetchBetStats()]);
      setBets(betsData);
      setStats(statsData);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao carregar apostas");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    reload();
  }, []);

  async function handleResultChange(betId: number, resultado: ResultadoAposta) {
    try {
      await updateBet(betId, { resultado });
      await reload();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao atualizar aposta");
    }
  }

  const filteredBets = useMemo(
    () => (filtro === "todas" ? bets : bets.filter((bet) => bet.resultado === filtro)),
    [bets, filtro]
  );

  return (
    <div className="space-y-6 pb-4">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Minhas apostas</h1>
        <p className="text-sm text-muted">Histórico, performance e evolução da banca.</p>
      </div>

      {error && (
        <p className="rounded-lg border border-ev-negative/30 bg-ev-negative/10 p-3 text-sm text-ev-negative">
          {error}
        </p>
      )}

      {stats && (
        <>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
            <StatCard
              label="Total apostado"
              value={stats.total_investido}
              accent="primary"
              format={(v) => v.toFixed(2)}
            />
            <StatCard
              label="Lucro/Prejuízo"
              value={stats.lucro_acumulado}
              accent={stats.lucro_acumulado >= 0 ? "positive" : "negative"}
              format={(v) => v.toFixed(2)}
            />
            <StatCard
              label="ROI"
              value={stats.roi}
              accent={stats.roi !== null && stats.roi >= 0 ? "positive" : "negative"}
              format={(v) => `${(v * 100).toFixed(1)}%`}
            />
            <StatCard
              label="Yield"
              value={stats.yield_}
              accent={stats.yield_ !== null && stats.yield_ >= 0 ? "positive" : "negative"}
              format={(v) => `${(v * 100).toFixed(1)}%`}
            />
            <StatCard
              label="Taxa de acerto"
              value={stats.taxa_acerto}
              accent="gold"
              format={(v) => `${(v * 100).toFixed(1)}%`}
            />
          </div>

          <div className="card-gradient-border rounded-xl border border-border bg-surface p-4">
            <h2 className="mb-2 text-sm font-semibold text-foreground/80">Evolução da banca</h2>
            <BankrollChart evolucao={stats.evolucao} />
          </div>
        </>
      )}

      <div className="scroll-hide -mx-4 flex gap-2 overflow-x-auto px-4 sm:mx-0 sm:overflow-visible sm:px-0">
        {(Object.keys(FILTRO_LABELS) as Filtro[]).map((f) => (
          <button
            key={f}
            onClick={() => setFiltro(f)}
            className={`min-h-[44px] shrink-0 whitespace-nowrap rounded-full border px-4 py-2 text-sm font-medium transition-colors ${
              filtro === f
                ? "border-transparent bg-gradient-primary text-background shadow-glow"
                : "border-border bg-surface text-muted hover:text-foreground"
            }`}
          >
            {FILTRO_LABELS[f]}
          </button>
        ))}
      </div>

      {/* Tabela (tablet/desktop) */}
      <div className="hidden overflow-x-auto rounded-xl border border-border bg-surface md:block">
        <table className="w-full text-sm">
          <thead className="text-left text-xs text-muted">
            <tr className="border-b border-border">
              <th className="px-4 py-3 font-medium">Jogo</th>
              <th className="px-4 py-3 font-medium">Mercado/Seleção</th>
              <th className="px-4 py-3 font-medium">Odd</th>
              <th className="px-4 py-3 font-medium">Stake</th>
              <th className="px-4 py-3 font-medium">Resultado</th>
              <th className="px-4 py-3 font-medium">Lucro</th>
            </tr>
          </thead>
          <tbody>
            {!loading &&
              filteredBets.map((bet) => (
                <tr
                  key={bet.id}
                  className="border-b border-border last:border-0 hover:bg-surface-hover"
                >
                  <td className="px-4 py-3">
                    {bet.fixture
                      ? `${bet.fixture.time_casa} x ${bet.fixture.time_fora}`
                      : `Jogo #${bet.fixture_id}`}
                  </td>
                  <td className="px-4 py-3 text-muted">
                    {bet.mercado} / {bet.selecao}
                  </td>
                  <td className="px-4 py-3 font-mono">{bet.odd.toFixed(2)}</td>
                  <td className="px-4 py-3 font-mono">{bet.stake.toFixed(2)}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <BetResultBadge resultado={bet.resultado} />
                      {bet.resultado === "pendente" && (
                        <BetResultQuickActions
                          onSelect={(resultado) => handleResultChange(bet.id, resultado)}
                        />
                      )}
                    </div>
                  </td>
                  <td
                    className={`px-4 py-3 font-mono font-semibold ${
                      bet.lucro && bet.lucro > 0
                        ? "text-ev-positive"
                        : bet.lucro && bet.lucro < 0
                          ? "text-ev-negative"
                          : "text-muted"
                    }`}
                  >
                    {bet.lucro !== null ? bet.lucro.toFixed(2) : "—"}
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
        {!loading && filteredBets.length === 0 && (
          <p className="p-6 text-center text-sm text-muted">
            {bets.length === 0
              ? "Nenhuma aposta registrada ainda."
              : "Nenhuma aposta encontrada para este filtro."}
          </p>
        )}
      </div>

      {/* Cards (mobile) */}
      <div className="space-y-3 md:hidden">
        {!loading &&
          filteredBets.map((bet) => (
            <motion.div
              key={bet.id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              className="card-gradient-border rounded-xl border border-border bg-surface p-4"
            >
              <div className="flex items-center justify-between gap-2">
                <span className="truncate text-sm font-medium text-foreground">
                  {bet.fixture
                    ? `${bet.fixture.time_casa} x ${bet.fixture.time_fora}`
                    : `Jogo #${bet.fixture_id}`}
                </span>
                <BetResultBadge resultado={bet.resultado} />
              </div>
              <p className="mt-1 text-xs text-muted">
                {bet.mercado} / {bet.selecao}
              </p>

              <div className="mt-3 grid grid-cols-3 gap-2 text-center">
                <div>
                  <p className="text-[11px] text-muted">Odd</p>
                  <p className="font-mono text-sm font-semibold text-foreground">
                    {bet.odd.toFixed(2)}
                  </p>
                </div>
                <div>
                  <p className="text-[11px] text-muted">Stake</p>
                  <p className="font-mono text-sm font-semibold text-foreground">
                    {bet.stake.toFixed(2)}
                  </p>
                </div>
                <div>
                  <p className="text-[11px] text-muted">Lucro</p>
                  <p
                    className={`font-mono text-sm font-semibold ${
                      bet.lucro && bet.lucro > 0
                        ? "text-ev-positive"
                        : bet.lucro && bet.lucro < 0
                          ? "text-ev-negative"
                          : "text-muted"
                    }`}
                  >
                    {bet.lucro !== null ? bet.lucro.toFixed(2) : "—"}
                  </p>
                </div>
              </div>

              {bet.resultado === "pendente" && (
                <div className="mt-3 flex justify-end border-t border-border pt-3">
                  <BetResultQuickActions
                    onSelect={(resultado) => handleResultChange(bet.id, resultado)}
                  />
                </div>
              )}
            </motion.div>
          ))}
        {!loading && filteredBets.length === 0 && (
          <p className="rounded-xl border border-border bg-surface p-6 text-center text-sm text-muted">
            {bets.length === 0
              ? "Nenhuma aposta registrada ainda."
              : "Nenhuma aposta encontrada para este filtro."}
          </p>
        )}
      </div>
    </div>
  );
}
