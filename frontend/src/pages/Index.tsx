import { useState, useRef, useEffect } from "react";
import { Lock, Sparkles, ShieldCheck } from "lucide-react";
import { Logo } from "@/components/banco/Logo";
import { MessageBubble, type ChatMessage } from "@/components/banco/MessageBubble";
import { TypingIndicator } from "@/components/banco/TypingIndicator";
import { ChatComposer } from "@/components/banco/ChatComposer";
import { SessionPanel } from "@/components/banco/SessionPanel";
import { sendMessage as apiSendMessage } from "@/lib/api";

const uid = () => Math.random().toString(36).slice(2, 10);

const extractOptions = (text: string) => {
  const options: { value: string; label: string }[] = [];
  // Regex exige que o número da opção (1-9) esteja no início da string ou após uma quebra de linha (\n)
  const regex = /(?:^|\n)\**([1-9])(?:\.|\uFE0F?\u20E3|\)|-)\**\s+(.*?)(?=\s*(?:[,.?!;]|\n|\r|\bou\b|\be\b|$|[1-9](?:\.|\uFE0F?\u20E3|\)|-)\s))/gi;
  let match;
  while ((match = regex.exec(text)) !== null) {
    const label = match[2].trim();
    if (label.length > 2) {
      options.push({ value: match[1], label });
    }
  }
  return options;
};

const Index = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [typing, setTyping] = useState(false);
  const [authenticated, setAuthenticated] = useState(false);
  const [customerData, setCustomerData] = useState<Record<string, any> | null>(null);
  const [threadId, setThreadId] = useState<string | null>(null);
  const [startedAt] = useState(new Date());

  const scrollRef = useRef<HTMLDivElement>(null);
  // Ref espelha threadId para evitar closure stale no restartConversation
  const threadIdRef = useRef<string | null>(null);

  useEffect(() => {
    threadIdRef.current = threadId;
  }, [threadId]);

  const endConversation = () => {
    setMessages((m) => [
      ...m,
      {
        id: uid(),
        role: "system",
        content: "Atendimento encerrado. Obrigado por escolher o Banco Ágil.",
        timestamp: new Date(),
      },
    ]);
  };

  const restartConversation = () => {
    setMessages([]);
    setThreadId(null);
    threadIdRef.current = null;
    setAuthenticated(false);
    setCustomerData(null);
    // Usa ref para garantir que null chegue ao sendMessage, sem closure stale
    setTimeout(() => handleSendMessageWithThread("Ola", null, true), 10);
  };

  // Versao interna que aceita threadId explicito (evita closure stale)
  const handleSendMessageWithThread = async (text: string, explicitThreadId: string | null | undefined, isHidden = false) => {
    const currentThreadId = explicitThreadId !== undefined ? explicitThreadId : threadIdRef.current;
    if (!isHidden) {
      const userMsg: ChatMessage = { id: uid(), role: "user", content: text, timestamp: new Date() };
      setMessages((m) => [...m, userMsg]);
    }
    
    setTyping(true);

    try {
      const res = await apiSendMessage(text, currentThreadId);
      
      setThreadId(res.thread_id);
      threadIdRef.current = res.thread_id;
      setAuthenticated(res.cliente_autenticado);
      setCustomerData(res.dados_cliente);
      
      setMessages((m) => [
        ...m,
        {
          id: uid(),
          role: "agent",
          content: res.reply,
          timestamp: new Date(),
          meta: res.cliente_autenticado && !authenticated ? { kind: "success", label: "Autenticação concluída" } : undefined
        },
      ]);

      if (res.encerrado) {
        endConversation();
      }
    } catch (error) {
      console.error(error);
      setMessages((m) => [
        ...m,
        {
          id: uid(),
          role: "system",
          content: "Erro de comunicação com o servidor. Tente novamente.",
          timestamp: new Date(),
        },
      ]);
    } finally {
      setTyping(false);
    }
  };

  const handleSendMessage = async (text: string, isHidden = false) => {
    return handleSendMessageWithThread(text, undefined, isHidden);
  };

  useEffect(() => {
    // Initial greeting if no messages
    if (messages.length === 0 && !typing && !threadId) {
      const timer = setTimeout(() => handleSendMessage("Olá", true), 10);
      return () => clearTimeout(timer);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, typing]);

  return (
    <div className="flex h-screen flex-col bg-background">
      {/* Top bar */}
      <header className="flex items-center justify-between border-b border-border/70 bg-card/60 px-4 py-3 backdrop-blur sm:px-6">
        <Logo />
        <div className="flex items-center gap-3">
          <div className="hidden items-center gap-2 rounded-full border border-border bg-card px-3 py-1.5 text-xs text-muted-foreground sm:flex">
            <Lock className="h-3 w-3" />
            Conexão segura · TLS 1.3
          </div>
          <div className="flex items-center gap-2 rounded-full border border-success/30 bg-success/10 px-3 py-1.5 text-xs font-medium text-success">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-success opacity-60" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-success" />
            </span>
            Online
          </div>
        </div>
      </header>

      {/* Main */}
      <div className="flex flex-1 overflow-hidden">
        <main className="relative flex flex-1 flex-col">
          {/* Hero strip */}
          <div className="border-b border-border/70 bg-gradient-hero px-4 py-6 text-primary-foreground sm:px-8">
            <div className="mx-auto max-w-3xl">
              <div className="flex items-center gap-2 text-xs uppercase tracking-[0.18em] text-primary-foreground/70">
                <Sparkles className="h-3.5 w-3.5 text-accent" />
                Atendimento Banco Ágil
              </div>
              <h1 className="mt-2 font-display text-2xl font-semibold leading-tight sm:text-3xl">
                Como podemos te ajudar hoje?
              </h1>
              <p className="mt-1 flex items-center gap-2 text-sm text-primary-foreground/75">
                <ShieldCheck className="h-4 w-4 text-accent" />
                Crédito, câmbio, score e muito mais — em uma única conversa.
              </p>
            </div>
          </div>

          {/* Messages */}
          <div ref={scrollRef} className="chat-scroll flex-1 overflow-y-auto px-4 py-6 sm:px-6">
            <div className="mx-auto flex max-w-3xl flex-col gap-4">
              {messages.map((m) => (
                <MessageBubble key={m.id} msg={m} />
              ))}
              {typing && <TypingIndicator />}
            </div>
          </div>



          {/* Dynamic Options */}
          {messages.length > 0 && messages[messages.length - 1].role === "agent" && !typing && (() => {
            const opts = extractOptions(messages[messages.length - 1].content);
            if (opts.length === 0) return null;
            return (
              <div className="pb-3">
                <div className="mx-auto flex max-w-3xl flex-wrap gap-2 px-4 sm:px-6">
                  {opts.map((opt) => (
                    <button
                      key={opt.value}
                      onClick={() => handleSendMessage(opt.value)}
                      className="flex items-center gap-2 rounded-xl border border-border bg-card px-4 py-2 text-sm shadow-soft transition-all hover:border-accent/40 hover:shadow-glow"
                    >
                      <span className="flex h-6 w-6 items-center justify-center rounded bg-accent-soft text-xs font-semibold text-accent-foreground">
                        {opt.value}
                      </span>
                      {opt.label}
                    </button>
                  ))}
                </div>
              </div>
            );
          })()}

          {/* Composer */}
          <ChatComposer onSend={(t) => handleSendMessage(t)} onRestart={restartConversation} />
        </main>

        <SessionPanel 
          authenticated={authenticated} 
          customerName={customerData?.nome}
          customerCpf={customerData?.cpf}
          startedAt={startedAt} 
        />
      </div>
    </div>
  );
};

export default Index;
