<p align="center">
  <img src="https://github.com/user-attachments/assets/4deb58e7-9fce-40d0-be78-9bc505c40eeb" alt="Banco Ágil — Plataforma de Agentes Inteligentes" width="100%"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Streamlit-1.32-FF4B4B?logo=streamlit&logoColor=white" alt="Streamlit"/>
  <img src="https://img.shields.io/badge/LangGraph-Latest-orange" alt="LangGraph"/>
  <img src="https://img.shields.io/badge/Pandas-Latest-150458?logo=pandas&logoColor=white" alt="Pandas"/>
</p>

---

## Visão Geral (Versão Streamlit)

O **Banco Ágil** é uma plataforma de atendimento bancário baseada em **agentes de inteligência artificial especializados**. Esta versão utiliza o **Streamlit** para fornecer uma interface de chat rápida e funcional, ideal para testes de lógica de agentes e demonstrações rápidas.

Cada agente possui um domínio de competência específico (câmbio, crédito, entrevista de crédito) e opera de forma autônoma, sendo orquestrado por um grafo de estados que classifica a intenção do cliente.

### Principais capacidades

- **Multi-agente com roteamento inteligente**: Triagem automática por intenção via LangGraph.
- **Cálculo de Score Dinâmico**: Algoritmo que processa dados financeiros coletados durante a entrevista.
- **LLM Gateway Multi-provider**: Suporte para Groq, Google Gemini, OpenAI e OpenRouter.
- **Persistência em CSV**: Auditoria imediata dos dados de teste sem necessidade de banco de dados.

---

## Arquitetura do Sistema

O sistema opera com uma arquitetura multi-agente onde cada nó do grafo é um especialista isolado:

| Agente | Slug | Responsabilidade |
|---|---|---|
| **Triagem** | `triagem` | Boas-vindas e Autenticação. |
| **Crédito** | `credito` | Consulta limites e processa pedidos de aumento. |
| **Entrevista** | `entrevista` | Coleta dados financeiros e recalcula score. |
| **Câmbio** | `cambio` | Consulta cotações em tempo real via AwesomeAPI. |

---

## Tutorial de Execução

### Pré-requisitos
- Python 3.10+
- Chave de API (Groq, OpenRouter ou Google)

### 1. Instalação

```bash
# Clone o repositório
git clone https://github.com/gusttavosants/BankChat.git
cd BankChat

# Setup Backend
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Configuração do `.env`

Crie o arquivo `backend/.env`:
```ini
# API Keys
GROQ_API_KEY=sua_chave_aqui
OPENROUTER_API_KEY=sua_chave_aqui

# Configurações de LLM
LLM_PROVIDER=openrouter # groq | google | openrouter
MODEL_NAME=minimax/minimax-01
```

### 3. Execução

Inicie a interface Streamlit:
```bash
streamlit run app/streamlit_app.py
```

---

## Estrutura do Repositório

```text
banco-agil/
├── backend/                # Lógica Central e Agentes
│   ├── agents/             # Nós do LangGraph
│   ├── app/                # Interface Streamlit (streamlit_app.py)
│   ├── core/               # Orquestração e Estado
│   ├── data/               # Banco de dados em CSV
│   ├── repositories/       # Camada de Acesso a Dados
│   ├── services/           # Lógica de Negócio
│   └── utils/              # Formatadores e Loggers
└── README.md
```

---
*Desenvolvido por Gustavo Santos como parte do desafio técnico para Agente Bancário Inteligente.*
