"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { useState } from "react";

import { Logo } from "@/components/Logo";
import { requestPasswordReset } from "@/lib/api";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await requestPasswordReset(email);
      setSent(true);
    } catch {
      setError("Não foi possível enviar o email agora. Tente novamente em breve.");
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
          <h2 className="text-2xl font-bold text-foreground">Esqueci minha senha</h2>
          <p className="mt-1 text-sm text-muted">
            Informe seu e-mail e enviaremos um link para redefinir sua senha.
          </p>

          {sent ? (
            <p className="mt-6 rounded-lg border border-ev-positive/30 bg-ev-positive/10 px-3 py-3 text-sm text-ev-positive">
              Se este e-mail estiver cadastrado, você vai receber um link de redefinição em
              poucos minutos. Verifique também a caixa de spam.
            </p>
          ) : (
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
                {submitting ? "Enviando..." : "Enviar link de redefinição"}
              </motion.button>
            </form>
          )}

          <p className="mt-6 text-center text-sm text-muted">
            Lembrou a senha?{" "}
            <Link href="/login" className="font-semibold text-primary hover:underline">
              Entrar
            </Link>
          </p>
        </div>
      </motion.div>
    </div>
  );
}
