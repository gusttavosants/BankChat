# Banco Ágil - Intelligent Agent Implementation

## Goal
Build a multi-agent digital banking system (Banco Ágil) using LangGraph and Streamlit, featuring triage, credit, interview, and exchange agents, with all commits following Conventional Commits in English.

## Tasks
- [x] Task 1: Initialize project structure, config, `.env.example`, and `.gitignore`. → Verify: Root folders (`agents`, `tools`, `services`, etc.) exist.
- [x] Task 2: Add test data files and create Pydantic/dataclass models (`Cliente`, `SolicitacaoAumento`, `Cotacao`). → Verify: `models/` files are created and typed.
- [x] Task 3: Create custom exceptions and utility functions (formatters, validators, logger). → Verify: Custom exceptions exist and CPF/date utilities work correctly.
- [x] Task 4: Implement repository layer (`ClientesRepository`, `ScoreRepository`, `SolicitacoesRepository`). → Verify: Can read from `clientes.csv` and write to `solicitacoes_aumento_limite.csv` via Pandas.
- [x] Task 5: Implement service layer (`AuthService`, `CreditoService`, `ScoreService`, `CambioService`). → Verify: Business rules (like score calculation and HTTP calls) are applied.
- [x] Task 6: Implement LangChain tools with standardized response contracts. → Verify: Tools return valid `{"status_code", "message", "data"}` payloads.
- [x] Task 7: Implement the 4 LangGraph agents (Triage, Credit, Interview, Exchange). → Verify: Agents correctly wrap their tools and logic.
- [x] Task 8: Define `BancoAgilState` and construct the main LangGraph with conditional routing. → Verify: The graph state updates properly and routing transitions between agents.
- [x] Task 9: Build the Streamlit interface (`app.py`) with chat history, agent badges, and spinner. → Verify: `streamlit run app.py` launches a functional UI.
- [x] Task 10: Write automated tests for services and complete the documentation (`README.md`). → Verify: Tests pass and documentation explains the execution steps.

## Done When
- [x] The Streamlit UI allows a fluid conversation that transparently shifts between all 4 agents.
- [x] Authentication respects the 3-attempt limit.
- [x] Credit scores and limits are accurately verified, recalculated (if needed), and stored.
- [x] Live exchange rates are properly fetched and handled.
- [x] Commit history is maintained strictly in English using Conventional Commits.
