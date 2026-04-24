# 📄 Spec Técnico — Banco Ágil: Agente Bancário Inteligente

> Desafio Técnico — Tech For Humans
> Prazo de entrega: **29/04/2026**

---

## 1. Visão Geral

Sistema de atendimento bancário digital baseado em múltiplos agentes de IA. O sistema simula o atendimento completo de um banco digital fictício chamado **Banco Ágil**, onde agentes especializados colaboram de forma transparente — o cliente percebe apenas uma única conversa fluida, sem perceber as transições internas.

---

## 2. Objetivos

- Construir um sistema multi-agente com LangGraph capaz de autenticar clientes, consultar crédito, conduzir entrevistas financeiras e consultar câmbio em tempo real
- Garantir transições imperceptíveis entre agentes
- Entregar uma interface funcional via Streamlit
- Produzir código limpo, modular, bem documentado e com tratamento de erros robusto

---

## 3. Stack Tecnológica

| Camada | Tecnologia | Justificativa |
|---|---|---|
| Orquestração de Agentes | LangGraph | Controle de estado e roteamento entre agentes com grafo explícito |
| LLM | Gemini API / Groq | Free tier disponível, boa performance |
| Ferramentas e Prompts | LangChain | Integração nativa com LangGraph, ecosystem maduro |
| Interface | Streamlit | Simples, rápido e indicado no desafio |
| Manipulação de dados | Pandas | Leitura e escrita dos arquivos CSV |
| API de câmbio | AwesomeAPI | Gratuita, sem necessidade de chave de API |
| Variáveis de ambiente | python-dotenv | Gerenciamento seguro de chaves e configurações |
| Logging | logging (stdlib) | Registro de erros e eventos internos |

---

## 4. Estrutura de Pastas Detalhada

```
banco-agil/
│
├── app.py                          # Entrypoint — Interface Streamlit
│
├── graph.py                        # Grafo LangGraph principal
│                                   # Define nós, arestas e roteamento entre agentes
│
├── state.py                        # BancoAgilState — TypedDict compartilhado
│                                   # Estado global passado entre todos os nós do grafo
│
├── config.py                       # Configurações globais (modelo LLM, paths, constantes)
│
├── agents/                         # Módulo de agentes
│   ├── __init__.py                 # Exporta todos os agentes
│   ├── triagem.py                  # Agente de Triagem (autenticação + roteamento)
│   ├── credito.py                  # Agente de Crédito (limite + solicitação de aumento)
│   ├── entrevista.py               # Agente de Entrevista de Crédito (score financeiro)
│   └── cambio.py                   # Agente de Câmbio (cotação em tempo real)
│
├── tools/                          # Ferramentas LangChain usadas pelos agentes
│   ├── __init__.py                 # Exporta todas as tools
│   ├── auth_tools.py               # autenticar_cliente()
│   ├── credito_tools.py            # consultar_limite(), solicitar_aumento(),
│   │                               # verificar_score_limite()
│   ├── score_tools.py              # calcular_score(), atualizar_score()
│   ├── cambio_tools.py             # consultar_cotacao()
│   └── encerramento_tools.py       # encerrar_atendimento()
│
├── services/                       # Lógica de negócio desacoplada das tools
│   ├── __init__.py
│   ├── auth_service.py             # Regras de autenticação, validação de CPF/data
│   ├── credito_service.py          # Regras de crédito, escrita de solicitações
│   ├── score_service.py            # Fórmula de cálculo de score
│   └── cambio_service.py           # Chamada HTTP à API de câmbio, parsing
│
├── repositories/                   # Camada de acesso a dados (CSVs)
│   ├── __init__.py
│   ├── clientes_repository.py      # CRUD em clientes.csv via Pandas
│   ├── score_repository.py         # Leitura de score_limite.csv
│   └── solicitacoes_repository.py  # Escrita em solicitacoes_aumento_limite.csv
│
├── models/                         # Modelos de dados (dataclasses / Pydantic)
│   ├── __init__.py
│   ├── cliente.py                  # Cliente — CPF, nome, score, limite
│   ├── solicitacao.py              # SolicitacaoAumento — campos do CSV
│   └── cotacao.py                  # Cotacao — moeda, valor, timestamp
│
├── exceptions/                     # Exceções customizadas do domínio
│   ├── __init__.py
│   ├── auth_exceptions.py          # ClienteNaoEncontrado, CredenciaisInvalidas,
│   │                               # MaxTentativasAtingidas
│   ├── credito_exceptions.py       # ScoreInsuficiente, ErroAoGravarSolicitacao
│   └── cambio_exceptions.py        # APIIndisponivel, MoedaNaoSuportada
│
├── utils/                          # Utilitários genéricos
│   ├── __init__.py
│   ├── formatters.py               # Formatação de CPF, moeda, data
│   ├── validators.py               # Validação de CPF, data de nascimento
│   └── logger.py                   # Configuração centralizada de logging
│
├── data/                           # Arquivos de dados CSV
│   ├── clientes.csv
│   ├── score_limite.csv
│   └── solicitacoes_aumento_limite.csv
│
├── tests/                          # Testes automatizados
│   ├── __init__.py
│   ├── test_auth_service.py
│   ├── test_credito_service.py
│   ├── test_score_service.py
│   └── test_cambio_service.py      # Com mock HTTP
│
├── logs/                           # Logs gerados em runtime
│   └── .gitkeep
│
├── .env                            # Variáveis de ambiente (não versionar)
├── .env.example                    # Exemplo de variáveis necessárias
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 5. Fluxo Geral do Sistema

```
Usuário
  │
  ▼
[Agente de Triagem]
  ├── Coleta CPF + data de nascimento
  ├── Autentica via clientes.csv
  ├── Até 3 tentativas → 3ª falha encerra (403)
  └── Identifica intenção → roteia
        │
        ├──► [Agente de Crédito]
        │         ├── Consulta limite atual (200)
        │         ├── Grava solicitação de aumento (201)
        │         ├── Verifica score → aprovado (200) ou rejeitado (422)
        │         └── Se rejeitado → oferece Entrevista de Crédito
        │
        ├──► [Agente de Entrevista de Crédito]
        │         ├── Coleta dados financeiros conversacionalmente
        │         ├── Calcula novo score (200)
        │         ├── Atualiza clientes.csv (200)
        │         └── Redireciona para Agente de Crédito
        │
        └──► [Agente de Câmbio]
                  ├── Consulta cotação via AwesomeAPI (200) ou falha (503)
                  └── Apresenta resultado e encerra (200)
```

---

## 6. Agentes

### 6.1 Agente de Triagem

**Responsabilidade:** Porta de entrada. Autentica e roteia.

**Fluxo:**
1. Saudação inicial
2. Coleta CPF e data de nascimento
3. Valida contra `clientes.csv`
4. Autenticado: identifica intenção e redireciona
5. Falhou: até 3 tentativas — na 3ª encerra com mensagem amigável

**Tools:** `autenticar_cliente`, `encerrar_atendimento`

---

### 6.2 Agente de Crédito

**Responsabilidade:** Consulta de limite e processamento de aumento.

**Fluxo:**
1. Consulta limite atual
2. Recebe novo limite desejado
3. Grava solicitação como `pendente`
4. Verifica score vs `score_limite.csv`
5. Atualiza status para `aprovado` ou `rejeitado`
6. Se rejeitado: oferece Agente de Entrevista

**Tools:** `consultar_limite`, `solicitar_aumento`, `verificar_score_limite`, `encerrar_atendimento`

---

### 6.3 Agente de Entrevista de Crédito

**Responsabilidade:** Entrevista financeira e recálculo de score.

**Coleta:** renda mensal, tipo de emprego, despesas fixas, número de dependentes, existência de dívidas.

**Fórmula de Score:**

```python
score = (
    (renda_mensal / (despesas_fixas + 1)) * 30 +
    peso_emprego[tipo_emprego] +
    peso_dependentes[num_dependentes] +
    peso_dividas[tem_dividas]
)

peso_emprego     = { "formal": 300, "autônomo": 200, "desempregado": 0 }
peso_dependentes = { 0: 100, 1: 80, 2: 60, "3+": 30 }
peso_dividas     = { "sim": -100, "não": 100 }

score_final = min(max(score, 0), 1000)
```

**Tools:** `calcular_score`, `atualizar_score`

---

### 6.4 Agente de Câmbio

**Responsabilidade:** Cotação de moedas em tempo real.

**API:** `https://economia.awesomeapi.com.br/json/last/{MOEDA}-BRL`

**Tools:** `consultar_cotacao`, `encerrar_atendimento`

---

## 7. Estado Compartilhado (LangGraph State)

```python
from typing import TypedDict, Optional

class BancoAgilState(TypedDict):
    messages: list                         # Histórico completo da conversa
    cliente_autenticado: bool              # True após autenticação bem-sucedida
    cpf_cliente: Optional[str]             # CPF do cliente autenticado
    dados_cliente: Optional[dict]          # Dados completos do clientes.csv
    agente_atual: str                      # "triagem" | "credito" | "entrevista" | "cambio"
    tentativas_auth: int                   # Contador de tentativas (max 3)
    encerrado: bool                        # True quando atendimento encerrado
    ultimo_erro: Optional[str]             # Último erro interno registrado
    solicitacao_em_aberto: Optional[dict]  # Solicitação de aumento em andamento
```

---

## 8. Schemas de Dados

### clientes.csv

| Campo | Tipo | Exemplo |
|---|---|---|
| cpf | string | 123.456.789-00 |
| nome | string | João Silva |
| data_nascimento | string DD/MM/YYYY | 15/03/1990 |
| limite_credito | float | 3000.00 |
| score_credito | int (0-1000) | 650 |

### score_limite.csv

| Campo | Tipo | Exemplo |
|---|---|---|
| score_minimo | int | 0 |
| score_maximo | int | 399 |
| limite_maximo_permitido | float | 2000.00 |

### solicitacoes_aumento_limite.csv

| Campo | Tipo | Exemplo |
|---|---|---|
| cpf_cliente | string | 123.456.789-00 |
| data_hora_solicitacao | timestamp ISO 8601 | 2026-04-22T14:30:00 |
| limite_atual | float | 3000.00 |
| novo_limite_solicitado | float | 6000.00 |
| status_pedido | string | pendente / aprovado / rejeitado |

---

## 9. Contratos de Resposta das Tools

Todas as tools retornam um dicionário padronizado:

```python
{
    "status_code": int,    # Código HTTP semântico
    "message": str,        # Mensagem legível para o agente interpretar
    "data": dict | None    # Payload com dados ou None em caso de erro
}
```

---

### 9.1 `autenticar_cliente(cpf, data_nascimento)`

| Situação | status_code | message | data |
|---|---|---|---|
| Autenticado | 200 | "Cliente autenticado com sucesso." | `{cpf, nome, limite_credito, score_credito}` |
| Credenciais inválidas | 401 | "CPF ou data de nascimento incorretos." | None |
| Cliente não encontrado | 404 | "Nenhum cliente encontrado com o CPF informado." | None |
| Máx. tentativas atingido | 403 | "Número máximo de tentativas atingido. Atendimento encerrado." | None |

**Exemplo de retorno 200:**
```python
{
    "status_code": 200,
    "message": "Cliente autenticado com sucesso.",
    "data": {
        "cpf": "123.456.789-00",
        "nome": "João Silva",
        "limite_credito": 3000.00,
        "score_credito": 650
    }
}
```

**Exemplo de retorno 401:**
```python
{
    "status_code": 401,
    "message": "CPF ou data de nascimento incorretos. Verifique os dados e tente novamente.",
    "data": None
}
```

---

### 9.2 `consultar_limite(cpf)`

| Situação | status_code | message | data |
|---|---|---|---|
| Sucesso | 200 | "Limite consultado com sucesso." | `{cpf, limite_atual, score_credito}` |
| Não encontrado | 404 | "Cliente não encontrado na base de dados." | None |

---

### 9.3 `solicitar_aumento(cpf, novo_limite)`

| Situação | status_code | message | data |
|---|---|---|---|
| Criado | 201 | "Solicitação de aumento registrada com sucesso." | `{cpf, limite_atual, novo_limite_solicitado, status_pedido, data_hora}` |
| Erro ao gravar | 500 | "Erro interno ao registrar solicitação." | None |

**Exemplo de retorno 201:**
```python
{
    "status_code": 201,
    "message": "Solicitação de aumento registrada com sucesso.",
    "data": {
        "cpf_cliente": "123.456.789-00",
        "limite_atual": 3000.00,
        "novo_limite_solicitado": 6000.00,
        "status_pedido": "pendente",
        "data_hora_solicitacao": "2026-04-22T14:30:00"
    }
}
```

---

### 9.4 `verificar_score_limite(score, limite_solicitado)`

| Situação | status_code | message | data |
|---|---|---|---|
| Aprovado | 200 | "Score suficiente. Solicitação aprovada." | `{status_pedido, score_atual, limite_maximo_permitido, novo_limite_solicitado}` |
| Rejeitado | 422 | "Score insuficiente para o limite solicitado." | `{status_pedido, score_atual, limite_maximo_permitido, novo_limite_solicitado}` |

---

### 9.5 `calcular_score(renda, tipo_emprego, despesas, dependentes, tem_dividas)`

| Situação | status_code | message | data |
|---|---|---|---|
| Sucesso | 200 | "Score calculado com sucesso." | `{score_calculado, detalhes}` |
| Dados inválidos | 400 | "Tipo de emprego inválido. Use: formal, autônomo ou desempregado." | None |

---

### 9.6 `atualizar_score(cpf, novo_score)`

| Situação | status_code | message | data |
|---|---|---|---|
| Sucesso | 200 | "Score atualizado com sucesso." | `{cpf, score_anterior, score_novo}` |
| Não encontrado | 404 | "Cliente não encontrado. Score não atualizado." | None |

---

### 9.7 `consultar_cotacao(moeda)`

| Situação | status_code | message | data |
|---|---|---|---|
| Sucesso | 200 | "Cotação obtida com sucesso." | `{moeda, moeda_destino, valor_compra, valor_venda, timestamp}` |
| Moeda inválida | 400 | "Moeda não suportada. Disponíveis: USD, EUR, GBP, BTC." | None |
| API fora do ar | 503 | "Serviço de câmbio temporariamente indisponível." | None |

---

### 9.8 `encerrar_atendimento()`

```python
{
    "status_code": 200,
    "message": "Atendimento encerrado.",
    "data": { "encerrado": True }
}
```

---

### Tabela de Status Codes

| Código | Significado | Quando usar |
|---|---|---|
| 200 | OK | Operação realizada com sucesso |
| 201 | Created | Novo registro criado (solicitação gravada no CSV) |
| 400 | Bad Request | Dados inválidos enviados |
| 401 | Unauthorized | Credenciais incorretas |
| 403 | Forbidden | Acesso bloqueado (máximo de tentativas) |
| 404 | Not Found | Recurso não encontrado |
| 422 | Unprocessable Entity | Dados válidos mas regra de negócio não permite |
| 500 | Internal Server Error | Erro inesperado interno |
| 503 | Service Unavailable | Serviço externo indisponível |

---

## 10. Exceções Customizadas

```python
# exceptions/auth_exceptions.py
class ClienteNaoEncontradoError(Exception): pass
class CredenciaisInvalidasError(Exception): pass
class MaxTentativasAtingidasError(Exception): pass

# exceptions/credito_exceptions.py
class ScoreInsuficienteError(Exception): pass
class ErroAoGravarSolicitacaoError(Exception): pass

# exceptions/cambio_exceptions.py
class APIIndisponivelError(Exception): pass
class MoedaNaoSuportadaError(Exception): pass
```

---

## 11. Interface Streamlit

**Funcionalidades:**
- Campo de input de mensagem
- Histórico de conversa com balões diferenciados (usuário / agente)
- Badge visual com o agente ativo atual
- Nome do cliente exibido após autenticação
- Botão de encerrar atendimento
- Spinner durante processamento da resposta

---

## 12. Conventional Commits

Todo commit deve seguir: `tipo(escopo): descrição curta no imperativo`

### Tipos

| Tipo | Quando usar |
|---|---|
| `feat` | Nova funcionalidade |
| `fix` | Correção de bug |
| `refactor` | Refatoração sem mudança de comportamento |
| `docs` | Criação ou edição de documentação |
| `test` | Adição ou correção de testes |
| `chore` | Configuração, dependências, arquivos auxiliares |
| `style` | Formatação, lint (sem mudança de lógica) |
| `perf` | Melhoria de performance |

### Escopos sugeridos

`triagem` · `credito` · `entrevista` · `cambio` · `graph` · `state` · `tools` · `services` · `repositories` · `models` · `exceptions` · `utils` · `ui` · `config` · `tests` · `docs`

---

### Plano de Commits por Ordem de Desenvolvimento

```bash
# Setup
chore(config): initialize project with folder structure and requirements.txt
chore(config): add .env.example with required variables
chore(config): configure .gitignore

# Data and models
chore(data): add clientes.csv and score_limite.csv with test data
feat(models): create Cliente model with CPF, name, score, and limit
feat(models): create SolicitacaoAumento model with CSV fields
feat(models): create Cotacao model with currency, value, and timestamp

# Exceptions
feat(exceptions): add authentication exceptions
feat(exceptions): add credit exceptions
feat(exceptions): add exchange exceptions

# Utilities
feat(utils): add formatters for CPF, currency, and date
feat(utils): add validators for CPF and birth date
feat(utils): configure centralized logger

# Repositories
feat(repositories): implement ClientesRepository with Pandas read/write
feat(repositories): implement ScoreRepository to read score_limite.csv
feat(repositories): implement SolicitacoesRepository to write requests

# Services
feat(services): implement AuthService with CPF and date validation
feat(services): implement CreditoService with limit and score rules
feat(services): implement ScoreService with weighted calculation formula
feat(services): implement CambioService with HTTP call to AwesomeAPI

# Tools
feat(tools): implement autenticar_cliente with standardized response contract
feat(tools): implement consultar_limite
feat(tools): implement solicitar_aumento with CSV writing and 201 return
feat(tools): implement verificar_score_limite with 200 and 422 returns
feat(tools): implement calcular_score
feat(tools): implement atualizar_score
feat(tools): implement consultar_cotacao with 503 error handling
feat(tools): implement encerrar_atendimento

# Agents
feat(triagem): implement Triage Agent with authentication and routing
feat(credito): implement Credit Agent with consultation and limit increase request
feat(entrevista): implement Interview Agent with conversational collection and score calculation
feat(cambio): implement Exchange Agent with real-time quotation

# State and Graph
feat(state): define BancoAgilState with all typed fields
feat(graph): create LangGraph graph with nodes and edges between agents
feat(graph): implement conditional routing function between agents

# Interface
feat(ui): create Streamlit interface with conversation history
feat(ui): add active agent badge and authenticated client name
feat(ui): add end service button and loading spinner

# Tests
test(services): add tests for AuthService
test(services): add tests for ScoreService with edge cases
test(services): add tests for CreditoService
test(services): add tests for CambioService with HTTP mock

# Documentation and final tweaks
docs(readme): add system overview and architecture
docs(readme): add execution tutorial and environment variables
docs(readme): add technical choices and challenges section
fix(credito): fix status update in CSV after approval
refactor(graph): simplify conditional routing logic
chore(config): update requirements.txt with fixed versions
```

---

## 13. Regras Gerais

- Qualquer agente encerra se o usuário pedir
- Nenhum agente atua fora do seu escopo
- Transições entre agentes são imperceptíveis ao cliente
- Tom sempre respeitoso e objetivo
- Erros de CSV ou API tratados graciosamente sem interromper o fluxo
- Logs internos para todos os erros e eventos relevantes

---

## 14. Checklist de Entrega

- [ ] Estrutura de pastas completa e organizada
- [ ] Modelos de dados com Pydantic/dataclass
- [ ] Exceções customizadas por domínio
- [ ] Repositories desacoplados dos services
- [ ] Todas as tools com contratos de resposta padronizados
- [ ] Agente de Triagem com autenticação e 3 tentativas
- [ ] Agente de Crédito com consulta e solicitação de aumento
- [ ] Gravação em `solicitacoes_aumento_limite.csv` com status 201
- [ ] Verificação de score vs `score_limite.csv`
- [ ] Agente de Entrevista com fórmula de score
- [ ] Atualização de score no `clientes.csv`
- [ ] Agente de Câmbio com API real e tratamento de 503
- [ ] LangGraph orquestrando todos os agentes
- [ ] Interface Streamlit funcional com badge de agente
- [ ] Testes automatizados nos services
- [ ] Repositório público no GitHub
- [ ] README completo com todas as seções obrigatórias
- [ ] `.env.example` com todas as variáveis
- [ ] `requirements.txt` com versões fixas
- [ ] Commits seguindo Conventional Commits
