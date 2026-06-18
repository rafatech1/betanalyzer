"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { fetchFixtures, fetchLeagues, type FixturePeriod } from "@/lib/api";
import { usePolling } from "@/hooks/usePolling";
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

const REFRESH_INTERVAL_MS = 5 * 60_000;

export default function DashboardPage() {
  const [period, setPeriod] = useState<FixturePeriod>("week");
  const [leagueId, setLeagueId] = useState<number | "">("");
  const [pais, setPais] = useState<string>("");
  const [busca, setBusca] = useState("");
  const [leagues, setLeagues] = useState<League[]>([]);
  const [fixtures, setFixtures] = useState<Fixture[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const skipNextDebounce = useRef(true);

  useEffect(() => {
    fetchLeagues().then(setLeagues).catch(() => setLeagues([]));
  }, []);

  const loadFixtures = useCallback(async () => {
    try {
      const data = await fetchFixtures({
        period,
        league: leagueId === "" ? undefined : leagueId,
        pais: pais || undefined,
        busca: busca || undefined,
      });
      setFixtures(data.filter((f) => f.status !== "finalizada"));
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao carregar jogos");
    } finally {
      setLoading(false);
    }
  }, [period, leagueId, pais, busca]);

  const { msToNextUpdate, refresh } = usePolling(loadFixtures, REFRESH_INTERVAL_MS);

  useEffect(() => {
    if (skipNextDebounce.current) {
      skipNextDebounce.current = false;
      return;
    }
    setLoading(true);
    const timeout = setTimeout(() => refresh(), 300);
    return () => clearTimeout(timeout);
  }, [period, leagueId, pais, busca, refresh]);

  const countries = useMemo(
    () => Array.from(new Set(leagues.map((l) => l.pais))).sort(),
    [leagues]
  );

  const live = useMemo(
    () => fixtures.filter((f) => f.status === "em_andamento").length,
    [fixtures]
  );

  // Jogos em andamento têm seu próprio indicador "ao vivo" na página do jogo;
  // aqui a listagem foca nos próximos jogos, então eles somem ao começar.
  const visibleFixtures = useMemo(
    () => fixtures.filter((f) => f.status !== "em_andamento"),
    [fixtures]
  );

  const minutesToNextUpdate = Math.max(1, Math.ceil(msToNextUpdate / 60_000));

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

      {!loading && (
        <p className="text-right text-[11px] text-muted">
          Próxima atualização em {minutesToNextUpdate} min
        </p>
      )}

      <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
        {loading
          ? Array.from({ length: 6 }).map((_, i) => <GameCardSkeleton key={i} />)
          : visibleFixtures.map((fixture) => <GameCard key={fixture.id} fixture={fixture} />)}
      </div>

      {!loading && visibleFixtures.length === 0 && !error && (
        <p className="py-8 text-center text-sm text-muted">
          Nenhum jogo encontrado para os filtros selecionados.
        </p>
      )}
    </div>
  );
}
