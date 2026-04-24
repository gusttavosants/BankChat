"use client";

import { User, CreditCard, TrendingUp, Shield } from "lucide-react";
import type { ClientData } from "@/store/chatStore";

interface ClientPanelProps {
  client: ClientData;
}

function Stat({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="glass rounded-2xl px-4 py-3 flex flex-col gap-0.5">
      <span className="text-xs text-text-muted uppercase tracking-widest">{label}</span>
      <span className="text-text-primary font-semibold text-sm">{value}</span>
    </div>
  );
}

function scoreLabel(score: number) {
  if (score >= 700) return { label: "Excelente", color: "text-brand" };
  if (score >= 500) return { label: "Bom", color: "text-amber-400" };
  return { label: "Regular", color: "text-rose-400" };
}

export function ClientPanel({ client }: ClientPanelProps) {
  const score = client.score_credito ?? 0;
  const scoreMeta = scoreLabel(score);

  return (
    <div className="w-72 flex flex-col gap-4 p-4">
      {/* Profile card */}
      <div className="glass rounded-zen p-5 flex flex-col gap-3">
        <div className="flex items-center gap-3">
          <div className="w-11 h-11 rounded-full bg-brand/20 border border-brand/40 flex items-center justify-center">
            <User size={20} className="text-brand" />
          </div>
          <div>
            <p className="text-text-primary font-bold text-sm leading-tight">
              {client.nome ?? "Cliente"}
            </p>
            <p className="text-text-muted text-xs font-mono">{client.cpf ?? "—"}</p>
          </div>
        </div>
        <div className="h-px bg-white/5" />
        <div className="flex items-center gap-2">
          <Shield size={14} className="text-brand" />
          <span className="text-xs text-text-muted">Sessão autenticada</span>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 gap-2">
        <Stat
          label="Limite de Crédito"
          value={
            <span className="text-brand">
              {client.limite_credito != null
                ? `R$ ${client.limite_credito.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}`
                : "—"}
            </span>
          }
        />
        <Stat
          label="Score de Crédito"
          value={
            <span className={scoreMeta.color}>
              {score} pts — {scoreMeta.label}
            </span>
          }
        />
      </div>

      {/* Score bar */}
      <div className="glass rounded-2xl px-4 py-3">
        <div className="flex justify-between items-center mb-2">
          <span className="text-xs text-text-muted">Saúde Financeira</span>
          <TrendingUp size={14} className="text-brand" />
        </div>
        <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-brand/60 to-brand rounded-full transition-all duration-700"
            style={{ width: `${Math.min((score / 1000) * 100, 100)}%` }}
          />
        </div>
        <div className="flex justify-between mt-1">
          <span className="text-[10px] text-text-muted">0</span>
          <span className="text-[10px] text-text-muted">1000</span>
        </div>
      </div>

      {/* Services */}
      <div className="glass rounded-2xl p-4">
        <p className="text-xs text-text-muted uppercase tracking-widest mb-3">Serviços</p>
        <div className="flex flex-col gap-2">
          <button className="w-full flex items-center gap-2 text-sm text-text-primary hover:text-brand transition-colors py-1.5">
            <CreditCard size={15} className="text-brand" />
            Crédito
          </button>
          <button className="w-full flex items-center gap-2 text-sm text-text-primary hover:text-amber-400 transition-colors py-1.5">
            <TrendingUp size={15} className="text-amber-400" />
            Câmbio
          </button>
        </div>
      </div>
    </div>
  );
}
