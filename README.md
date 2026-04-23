# 🏦 Banco Ágil - Agente Bancário Inteligente

Sistema de atendimento bancário digital construído com múltiplos agentes de Inteligência Artificial usando LangGraph e Streamlit. Este sistema simula o atendimento completo de um banco digital, orquestrando tarefas como autenticação, consulta de limite, análise de crédito (entrevista financeira) e consulta de cotações em tempo real.

## 🌟 Visão Geral e Arquitetura

O Banco Ágil funciona como uma malha de agentes especializados (Multi-Agent System). A experiência para o usuário é única e fluida, sem que ele perceba que está trafegando entre diferentes cérebros (nós) do sistema.

### Agentes:
1. **Agente de Triagem**: Porta de entrada do sistema. Coleta CPF e Data de Nascimento, autentica o usuário (máximo 3 tentativas) e realiza o roteamento baseado na intenção.
2. **Agente de Crédito**: Especialista em conta. Verifica o limite atual e processa pedidos de aumento. Caso o score do cliente não seja compatível, redireciona para a Entrevista.
3. **Agente de Entrevista (Score)**: Faz uma análise profunda e conversacional. Coleta renda mensal, tipo de emprego, despesas, número de dependentes e dívidas, aplicando a fórmula do Banco Ágil para atualizar o score do cliente.
4. **Agente de Câmbio**: Informa a cotação de moedas estrangeiras (USD, EUR, GBP, BTC) em tempo real buscando da AwesomeAPI.

## 🛠️ Escolhas Técnicas

- **LangGraph**: Orquestração do fluxo de controle (Grafos) e estado compartilhado entre os agentes de forma previsível e auditável.
- **LangChain**: Integração de Tools padrão da indústria, facilitando o acoplamento do LLM com funções Python (Services).
- **Streamlit**: Criação rápida de interfaces conversacionais interativas sem necessidade de escrever Javascript.
- **Pandas**: Utilizado como Repository (Banco de Dados em memória/disco via CSV) para facilitar as avaliações locais.
- **AwesomeAPI**: Endpoint gratuito para conversão de moedas sem necessidade de chaves de API extras.
- **Provider LLM Agóstico**: Suporte nativo para Gemini, Groq e OpenRouter.

## 🚀 Tutorial de Execução

### Pré-requisitos
- Python 3.10 ou superior.

### Instalação
1. Clone o repositório.
2. Crie um ambiente virtual:
   ```bash
   python -m venv venv
   # No Windows:
   venv\Scripts\activate
   # No Linux/Mac:
   source venv/bin/activate
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

### Configuração de Ambiente
Crie um arquivo `.env` na raiz do projeto (ou copie o `.env.example`) e configure suas chaves:

```ini
# API Keys (exemplo)
OPENROUTER_API_KEY=sk-or-v1-...
GOOGLE_API_KEY=AIzaSy...

# Provider e Modelo
LLM_PROVIDER=openrouter
MODEL_NAME=openrouter/free
```
*(Nota: O provedor OpenRouter e o modelo `openrouter/free` garantem um roteamento gratuito de IA sem limites de uso).*

### Rodando o Projeto
Inicie a interface com o comando:
```bash
streamlit run app.py
```
Acesse `http://localhost:8501` em seu navegador.

### Testando
Os CPFs de testes disponíveis no banco de dados (`data/clientes.csv`) são:
- `123.456.789-00` (Nasc: 15/03/1990)
- `098.765.432-11` (Nasc: 20/07/1985)
- `111.222.333-44` (Nasc: 10/10/2000)

## 🧪 Testes Automatizados

O sistema conta com testes automatizados utilizando `pytest` focados na camada de serviços (Regras de Negócio). Para executá-los, rode:
```bash
pytest tests/
```
