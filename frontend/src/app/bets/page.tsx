"use client";

import { motion } from "framer-motion";
import { useEffect, useState } from "react";

import { createBet, fetchBetStats, fetchBets, updateBet } from "@/lib/api";
import { BankrollChart } from "@/components/BankrollChart";
import { StatCard } from "@/components/StatCard";
import type { Bet, BetStats, ResultadoAposta } from "@/types/bet";

const RESULTADO_LABELS: Record<ResultadoAposta, string> = {
  pendente: "Pendente",
  ganha: "Ganha",
  perdida: "Perdida",
  anulada: "Anulada",
  cashout: "Cashout",
};

const RESULTADO_DOT: Record<ResultadoAposta, string> = {
  pendente: "bg-gold",
  ganha: "bg-ev-positive",
  perdida: "bg-ev-negative",
  anulada: "bg-muted",
  cashout: "bg-primary",
};

export default function BetsPage() {
  const [bets, setBets] = useState<Bet[]>([]);
  const [stats, setStats] = useState<BetStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [form, setForm] = useState({
    fixture_id: "",
    mercado: "1x2",
    selecao: "",
    odd: "",
    stake: "",
  });
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
      setForm({ fixture_id: "", mercado: "1x2", selecao: "", odd: "", stake: "" });
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

  return (
    <div className="space-y-6">
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
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
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
            <StatCard
              label="Lucro acumulado"
              value={stats.lucro_acumulado}
              accent={stats.lucro_acumulado >= 0 ? "positive" : "negative"}
              format={(v) => v.toFixed(2)}
            />
          </div>

          <div className="card-gradient-border rounded-xl border border-border bg-surface p-4">
            <h2 className="mb-2 text-sm font-semibold text-foreground/80">Evolução da banca</h2>
            <BankrollChart evolucao={stats.evolucao} />
          </div>
        </>
      )}

      <form
        onSubmit={handleSubmit}
        className="grid grid-cols-2 gap-3 rounded-xl border border-border bg-surface p-4 sm:grid-cols-5"
      >
        <input
          required
          type="number"
          placeholder="ID do jogo"
          value={form.fixture_id}
          onChange={(e) => setForm({ ...form, fixture_id: e.target.value })}
          className="rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus:border-primary"
        />
        <input
          required
          placeholder="Mercado (ex: 1x2)"
          value={form.mercado}
          onChange={(e) => setForm({ ...form, mercado: e.target.value })}
          className="rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus:border-primary"
        />
        <input
          required
          placeholder="Seleção (ex: casa)"
          value={form.selecao}
          onChange={(e) => setForm({ ...form, selecao: e.target.value })}
          className="rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus:border-primary"
        />
        <input
          required
          type="number"
          step="0.01"
          placeholder="Odd"
          value={form.odd}
          onChange={(e) => setForm({ ...form, odd: e.target.value })}
          className="rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus:border-primary"
        />
        <input
          required
          type="number"
          step="0.01"
          placeholder="Stake"
          value={form.stake}
          onChange={(e) => setForm({ ...form, stake: e.target.value })}
          className="rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus:border-primary"
        />
        <motion.button
          whileTap={{ scale: 0.98 }}
          type="submit"
          disabled={submitting}
          className="col-span-2 rounded-lg bg-gradient-primary px-3 py-2 text-sm font-semibold text-background shadow-glow disabled:opacity-50 sm:col-span-5"
        >
          {submitting ? "Registrando..." : "Registrar aposta"}
        </motion.button>
      </form>

      <div className="overflow-x-auto rounded-xl border border-border bg-surface">
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
              bets.map((bet) => (
                <tr
                  key={bet.id}
                  className="border-b border-border last:border-0 hover:bg-surface-hover"
                >
                  <td className="px-4 py-3">
                    {bet.fixture
                      ? `${bet.fixture.time_casa} x ${bet.fixture.time_fora}`
                      : bet.fixture_id}
                  </td>
                  <td className="px-4 py-3 text-muted">
                    {bet.mercado} / {bet.selecao}
                  </td>
                  <td className="px-4 py-3 font-mono">{bet.odd.toFixed(2)}</td>
                  <td className="px-4 py-3 font-mono">{bet.stake.toFixed(2)}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <span className={`h-1.5 w-1.5 rounded-full ${RESULTADO_DOT[bet.resultado]}`} />
                      <select
                        value={bet.resultado}
                        onChange={(e) =>
                          handleResultChange(bet.id, e.target.value as ResultadoAposta)
                        }
                        className="rounded-md border border-border bg-background px-2 py-1 text-xs outline-none focus:border-primary"
                      >
                        {Object.entries(RESULTADO_LABELS).map(([value, label]) => (
                          <option key={value} value={value}>
                            {label}
                          </option>
                        ))}
                      </select>
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
        {!loading && bets.length === 0 && (
          <p className="p-6 text-center text-sm text-muted">Nenhuma aposta registrada ainda.</p>
        )}
      </div>
    </div>
  );
}
