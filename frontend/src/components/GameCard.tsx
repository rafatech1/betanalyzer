"use client";

import { motion } from "framer-motion";
import Link from "next/link";

import type { Fixture } from "@/types/fixture";

function formatKickoff(dataHora: string): string {
  return new Date(dataHora).toLocaleString("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

const STATUS_LABELS: Record<Fixture["status"], string> = {
  agendada: "Agendado",
  em_andamento: "Em andamento",
  finalizada: "Finalizado",
  cancelada: "Cancelado",
  postergada: "Postergado",
};

const STATUS_DOT: Record<Fixture["status"], string> = {
  agendada: "bg-muted",
  em_andamento: "bg-ev-positive animate-pulse",
  finalizada: "bg-muted",
  cancelada: "bg-ev-negative",
  postergada: "bg-gold",
};

export function GameCard({ fixture }: { fixture: Fixture }) {
  const odds = fixture.odds_1x2;
  const hasScore = fixture.placar_casa !== null && fixture.placar_fora !== null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -2 }}
      transition={{ duration: 0.2 }}
    >
      <Link
        href={`/fixtures/${fixture.id}`}
        className="card-gradient-border block rounded-xl border border-border bg-surface p-4 transition-colors hover:bg-surface-hover"
      >
        <div className="flex items-center justify-between text-xs text-muted">
          <span className="truncate">
            {fixture.liga.nome} · {fixture.liga.pais}
          </span>
          {fixture.status === "em_andamento" ? (
            <span className="inline-flex items-center gap-1 whitespace-nowrap rounded-full bg-ev-negative/15 px-2 py-0.5 font-semibold text-ev-negative">
              <span className="animate-pulse">🔴</span> Ao vivo
            </span>
          ) : (
            <span className="flex items-center gap-1.5 whitespace-nowrap">
              <span className={`h-1.5 w-1.5 rounded-full ${STATUS_DOT[fixture.status]}`} />
              {STATUS_LABELS[fixture.status]}
            </span>
          )}
        </div>

        <div className="mt-3 flex items-center justify-between gap-4">
          <span className="flex-1 truncate text-sm font-medium">{fixture.time_casa.nome}</span>
          {hasScore ? (
            <span className="font-mono text-sm font-semibold text-primary">
              {fixture.placar_casa} - {fixture.placar_fora}
            </span>
          ) : (
            <span className="whitespace-nowrap font-mono text-xs text-muted">
              {formatKickoff(fixture.data_hora)}
            </span>
          )}
          <span className="flex-1 truncate text-right text-sm font-medium">
            {fixture.time_fora.nome}
          </span>
        </div>

        {odds && (
          <div className="mt-3 flex gap-2 text-xs">
            <OddPill label="1" value={odds.casa} />
            <OddPill label="X" value={odds.empate} />
            <OddPill label="2" value={odds.fora} />
          </div>
        )}
      </Link>
    </motion.div>
  );
}

function OddPill({ label, value }: { label: string; value: number | undefined }) {
  if (value === undefined) return null;

  return (
    <span className="flex-1 rounded-md border border-border bg-background/60 px-2 py-1 text-center">
      <span className="text-muted">{label}</span>{" "}
      <span className="font-mono font-semibold text-foreground">{value.toFixed(2)}</span>
    </span>
  );
}
