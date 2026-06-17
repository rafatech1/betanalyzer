export type ResultadoAposta = "pendente" | "ganha" | "perdida" | "anulada" | "cashout";

export interface BetFixtureSummary {
  id: number;
  time_casa: string;
  time_fora: string;
  data_hora: string;
}

export interface Bet {
  id: number;
  fixture_id: number;
  analysis_id: number | null;
  mercado: string;
  selecao: string;
  odd: number;
  stake: number;
  resultado: ResultadoAposta;
  lucro: number | null;
  created_at: string;
  fixture: BetFixtureSummary | null;
}

export interface BetCreate {
  fixture_id: number;
  mercado: string;
  selecao: string;
  odd: number;
  stake: number;
  analysis_id?: number | null;
}

export interface BetUpdate {
  resultado: ResultadoAposta;
  lucro?: number | null;
}

export interface BankrollPoint {
  data: string;
  saldo_acumulado: number;
}

export interface BetStats {
  total_apostas: number;
  apostas_resolvidas: number;
  taxa_acerto: number | null;
  total_investido: number;
  lucro_acumulado: number;
  roi: number | null;
  yield_: number | null;
  evolucao: BankrollPoint[];
}
