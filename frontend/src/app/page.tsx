"use client";

import { useEffect, useMemo, useState } from "react";

import { fetchFixtures, fetchLeagues, type FixturePeriod } from "@/lib/api";
import { GameCard } from "@/components/GameCard";
import { GameCardSkeleton } from "@/components/Skeleton";
import { StatCard } from "@/components/StatCard";
import type { Fixture } from "@/types/fixture";
import type { League } from "@/types/odds";

const PERIOD_LABELS: Record<FixturePeriod, string> = {
  today: "Hoje",
  week: "7 dias",
  month: "30 dias",
};

export default function DashboardPage() {
  const [period, setPeriod] = useState<FixturePeriod>("today");
  const [leagueId, setLeagueId] = useState<number | "">("");
  const [pais, setPais] = useState<string>("");
  const [busca, setBusca] = useState("");
  const [leagues, setLeagues] = useState<League[]>([]);
  const [fixtures, setFixtures] = useState<Fixture[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchLeagues().then(setLeagues).catch(() => setLeagues([]));
  }, []);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    const timeout = setTimeout(() => {
      fetchFixtures({
        period,
        league: leagueId === "" ? undefined : leagueId,
        pais: pais || undefined,
        busca: busca || undefined,
      })
        .then((data) => {
          if (!cancelled) setFixtures(data);
        })
        .catch((err: Error) => {
          if (!cancelled) setError(err.message);
        })
        .finally(() => {
          if (!cancelled) setLoading(false);
        });
    }, 300);

    return () => {
      cancelled = true;
      clearTimeout(timeout);
    };
  }, [period, leagueId, pais, busca]);

  const countries = useMemo(
    () => Array.from(new Set(leagues.map((l) => l.pais))).sort(),
    [leagues]
  );

  const live = useMemo(
    () => fixtures.filter((f) => f.status === "em_andamento").length,
    [fixtures]
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Dashboard</h1>
        <p className="text-sm text-muted">Jogos monitorados e oportunidades de EV+.</p>
      </div>

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatCard label="Jogos no período" value={fixtures.length} accent="primary" format={(v) => v.toFixed(0)} />
        <StatCard label="Em andamento" value={live} accent="positive" format={(v) => v.toFixed(0)} />
        <StatCard label="Ligas disponíveis" value={leagues.length} accent="gold" format={(v) => v.toFixed(0)} />
        <StatCard label="Países" value={countries.length} accent="neutral" format={(v) => v.toFixed(0)} />
      </div>

      <div className="card-gradient-border rounded-xl border border-primary/30 bg-primary/5 p-4 text-xs text-foreground/80">
        <strong className="text-primary">BetAnalyzer</strong> identifica apostas com valor
        esperado positivo (EV+), comparando a probabilidade do modelo com a probabilidade
        implícita das odds sem a margem da casa. Isto não é garantia de resultado.
      </div>

      <div className="flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-end">
        <div className="scroll-hide -mx-4 flex gap-2 overflow-x-auto px-4 sm:mx-0 sm:overflow-visible sm:px-0">
          {(Object.keys(PERIOD_LABELS) as FixturePeriod[]).map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`min-h-[44px] shrink-0 whitespace-nowrap rounded-full border px-4 py-2 text-sm font-medium transition-colors ${
                period === p
                  ? "border-transparent bg-gradient-primary text-background shadow-glow"
                  : "border-border bg-surface text-muted hover:text-foreground"
              }`}
            >
              {PERIOD_LABELS[p]}
            </button>
          ))}
        </div>

        <select
          value={leagueId}
          onChange={(e) => setLeagueId(e.target.value === "" ? "" : Number(e.target.value))}
          className="min-h-[44px] w-full rounded-lg border border-border bg-surface px-3 py-2.5 text-sm text-foreground outline-none focus:border-primary sm:w-auto"
        >
          <option value="">Todas as ligas</option>
          {leagues.map((league) => (
            <option key={league.id} value={league.id}>
              {league.nome}
            </option>
          ))}
        </select>

        <select
          value={pais}
          onChange={(e) => setPais(e.target.value)}
          className="min-h-[44px] w-full rounded-lg border border-border bg-surface px-3 py-2.5 text-sm text-foreground outline-none focus:border-primary sm:w-auto"
        >
          <option value="">Todos os países</option>
          {countries.map((country) => (
            <option key={country} value={country}>
              {country}
            </option>
          ))}
        </select>

        <input
          type="text"
          placeholder="Buscar time..."
          value={busca}
          onChange={(e) => setBusca(e.target.value)}
          className="min-h-[44px] w-full flex-1 rounded-lg border border-border bg-surface px-3 py-2.5 text-sm text-foreground outline-none placeholder:text-muted focus:border-primary sm:min-w-[180px]"
        />
      </div>

      {error && (
        <div className="rounded-lg border border-ev-negative/30 bg-ev-negative/10 p-3 text-sm text-ev-negative">
          Erro ao carregar jogos: {error}
        </div>
      )}

      <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
        {loading
          ? Array.from({ length: 6 }).map((_, i) => <GameCardSkeleton key={i} />)
          : fixtures.map((fixture) => <GameCard key={fixture.id} fixture={fixture} />)}
      </div>

      {!loading && fixtures.length === 0 && !error && (
        <p className="py-8 text-center text-sm text-muted">
          Nenhum jogo encontrado para os filtros selecionados.
        </p>
      )}
    </div>
  );
}
