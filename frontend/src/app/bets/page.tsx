"use client";

import { useEffect, useState } from "react";

import { createBet, fetchBetStats, fetchBets, updateBet } from "@/lib/api";
import { BankrollChart } from "@/components/BankrollChart";
import type { Bet, BetStats, ResultadoAposta } from "@/types/bet";

const RESULTADO_LABELS: Record<ResultadoAposta, string> = {
  pendente: "Pendente",
  ganha: "Ganha",
  perdida: "Perdida",
  anulada: "Anulada",
  cashout: "Cashout",
};

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-foreground/10 bg-[#161616] p-3 text-center">
      <p className="text-xs text-foreground/50">{label}</p>
      <p className="mt-1 text-lg font-semibold">{value}</p>
    </div>
  );
}

function formatPct(value: number | null): string {
  return value === null ? "—" : `${(value * 100).toFixed(1)}%`;
}

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
      <h1 className="text-xl font-bold">Minhas apostas</h1>

      {error && <p className="text-sm text-ev-negative">{error}</p>}

      {stats && (
        <>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            <StatCard label="ROI" value={formatPct(stats.roi)} />
            <StatCard label="Yield" value={formatPct(stats.yield_)} />
            <StatCard label="Taxa de acerto" value={formatPct(stats.taxa_acerto)} />
            <StatCard label="Lucro acumulado" value={stats.lucro_acumulado.toFixed(2)} />
          </div>

          <div className="rounded-lg border border-foreground/10 bg-[#161616] p-4">
            <h2 className="mb-2 text-sm font-semibold text-foreground/80">Evolução da banca</h2>
            <BankrollChart evolucao={stats.evolucao} />
          </div>
        </>
      )}

      <form
        onSubmit={handleSubmit}
        className="grid grid-cols-2 gap-3 rounded-lg border border-foreground/10 bg-[#161616] p-4 sm:grid-cols-5"
      >
        <input
          required
          type="number"
          placeholder="ID do jogo"
          value={form.fixture_id}
          onChange={(e) => setForm({ ...form, fixture_id: e.target.value })}
          className="rounded-md border border-foreground/20 bg-background px-2 py-1.5 text-sm"
        />
        <input
          required
          placeholder="Mercado (ex: 1x2)"
          value={form.mercado}
          onChange={(e) => setForm({ ...form, mercado: e.target.value })}
          className="rounded-md border border-foreground/20 bg-background px-2 py-1.5 text-sm"
        />
        <input
          required
          placeholder="Seleção (ex: casa)"
          value={form.selecao}
          onChange={(e) => setForm({ ...form, selecao: e.target.value })}
          className="rounded-md border border-foreground/20 bg-background px-2 py-1.5 text-sm"
        />
        <input
          required
          type="number"
          step="0.01"
          placeholder="Odd"
          value={form.odd}
          onChange={(e) => setForm({ ...form, odd: e.target.value })}
          className="rounded-md border border-foreground/20 bg-background px-2 py-1.5 text-sm"
        />
        <input
          required
          type="number"
          step="0.01"
          placeholder="Stake"
          value={form.stake}
          onChange={(e) => setForm({ ...form, stake: e.target.value })}
          className="rounded-md border border-foreground/20 bg-background px-2 py-1.5 text-sm"
        />
        <button
          type="submit"
          disabled={submitting}
          className="col-span-2 rounded-md bg-primary px-3 py-1.5 text-sm font-semibold text-black disabled:opacity-50 sm:col-span-5"
        >
          {submitting ? "Registrando..." : "Registrar aposta"}
        </button>
      </form>

      <div className="overflow-x-auto rounded-lg border border-foreground/10">
        <table className="w-full text-sm">
          <thead className="bg-foreground/5 text-left text-xs text-foreground/60">
            <tr>
              <th className="px-3 py-2">Jogo</th>
              <th className="px-3 py-2">Mercado/Seleção</th>
              <th className="px-3 py-2">Odd</th>
              <th className="px-3 py-2">Stake</th>
              <th className="px-3 py-2">Resultado</th>
              <th className="px-3 py-2">Lucro</th>
            </tr>
          </thead>
          <tbody>
            {!loading &&
              bets.map((bet) => (
                <tr key={bet.id} className="border-t border-foreground/10">
                  <td className="px-3 py-2">
                    {bet.fixture ? `${bet.fixture.time_casa} x ${bet.fixture.time_fora}` : bet.fixture_id}
                  </td>
                  <td className="px-3 py-2">
                    {bet.mercado} / {bet.selecao}
                  </td>
                  <td className="px-3 py-2">{bet.odd.toFixed(2)}</td>
                  <td className="px-3 py-2">{bet.stake.toFixed(2)}</td>
                  <td className="px-3 py-2">
                    <select
                      value={bet.resultado}
                      onChange={(e) =>
                        handleResultChange(bet.id, e.target.value as ResultadoAposta)
                      }
                      className="rounded-md border border-foreground/20 bg-background px-2 py-1 text-xs"
                    >
                      {Object.entries(RESULTADO_LABELS).map(([value, label]) => (
                        <option key={value} value={value}>
                          {label}
                        </option>
                      ))}
                    </select>
                  </td>
                  <td
                    className={`px-3 py-2 font-semibold ${
                      bet.lucro && bet.lucro > 0
                        ? "text-ev-positive"
                        : bet.lucro && bet.lucro < 0
                          ? "text-ev-negative"
                          : ""
                    }`}
                  >
                    {bet.lucro !== null ? bet.lucro.toFixed(2) : "—"}
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
        {!loading && bets.length === 0 && (
          <p className="p-4 text-center text-sm text-foreground/50">
            Nenhuma aposta registrada ainda.
          </p>
        )}
      </div>
    </div>
  );
}
