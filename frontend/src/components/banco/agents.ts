import { Shield, CreditCard, MessageSquareHeart, Globe2, type LucideIcon } from "lucide-react";

export type AgentKey = "triagem" | "credito" | "entrevista" | "cambio";

export interface AgentMeta {
  key: AgentKey;
  name: string;
  shortName: string;
  description: string;
  icon: LucideIcon;
  colorVar: string; // tailwind text/bg helper
}

export const AGENTS: Record<AgentKey, AgentMeta> = {
  triagem: {
    key: "triagem",
    name: "Atendimento Triagem",
    shortName: "Triagem",
    description: "Recepciona e autentica o cliente.",
    icon: Shield,
    colorVar: "agent-triagem",
  },
  credito: {
    key: "credito",
    name: "Especialista de Crédito",
    shortName: "Crédito",
    description: "Limites e solicitações de aumento.",
    icon: CreditCard,
    colorVar: "agent-credito",
  },
  entrevista: {
    key: "entrevista",
    name: "Entrevista Financeira",
    shortName: "Entrevista",
    description: "Atualiza seu score de crédito.",
    icon: MessageSquareHeart,
    colorVar: "agent-entrevista",
  },
  cambio: {
    key: "cambio",
    name: "Mesa de Câmbio",
    shortName: "Câmbio",
    description: "Cotações de moedas em tempo real.",
    icon: Globe2,
    colorVar: "agent-cambio",
  },
};

export const AGENT_LIST: AgentMeta[] = Object.values(AGENTS);
