"use client";

import { useState } from "react";

import { createBet } from "@/lib/api";
import { useBetSlip } from "@/contexts/BetSlipContext";
import { IconClose, IconX } from "@/components/icons";

export function BetSlip() {
  const { items, isOpen, close, removeItem, setStake, clear } = useBetSlip();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const allStakesValid =
    items.length > 0 && items.every((item) => Number(item.stake) > 0);
  const totalStake = items.reduce((sum, item) => sum + (Number(item.stake) || 0), 0);

  async function handleSubmit() {
    setError(null);
    setSubmitting(true);
    try {
      await Promise.all(
        items.map((item) =>
          createBet({
            fixture_id: item.fixture_id,
            mercado: item.mercado,
            selecao: item.selecao,
            odd: item.odd,
            stake: Number(item.stake),
          })
        )
      );
      clear();
      close();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao registrar apostas");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <>
      <div
        onClick={close}
        className={`fixed inset-0 z-40 bg-black/60 backdrop-blur-sm transition-opacity ${
          isOpen ? "opacity-100" : "pointer-events-none opacity-0"
        }`}
      />

      <div
        className={`fixed inset-x-0 bottom-0 z-50 flex max-h-[85vh] flex-col rounded-t-2xl border-t border-border bg-surface shadow-2xl transition-transform duration-300 ease-out lg:inset-x-auto lg:inset-y-0 lg:right-0 lg:top-0 lg:h-screen lg:max-h-none lg:w-96 lg:rounded-none lg:rounded-l-2xl lg:border-l lg:border-t-0 ${
          isOpen
            ? "translate-y-0 lg:translate-x-0"
            : "translate-y-full lg:translate-y-0 lg:translate-x-full"
        }`}
        style={{ paddingBottom: "max(0px, env(safe-area-inset-bottom))" }}
      >
        <div className="flex items-center justify-between border-b border-border px-5 py-4">
          <h2 className="text-base font-semibold text-foreground">
            Carrinho de apostas
            {items.length > 0 && <span className="ml-2 text-sm text-muted">({items.length})</span>}
          </h2>
          <button
            type="button"
            onClick={close}
            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-muted transition-colors hover:bg-surface-hover hover:text-foreground"
          >
            <IconClose className="h-4 w-4" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-5 py-4">
          {items.length === 0 ? (
            <p className="py-10 text-center text-sm text-muted">
              Nenhuma seleção adicionada ainda. Toque no botão{" "}
              <span className="font-semibold text-primary">+</span> nas odds de um jogo para
              começar.
            </p>
          ) : (
            <div className="space-y-3">
              {items.map((item) => (
                <div
                  key={item.id}
                  className="rounded-xl border border-border bg-background/60 p-3"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium text-foreground">
                        {item.time_casa} x {item.time_fora}
                      </p>
                      <p className="text-xs text-muted">
                        {item.mercado} / {item.selecao}
                      </p>
                    </div>
                    <button
                      type="button"
                      onClick={() => removeItem(item.id)}
                      title="Remover"
                      className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-muted transition-colors hover:bg-ev-negative/15 hover:text-ev-negative"
                    >
                      <IconX className="h-3.5 w-3.5" />
                    </button>
                  </div>

                  <div className="mt-3 flex items-center gap-3">
                    <span className="font-mono text-lg font-bold text-primary">
                      {item.odd.toFixed(2)}
                    </span>
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      placeholder="Stake"
                      value={item.stake}
                      onChange={(e) => setStake(item.id, e.target.value)}
                      className="min-h-[40px] w-full rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus:border-primary"
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {items.length > 0 && (
          <div className="space-y-3 border-t border-border px-5 py-4">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted">Total apostado</span>
              <span className="font-mono font-semibold text-foreground">
                {totalStake.toFixed(2)}
              </span>
            </div>

            {error && (
              <p className="rounded-lg border border-ev-negative/30 bg-ev-negative/10 px-3 py-2 text-xs text-ev-negative">
                {error}
              </p>
            )}

            <button
              type="button"
              onClick={handleSubmit}
              disabled={!allStakesValid || submitting}
              className="min-h-[44px] w-full rounded-lg bg-gradient-primary px-4 text-sm font-semibold text-background shadow-glow transition-opacity hover:opacity-90 disabled:opacity-50"
            >
              {submitting ? "Registrando..." : "Registrar apostas"}
            </button>
            {!allStakesValid && (
              <p className="text-center text-[11px] text-muted">
                Informe um stake maior que zero para cada seleção.
              </p>
            )}
          </div>
        )}
      </div>
    </>
  );
}
