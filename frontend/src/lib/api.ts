import type { AnalyzeResponse } from "@/types/analysis";
import type { BankrollMovementCreate, BankrollSummary } from "@/types/bankroll";
import type { Bet, BetCreate, BetStats, BetUpdate } from "@/types/bet";
import type { TokenResponse, User } from "@/types/auth";
import type { Fixture, FixtureDetails } from "@/types/fixture";
import type { League, Odds } from "@/types/odds";
import type { AppSettings, AppSettingsUpdate } from "@/types/settings";

declare global {
  interface Window {
    __ENV__?: { API_URL?: string };
  }
}

// Lido em runtime de public/env-config.js (gerado no startup do container),
// e não em build-time via process.env.NEXT_PUBLIC_API_URL — o Dockerfile do
// frontend builda a imagem sem acesso ao .env real da VPS, então uma URL
// embutida no bundle no build sempre apontaria para o valor de dev/local.
function getApiBaseUrl(): string {
  if (typeof window !== "undefined" && window.__ENV__?.API_URL) {
    return window.__ENV__.API_URL;
  }
  return "http://localhost:8000";
}

let accessToken: string | null = null;

export function setAccessToken(token: string | null): void {
  accessToken = token;
}

export function getAccessToken(): string | null {
  return accessToken;
}

async function rawRequest(path: string, init?: RequestInit): Promise<Response> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((init?.headers as Record<string, string>) ?? {}),
  };
  if (accessToken) headers["Authorization"] = `Bearer ${accessToken}`;

  return fetch(`${getApiBaseUrl()}${path}`, {
    cache: "no-store",
    credentials: "include",
    ...init,
    headers,
  });
}

async function request<T>(path: string, init?: RequestInit, allowRefresh = true): Promise<T> {
  let response = await rawRequest(path, init);

  if (response.status === 401 && allowRefresh && path !== "/auth/refresh" && path !== "/auth/login") {
    try {
      await refreshAccessToken();
      response = await rawRequest(path, init);
    } catch {
      // refresh falhou; segue para o tratamento de erro abaixo com a resposta original
    }
  }

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`${init?.method ?? "GET"} ${path} falhou (${response.status}): ${body}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

export async function login(email: string, senha: string): Promise<TokenResponse> {
  const data = await request<TokenResponse>(
    "/auth/login",
    { method: "POST", body: JSON.stringify({ email, senha }) },
    false
  );
  setAccessToken(data.access_token);
  return data;
}

export async function register(
  nome: string,
  email: string,
  senha: string
): Promise<TokenResponse> {
  const data = await request<TokenResponse>(
    "/auth/register",
    { method: "POST", body: JSON.stringify({ nome, email, senha }) },
    false
  );
  setAccessToken(data.access_token);
  return data;
}

export async function requestPasswordReset(email: string): Promise<void> {
  await request<void>(
    "/auth/forgot-password",
    { method: "POST", body: JSON.stringify({ email }) },
    false
  );
}

export async function resetPassword(token: string, senha: string): Promise<void> {
  await request<void>(
    "/auth/reset-password",
    { method: "POST", body: JSON.stringify({ token, senha }) },
    false
  );
}

export async function refreshAccessToken(): Promise<string> {
  const response = await rawRequest("/auth/refresh", { method: "POST" });
  if (!response.ok) {
    setAccessToken(null);
    throw new Error("Sessão expirada");
  }
  const data = (await response.json()) as TokenResponse;
  setAccessToken(data.access_token);
  return data.access_token;
}

export async function logout(): Promise<void> {
  await rawRequest("/auth/logout", { method: "POST" });
  setAccessToken(null);
}

export async function fetchMe(): Promise<User> {
  return request("/auth/me");
}

export async function fetchHealth(): Promise<{
  status: string;
  database: string;
  redis: string;
}> {
  return request("/health");
}

export type FixturePeriod = "today" | "week" | "month";

export interface FixtureFilters {
  period?: FixturePeriod;
  league?: number;
  pais?: string;
  hora_inicio?: string;
  hora_fim?: string;
  busca?: string;
}

export async function fetchFixtures(filters: FixtureFilters = {}): Promise<Fixture[]> {
  const params = new URLSearchParams();
  if (filters.period) params.set("period", filters.period);
  if (filters.league !== undefined) params.set("league", String(filters.league));
  if (filters.pais) params.set("pais", filters.pais);
  if (filters.hora_inicio) params.set("hora_inicio", filters.hora_inicio);
  if (filters.hora_fim) params.set("hora_fim", filters.hora_fim);
  if (filters.busca) params.set("busca", filters.busca);

  const query = params.toString();
  return request(`/fixtures${query ? `?${query}` : ""}`);
}

export async function fetchFixture(fixtureId: number): Promise<Fixture> {
  return request(`/fixtures/${fixtureId}`);
}

export async function fetchFixtureOdds(fixtureId: number, mercado?: string): Promise<Odds[]> {
  const query = mercado ? `?mercado=${encodeURIComponent(mercado)}` : "";
  return request(`/fixtures/${fixtureId}/odds${query}`);
}

export async function fetchFixtureDetails(fixtureId: number): Promise<FixtureDetails> {
  return request(`/fixtures/${fixtureId}/details`);
}

export async function analyzeFixture(
  fixtureId: number,
  contextoAdicional?: string
): Promise<AnalyzeResponse> {
  return request(`/fixtures/${fixtureId}/analyze`, {
    method: "POST",
    body: JSON.stringify({ contexto_adicional: contextoAdicional ?? null }),
  });
}

export async function fetchLeagues(): Promise<League[]> {
  return request("/leagues");
}

export async function fetchBets(): Promise<Bet[]> {
  return request("/bets");
}

export async function fetchBetStats(): Promise<BetStats> {
  return request("/bets/stats");
}

export async function createBet(payload: BetCreate): Promise<Bet> {
  return request("/bets", { method: "POST", body: JSON.stringify(payload) });
}

export async function updateBet(betId: number, payload: BetUpdate): Promise<Bet> {
  return request(`/bets/${betId}`, { method: "PATCH", body: JSON.stringify(payload) });
}

export async function fetchBankroll(): Promise<BankrollSummary> {
  return request("/bankroll");
}

export async function createBankrollMovement(
  payload: BankrollMovementCreate
): Promise<BankrollSummary> {
  return request("/bankroll", { method: "POST", body: JSON.stringify(payload) });
}

export async function fetchSettings(): Promise<AppSettings> {
  return request("/settings");
}

export async function updateSettings(payload: AppSettingsUpdate): Promise<AppSettings> {
  return request("/settings", { method: "PUT", body: JSON.stringify(payload) });
}
