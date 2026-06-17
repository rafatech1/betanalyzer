export type TipoMovimento = "deposito" | "retirada" | "aposta" | "ganho" | "ajuste";

export interface BankrollMovement {
  id: number;
  tipo: TipoMovimento;
  valor: number;
  saldo_resultante: number;
  descricao: string | null;
  created_at: string;
}

export interface BankrollSummary {
  saldo_atual: number;
  movimentos: BankrollMovement[];
}

export interface BankrollMovementCreate {
  tipo: TipoMovimento;
  valor: number;
  descricao?: string | null;
}
