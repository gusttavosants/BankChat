import uuid
import json
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver

from core.graph import workflow

# ── Persistence & Graph ────────────────────────────────────────────────
memory = MemorySaver()
app_graph = workflow.compile(checkpointer=memory)

# ── FastAPI App ────────────────────────────────────────────────────────
app = FastAPI(
    title="Banco Ágil API",
    description="Multi-agent banking assistant powered by LangGraph.",
    version="1.0.0",
)

import os

frontend_url = os.getenv("FRONTEND_URL", "*")
origins = [frontend_url] if frontend_url != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True if frontend_url != "*" else False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Schemas ────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None  # None = nova sessão


class ChatResponse(BaseModel):
    reply: str
    thread_id: str
    agente_atual: str
    cliente_autenticado: bool
    dados_cliente: Optional[dict]
    encerrado: bool
    tentativas_auth: int


# ── Helpers ────────────────────────────────────────────────────────────
def _build_config(thread_id: str) -> dict:
    return {"configurable": {"thread_id": thread_id}}


def _extract_reply(state: dict) -> str:
    """Returns the last AI message content from the graph state."""
    messages = state.get("messages", [])
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and msg.content:
            return msg.content
    return "Não foi possível processar sua solicitação."


# ── Endpoints ──────────────────────────────────────────────────────────
@app.get("/")
def read_root():
    return {
        "message": "Banco Ágil API is running!",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
def health():
    return {"status": "ok", "service": "banco-agil-api"}


@app.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest):
    """Sends a message and returns the agent response (synchronous)."""
    thread_id = body.thread_id or str(uuid.uuid4())
    config = _build_config(thread_id)

    try:
        # Get current state to build correct initial state for new sessions
        current = app_graph.get_state(config)
        if current.values:
            # Existing session – just add the new message
            input_state = {"messages": [HumanMessage(content=body.message)]}
        else:
            # New session – full initial state
            input_state = {
                "messages": [HumanMessage(content=body.message)],
                "agente_atual": "triagem",
                "cliente_autenticado": False,
                "cpf_cliente": None,
                "dados_cliente": None,
                "tentativas_auth": 0,
                "encerrado": False,
                "ultimo_erro": None,
                "solicitacao_em_aberto": None,
                "analise_realizada": False,
            }

        result = app_graph.invoke(input_state, config)

        return ChatResponse(
            reply=_extract_reply(result),
            thread_id=thread_id,
            agente_atual=result.get("agente_atual", "triagem"),
            cliente_autenticado=result.get("cliente_autenticado", False),
            dados_cliente=result.get("dados_cliente"),
            encerrado=result.get("encerrado", False),
            tentativas_auth=result.get("tentativas_auth", 0),
        )
    except Exception as exc:
        # Simplificamos o log para evitar erros de encoding no console
        print(f"!!! Erro no chat: {type(exc).__name__}")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/chat/stream")
async def chat_stream(body: ChatRequest):
    """Sends a message and streams the agent response token by token (SSE)."""
    thread_id = body.thread_id or str(uuid.uuid4())
    config = _build_config(thread_id)

    current = app_graph.get_state(config)
    if current.values:
        input_state = {"messages": [HumanMessage(content=body.message)]}
    else:
        input_state = {
            "messages": [HumanMessage(content=body.message)],
            "agente_atual": "triagem",
            "cliente_autenticado": False,
            "cpf_cliente": None,
            "dados_cliente": None,
            "tentativas_auth": 0,
            "encerrado": False,
            "ultimo_erro": None,
            "solicitacao_em_aberto": None,
            "analise_realizada": False,
        }

    async def event_generator():
        try:
            async for chunk in app_graph.astream(
                input_state, config, stream_mode="messages"
            ):
                msg, metadata = chunk if isinstance(chunk, tuple) else (chunk, {})
                if isinstance(msg, AIMessage) and msg.content:
                    payload = json.dumps(
                        {"token": msg.content, "thread_id": thread_id}
                    )
                    yield f"data: {payload}\n\n"

            final = app_graph.get_state(config)
            meta = json.dumps(
                {
                    "done": True,
                    "thread_id": thread_id,
                    "agente_atual": final.values.get("agente_atual", "triagem"),
                    "cliente_autenticado": final.values.get(
                        "cliente_autenticado", False
                    ),
                    "dados_cliente": final.values.get("dados_cliente"),
                    "encerrado": final.values.get("encerrado", False),
                    "tentativas_auth": final.values.get("tentativas_auth", 0),
                }
            )
            yield f"data: {meta}\n\n"
        except Exception as exc:
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/session/{thread_id}")
async def get_session(thread_id: str):
    """Returns the current session state for a given thread_id."""
    config = _build_config(thread_id)
    state = app_graph.get_state(config)
    if not state.values:
        raise HTTPException(status_code=404, detail="Session not found.")
    return {
        "thread_id": thread_id,
        "agente_atual": state.values.get("agente_atual", "triagem"),
        "cliente_autenticado": state.values.get("cliente_autenticado", False),
        "dados_cliente": state.values.get("dados_cliente"),
        "encerrado": state.values.get("encerrado", False),
        "tentativas_auth": state.values.get("tentativas_auth", 0),
        "analise_realizada": state.values.get("analise_realizada", False),
    }
