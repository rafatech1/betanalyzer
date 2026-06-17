"use client";

import { useEffect, useMemo, useState } from "react";

import { fetchFixtures, fetchLeagues, type FixturePeriod } from "@/lib/api";
import { GameCard } from "@/components/GameCard";
import { GameCardSkeleton } from "@/components/Skeleton";
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

  return (
    <div className="space-y-6">
      <div className="rounded-lg border border-primary/40 bg-primary/10 p-3 text-xs text-foreground/80">
        <strong className="text-primary">BetAnalyzer</strong> identifica apostas com valor
        esperado positivo (EV+), comparando a probabilidade do modelo com a probabilidade
        implícita das odds sem a margem da casa. Isto não é garantia de resultado.
      </div>

      <div className="flex flex-wrap items-end gap-3">
        <div className="flex gap-1 rounded-md bg-foreground/5 p-1">
          {(Object.keys(PERIOD_LABELS) as FixturePeriod[]).map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`rounded-md px-3 py-1.5 text-sm transition ${
                period === p ? "bg-primary text-black font-semibold" : "text-foreground/70"
              }`}
            >
              {PERIOD_LABELS[p]}
            </button>
          ))}
        </div>

        <select
          value={leagueId}
          onChange={(e) => setLeagueId(e.target.value === "" ? "" : Number(e.target.value))}
          className="rounded-md border border-foreground/20 bg-[#161616] px-3 py-1.5 text-sm"
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
          className="rounded-md border border-foreground/20 bg-[#161616] px-3 py-1.5 text-sm"
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
          className="flex-1 min-w-[180px] rounded-md border border-foreground/20 bg-[#161616] px-3 py-1.5 text-sm placeholder:text-foreground/40"
        />
      </div>

      {error && (
        <div className="rounded-md border border-ev-negative/40 bg-ev-negative/10 p-3 text-sm text-ev-negative">
          Erro ao carregar jogos: {error}
        </div>
      )}

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {loading
          ? Array.from({ length: 6 }).map((_, i) => <GameCardSkeleton key={i} />)
          : fixtures.map((fixture) => <GameCard key={fixture.id} fixture={fixture} />)}
      </div>

      {!loading && fixtures.length === 0 && !error && (
        <p className="py-8 text-center text-sm text-foreground/50">
          Nenhum jogo encontrado para os filtros selecionados.
        </p>
      )}
    </div>
  );
}
