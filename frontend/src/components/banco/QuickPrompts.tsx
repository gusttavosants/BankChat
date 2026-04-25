import { CreditCard, Globe2, TrendingUp, HelpCircle } from "lucide-react";

const PROMPTS = [
  { icon: CreditCard, label: "Consultar limite", text: "Quero consultar meu limite de crédito" },
  { icon: TrendingUp, label: "Aumentar limite", text: "Gostaria de solicitar aumento de limite" },
  { icon: Globe2, label: "Cotação do dólar", text: "Qual a cotação do dólar hoje?" },
  { icon: HelpCircle, label: "Atualizar score", text: "Quero atualizar meu score de crédito" },
];

export const QuickPrompts = ({ onPick }: { onPick: (t: string) => void }) => (
  <div className="mx-auto grid max-w-3xl gap-2 px-4 sm:grid-cols-2 sm:px-6">
    {PROMPTS.map((p) => (
      <button
        key={p.label}
        onClick={() => onPick(p.text)}
        className="group flex items-center gap-3 rounded-xl border border-border bg-card p-3 text-left text-sm shadow-soft transition-all hover:border-accent/40 hover:shadow-glow"
      >
        <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent-soft text-accent-foreground transition-transform group-hover:scale-105">
          <p.icon className="h-4 w-4" strokeWidth={2.2} />
        </span>
        <div>
          <div className="font-medium">{p.label}</div>
          <div className="text-xs text-muted-foreground">{p.text}</div>
        </div>
      </button>
    ))}
  </div>
);
