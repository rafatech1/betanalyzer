export type NivelConfianca = "baixa" | "media" | "alta";
export type Recomendacao = "apostar" | "evitar" | "observar";

export interface Analysis {
  id: number;
  fixture_id: number;
  mercado: string;
  selecao: string;
  odd_referencia: number;
  prob_estimada: number;
  prob_implicita: number;
  ev: number;
  confianca: NivelConfianca;
  recomendacao: Recomendacao;
  stake_sugerido: number;
  resumo_ia: string | null;
  created_at: string;
}

export interface AnalyzeResponse {
  aviso_risco: string;
  analises: Analysis[];
}

export interface AnalysisHistoryItem {
  id: number;
  fixture_id: number;
  time_casa: string;
  time_fora: string;
  data_hora: string;
  liga: { id: number; nome: string; pais: string };
  status: "agendada" | "em_andamento" | "finalizada" | "cancelada" | "postergada";
  placar_casa: number | null;
  placar_fora: number | null;
  mercado: string;
  selecao: string;
  odd_referencia: number;
  ev: number;
  confianca: NivelConfianca;
  recomendacao: Recomendacao;
  created_at: string;
}

export interface AnalysisHistoryResponse {
  items: AnalysisHistoryItem[];
  total: number;
}
