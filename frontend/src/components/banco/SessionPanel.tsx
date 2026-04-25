import { CheckCircle2, Clock, User2, ShieldCheck, Sparkles } from "lucide-react";

interface Props {
  authenticated: boolean;
  customerName?: string;
  customerCpf?: string;
  startedAt: Date;
}

const maskCpf = (cpf?: string) =>
  cpf ? cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, "$1.***.***-$4") : "—";

const TOPICS = [
  "Consulta e aumento de limite",
  "Atualização de score de crédito",
  "Cotação de moedas em tempo real",
  "Autenticação e identidade",
];

export const SessionPanel = ({ authenticated, customerName, customerCpf, startedAt }: Props) => {
  const elapsed = Math.max(1, Math.round((Date.now() - startedAt.getTime()) / 60000));
  return (
    <aside className="hidden w-72 shrink-0 flex-col gap-4 border-l border-border/70 bg-gradient-surface p-5 lg:flex">
      <div>
        <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
          Sessão atual
        </p>
        <h3 className="mt-1 font-display text-lg font-semibold">Atendimento</h3>
      </div>

      <div className="rounded-2xl border border-border bg-card p-4 shadow-soft">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-accent-soft text-accent-foreground">
            <User2 className="h-5 w-5" />
          </div>
          <div className="min-w-0">
            <div className="truncate text-sm font-semibold">
              {authenticated ? customerName ?? "Cliente" : "Não autenticado"}
            </div>
            <div className="font-mono text-xs text-muted-foreground">{maskCpf(customerCpf)}</div>
          </div>
        </div>
        <div className="mt-3 flex items-center gap-2 border-t border-border/70 pt-3 text-xs text-muted-foreground">
          {authenticated ? (
            <>
              <CheckCircle2 className="h-3.5 w-3.5 text-success" />
              <span>Identidade verificada</span>
            </>
          ) : (
            <>
              <Clock className="h-3.5 w-3.5 text-accent" />
              <span>Aguardando autenticação</span>
            </>
          )}
        </div>
      </div>

      <div>
        <p className="mb-2 flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
          <Sparkles className="h-3 w-3 text-accent" />
          Como podemos ajudar
        </p>
        <ul className="space-y-1.5">
          {TOPICS.map((t) => (
            <li
              key={t}
              className="flex items-start gap-2 rounded-xl border border-border/60 bg-card/50 px-3 py-2 text-xs text-foreground/80"
            >
              <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-accent" />
              {t}
            </li>
          ))}
        </ul>
      </div>

      <div className="mt-auto space-y-2">
        <div className="flex items-center gap-2 rounded-xl border border-border/60 bg-card/50 px-3 py-2 text-[11px] text-muted-foreground">
          <ShieldCheck className="h-3.5 w-3.5 text-success" />
          <span>Atendimento sigiloso · LGPD</span>
        </div>
        <div className="flex items-center gap-2 rounded-xl border border-border/60 bg-card/50 px-3 py-2 text-[11px] text-muted-foreground">
          <Clock className="h-3.5 w-3.5" />
          <span>{elapsed} min de sessão</span>
        </div>
      </div>
    </aside>
  );
};
