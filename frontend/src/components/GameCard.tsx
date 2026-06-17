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

export function GameCard({ fixture }: { fixture: Fixture }) {
  const odds = fixture.odds_1x2;
  const hasScore = fixture.placar_casa !== null && fixture.placar_fora !== null;

  return (
    <Link
      href={`/fixtures/${fixture.id}`}
      className="block rounded-lg border border-foreground/10 bg-[#161616] p-4 transition hover:border-primary/50"
    >
      <div className="flex items-center justify-between text-xs text-foreground/60">
        <span>
          {fixture.liga.nome} · {fixture.liga.pais}
        </span>
        <span>{STATUS_LABELS[fixture.status]}</span>
      </div>

      <div className="mt-3 flex items-center justify-between gap-4">
        <span className="flex-1 truncate text-sm font-medium">{fixture.time_casa.nome}</span>
        {hasScore ? (
          <span className="text-sm font-semibold text-primary">
            {fixture.placar_casa} - {fixture.placar_fora}
          </span>
        ) : (
          <span className="text-xs text-foreground/60">{formatKickoff(fixture.data_hora)}</span>
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
  );
}

function OddPill({ label, value }: { label: string; value: number | undefined }) {
  if (value === undefined) return null;

  return (
    <span className="flex-1 rounded-md bg-foreground/5 px-2 py-1 text-center">
      <span className="text-foreground/50">{label}</span>{" "}
      <span className="font-semibold">{value.toFixed(2)}</span>
    </span>
  );
}
