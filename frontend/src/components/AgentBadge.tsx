"use client";

import { ShieldCheck, Zap, Star } from "lucide-react";

const AGENT_LABELS: Record<string, { label: string; color: string; icon: React.ReactNode }> = {
  triagem: {
    label: "Triagem",
    color: "text-sky-400",
    icon: <ShieldCheck size={14} />,
  },
  credito: {
    label: "Crédito",
    color: "text-brand",
    icon: <Star size={14} />,
  },
  cambio: {
    label: "Câmbio",
    color: "text-amber-400",
    icon: <Zap size={14} />,
  },
  entrevista: {
    label: "Análise",
    color: "text-violet-400",
    icon: <Star size={14} />,
  },
};

interface AgentBadgeProps {
  agent: string;
}

export function AgentBadge({ agent }: AgentBadgeProps) {
  const meta = AGENT_LABELS[agent] ?? { label: agent, color: "text-text-muted", icon: null };
  return (
    <span
      className={`inline-flex items-center gap-1 text-xs font-semibold uppercase tracking-widest ${meta.color}`}
    >
      {meta.icon}
      {meta.label}
    </span>
  );
}
