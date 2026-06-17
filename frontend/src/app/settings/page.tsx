"use client";

import { motion } from "framer-motion";
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
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-border border-t-primary" />
      </div>
    );
  }

  if (!settings) {
    return (
      <p className="rounded-lg border border-ev-negative/30 bg-ev-negative/10 p-3 text-sm text-ev-negative">
        Erro ao carregar configurações: {error}
      </p>
    );
  }

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Configurações</h1>
        <p className="text-sm text-muted">Banca, gestão de risco e ligas favoritas.</p>
      </div>

      <div className="card-gradient-border rounded-xl border border-border bg-surface p-5">
        <p className="text-xs text-muted">Banca atual</p>
        <p className="font-mono text-3xl font-bold text-primary">
          {saldoAtual !== null ? saldoAtual.toFixed(2) : "—"}
        </p>
      </div>

      <form onSubmit={handleSave} className="space-y-4">
        <Section title="Gestão de banca">
          <Field label="Banca inicial (base para cálculo de ROI)">
            <input
              type="number"
              step="0.01"
              value={form.bancaInicial}
              onChange={(e) => setForm({ ...form, bancaInicial: e.target.value })}
              className="min-h-[44px] w-full rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus:border-primary"
            />
          </Field>

          <Field label="Fração de Kelly utilizada (% do Kelly completo, máx. recomendado 25%)">
            <input
              type="number"
              step="1"
              min="1"
              max="100"
              value={form.kelly}
              onChange={(e) => setForm({ ...form, kelly: e.target.value })}
              className="min-h-[44px] w-full rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus:border-primary"
            />
          </Field>

          <Field label="Limiar mínimo de EV para recomendação (%)">
            <input
              type="number"
              step="0.5"
              value={form.evThreshold}
              onChange={(e) => setForm({ ...form, evThreshold: e.target.value })}
              className="min-h-[44px] w-full rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus:border-primary"
            />
          </Field>
        </Section>

        <Section title="Ligas favoritas">
          <div className="grid max-h-60 gap-1 overflow-y-auto rounded-lg border border-border p-2 sm:grid-cols-2">
            {leagues.map((league) => (
              <label
                key={league.id}
                className="flex min-h-[44px] items-center gap-2 rounded-md px-2 py-1.5 text-sm hover:bg-surface-hover"
              >
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
              <p className="text-xs text-muted">Nenhuma liga disponível ainda.</p>
            )}
          </div>
        </Section>

        {error && (
          <p className="rounded-lg border border-ev-negative/30 bg-ev-negative/10 p-3 text-sm text-ev-negative">
            {error}
          </p>
        )}
        {savedAt && !error && (
          <p className="rounded-lg border border-ev-positive/30 bg-ev-positive/10 p-3 text-sm text-ev-positive">
            Configurações salvas com sucesso.
          </p>
        )}

        <motion.button
          whileTap={{ scale: 0.98 }}
          type="submit"
          disabled={saving}
          className="min-h-[44px] w-full rounded-lg bg-gradient-primary px-5 py-2.5 text-sm font-semibold text-background shadow-glow disabled:opacity-50 sm:w-auto"
        >
          {saving ? "Salvando..." : "Salvar configurações"}
        </motion.button>
      </form>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="card-gradient-border space-y-4 rounded-xl border border-border bg-surface p-5">
      <h2 className="text-sm font-semibold text-foreground/80">{title}</h2>
      {children}
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="mb-1.5 block text-sm text-muted">{label}</label>
      {children}
    </div>
  );
}
