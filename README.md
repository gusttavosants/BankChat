# 🏦 Banco Ágil - Agente Bancário Inteligente

Sistema de atendimento bancário digital construído com múltiplos agentes de Inteligência Artificial usando **LangGraph** e **Streamlit**. Este sistema simula o atendimento completo de um banco digital, orquestrando tarefas como autenticação, consulta de limite, análise de crédito (entrevista financeira) e consulta de cotações em tempo real.

---

## 🏗️ Arquitetura do Sistema

O Banco Ágil utiliza uma arquitetura de **Micro-Agentes Orquestrados** via Grafos de Estado (State Graphs). A lógica é separada por "nós" (nodes), onde cada nó representa um especialista.

![Diagrama de Arquitetura do Sistema](docs/arquitetura.png)
<img width="1271" height="388" alt="image" src="https://github.com/user-attachments/assets/4deb58e7-9fce-40d0-be78-9bc505c40eeb" />
https://drive.google.com/file/d/10r3nPogTvCEYKHrvI9Qr_k2RWA2NFJbu/view?usp=drive_link
*(A imagem acima ilustra o fluxo de estados e a interação entre os agentes)*

### Componentes Principais:
- **Estado Global (`state.py`)**: Um dicionário tipado que mantém o contexto da conversa, dados do cliente autenticado e flags de controle (ex: `analise_realizada`).
- **Grafo de Orquestração (`graph.py`)**: Define as transições entre agentes. Utiliza um **Router** inteligente que interpreta mensagens de sistema e intenções do usuário para decidir o próximo passo.
- **Camada de Serviços (`services/`)**: Contém a lógica de negócio pura (cálculo de score, integração com APIs, regras de crédito).
- **Camada de Dados (`repositories/`)**: Abstração para persistência de dados em arquivos CSV, garantindo que as informações do cliente persistam entre sessões.

### Fluxo de Dados:
1. O usuário interage via UI (Streamlit).
2. A mensagem é enviada para o Grafo.
3. O Agente Atual processa a mensagem usando Ferramentas (`tools/`).
4. O resultado pode disparar uma transição (handoff) para outro agente.
5. O estado é atualizado e a resposta retorna para a interface.

---

## 🤖 Agentes Especializados

1. **Agente de Triagem**: Responsável pelas boas-vindas e pela **Autenticação Segura**. Valida CPF e Data de Nascimento antes de liberar acesso aos serviços.
2. **Agente de Crédito**: Consulta limites e processa pedidos de aumento. Possui lógica para detectar quando uma análise financeira mais profunda é necessária.
3. **Agente de Entrevista (Score)**: Conduz uma conversa estruturada para coletar dados financeiros (renda, despesas, dependentes) e recalcular o score do cliente dinamicamente.
4. **Agente de Câmbio**: Integrado à **AwesomeAPI**, fornece cotações em tempo real de USD, EUR, GBP e BTC.

---

## ✨ Funcionalidades Implementadas

- [x] **Autenticação em 2 Etapas**: Validação de CPF e nascimento com limite de 3 tentativas.
- [x] **Consulta de Limite**: Visualização imediata do limite de crédito atual.
- [x] **Aumento de Limite Inteligente**: Aprovação automática baseada em score ou encaminhamento para entrevista.
- [x] **Entrevista de Crédito Conversacional**: Coleta de dados financeiros de forma natural.
- [x] **Cálculo de Score Dinâmico**: Algoritmo que pondera renda, estabilidade no emprego e compromissos financeiros.
- [x] **Câmbio em Tempo Real**: Integração externa para cotações atualizadas.
- [x] **Tratamento de Erros**: Sistema de logs e mensagens de erro amigáveis para instabilidades técnicas.

---

## 🛠️ Escolhas Técnicas e Justificativas

- **LangGraph**: Escolhido pela capacidade de criar fluxos cíclicos e manter o estado da conversa de forma robusta, essencial para handoffs entre agentes.
- **LangChain Tools**: Facilita a expansão do sistema; adicionar uma nova funcionalidade bancária é tão simples quanto criar uma nova função decorada com `@tool`.
- **Pandas/CSV**: Utilizado para persistência local rápida e fácil auditoria dos dados de teste sem necessidade de configurar um banco de dados complexo (como PostgreSQL) para este desafio.
- **Logging Centralizado**: Implementado para garantir que erros técnicos sejam registrados para análise sem interromper a interação do cliente.

---

## 🧠 Desafios Enfrentados e Soluções

- **Loops Infinitos de Agentes**: Durante o desenvolvimento, os agentes às vezes entravam em loop pedindo a mesma informação. **Solução**: Implementação de flags de estado (ex: `analise_realizada`) que bloqueiam reentradas em fluxos já concluídos.
- **Alucinações em Transições**: O LLM ocasionalmente "esquecia" de apresentar o menu após uma transferência. **Solução**: Refinamento dos prompts de sistema com instruções de "Primeira Tarefa" e uso de gatilhos naturais nas transições.
- **Consistência de Dados**: Garantir que o score calculado na entrevista fosse refletido no limite de crédito. **Solução**: Centralização da lógica de atualização no `ScoreService`, que agora atualiza score e limite de forma atômica no repositório.

---

## 🚀 Tutorial de Execução

### Pré-requisitos
- Python 3.10 ou superior.

### Instalação
1. Clone o repositório.
2. Crie e ative seu ambiente virtual:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

### Configuração
Crie um arquivo `.env` na raiz do projeto:
```ini
OPENROUTER_API_KEY=sua_chave_aqui
LLM_PROVIDER=openrouter
MODEL_NAME=openrouter/free
```

### Execução
Inicie o sistema com:
```bash
streamlit run app.py
```

### Testes
Para rodar a suíte de testes automatizados:
```bash
pytest tests/
```

---
*Desenvolvido como parte do desafio técnico para Agente Bancário Inteligente.*
