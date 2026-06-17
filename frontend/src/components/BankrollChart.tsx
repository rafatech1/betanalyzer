"use client";

import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { BankrollPoint } from "@/types/bet";

export function BankrollChart({ evolucao }: { evolucao: BankrollPoint[] }) {
  if (evolucao.length < 2) {
    return (
      <p className="text-sm text-foreground/50">
        Registre e resolva apostas para ver a evolução da banca.
      </p>
    );
  }

  const data = evolucao.map((point, index) => ({
    index,
    data: new Date(point.data).toLocaleDateString("pt-BR"),
    saldo: Number(point.saldo_acumulado.toFixed(2)),
  }));

  return (
    <ResponsiveContainer width="100%" height={240}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#ffffff1a" />
        <XAxis dataKey="data" stroke="#ffffff66" fontSize={11} />
        <YAxis stroke="#ffffff66" fontSize={11} />
        <Tooltip
          contentStyle={{ background: "#161616", border: "1px solid #ffffff1a", fontSize: 12 }}
          labelStyle={{ color: "#ffffff" }}
        />
        <Line type="monotone" dataKey="saldo" stroke="#FF6B00" strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}
