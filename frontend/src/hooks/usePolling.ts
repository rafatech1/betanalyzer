"use client";

import { useCallback, useEffect, useRef, useState } from "react";

interface UsePollingOptions {
  enabled?: boolean;
}

interface UsePollingResult {
  lastUpdated: Date | null;
  msToNextUpdate: number;
  refresh: () => void;
}

/**
 * Chama fetchFn imediatamente e depois a cada intervalMs. Pausa enquanto a aba
 * fica oculta (document.visibilityState !== "visible") e, ao voltar a ficar
 * visível, busca dados na hora e reinicia a contagem do próximo intervalo.
 */
export function usePolling(
  fetchFn: () => void | Promise<void>,
  intervalMs: number,
  { enabled = true }: UsePollingOptions = {}
): UsePollingResult {
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [msToNextUpdate, setMsToNextUpdate] = useState(intervalMs);
  const fetchFnRef = useRef(fetchFn);
  fetchFnRef.current = fetchFn;

  const runFetch = useCallback(async () => {
    await fetchFnRef.current();
    setLastUpdated(new Date());
  }, []);

  useEffect(() => {
    if (!enabled) return;

    let nextTick = Date.now() + intervalMs;
    let intervalId: ReturnType<typeof setInterval> | null = null;
    let countdownId: ReturnType<typeof setInterval> | null = null;

    function startTimers() {
      if (intervalId) return;
      nextTick = Date.now() + intervalMs;
      setMsToNextUpdate(intervalMs);
      intervalId = setInterval(() => {
        runFetch();
        nextTick = Date.now() + intervalMs;
      }, intervalMs);
      countdownId = setInterval(() => {
        setMsToNextUpdate(Math.max(0, nextTick - Date.now()));
      }, 1000);
    }

    function stopTimers() {
      if (intervalId) clearInterval(intervalId);
      if (countdownId) clearInterval(countdownId);
      intervalId = null;
      countdownId = null;
    }

    function handleVisibilityChange() {
      if (document.visibilityState === "visible") {
        runFetch();
        startTimers();
      } else {
        stopTimers();
      }
    }

    runFetch();
    if (document.visibilityState === "visible") {
      startTimers();
    }
    document.addEventListener("visibilitychange", handleVisibilityChange);

    return () => {
      stopTimers();
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, [intervalMs, enabled, runFetch]);

  return { lastUpdated, msToNextUpdate, refresh: runFetch };
}
