export type UserRole = "admin" | "user";

export interface User {
  id: number;
  nome: string;
  email: string;
  role: UserRole;
  ativo: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}
