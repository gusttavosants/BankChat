import { cn } from "@/lib/utils";

export type MessageRole = "user" | "agent" | "system";

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
  /** Optional inline status, e.g. for success/warning callouts. Never reveals which agent. */
  meta?: { kind: "info" | "success" | "warning"; label: string };
}

const formatTime = (d: Date) =>
  d.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });

/** Single, unified attendant identity — clients should never perceive agent transitions. */
const AssistantAvatar = () => (
  <div className="flex flex-col items-center pt-1">
    <span className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-hero text-primary-foreground shadow-soft">
      <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M3 10 12 4l9 6" />
        <path d="M5 10v8h14v-8" />
      </svg>
    </span>
  </div>
);

export const MessageBubble = ({ msg }: { msg: ChatMessage }) => {
  if (msg.role === "system") {
    return (
      <div className="flex items-center justify-center py-2 animate-fade-in">
        <div className="flex items-center gap-2 rounded-full border border-border/70 bg-card/60 px-3 py-1 text-xs text-muted-foreground backdrop-blur">
          <span className="h-1 w-1 rounded-full bg-accent" />
          {msg.content}
        </div>
      </div>
    );
  }

  const isUser = msg.role === "user";

  return (
    <div className={cn("flex w-full animate-message-in gap-3", isUser ? "justify-end" : "justify-start")}>
      {!isUser && <AssistantAvatar />}

      <div className={cn("flex max-w-[78%] flex-col gap-1", isUser && "items-end")}>
        {!isUser && (
          <div className="flex items-center gap-2 px-1 text-[11px] text-muted-foreground">
            <span className="font-medium text-foreground/80">Banco Ágil</span>
            <span className="opacity-50">•</span>
            <span>{formatTime(msg.timestamp)}</span>
          </div>
        )}

        <div
          className={cn(
            "rounded-2xl px-4 py-2.5 text-sm leading-relaxed shadow-bubble",
            isUser
              ? "bg-gradient-bubble-user text-primary-foreground rounded-br-md"
              : "bg-card text-card-foreground rounded-bl-md border border-border/60"
          )}
        >
          <p className="whitespace-pre-wrap">{msg.content}</p>
          {msg.meta && (
            <div
              className={cn(
                "mt-2 flex items-center gap-1.5 rounded-lg border px-2 py-1 text-[11px]",
                msg.meta.kind === "success" && "border-success/30 bg-success/10 text-success",
                msg.meta.kind === "warning" && "border-destructive/30 bg-destructive/10 text-destructive",
                msg.meta.kind === "info" && "border-border bg-muted text-muted-foreground"
              )}
            >
              <span className="h-1 w-1 rounded-full bg-current" />
              {msg.meta.label}
            </div>
          )}
        </div>

        {isUser && <span className="px-1 text-[11px] text-muted-foreground">{formatTime(msg.timestamp)}</span>}
      </div>
    </div>
  );
};
