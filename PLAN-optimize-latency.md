# Otimização de Tempo de Resposta (Latency)

## Visão Geral
O fluxo atual de "Entrevista Financeira" pode levar até 2 minutos para responder porque a arquitetura multi-agente (LangGraph) exige que a LLM (Gemini 3.1 Pro via OpenRouter) execute chamadas sequenciais (ReAct):
1. LLM decide chamar `calcular_score`
2. Backend roda a ferramenta e devolve
3. LLM decide chamar `atualizar_score`
4. Backend roda a ferramenta e devolve
5. LLM decide chamar `solicitar_aumento`
6. LLM gera a mensagem de texto final para o usuário.

Cada requisição de "raciocínio" à API está levando de 10s a 30s.

## Critérios de Sucesso
- Reduzir o número de viagens (round-trips) à API da LLM durante o uso de ferramentas.
- Fornecer feedback visual ao usuário (UX) caso o processo demore mais de 5 segundos.
- Manter as regras de negócio de cálculos e atualização de CSV intactas.

## Estratégias de Otimização Propostas

### 1. Consolidação de Ferramentas (Tool Consolidation) - *Alto Impacto*
Em vez de ter 3 ferramentas separadas que a LLM precisa descobrir e chamar em ordem, podemos criar uma única ferramenta chamada `processar_analise_credito(renda, tipo_emprego, despesas, dependentes, dividas, limite_atual)`. 
- O **backend** fará o cálculo do score.
- O **backend** verificará se é maior que o limite.
- O **backend** atualizará o CSV se necessário.
- A LLM só precisa fazer **UMA ÚNICA** chamada e receber a string final pronta para apresentar ao cliente.
- *Redução de latência esperada: de ~120s para ~20s.*

### 2. Provider / Modelo de Baixa Latência - *Médio Impacto*
Você está usando o modelo via OpenRouter, que pode ter oscilações de fila. Para agentes que tomam decisões rígidas e simples (Triagem, Roteamento), usar uma API focada em latência ultrabaixa (ex: Groq com Llama-3-8b-instant, que responde em <1s) e deixar o Gemini Pro apenas para a fase de Entrevista (compreensão natural profunda).

### 3. Feedback de UX (Server-Sent Events / LangGraph Streaming) - *Impacto Visual*
Se o processamento for demorar, podemos fazer o backend emitir eventos intermediários (Yields) para o Frontend.
- A UI exibirá: *"🤖 Analisando suas finanças..."*, *"📊 Calculando score..."*
- Isso não reduz o tempo técnico, mas zera a percepção de travamento (UX Psychology - Tolerância a Espera).

## Divisão de Tarefas (Task Breakdown)

### Task 1: Refatorar Ferramentas de Entrevista
- **Agent**: `backend-specialist`
- **Skill**: `api-patterns`, `python-patterns`
- **Ação**: Criar `processar_analise_credito` em `entrevista/tools.py` que agrupe toda a lógica do `service.py` internamente.
- **Input -> Output**: Receber 5 variáveis de input -> Devolver string formatada com novo score e se o limite foi aprovado.
- **Verify**: A LLM deverá chamar apenas 1 ferramenta em vez de 3.

### Task 2: Atualizar Prompt do Agente Entrevista
- **Agent**: `backend-specialist`
- **Skill**: `clean-code`
- **Ação**: Atualizar o `system_prompt` do nó de entrevista para usar apenas a nova macro-ferramenta e instruir como montar a resposta final baseada no retorno unificado.
- **Verify**: Agente de entrevista testado sem entrar em loop.

### Task 3 (Opcional): Implementar Mensagens de Status na UI
- **Agent**: `frontend-specialist`
- **Ação**: Ajustar a chamada da API e o `MessageBubble` para exibir *typing indicators* dinâmicos com base em retornos parciais (se o backend enviar status de ferramenta).

---
## ✅ FASE DE APROVAÇÃO (Socratic Gate)

Antes de escrever qualquer código, preciso entender sua prioridade para esta otimização. Responda:

1. **Abordagem de Backend**: Você concorda em unificarmos as 3 ferramentas (`calcular`, `atualizar` e `solicitar`) em uma única macro-ferramenta no Python para economizar chamadas da LLM?
2. **Mudança de Modelo**: Você prefere manter tudo no OpenRouter/Gemini e apenas otimizar o código, ou tem interesse em configurar um modelo ultrarrápido (Groq) para certas etapas?
3. **Qualidade Visual**: Acha necessário criarmos mensagens falsas de "carregando" na tela, ou apenas cortar o tempo para 20s unificando as ferramentas já resolve o seu problema atual?
