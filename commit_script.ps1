# Setup
git add requirements.txt config.py
git commit -m "chore(config): initialize project with folder structure and requirements.txt"
git add .env.example
git commit -m "chore(config): add .env.example with required variables"
git add .gitignore
git commit -m "chore(config): configure .gitignore"

# Data and models
git add data/clientes.csv data/score_limite.csv
git commit -m "chore(data): add clientes.csv and score_limite.csv with test data"
git add models/cliente.py
git commit -m "feat(models): create Cliente model with CPF, name, score, and limit"
git add models/solicitacao.py
git commit -m "feat(models): create SolicitacaoAumento model with CSV fields"
git add models/cotacao.py
git commit -m "feat(models): create Cotacao model with currency, value, and timestamp"
git add models/__init__.py
git commit -m "chore(models): configure models init"

# Exceptions
git add exceptions/auth_exceptions.py
git commit -m "feat(exceptions): add authentication exceptions"
git add exceptions/credito_exceptions.py
git commit -m "feat(exceptions): add credit exceptions"
git add exceptions/cambio_exceptions.py
git commit -m "feat(exceptions): add exchange exceptions"
git add exceptions/__init__.py
git commit -m "chore(exceptions): configure exceptions init"

# Utilities
git add utils/formatters.py
git commit -m "feat(utils): add formatters for CPF, currency, and date"
git add utils/validators.py
git commit -m "feat(utils): add validators for CPF and birth date"
git add utils/logger.py
git commit -m "feat(utils): configure centralized logger"
git add utils/__init__.py
git commit -m "chore(utils): configure utils init"

# Repositories
git add repositories/clientes_repository.py
git commit -m "feat(repositories): implement ClientesRepository with Pandas read/write"
git add repositories/score_repository.py
git commit -m "feat(repositories): implement ScoreRepository to read score_limite.csv"
git add repositories/solicitacoes_repository.py
git commit -m "feat(repositories): implement SolicitacoesRepository to write requests"
git add repositories/__init__.py
git commit -m "chore(repositories): configure repositories init"

# Services
git add services/auth_service.py
git commit -m "feat(services): implement AuthService with CPF and date validation"
git add services/credito_service.py
git commit -m "feat(services): implement CreditoService with limit and score rules"
git add services/score_service.py
git commit -m "feat(services): implement ScoreService with weighted calculation formula"
git add services/cambio_service.py
git commit -m "feat(services): implement CambioService with HTTP call to AwesomeAPI"
git add services/__init__.py
git commit -m "chore(services): configure services init"

# Tools
git add tools/auth_tools.py
git commit -m "feat(tools): implement autenticar_cliente with standardized response contract"
git add tools/credito_tools.py
git commit -m "feat(tools): implement consultar_limite and solicitar_aumento with CSV writing and 201 return"
git add tools/score_tools.py
git commit -m "feat(tools): implement verificar_score_limite with 200 and 422 returns, calcular_score, atualizar_score"
git add tools/cambio_tools.py
git commit -m "feat(tools): implement consultar_cotacao with 503 error handling"
git add tools/encerramento_tools.py
git commit -m "feat(tools): implement encerrar_atendimento"
git add tools/__init__.py
git commit -m "chore(tools): configure tools init"

# Agents
git add agents/triagem.py
git commit -m "feat(triagem): implement Triage Agent with authentication and routing"
git add agents/credito.py
git commit -m "feat(credito): implement Credit Agent with consultation and limit increase request"
git add agents/entrevista.py
git commit -m "feat(entrevista): implement Interview Agent with conversational collection and score calculation"
git add agents/cambio.py
git commit -m "feat(cambio): implement Exchange Agent with real-time quotation"
git add agents/__init__.py
git commit -m "chore(agents): configure agents init"

# State and Graph
git add state.py
git commit -m "feat(state): define BancoAgilState with all typed fields"
git add graph.py
git commit -m "feat(graph): create LangGraph graph with nodes and edges between agents"

# Interface
git add app.py .streamlit/config.toml
git commit -m "feat(ui): create Streamlit interface with conversation history, active agent badge, and end service button"

# Tests
git add tests/test_auth_service.py
git commit -m "test(services): add tests for AuthService"
git add tests/test_score_service.py
git commit -m "test(services): add tests for ScoreService with edge cases"
git add tests/test_credito_service.py
git commit -m "test(services): add tests for CreditoService"
git add tests/test_cambio_service.py
git commit -m "test(services): add tests for CambioService with HTTP mock"
git add tests/__init__.py
git commit -m "chore(tests): configure tests init"

# Documentation and final tweaks
git add README.md
git commit -m "docs(readme): add system overview, architecture, tech choices, execution tutorial and environment variables"

# Final fixes
git add .
git commit -m "chore(config): update requirements.txt with fixed versions and final cleanup"
