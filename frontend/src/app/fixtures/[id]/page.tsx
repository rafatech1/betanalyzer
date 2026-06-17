"use client";

import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

import { analyzeFixture, fetchFixture, fetchFixtureDetails, fetchFixtureOdds } from "@/lib/api";
import { Accordion } from "@/components/Accordion";
import { AnalysisResultCard } from "@/components/AnalysisResultCard";
import { AnalysisSkeleton, Skeleton } from "@/components/Skeleton";
import { ClaudeSummaryCard } from "@/components/ClaudeSummaryCard";
import { FixtureHeader } from "@/components/FixtureHeader";
import { IconBolt } from "@/components/icons";
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
      <div className="mx-auto max-w-4xl space-y-4">
        <Skeleton className="h-44 w-full rounded-2xl" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-48 w-full" />
      </div>
    );
  }

  if (loadError || !fixture) {
    return (
      <p className="mx-auto max-w-4xl rounded-lg border border-ev-negative/30 bg-ev-negative/10 p-3 text-sm text-ev-negative">
        Erro ao carregar o jogo: {loadError ?? "não encontrado"}
      </p>
    );
  }

  const claudeResumo = analyses?.find((a) => a.resumo_ia)?.resumo_ia ?? null;
  const hasContext = Boolean(
    details?.forma_casa ||
      details?.forma_fora ||
      details?.h2h_resumo ||
      details?.lesoes_casa.length ||
      details?.lesoes_fora.length
  );

  return (
    <div className="mx-auto max-w-4xl space-y-8">
      <FixtureHeader fixture={fixture} />

      <section className="space-y-4">
        <h2 className="text-sm font-semibold text-foreground/80">Odds</h2>
        <OddsTable odds={odds} />
      </section>

      <section className="space-y-4">
        <div className="flex justify-center">
          <motion.button
            whileTap={{ scale: 0.97 }}
            onClick={handleAnalyze}
            disabled={analyzing}
            className="flex min-h-[52px] items-center gap-2 rounded-xl bg-gradient-primary px-8 py-3 text-base font-semibold text-background shadow-glow transition-opacity hover:opacity-90 disabled:opacity-50"
          >
            <IconBolt className="h-5 w-5" />
            {analyzing ? "Analisando..." : "Analisar com IA"}
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
            <h2 className="text-sm font-semibold text-foreground/80">Análise EV+</h2>

            {claudeResumo && <ClaudeSummaryCard resumo={claudeResumo} />}

            {analyses.length === 0 ? (
              <p className="text-sm text-muted">
                Nenhuma odd disponível para gerar uma recomendação ainda.
              </p>
            ) : (
              <div className="grid gap-4 md:grid-cols-2">
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

      <Accordion title="Estatísticas e contexto">
        {hasContext ? (
          <>
            {details?.forma_casa && (
              <p>
                <span className="text-muted">Forma {fixture.time_casa.nome}:</span>{" "}
                {details.forma_casa}
              </p>
            )}
            {details?.forma_fora && (
              <p>
                <span className="text-muted">Forma {fixture.time_fora.nome}:</span>{" "}
                {details.forma_fora}
              </p>
            )}
            {details?.h2h_resumo && (
              <p>
                <span className="text-muted">H2H:</span> {details.h2h_resumo}
              </p>
            )}
            {details?.lesoes_casa && details.lesoes_casa.length > 0 && (
              <p>
                <span className="text-muted">Lesões {fixture.time_casa.nome}:</span>{" "}
                {details.lesoes_casa.join(", ")}
              </p>
            )}
            {details?.lesoes_fora && details.lesoes_fora.length > 0 && (
              <p>
                <span className="text-muted">Lesões {fixture.time_fora.nome}:</span>{" "}
                {details.lesoes_fora.join(", ")}
              </p>
            )}
          </>
        ) : (
          <p className="py-2 text-center text-muted">
            Nenhuma informação adicional disponível para este jogo ainda.
          </p>
        )}
      </Accordion>
    </div>
  );
}
