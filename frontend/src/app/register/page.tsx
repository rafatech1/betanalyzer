"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";

import { Logo } from "@/components/Logo";
import { useAuth } from "@/contexts/AuthContext";

export default function RegisterPage() {
  const { register } = useAuth();
  const router = useRouter();

  const [nome, setNome] = useState("");
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [confirmarSenha, setConfirmarSenha] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (senha.length < 8) {
      setError("A senha deve ter no mínimo 8 caracteres.");
      return;
    }
    if (senha !== confirmarSenha) {
      setError("As senhas não coincidem.");
      return;
    }

    setSubmitting(true);
    try {
      await register(nome, email, senha);
      router.replace("/");
    } catch (err) {
      const message = err instanceof Error ? err.message : "";
      setError(
        message.includes("409")
          ? "Este e-mail já está cadastrado."
          : "Não foi possível criar sua conta. Tente novamente."
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-radial-glow px-4 py-12 sm:px-6">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35 }}
        className="w-full max-w-sm"
      >
        <div className="mb-8 flex justify-center">
          <Logo size={36} />
        </div>

        <div className="card-gradient-border rounded-2xl border border-border bg-surface p-6 sm:p-8">
          <h2 className="text-2xl font-bold text-foreground">Criar conta</h2>
          <p className="mt-1 text-sm text-muted">
            Cadastre-se para começar a identificar apostas com EV+.
          </p>

          <form onSubmit={handleSubmit} className="mt-8 space-y-4">
            <div>
              <label className="mb-1.5 block text-sm font-medium text-foreground/80">Nome</label>
              <input
                required
                type="text"
                autoComplete="name"
                value={nome}
                onChange={(e) => setNome(e.target.value)}
                className="min-h-[44px] w-full rounded-lg border border-border bg-background px-3.5 py-2.5 text-sm text-foreground outline-none transition-colors focus:border-primary"
              />
            </div>

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
                className="min-h-[44px] w-full rounded-lg border border-border bg-background px-3.5 py-2.5 text-sm text-foreground outline-none transition-colors focus:border-primary"
              />
            </div>

            <div>
              <label className="mb-1.5 block text-sm font-medium text-foreground/80">
                Senha
              </label>
              <input
                required
                type="password"
                minLength={8}
                autoComplete="new-password"
                value={senha}
                onChange={(e) => setSenha(e.target.value)}
                className="min-h-[44px] w-full rounded-lg border border-border bg-background px-3.5 py-2.5 text-sm text-foreground outline-none transition-colors focus:border-primary"
              />
              <p className="mt-1 text-xs text-muted">Mínimo de 8 caracteres.</p>
            </div>

            <div>
              <label className="mb-1.5 block text-sm font-medium text-foreground/80">
                Confirmar senha
              </label>
              <input
                required
                type="password"
                minLength={8}
                autoComplete="new-password"
                value={confirmarSenha}
                onChange={(e) => setConfirmarSenha(e.target.value)}
                className="min-h-[44px] w-full rounded-lg border border-border bg-background px-3.5 py-2.5 text-sm text-foreground outline-none transition-colors focus:border-primary"
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
              {submitting ? "Criando conta..." : "Criar conta"}
            </motion.button>
          </form>

          <p className="mt-6 text-center text-sm text-muted">
            Já tenho conta —{" "}
            <Link href="/login" className="font-semibold text-primary hover:underline">
              Entrar
            </Link>
          </p>
        </div>
      </motion.div>
    </div>
  );
}
