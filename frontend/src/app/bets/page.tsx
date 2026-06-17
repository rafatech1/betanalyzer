"use client";

import { motion } from "framer-motion";
import { useEffect, useMemo, useState } from "react";

import { createBet, fetchBetStats, fetchBets, updateBet } from "@/lib/api";
import { BankrollChart } from "@/components/BankrollChart";
import { BetResultBadge } from "@/components/BetResultBadge";
import { BetResultQuickActions } from "@/components/BetResultQuickActions";
import { Drawer } from "@/components/Drawer";
import { IconPlus } from "@/components/icons";
import { StatCard } from "@/components/StatCard";
import type { Bet, BetStats, ResultadoAposta } from "@/types/bet";

type Filtro = "todas" | "pendente" | "ganha" | "perdida";

const FILTRO_LABELS: Record<Filtro, string> = {
  todas: "Todas",
  pendente: "Pendentes",
  ganha: "Ganhas",
  perdida: "Perdidas",
};

const EMPTY_FORM = { fixture_id: "", mercado: "1x2", selecao: "", odd: "", stake: "" };

export default function BetsPage() {
  const [bets, setBets] = useState<Bet[]>([]);
  const [stats, setStats] = useState<BetStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filtro, setFiltro] = useState<Filtro>("todas");

  const [drawerOpen, setDrawerOpen] = useState(false);
  const [form, setForm] = useState(EMPTY_FORM);
  const [submitting, setSubmitting] = useState(false);

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

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    try {
      await createBet({
        fixture_id: Number(form.fixture_id),
        mercado: form.mercado,
        selecao: form.selecao,
        odd: Number(form.odd),
        stake: Number(form.stake),
      });
      setForm(EMPTY_FORM);
      setDrawerOpen(false);
      await reload();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao registrar aposta");
    } finally {
      setSubmitting(false);
    }
  }

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
      <div className="flex items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Minhas apostas</h1>
          <p className="text-sm text-muted">Histórico, performance e evolução da banca.</p>
        </div>
        <button
          type="button"
          onClick={() => setDrawerOpen(true)}
          className="hidden min-h-[44px] items-center gap-2 rounded-lg bg-gradient-primary px-4 text-sm font-semibold text-background shadow-glow transition-opacity hover:opacity-90 lg:inline-flex"
        >
          <IconPlus className="h-4 w-4" />
          Nova aposta
        </button>
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

      {/* FAB (mobile) */}
      <motion.button
        whileTap={{ scale: 0.92 }}
        onClick={() => setDrawerOpen(true)}
        className="fixed bottom-20 right-4 z-30 flex h-14 w-14 items-center justify-center rounded-full bg-gradient-primary text-background shadow-glow lg:hidden"
      >
        <IconPlus className="h-6 w-6" />
      </motion.button>

      <Drawer open={drawerOpen} onClose={() => setDrawerOpen(false)} title="Nova aposta">
        <form onSubmit={handleSubmit} className="space-y-3">
          <div>
            <label className="mb-1.5 block text-xs text-muted">ID do jogo</label>
            <input
              required
              type="number"
              value={form.fixture_id}
              onChange={(e) => setForm({ ...form, fixture_id: e.target.value })}
              className="min-h-[44px] w-full rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus:border-primary"
            />
          </div>
          <div>
            <label className="mb-1.5 block text-xs text-muted">Mercado</label>
            <input
              required
              placeholder="ex: 1x2"
              value={form.mercado}
              onChange={(e) => setForm({ ...form, mercado: e.target.value })}
              className="min-h-[44px] w-full rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus:border-primary"
            />
          </div>
          <div>
            <label className="mb-1.5 block text-xs text-muted">Seleção</label>
            <input
              required
              placeholder="ex: casa"
              value={form.selecao}
              onChange={(e) => setForm({ ...form, selecao: e.target.value })}
              className="min-h-[44px] w-full rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus:border-primary"
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1.5 block text-xs text-muted">Odd</label>
              <input
                required
                type="number"
                step="0.01"
                value={form.odd}
                onChange={(e) => setForm({ ...form, odd: e.target.value })}
                className="min-h-[44px] w-full rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus:border-primary"
              />
            </div>
            <div>
              <label className="mb-1.5 block text-xs text-muted">Stake</label>
              <input
                required
                type="number"
                step="0.01"
                value={form.stake}
                onChange={(e) => setForm({ ...form, stake: e.target.value })}
                className="min-h-[44px] w-full rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus:border-primary"
              />
            </div>
          </div>

          <motion.button
            whileTap={{ scale: 0.98 }}
            type="submit"
            disabled={submitting}
            className="min-h-[44px] w-full rounded-lg bg-gradient-primary px-3 py-2 text-sm font-semibold text-background shadow-glow disabled:opacity-50"
          >
            {submitting ? "Registrando..." : "Registrar aposta"}
          </motion.button>
        </form>
      </Drawer>
    </div>
  );
}
