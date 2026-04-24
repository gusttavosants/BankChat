"use client";

import { useRef, useEffect, useState } from "react";
import { Send, RotateCcw, Lock } from "lucide-react";
import { useChatStore } from "@/store/chatStore";
import { sendMessage } from "@/lib/api";
import { MessageBubble } from "./MessageBubble";
import { ClientPanel } from "./ClientPanel";
import { AgentBadge } from "./AgentBadge";

export function ChatWindow() {
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);
  const {
    messages,
    threadId,
    agenteCurrent,
    isAuthenticated,
    clientData,
    isEnded,
    isLoading,
    addMessage,
    setThreadId,
    setAgenteCurrent,
    setAuthenticated,
    setEnded,
    setLoading,
    reset,
  } = useChatStore();

  // Scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const handleSend = async () => {
    const text = input.trim();
    if (!text || isLoading || isEnded) return;

    setInput("");
    addMessage({ role: "user", content: text });
    setLoading(true);

    try {
      const res = await sendMessage(text, threadId);
      if (!threadId) setThreadId(res.thread_id);
      setAgenteCurrent(res.agente_atual);
      if (res.cliente_autenticado && res.dados_cliente) {
        setAuthenticated(true, res.dados_cliente as Parameters<typeof setAuthenticated>[1]);
      }
      if (res.encerrado) setEnded(true);
      addMessage({ role: "assistant", content: res.reply });
    } catch (err) {
      addMessage({
        role: "assistant",
        content: "Erro de conexão. Verifique se o servidor está ativo.",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex h-full w-full">
      {/* ── Chat Column ── */}
      <div className="flex flex-col flex-1 min-w-0">
        {/* Header */}
        <header className="flex items-center justify-between px-6 py-4 border-b border-white/5">
          <div className="flex items-center gap-3">
            {/* Logo */}
            <div className="w-9 h-9 rounded-[14px] bg-brand/20 border border-brand/40 flex items-center justify-center">
              <span className="text-brand font-black text-lg">B</span>
            </div>
            <div>
              <p className="text-text-primary font-bold text-sm leading-none">Banco Ágil</p>
              <p className="text-text-muted text-xs mt-0.5">Assistente Virtual</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <AgentBadge agent={agenteCurrent} />
            <button
              onClick={reset}
              title="Novo atendimento"
              className="p-2 rounded-xl text-text-muted hover:text-text-primary hover:bg-white/5 transition-all"
            >
              <RotateCcw size={16} />
            </button>
          </div>
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 md:px-6 py-6 flex flex-col gap-4">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full gap-4 text-center animate-fade-in">
              <div className="w-16 h-16 rounded-[24px] bg-brand/10 border border-brand/20 flex items-center justify-center">
                <span className="text-brand font-black text-3xl">B</span>
              </div>
              <div>
                <h2 className="text-text-primary font-bold text-xl">Banco Ágil</h2>
                <p className="text-text-muted text-sm mt-1 max-w-xs">
                  Seu assistente financeiro inteligente. Digite uma mensagem para começar.
                </p>
              </div>
            </div>
          )}
          {messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} agentName={agenteCurrent} />
          ))}
          {isLoading && (
            <div className="flex justify-start animate-fade-in">
              <div className="glass rounded-[24px] rounded-tl-[6px] px-5 py-4 flex gap-1.5 items-center">
                <span className="w-1.5 h-1.5 rounded-full bg-brand animate-bounce [animation-delay:0ms]" />
                <span className="w-1.5 h-1.5 rounded-full bg-brand animate-bounce [animation-delay:150ms]" />
                <span className="w-1.5 h-1.5 rounded-full bg-brand animate-bounce [animation-delay:300ms]" />
              </div>
            </div>
          )}
          {isEnded && (
            <div className="flex justify-center animate-fade-in">
              <div className="glass rounded-2xl px-6 py-3 flex items-center gap-2 border border-white/10">
                <Lock size={14} className="text-text-muted" />
                <span className="text-text-muted text-xs">
                  Atendimento encerrado.{" "}
                  <button onClick={reset} className="text-brand underline-offset-2 underline">
                    Iniciar novo
                  </button>
                </span>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div className="px-4 md:px-6 pb-6 pt-2">
          <div className="glass rounded-button flex items-end gap-3 px-4 py-3 border border-white/10 focus-within:border-brand/40 transition-colors">
            <textarea
              className="flex-1 bg-transparent resize-none text-text-primary placeholder:text-text-muted text-sm outline-none max-h-32 leading-relaxed"
              placeholder={isEnded ? "Atendimento encerrado." : "Digite sua mensagem..."}
              rows={1}
              value={input}
              disabled={isEnded || isLoading}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || isLoading || isEnded}
              className="w-9 h-9 rounded-full bg-brand flex items-center justify-center shrink-0 transition-all hover:-translate-y-0.5 active:scale-95 disabled:opacity-30 disabled:cursor-not-allowed disabled:hover:translate-y-0"
            >
              <Send size={16} className="text-white" />
            </button>
          </div>
          <p className="text-center text-[10px] text-text-muted mt-2">
            Banco Ágil · Assistente em ambiente controlado
          </p>
        </div>
      </div>

      {/* ── Client Panel (only when authenticated) ── */}
      {isAuthenticated && clientData && (
        <aside className="hidden lg:flex flex-col border-l border-white/5 overflow-y-auto">
          <div className="pt-4">
            <ClientPanel client={clientData} />
          </div>
        </aside>
      )}
    </div>
  );
}
