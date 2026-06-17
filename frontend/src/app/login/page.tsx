"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";

import { Logo } from "@/components/Logo";
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
    <div className="grid min-h-screen lg:grid-cols-2">
      <div className="relative flex flex-col items-center overflow-hidden bg-gradient-to-br from-[#0F1624] via-background to-background px-6 py-10 text-center lg:min-h-screen lg:items-start lg:justify-between lg:p-12 lg:text-left">
        <div className="pointer-events-none absolute inset-0 bg-gradient-radial-glow" />
        <div className="pointer-events-none absolute -right-24 -top-24 h-96 w-96 rounded-full bg-primary/10 blur-3xl" />
        <div className="pointer-events-none absolute bottom-0 left-0 h-72 w-72 rounded-full bg-gold/10 blur-3xl" />

        <div className="relative z-10">
          <Logo size={36} />
        </div>

        <div className="relative z-10 my-6 max-w-md space-y-4 lg:my-0">
          <h1 className="text-3xl font-bold leading-tight text-foreground lg:text-4xl">
            Aposte com <span className="text-primary">valor</span>, não com sorte.
          </h1>
          <p className="text-sm leading-relaxed text-muted">
            BetAnalyzer compara a probabilidade estimada do modelo com a probabilidade
            implícita das odds — já sem a margem da casa — para identificar oportunidades
            reais de EV+ no futebol.
          </p>
          <div className="flex justify-center gap-6 pt-2 lg:justify-start">
            <StatPreview label="EV médio" value="+4.2%" accent="text-ev-positive" />
            <StatPreview label="Yield" value="+2.8%" accent="text-gold" />
            <StatPreview label="ROI" value="+11.6%" accent="text-primary" />
          </div>
        </div>

        <p className="relative z-10 text-xs text-muted">
          Apostas envolvem risco. Use sempre controle de banca (Kelly fracionado).
        </p>
      </div>

      <div className="flex items-center justify-center bg-background px-4 py-12 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35 }}
          className="w-full max-w-sm"
        >
          <h2 className="text-2xl font-bold text-foreground">Bem-vindo de volta</h2>
          <p className="mt-1 text-sm text-muted">Entre com sua conta para continuar.</p>

          <form onSubmit={handleSubmit} className="mt-8 space-y-4">
            <div>
              <label className="mb-1.5 block text-sm font-medium text-foreground/80">
                E-mail
              </label>
              <input
                required
                type="email"
                autoComplete="username"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="min-h-[44px] w-full rounded-lg border border-border bg-surface px-3.5 py-2.5 text-sm text-foreground outline-none transition-colors focus:border-primary"
              />
            </div>

            <div>
              <div className="flex items-center justify-between">
                <label className="mb-1.5 block text-sm font-medium text-foreground/80">
                  Senha
                </label>
                <Link href="/forgot-password" className="text-xs text-primary hover:underline">
                  Esqueci minha senha
                </Link>
              </div>
              <input
                required
                type="password"
                autoComplete="current-password"
                value={senha}
                onChange={(e) => setSenha(e.target.value)}
                className="min-h-[44px] w-full rounded-lg border border-border bg-surface px-3.5 py-2.5 text-sm text-foreground outline-none transition-colors focus:border-primary"
              />
            </div>

            {error && (
              <p className="rounded-lg border border-ev-negative/30 bg-ev-negative/10 px-3 py-2 text-sm text-ev-negative">
                {error}
              </p>
            )}

            <motion.button
              whileTap={{ scale: 0.98 }}
              type="submit"
              disabled={submitting}
              className="min-h-[44px] w-full rounded-lg bg-gradient-primary px-4 py-2.5 text-sm font-semibold text-background shadow-glow transition-opacity hover:opacity-90 disabled:opacity-50"
            >
              {submitting ? "Entrando..." : "Entrar"}
            </motion.button>
          </form>

          <p className="mt-6 text-center text-sm text-muted">
            Não tem conta?{" "}
            <Link href="/register" className="font-semibold text-primary hover:underline">
              Criar conta
            </Link>
          </p>
        </motion.div>
      </div>
    </div>
  );
}

function StatPreview({
  label,
  value,
  accent,
}: {
  label: string;
  value: string;
  accent: string;
}) {
  return (
    <div>
      <p className={`font-mono text-lg font-bold ${accent}`}>{value}</p>
      <p className="text-[11px] text-muted">{label}</p>
    </div>
  );
}
