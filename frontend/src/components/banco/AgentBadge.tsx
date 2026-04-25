import { AGENTS, type AgentKey } from "./agents";
import { cn } from "@/lib/utils";

interface Props {
  agent: AgentKey;
  active?: boolean;
  compact?: boolean;
}

export const AgentBadge = ({ agent, active, compact }: Props) => {
  const meta = AGENTS[agent];
  const Icon = meta.icon;
  return (
    <div
      className={cn(
        "flex items-center gap-2 rounded-full border bg-card/60 px-2.5 py-1 transition-all",
        active ? "border-accent/40 shadow-glow" : "border-border",
        compact && "px-2 py-0.5"
      )}
    >
      <span
        className={cn(
          "flex h-5 w-5 items-center justify-center rounded-full text-primary-foreground",
          active && "animate-pulse-ring"
        )}
        style={{ backgroundColor: `hsl(var(--${meta.colorVar}))` }}
      >
        <Icon className="h-3 w-3" strokeWidth={2.5} />
      </span>
      <span className="text-xs font-medium">{meta.shortName}</span>
    </div>
  );
};
