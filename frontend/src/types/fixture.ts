export type FixtureStatus =
  | "agendada"
  | "em_andamento"
  | "finalizada"
  | "cancelada"
  | "postergada";

export interface Team {
  id: number;
  nome: string;
}

export interface LeagueSummary {
  id: number;
  nome: string;
  pais: string;
}

export interface Fixture {
  id: number;
  liga_id: number;
  liga: LeagueSummary;
  time_casa: Team;
  time_fora: Team;
  data_hora: string;
  status: FixtureStatus;
  placar_casa: number | null;
  placar_fora: number | null;
  odds_1x2: Record<string, number> | null;
}

export interface FixtureDetails {
  forma_casa: string | null;
  forma_fora: string | null;
  h2h_resumo: string | null;
  lesoes_casa: string[];
  lesoes_fora: string[];
}
