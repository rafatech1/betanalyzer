"use client";

import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

import { analyzeFixture, fetchFixture, fetchFixtureDetails, fetchFixtureOdds } from "@/lib/api";
import { AnalysisResultCard } from "@/components/AnalysisResultCard";
import { AnalysisSkeleton, Skeleton } from "@/components/Skeleton";
import { ClaudeSummaryCard } from "@/components/ClaudeSummaryCard";
import { OddsTable } from "@/components/OddsTable";
import type { Analysis } from "@/types/analysis";
import type { Fixture, FixtureDetails } from "@/types/fixture";
import type { Odds } from "@/types/odds";

export default function FixturePage() {
  const params = useParams<{ id: string }>();
  const fixtureId = Number(params.id);

  const [fixture, setFixture] = useState<Fixture | null>(null);
  const [odds, setOdds] = useState<Odds[]>([]);
  const [details, setDetails] = useState<FixtureDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  const [analyzing, setAnalyzing] = useState(false);
  const [analyses, setAnalyses] = useState<Analysis[] | null>(null);
  const [avisoRisco, setAvisoRisco] = useState<string | null>(null);
  const [analyzeError, setAnalyzeError] = useState<string | null>(null);

  useEffect(() => {
    if (!fixtureId) return;
    setLoading(true);
    setLoadError(null);

    Promise.all([
      fetchFixture(fixtureId),
      fetchFixtureOdds(fixtureId),
      fetchFixtureDetails(fixtureId).catch(() => null),
    ])
      .then(([fixtureData, oddsData, detailsData]) => {
        setFixture(fixtureData);
        setOdds(oddsData);
        setDetails(detailsData);
      })
      .catch((err: Error) => setLoadError(err.message))
      .finally(() => setLoading(false));
  }, [fixtureId]);

  async function handleAnalyze() {
    setAnalyzing(true);
    setAnalyzeError(null);
    try {
      const response = await analyzeFixture(fixtureId);
      setAnalyses(response.analises);
      setAvisoRisco(response.aviso_risco);
    } catch (err) {
      setAnalyzeError(err instanceof Error ? err.message : "Falha ao analisar o jogo");
    } finally {
      setAnalyzing(false);
    }
  }

  if (loading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-6 w-2/3" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-48 w-full" />
      </div>
    );
  }

  const claudeResumo = analyses?.find((a) => a.resumo_ia)?.resumo_ia ?? null;

  if (loadError || !fixture) {
    return (
      <p className="rounded-lg border border-ev-negative/30 bg-ev-negative/10 p-3 text-sm text-ev-negative">
        Erro ao carregar o jogo: {loadError ?? "não encontrado"}
      </p>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <p className="text-xs text-muted">
          {fixture.liga.nome} · {fixture.liga.pais}
        </p>
        <h1 className="text-2xl font-bold text-foreground">
          {fixture.time_casa.nome} <span className="text-muted">vs</span> {fixture.time_fora.nome}
        </h1>
        <p className="font-mono text-sm text-muted">
          {new Date(fixture.data_hora).toLocaleString("pt-BR")}
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <section>
            <h2 className="mb-2 text-sm font-semibold text-foreground/80">Odds</h2>
            <OddsTable odds={odds} />
          </section>

          <section className="space-y-3">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold text-foreground/80">Análise EV+</h2>
              <motion.button
                whileTap={{ scale: 0.97 }}
                onClick={handleAnalyze}
                disabled={analyzing}
                className="rounded-lg bg-gradient-primary px-4 py-2 text-sm font-semibold text-background shadow-glow transition-opacity hover:opacity-90 disabled:opacity-50"
              >
                {analyzing ? "Analisando..." : "Analisar jogo"}
              </motion.button>
            </div>

            {analyzeError && (
              <p className="rounded-lg border border-ev-negative/30 bg-ev-negative/10 p-3 text-sm text-ev-negative">
                {analyzeError}
              </p>
            )}

            {analyzing && (
              <div className="space-y-3">
                <AnalysisSkeleton />
                <AnalysisSkeleton />
              </div>
            )}

            {!analyzing && analyses && (
              <div className="space-y-4">
                {claudeResumo && <ClaudeSummaryCard resumo={claudeResumo} />}

                {analyses.length === 0 ? (
                  <p className="text-sm text-muted">
                    Nenhuma odd disponível para gerar uma recomendação ainda.
                  </p>
                ) : (
                  <div className="grid gap-4 sm:grid-cols-2">
                    {analyses.map((analysis, index) => (
                      <AnalysisResultCard key={analysis.id} analysis={analysis} index={index} />
                    ))}
                  </div>
                )}

                {avisoRisco && (
                  <p className="rounded-lg border border-primary/30 bg-primary/10 p-3 text-xs text-foreground/80">
                    {avisoRisco}
                  </p>
                )}
              </div>
            )}
          </section>
        </div>

        <aside className="space-y-3">
          {details && (
            <section className="card-gradient-border space-y-2.5 rounded-xl border border-border bg-surface p-4 text-sm">
              <h2 className="text-sm font-semibold text-foreground/80">Estatísticas e contexto</h2>
              {details.forma_casa && (
                <p>
                  <span className="text-muted">Forma {fixture.time_casa.nome}:</span>{" "}
                  {details.forma_casa}
                </p>
              )}
              {details.forma_fora && (
                <p>
                  <span className="text-muted">Forma {fixture.time_fora.nome}:</span>{" "}
                  {details.forma_fora}
                </p>
              )}
              {details.h2h_resumo && (
                <p>
                  <span className="text-muted">H2H:</span> {details.h2h_resumo}
                </p>
              )}
              {details.lesoes_casa.length > 0 && (
                <p>
                  <span className="text-muted">Lesões {fixture.time_casa.nome}:</span>{" "}
                  {details.lesoes_casa.join(", ")}
                </p>
              )}
              {details.lesoes_fora.length > 0 && (
                <p>
                  <span className="text-muted">Lesões {fixture.time_fora.nome}:</span>{" "}
                  {details.lesoes_fora.join(", ")}
                </p>
              )}
            </section>
          )}
        </aside>
      </div>
    </div>
  );
}
