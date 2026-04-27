<p align="center">
  <img src="docs/assets/banner.svg" alt="Banco Ágil Streamlit — Plataforma de Agentes Inteligentes" width="100%"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Streamlit-1.32-FF4B4B?logo=streamlit&logoColor=white" alt="Streamlit"/>
  <img src="https://img.shields.io/badge/LangGraph-Latest-orange" alt="LangGraph"/>
  <img src="https://img.shields.io/badge/Pandas-Latest-150458?logo=pandas&logoColor=white" alt="Pandas"/>
</p>

---

## 1. Visão Geral (Versão Streamlit)
Esta é a versão de **Prototipagem Ágil** do Banco Ágil. Desenvolvida em **Streamlit**, esta versão foca na validação rápida da lógica dos agentes, testes de fluxo e experimentação de prompts, utilizando uma infraestrutura simplificada baseada em arquivos locais.

---

## 2. Arquitetura do Sistema
A inteligência do sistema reside no `backend/`, utilizando **LangGraph** para orquestrar agentes especialistas.

### Agentes e Fluxos
- **Triagem**: Gerencia a autenticação e boas-vindas.
- **Especialistas (Crédito, Câmbio, Entrevista)**: Nós do grafo que assumem a conversa conforme a intenção detectada.
- **Roteador Dinâmico**: Lógica de transição que decide o próximo nó com base na resposta da LLM.

### Manipulação de Dados
Nesta versão, a persistência é feita via **Pandas** em arquivos **CSV** localizados em `backend/data/`. Isso permite auditoria imediata e execução sem dependência de bancos de dados em nuvem durante o desenvolvimento.

<p align="center">
  <img src="docs/assets/flow.svg" alt="Arquitetura Multi-Agente" width="100%"/>
</p>

---

## 3. Funcionalidades Implementadas
- **Interface de Chat Funcional**: Chat interativo completo via Streamlit.
- **Mapa de Fluxo Visual**: Visualização do diagrama de agentes diretamente na barra lateral.
- **Simulação de Autenticação**: Validação de dados contra registros em CSV.
- **Lógica de Especialistas Completa**: Câmbio, Limites e Análise Financeira 100% operacionais.
- **Tratamento de Erros Resiliente**: Gestão de instabilidades de rede e timeouts.

---

## 4. Escolhas Técnicas e Justificativas
- **Streamlit**: Escolhido pela velocidade de desenvolvimento. Permite transformar scripts Python em aplicações web em minutos, ideal para validar fluxos de IA.
- **CSV/Pandas**: Justifica-se pela facilidade de teste "zero-config". Não requer setup de Docker ou Cloud para validar a lógica de negócios.
- **Modularização por Agentes**: Cada agente possui seu próprio diretório, facilitando a manutenção e a troca de prompts específicos.

---

## 5. Desafios Enfrentados e Resoluções
- **Feedback Visual de Transição**: No Streamlit, a troca de agentes era invisível para o usuário. **Resolução**: Implementação de nomes de agentes nas mensagens e um indicador de "Agente Atual" na barra lateral.
- **Loop de Menus**: Repetições de menus ao trocar de contexto. **Resolução**: Refatoração do roteador (`router`) para encerrar o turno (`END`) imediatamente após a resposta do especialista.
- **Depreciações de UI**: Mudanças na API do Streamlit afetando o layout. **Resolução**: Migração de parâmetros de largura de imagem para os padrões mais recentes.

---

## 6. Tutorial de Execução e Testes

### Pré-requisitos
- Python 3.10+
- Chave de API (OpenRouter, Groq ou Google) no arquivo `.env`

### Passo a Passo
1. **Instalação**:
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. **Execução**:
   ```bash
   streamlit run app/streamlit_app.py
   ```
3. **Testes**: Use os CPFs presentes em `backend/data/clientes.csv` para testar a autenticação e os diferentes fluxos de crédito e câmbio.

---
*Desenvolvido por Gustavo Santos como parte do protótipo Banco Ágil (Versão Streamlit).*
