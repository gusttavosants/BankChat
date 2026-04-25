import { useState, useRef, useEffect, KeyboardEvent } from "react";
import { Send, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface Props {
  onSend: (text: string) => void;
  onRestart?: () => void;
  disabled?: boolean;
  placeholder?: string;
}

export const ChatComposer = ({ onSend, onRestart, disabled, placeholder }: Props) => {
  const [value, setValue] = useState("");
  const ref = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (!ref.current) return;
    ref.current.style.height = "auto";
    ref.current.style.height = Math.min(ref.current.scrollHeight, 160) + "px";
  }, [value]);

  const submit = () => {
    const t = value.trim();
    if (!t || disabled) return;
    onSend(t);
    setValue("");
  };

  const onKey = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  };

  return (
    <div className="border-t border-border/70 bg-gradient-surface px-4 py-4 sm:px-6">
      <div className="mx-auto flex max-w-3xl items-end gap-2">
        <div
          className={cn(
            "flex flex-1 items-end gap-2 rounded-2xl border border-border bg-card p-1.5 pl-4 shadow-soft transition-all",
            "focus-within:border-accent/50 focus-within:shadow-glow"
          )}
        >
          <textarea
            ref={ref}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={onKey}
            disabled={disabled}
            rows={1}
            placeholder={placeholder ?? "Escreva sua mensagem..."}
            className="flex-1 resize-none bg-transparent py-2 min-h-[36px] text-sm leading-5 outline-none placeholder:text-muted-foreground/70 disabled:opacity-50"
          />
          <Button
            type="button"
            size="icon"
            onClick={submit}
            disabled={disabled || !value.trim()}
            className="h-9 w-9 shrink-0 rounded-xl bg-primary text-primary-foreground hover:bg-primary/90"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
        {onRestart && (
          <Button
            variant="outline"
            size="icon"
            onClick={onRestart}
            className="h-12 w-12 shrink-0 rounded-2xl border-border bg-card hover:bg-accent/10 hover:text-accent hover:border-accent/30"
            title="Reiniciar atendimento"
          >
            <RotateCcw className="h-5 w-5" />
          </Button>
        )}
      </div>
      <p className="mx-auto mt-2 max-w-3xl text-center text-[11px] text-muted-foreground">
        Pressione <kbd className="rounded border border-border bg-card px-1 font-mono">Enter</kbd> para enviar •{" "}
        <kbd className="rounded border border-border bg-card px-1 font-mono">Shift + Enter</kbd> nova linha
      </p>
    </div>
  );
};
