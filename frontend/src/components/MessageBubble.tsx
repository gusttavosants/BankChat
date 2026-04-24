"use client";

import { AgentBadge } from "./AgentBadge";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: number;
}

interface MessageBubbleProps {
  message: Message;
  agentName?: string;
}

export function MessageBubble({ message, agentName = "triagem" }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const time = new Date(message.timestamp).toLocaleTimeString("pt-BR", {
    hour: "2-digit",
    minute: "2-digit",
  });

  if (isUser) {
    return (
      <div className="flex justify-end animate-fade-in">
        <div className="flex flex-col items-end gap-1 max-w-[75%]">
          <div className="bg-brand/20 border border-brand/30 text-text-primary rounded-[24px] rounded-br-[6px] px-5 py-3 text-sm leading-relaxed">
            {message.content}
          </div>
          <span className="text-xs text-text-muted pr-1">{time}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start animate-fade-in">
      <div className="flex flex-col items-start gap-1 max-w-[80%]">
        <div className="flex items-center gap-2 pl-1 mb-0.5">
          {/* Bank logo mark */}
          <div className="w-6 h-6 rounded-full bg-brand/20 border border-brand/40 flex items-center justify-center">
            <span className="text-brand text-[10px] font-black">B</span>
          </div>
          <AgentBadge agent={agentName} />
        </div>
        <div className="glass rounded-[24px] rounded-tl-[6px] px-5 py-3 text-sm leading-relaxed text-text-primary whitespace-pre-wrap">
          {message.content}
        </div>
        <span className="text-xs text-text-muted pl-1">{time}</span>
      </div>
    </div>
  );
}
