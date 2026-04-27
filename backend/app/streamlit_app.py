import sys
import os

# Adiciona a pasta raiz (backend) ao path para resolver os imports de core e agents
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from core.graph import app_graph
from core.state import BancoAgilState

st.set_page_config(page_title="Banco Ágil", page_icon="🏦", layout="centered")

# Exibe o Banner SVG
banner_path = os.path.join(os.path.dirname(__file__), "static", "banner.svg")
if os.path.exists(banner_path):
    st.image(banner_path, width="stretch")
else:
    st.title("🏦 Banco Ágil - Atendimento Digital")

# Inicializa state no session_state
if "state" not in st.session_state:
    st.session_state.state = BancoAgilState(
        messages=[],
        cliente_autenticado=False,
        cpf_cliente=None,
        dados_cliente=None,
        agente_atual="triagem",
        tentativas_auth=0,
        encerrado=False,
        ultimo_erro=None,
        solicitacao_em_aberto=None,
        analise_realizada=False
    )

# Exibe histórico
messages = st.session_state.state.get("messages", [])
i = 0
while i < len(messages):
    msg = messages[i]
    
    if isinstance(msg, HumanMessage) and msg.content:
        with st.chat_message("user"):
            st.write(msg.content)
        i += 1
    elif isinstance(msg, AIMessage) and msg.content:
        # Agrupa mensagens consecutivas do assistente
        with st.chat_message("assistant", avatar="🏦"):
            st.markdown("**Atendimento Ágil**")
            while i < len(messages) and isinstance(messages[i], AIMessage):
                if messages[i].content:
                    st.write(messages[i].content)
                i += 1
    else:
        i += 1

# Status/Badge
st.sidebar.title("Informações da Sessão")
st.sidebar.badge = st.sidebar.info(f"Agente Atual: {st.session_state.state.get('agente_atual', 'triagem').title()}")

# Exibe o Fluxo SVG no Sidebar
flow_path = os.path.join(os.path.dirname(__file__), "static", "flow.svg")
if os.path.exists(flow_path):
    with st.sidebar.expander("Visualizar Fluxo de Atendimento", expanded=False):
        st.image(flow_path, width="stretch")

if st.session_state.state.get("cliente_autenticado"):
    dados = st.session_state.state.get("dados_cliente", {})
    st.sidebar.success(f"Autenticado como: {dados.get('nome', 'Cliente')}")

if st.sidebar.button("Encerrar Atendimento"):
    st.session_state.state["encerrado"] = True
    st.rerun()

if st.sidebar.button("Reiniciar Atendimento"):
    del st.session_state.state
    st.rerun()

if st.session_state.state.get("encerrado"):
    st.success("Atendimento encerrado. Obrigado por utilizar o Banco Ágil!")
    if st.button("Iniciar Novo Atendimento"):
        del st.session_state.state
        st.rerun()
    st.stop()

# Chat input
if prompt := st.chat_input("Digite sua mensagem..."):
    # Exibe a mensagem do usuário
    with st.chat_message("user"):
        st.write(prompt)
        
    user_msg = HumanMessage(content=prompt)
    st.session_state.state["messages"].append(user_msg)
    
    with st.spinner("Processando..."):
        try:
            # Executa o grafo com limite de recursão aumentado
            result = app_graph.invoke(
                st.session_state.state, 
                config={"recursion_limit": 50}
            )
            
            # Atualiza o estado
            st.session_state.state.update(result)
        except Exception as e:
            st.error("Ops! Tivemos uma instabilidade na conexão com nossos servidores de inteligência artificial.")
            st.warning("Isso geralmente é temporário. Por favor, tente enviar sua mensagem novamente em alguns segundos.")
            # Remove a última mensagem do usuário para permitir tentar de novo sem duplicar no histórico visual se o usuário reenviar
            if st.session_state.state["messages"] and isinstance(st.session_state.state["messages"][-1], HumanMessage):
                st.session_state.state["messages"].pop()
            st.stop()

    st.rerun()
