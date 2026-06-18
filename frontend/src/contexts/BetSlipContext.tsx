"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

export interface BetSlipItem {
  id: string;
  fixture_id: number;
  time_casa: string;
  time_fora: string;
  mercado: string;
  selecao: string;
  odd: number;
  stake: string;
}

interface BetSlipContextValue {
  items: BetSlipItem[];
  isOpen: boolean;
  open: () => void;
  close: () => void;
  toggle: () => void;
  isInSlip: (id: string) => boolean;
  addItem: (item: Omit<BetSlipItem, "stake">) => void;
  removeItem: (id: string) => void;
  setStake: (id: string, stake: string) => void;
  clear: () => void;
}

const STORAGE_KEY = "betanalyzer:betslip";

const BetSlipContext = createContext<BetSlipContextValue | null>(null);

export function makeBetSlipId(fixtureId: number, mercado: string, selecao: string): string {
  return `${fixtureId}:${mercado}:${selecao}`;
}

export function BetSlipProvider({ children }: { children: React.ReactNode }) {
  const [items, setItems] = useState<BetSlipItem[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) setItems(JSON.parse(raw) as BetSlipItem[]);
    } catch {
      // localStorage indisponível ou conteúdo corrompido — começa vazio
    } finally {
      setHydrated(true);
    }
  }, []);

  useEffect(() => {
    if (!hydrated) return;
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
  }, [items, hydrated]);

  const isInSlip = useCallback(
    (id: string) => items.some((item) => item.id === id),
    [items]
  );

  const addItem = useCallback((item: Omit<BetSlipItem, "stake">) => {
    setItems((prev) => {
      if (prev.some((existing) => existing.id === item.id)) return prev;
      return [...prev, { ...item, stake: "" }];
    });
  }, []);

  const removeItem = useCallback((id: string) => {
    setItems((prev) => prev.filter((item) => item.id !== id));
  }, []);

  const setStake = useCallback((id: string, stake: string) => {
    setItems((prev) => prev.map((item) => (item.id === id ? { ...item, stake } : item)));
  }, []);

  const clear = useCallback(() => setItems([]), []);

  const value = useMemo<BetSlipContextValue>(
    () => ({
      items,
      isOpen,
      open: () => setIsOpen(true),
      close: () => setIsOpen(false),
      toggle: () => setIsOpen((prev) => !prev),
      isInSlip,
      addItem,
      removeItem,
      setStake,
      clear,
    }),
    [items, isOpen, isInSlip, addItem, removeItem, setStake, clear]
  );

  return <BetSlipContext.Provider value={value}>{children}</BetSlipContext.Provider>;
}

export function useBetSlip(): BetSlipContextValue {
  const ctx = useContext(BetSlipContext);
  if (!ctx) throw new Error("useBetSlip deve ser usado dentro de um BetSlipProvider");
  return ctx;
}
