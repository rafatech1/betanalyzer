export interface Odds {
  id: number;
  fixture_id: number;
  casa_de_aposta: string;
  mercado: string;
  selecao: string;
  odd: number;
  prob_implicita: number;
  timestamp: string;
}

export interface League {
  id: number;
  nome: string;
  pais: string;
  temporada: number;
}
