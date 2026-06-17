"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { useAuth } from "@/contexts/AuthContext";

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await login(email, senha);
      router.replace("/");
    } catch {
      setError("E-mail ou senha inválidos.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-[70vh] items-center justify-center">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-sm space-y-4 rounded-lg border border-foreground/10 bg-[#161616] p-6"
      >
        <div className="text-center">
          <h1 className="text-xl font-bold text-primary">BetAnalyzer</h1>
          <p className="mt-1 text-sm text-foreground/60">Entre com sua conta</p>
        </div>

        <div>
          <label className="mb-1 block text-sm text-foreground/70">E-mail</label>
          <input
            required
            type="email"
            autoComplete="username"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full rounded-md border border-foreground/20 bg-background px-3 py-2 text-sm"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm text-foreground/70">Senha</label>
          <input
            required
            type="password"
            autoComplete="current-password"
            value={senha}
            onChange={(e) => setSenha(e.target.value)}
            className="w-full rounded-md border border-foreground/20 bg-background px-3 py-2 text-sm"
          />
        </div>

        {error && <p className="text-sm text-ev-negative">{error}</p>}

        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded-md bg-primary px-4 py-2 text-sm font-semibold text-black transition hover:opacity-90 disabled:opacity-50"
        >
          {submitting ? "Entrando..." : "Entrar"}
        </button>
      </form>
    </div>
  );
}
