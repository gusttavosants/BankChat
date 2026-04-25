export interface ChatResponse {
  reply: string;
  thread_id: string;
  agente_atual: string;
  cliente_autenticado: boolean;
  dados_cliente: Record<string, any> | null;
  encerrado: boolean;
  tentativas_auth: number;
}

export async function sendMessage(
  message: string,
  threadId: string | null
): Promise<ChatResponse> {
  // Uses Vite env var or fallback
  const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
  
  const res = await fetch(`${apiUrl}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message,
      thread_id: threadId,
    }),
  });

  if (!res.ok) {
    throw new Error(`Failed to send message: ${res.statusText}`);
  }

  return res.json();
}
