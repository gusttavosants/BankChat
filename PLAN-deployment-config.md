# Plano de Configuração de Deploy (Vercel + Render)

## Visão Geral
O objetivo é preparar o repositório "Banco Ágil" para ser implantado em ambiente de produção, separando o frontend (Vercel) e o backend (Render). Além disso, analisaremos a necessidade de uma base de dados externa (Supabase).

## Análise sobre o Banco de Dados (CSV vs Supabase)
**É necessário usar o Supabase? SIM.**
Atualmente, o sistema lê e escreve em arquivos `.csv` locais (ex: `clientes.csv`). Serviços de hospedagem em nuvem como o **Render** utilizam sistemas de arquivos efêmeros em seus serviços Web (especialmente no plano gratuito). Isso significa que:
1. Toda vez que o backend for reiniciado ou atualizado, os dados inseridos (novos limites, scores) **serão perdidos**.
2. O Render não foi feito para manter arquivos modificados localmente.
Portanto, a migração dos CSVs para um banco de dados PostgreSQL (como o **Supabase**) é **obrigatória** para que os dados dos clientes persistam em produção.

## Arquitetura de Deploy Proposta
- **Frontend (Vite/React)**: Hospedado na **Vercel**. Simples, rápido e com CI/CD nativo.
- **Backend (FastAPI)**: Hospedado no **Render** como um Web Service.
- **Database (PostgreSQL)**: Hospedado no **Supabase** (Plano gratuito atende perfeitamente).

---

## Divisão de Tarefas (Task Breakdown)

### Task 1: Migração para Supabase (Banco de Dados)
- **Agent**: `database-architect`
- **Ação**: Criar o schema SQL correspondente aos arquivos `clientes.csv` e `solicitacoes_aumento_limite.csv`. Substituir a leitura/escrita de arquivos no repositório (`clientes_repository.py`) por conexões HTTP ao Supabase usando a lib `supabase-py`.
- **Input -> Output**: CSV atual -> Tabelas relacionais no Supabase.
- **Verify**: Cadastro, atualização de score e limite devem persistir na nuvem.

### Task 2: Configuração do Backend (Render)
- **Agent**: `devops-engineer`
- **Ação**: 
  - Adicionar arquivo `render.yaml` ou configurar o `Procfile` / `start.sh` para rodar o Uvicorn.
  - Ajustar o CORS no `main.py` para aceitar a futura URL da Vercel (ou `*` temporariamente).
  - Listar corretamente as variáveis de ambiente necessárias (`GROQ_API_KEY`, `OPENROUTER_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY`).
- **Verify**: O backend sobe corretamente ouvindo na variável `$PORT` injetada pelo Render.

### Task 3: Configuração do Frontend (Vercel)
- **Agent**: `devops-engineer` / `frontend-specialist`
- **Ação**: 
  - Adicionar arquivo `vercel.json` se necessário para roteamento, ou apenas garantir que o comando `npm run build` do Vite gera a pasta `dist` corretamente.
  - Alterar a variável de ambiente `VITE_API_URL` para apontar para o domínio gerado pelo Render em vez de `localhost:8000`.
- **Verify**: A build passa sem erros de TypeScript e os assets são otimizados.

---

## ✅ FASE DE APROVAÇÃO (Socratic Gate)

Antes de iniciarmos a configuração e a escrita de código, preciso alinhar os seguintes pontos:

1. **Conta Supabase**: Você já tem uma conta no Supabase para criarmos o banco de dados, ou prefere que eu te ensine os passos rápidos para pegar a `URL` e `KEY` de lá?
2. **CORS de Segurança**: Você quer que eu já restrinja a comunicação do Backend para aceitar apenas requisições da Vercel, ou deixamos aberto temporariamente para facilitar o debug?
3. **Migração Inicial**: Quer que eu crie um script Python (`migrate.py`) para pegar os dados que já existem nos seus CSVs atuais e injetar automaticamente no banco do Supabase?
