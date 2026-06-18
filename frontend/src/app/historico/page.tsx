"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { fetchAnalysesHistory, fetchLeagues, type AnalysisPeriod } from "@/lib/api";
import { ConfidenceBadge } from "@/components/ConfidenceBadge";
import { EvBadge } from "@/components/EvBadge";
import { RecommendationBadge } from "@/components/RecommendationBadge";
import { Skeleton } from "@/components/Skeleton";
import { translateTeamName } from "@/lib/teamNames";
import type { AnalysisHistoryItem, Recomendacao } from "@/types/analysis";
import type { League } from "@/types/odds";

const PAGE_SIZE = 50;

const PERIOD_LABELS: Record<AnalysisPeriod, string> = {
  "7d": "7 dias",
  "30d": "30 dias",
  all: "Tudo",
};

const RECOMENDACAO_LABELS: Record<Recomendacao, string> = {
  apostar: "Apostar",
  observar: "Observar",
  evitar: "Evitar",
};

function formatDate(dataHora: string): string {
  return new Date(dataHora).toLocaleString("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    year: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function HistoricoPage() {
  const [items, setItems] = useState<AnalysisHistoryItem[]>([]);
  const [total, setTotal] = useState(0);
  const [leagues, setLeagues] = useState<League[]>([]);
  const [leagueId, setLeagueId] = useState<number | "">("");
  const [recomendacao, setRecomendacao] = useState<Recomendacao | "">("");
  const [period, setPeriod] = useState<AnalysisPeriod>("all");
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchLeagues().then(setLeagues).catch(() => setLeagues([]));
  }, []);

  const load = useCallback(
    async (offset: number, append: boolean) => {
      if (append) setLoadingMore(true);
      else setLoading(true);
      setError(null);
      try {
        const data = await fetchAnalysesHistory({
          limit: PAGE_SIZE,
          offset,
          liga: leagueId === "" ? undefined : leagueId,
          recomendacao: recomendacao === "" ? undefined : recomendacao,
          period,
        });
        setItems((prev) => (append ? [...prev, ...data.items] : data.items));
        setTotal(data.total);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Erro ao carregar histórico");
      } finally {
        if (append) setLoadingMore(false);
        else setLoading(false);
      }
    },
    [leagueId, recomendacao, period]
  );

  useEffect(() => {
    load(0, false);
  }, [load]);

  const hasMore = items.length < total;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Histórico de análises</h1>
        <p className="text-sm text-muted">Todas as análises de EV+ já realizadas.</p>
      </div>

      <div className="flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-end">
        <div className="scroll-hide -mx-4 flex gap-2 overflow-x-auto px-4 sm:mx-0 sm:overflow-visible sm:px-0">
          {(Object.keys(PERIOD_LABELS) as AnalysisPeriod[]).map((p) => (
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
          value={recomendacao}
          onChange={(e) => setRecomendacao(e.target.value as Recomendacao | "")}
          className="min-h-[44px] w-full rounded-lg border border-border bg-surface px-3 py-2.5 text-sm text-foreground outline-none focus:border-primary sm:w-auto"
        >
          <option value="">Todas as recomendações</option>
          {(Object.keys(RECOMENDACAO_LABELS) as Recomendacao[]).map((r) => (
            <option key={r} value={r}>
              {RECOMENDACAO_LABELS[r]}
            </option>
          ))}
        </select>
      </div>

      {error && (
        <p className="rounded-lg border border-ev-negative/30 bg-ev-negative/10 p-3 text-sm text-ev-negative">
          {error}
        </p>
      )}

      <div className="space-y-3">
        {loading
          ? Array.from({ length: 6 }).map((_, i) => (
              <Skeleton key={i} className="h-24 w-full rounded-xl" />
            ))
          : items.map((item) => <HistoryItem key={item.id} item={item} />)}
      </div>

      {!loading && items.length === 0 && !error && (
        <p className="py-8 text-center text-sm text-muted">
          Nenhuma análise encontrada para os filtros selecionados.
        </p>
      )}

      {!loading && hasMore && (
        <div className="flex justify-center">
          <button
            type="button"
            onClick={() => load(items.length, true)}
            disabled={loadingMore}
            className="min-h-[44px] rounded-lg border border-border bg-surface px-5 py-2.5 text-sm font-medium text-foreground transition-colors hover:bg-surface-hover disabled:opacity-50"
          >
            {loadingMore ? "Carregando..." : "Carregar mais"}
          </button>
        </div>
      )}
    </div>
  );
}

function HistoryItem({ item }: { item: AnalysisHistoryItem }) {
  const fixture = item.fixture;
  const isFinished = fixture.status === "finalizada";

  return (
    <Link
      href={`/fixtures/${fixture.id}`}
      className="card-gradient-border block rounded-xl border border-border bg-surface p-4 transition-colors hover:bg-surface-hover"
    >
      <div className="flex items-center justify-between gap-2 text-xs text-muted">
        <span className="truncate">
          {fixture.liga.nome} · {fixture.liga.pais}
        </span>
        <span
          className={`whitespace-nowrap rounded-full px-2 py-0.5 font-medium ${
            isFinished ? "bg-surface-hover text-muted" : "bg-gold/15 text-gold"
          }`}
        >
          {isFinished ? "Finalizado" : "Aguardando resultado"}
        </span>
      </div>

      <div className="mt-2 flex items-center justify-between gap-2">
        <span className="truncate text-sm font-medium text-foreground">
          {translateTeamName(fixture.time_casa.nome)} x {translateTeamName(fixture.time_fora.nome)}
        </span>
        <span className="whitespace-nowrap font-mono text-xs text-muted">
          {formatDate(fixture.data_hora)}
        </span>
      </div>

      {isFinished && fixture.placar_casa !== null && fixture.placar_fora !== null && (
        <p className="mt-0.5 font-mono text-xs text-muted">
          Placar: {fixture.placar_casa} - {fixture.placar_fora}
        </p>
      )}

      <div className="mt-3 flex flex-wrap items-center gap-2">
        <RecommendationBadge recomendacao={item.recomendacao} />
        <ConfidenceBadge confianca={item.confianca} />
        <EvBadge ev={item.ev} />
        <span className="rounded-full border border-border bg-background/60 px-2.5 py-1 text-xs text-muted">
          {item.mercado} / {item.selecao}
        </span>
        <span className="rounded-full border border-border bg-background/60 px-2.5 py-1 font-mono text-xs text-muted">
          odd {item.odd_referencia.toFixed(2)}
        </span>
      </div>
    </Link>
  );
}
