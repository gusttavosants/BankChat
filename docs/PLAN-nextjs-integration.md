# PLAN: Next.js Frontend Integration for Banco Ágil

## Context & Objectives
Migrate the user interface from Streamlit to a modern Next.js frontend, maintaining the multi-agent logic (LangGraph) in a decoupled Python backend.

---

## Phase 1: Backend Decoupling (Python)
- [ ] Create `api.py` using **FastAPI**.
- [ ] Integrate `app_graph` from `graph.py` into FastAPI endpoints.
- [ ] Implement **LangGraph Persistence** using `MemorySaver` to allow multi-turn conversations via `thread_id`.
- [ ] Standardize API response schemas (JSON) for Chat messages, tool calls, and state updates.

## Phase 2: API Exposure
- [ ] Setup CORS for Next.js communication.
- [ ] Implement a `/chat` endpoint supporting both synchronous and streaming responses.
- [ ] (Optional) Setup **LangServe** for easier integration.

## Phase 3: Frontend Development (Next.js)
- [ ] Initialize Next.js project with Tailwind CSS and ShadcnUI.
- [ ] Build a premium Chat Interface (Dark Mode, Framer Motion animations).
- [ ] Implement State Management (Zustand or React Context) to track session info.
- [ ] Integrate with the Backend API using `fetch` or `SWR`.

## Phase 4: Security & Deployment
- [ ] Configure environment variables (`.env`) for API URLs.
- [ ] Ensure authentication headers if moving beyond a local test.

---

## Verification Checklist
- [ ] Backend returns correct responses for Triage, Credit, and Exchange.
- [ ] Session is persisted (user can refresh the page and continue).
- [ ] UI correctly reflects agent transitions (e.g., color changes per agent).
