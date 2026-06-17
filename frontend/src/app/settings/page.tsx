"use client";

import { useEffect, useState } from "react";

import { fetchBankroll, fetchLeagues, fetchSettings, updateSettings } from "@/lib/api";
import type { League } from "@/types/odds";
import type { AppSettings } from "@/types/settings";

export default function SettingsPage() {
  const [settings, setSettings] = useState<AppSettings | null>(null);
  const [saldoAtual, setSaldoAtual] = useState<number | null>(null);
  const [leagues, setLeagues] = useState<League[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [savedAt, setSavedAt] = useState<number | null>(null);

  const [form, setForm] = useState({ bancaInicial: "", kelly: "", evThreshold: "" });
  const [favoriteLeagues, setFavoriteLeagues] = useState<Set<number>>(new Set());

  useEffect(() => {
    Promise.all([fetchSettings(), fetchBankroll(), fetchLeagues()])
      .then(([settingsData, bankrollData, leaguesData]) => {
        setSettings(settingsData);
        setSaldoAtual(bankrollData.saldo_atual);
        setLeagues(leaguesData);
        setForm({
          bancaInicial: String(settingsData.banca_inicial),
          kelly: String(settingsData.kelly_fraction * 100),
          evThreshold: String(settingsData.ev_threshold * 100),
        });
        setFavoriteLeagues(new Set(settingsData.favorite_league_ids));
      })
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  function toggleLeague(id: number) {
    setFavoriteLeagues((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const updated = await updateSettings({
        banca_inicial: Number(form.bancaInicial),
        kelly_fraction: Number(form.kelly) / 100,
        ev_threshold: Number(form.evThreshold) / 100,
        favorite_league_ids: Array.from(favoriteLeagues),
      });
      setSettings(updated);
      setSavedAt(Date.now());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao salvar configurações");
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return <p className="text-sm text-foreground/50">Carregando configurações...</p>;
  }

  if (!settings) {
    return <p className="text-sm text-ev-negative">Erro ao carregar configurações: {error}</p>;
  }

  return (
    <div className="max-w-2xl space-y-6">
      <h1 className="text-xl font-bold">Configurações</h1>

      <div className="rounded-lg border border-foreground/10 bg-[#161616] p-4">
        <p className="text-xs text-foreground/50">Banca atual</p>
        <p className="text-2xl font-bold text-primary">
          {saldoAtual !== null ? saldoAtual.toFixed(2) : "—"}
        </p>
      </div>

      <form onSubmit={handleSave} className="space-y-4">
        <div>
          <label className="mb-1 block text-sm text-foreground/70">
            Banca inicial (base para cálculo de ROI)
          </label>
          <input
            type="number"
            step="0.01"
            value={form.bancaInicial}
            onChange={(e) => setForm({ ...form, bancaInicial: e.target.value })}
            className="w-full rounded-md border border-foreground/20 bg-[#161616] px-3 py-2 text-sm"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm text-foreground/70">
            Fração de Kelly utilizada (% do Kelly completo, máx. recomendado 25%)
          </label>
          <input
            type="number"
            step="1"
            min="1"
            max="100"
            value={form.kelly}
            onChange={(e) => setForm({ ...form, kelly: e.target.value })}
            className="w-full rounded-md border border-foreground/20 bg-[#161616] px-3 py-2 text-sm"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm text-foreground/70">
            Limiar mínimo de EV para recomendação (%)
          </label>
          <input
            type="number"
            step="0.5"
            value={form.evThreshold}
            onChange={(e) => setForm({ ...form, evThreshold: e.target.value })}
            className="w-full rounded-md border border-foreground/20 bg-[#161616] px-3 py-2 text-sm"
          />
        </div>

        <div>
          <label className="mb-2 block text-sm text-foreground/70">Ligas favoritas</label>
          <div className="grid max-h-60 gap-1 overflow-y-auto rounded-md border border-foreground/10 p-2 sm:grid-cols-2">
            {leagues.map((league) => (
              <label key={league.id} className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={favoriteLeagues.has(league.id)}
                  onChange={() => toggleLeague(league.id)}
                  className="accent-primary"
                />
                {league.nome} ({league.pais})
              </label>
            ))}
            {leagues.length === 0 && (
              <p className="text-xs text-foreground/50">Nenhuma liga disponível ainda.</p>
            )}
          </div>
        </div>

        {error && <p className="text-sm text-ev-negative">{error}</p>}
        {savedAt && !error && (
          <p className="text-sm text-ev-positive">Configurações salvas com sucesso.</p>
        )}

        <button
          type="submit"
          disabled={saving}
          className="rounded-md bg-primary px-4 py-2 text-sm font-semibold text-black disabled:opacity-50"
        >
          {saving ? "Salvando..." : "Salvar configurações"}
        </button>
      </form>
    </div>
  );
}
