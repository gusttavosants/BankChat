const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface ChatApiResponse {
  reply: string;
  thread_id: string;
  agente_atual: string;
  cliente_autenticado: boolean;
  dados_cliente: Record<string, unknown> | null;
  encerrado: boolean;
  tentativas_auth: number;
}

export async function sendMessage(
  message: string,
  threadId: string | null
): Promise<ChatApiResponse> {
  const res = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, thread_id: threadId }),
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || "Falha na comunicação com o servidor.");
  }

  return res.json();
}

export async function getSession(threadId: string) {
  const res = await fetch(`${API_URL}/session/${threadId}`);
  if (!res.ok) return null;
  return res.json();
}
