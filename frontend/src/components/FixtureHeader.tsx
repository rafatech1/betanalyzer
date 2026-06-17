"use client";

import { motion } from "framer-motion";

import { getFlagUrl } from "@/lib/teamFlags";
import type { Fixture } from "@/types/fixture";

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

const PALETTE = [
  "from-primary to-gold",
  "from-ev-positive to-primary",
  "from-gold to-ev-negative",
  "from-ev-negative to-primary",
  "from-primary to-ev-positive",
];

function initials(nome: string): string {
  return nome
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((word) => word[0])
    .join("")
    .toUpperCase();
}

function colorFor(nome: string): string {
  let hash = 0;
  for (const ch of nome) hash = (hash * 31 + ch.charCodeAt(0)) % PALETTE.length;
  return PALETTE[Math.abs(hash) % PALETTE.length];
}

function TeamBadge({ nome }: { nome: string }) {
  const flagUrl = getFlagUrl(nome);

  if (flagUrl) {
    return (
      // eslint-disable-next-line @next/next/no-img-element -- domínio externo (flagcdn.com), sem necessidade de otimização do next/image
      <img
        src={flagUrl}
        alt={`Bandeira de ${nome}`}
        loading="lazy"
        className="h-16 w-16 shrink-0 rounded-full border border-border object-cover shadow-glow sm:h-20 sm:w-20"
      />
    );
  }

  return (
    <div
      className={`flex h-16 w-16 shrink-0 items-center justify-center rounded-full bg-gradient-to-br text-xl font-bold text-background shadow-glow sm:h-20 sm:w-20 sm:text-2xl ${colorFor(nome)}`}
    >
      {initials(nome)}
    </div>
  );
}

export function FixtureHeader({ fixture }: { fixture: Fixture }) {
  const hasScore = fixture.placar_casa !== null && fixture.placar_fora !== null;

  return (
    <motion.div
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      className="relative overflow-hidden rounded-2xl border border-border bg-gradient-to-b from-surface to-background p-6 sm:p-8"
    >
      <div className="pointer-events-none absolute inset-0 bg-gradient-radial-glow" />

      <div className="relative z-10 flex items-center justify-between gap-2 sm:gap-6">
        <div className="flex flex-1 flex-col items-center gap-2 text-center">
          <TeamBadge nome={fixture.time_casa.nome} />
          <span className="text-sm font-semibold text-foreground sm:text-base">
            {fixture.time_casa.nome}
          </span>
        </div>

        <div className="flex shrink-0 flex-col items-center">
          {hasScore ? (
            <span className="font-mono text-3xl font-bold text-foreground sm:text-4xl">
              {fixture.placar_casa} - {fixture.placar_fora}
            </span>
          ) : (
            <span className="font-mono text-2xl font-bold text-muted sm:text-3xl">VS</span>
          )}
        </div>

        <div className="flex flex-1 flex-col items-center gap-2 text-center">
          <TeamBadge nome={fixture.time_fora.nome} />
          <span className="text-sm font-semibold text-foreground sm:text-base">
            {fixture.time_fora.nome}
          </span>
        </div>
      </div>

      <div className="relative z-10 mt-6 flex flex-wrap items-center justify-center gap-x-3 gap-y-1.5 border-t border-border pt-4 text-xs text-muted">
        <span>
          {fixture.liga.nome} · {fixture.liga.pais}
        </span>
        <span className="text-border">•</span>
        <span className="font-mono">{new Date(fixture.data_hora).toLocaleString("pt-BR")}</span>
        <span className="text-border">•</span>
        <span className="inline-flex items-center gap-1.5">
          <span className={`h-1.5 w-1.5 rounded-full ${STATUS_DOT[fixture.status]}`} />
          {STATUS_LABELS[fixture.status]}
        </span>
      </div>
    </motion.div>
  );
}
