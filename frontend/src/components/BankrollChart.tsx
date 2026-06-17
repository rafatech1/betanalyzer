"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { BankrollPoint } from "@/types/bet";

export function BankrollChart({ evolucao }: { evolucao: BankrollPoint[] }) {
  if (evolucao.length < 2) {
    return (
      <p className="text-sm text-muted">
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
    <ResponsiveContainer width="100%" height={260}>
      <AreaChart data={data}>
        <defs>
          <linearGradient id="bankroll-fill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#FF6B00" stopOpacity={0.35} />
            <stop offset="100%" stopColor="#FF6B00" stopOpacity={0} />
          </linearGradient>
          <linearGradient id="bankroll-stroke" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#FF6B00" />
            <stop offset="100%" stopColor="#F0B429" />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#1E2D4A" />
        <XAxis dataKey="data" stroke="#8896B3" fontSize={11} tickLine={false} axisLine={false} />
        <YAxis stroke="#8896B3" fontSize={11} tickLine={false} axisLine={false} />
        <Tooltip
          contentStyle={{
            background: "#0F1624",
            border: "1px solid #1E2D4A",
            borderRadius: 8,
            fontSize: 12,
          }}
          labelStyle={{ color: "#F0F4FF" }}
          itemStyle={{ color: "#FF6B00" }}
        />
        <Area
          type="monotone"
          dataKey="saldo"
          stroke="url(#bankroll-stroke)"
          strokeWidth={2.5}
          fill="url(#bankroll-fill)"
          dot={false}
          activeDot={{ r: 4, fill: "#F0B429" }}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
