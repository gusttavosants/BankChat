import { create } from "zustand";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: number;
}

export interface ClientData {
  nome?: string;
  cpf?: string;
  limite_credito?: number;
  score_credito?: number;
}

interface ChatState {
  messages: Message[];
  threadId: string | null;
  agenteCurrent: string;
  isAuthenticated: boolean;
  clientData: ClientData | null;
  isEnded: boolean;
  isLoading: boolean;

  // Actions
  addMessage: (msg: Omit<Message, "id" | "timestamp">) => void;
  setThreadId: (id: string) => void;
  setAgenteCurrent: (agent: string) => void;
  setAuthenticated: (val: boolean, data?: ClientData) => void;
  setEnded: (val: boolean) => void;
  setLoading: (val: boolean) => void;
  reset: () => void;
}

const initialState = {
  messages: [] as Message[],
  threadId: null as string | null,
  agenteCurrent: "triagem",
  isAuthenticated: false,
  clientData: null as ClientData | null,
  isEnded: false,
  isLoading: false,
};

export const useChatStore = create<ChatState>((set) => ({
  ...initialState,

  addMessage: (msg) =>
    set((state) => ({
      messages: [
        ...state.messages,
        { ...msg, id: crypto.randomUUID(), timestamp: Date.now() },
      ],
    })),

  setThreadId: (id) => set({ threadId: id }),

  setAgenteCurrent: (agent) => set({ agenteCurrent: agent }),

  setAuthenticated: (val, data) =>
    set({ isAuthenticated: val, clientData: data ?? null }),

  setEnded: (val) => set({ isEnded: val }),

  setLoading: (val) => set({ isLoading: val }),

  reset: () => set({ ...initialState }),
}));
