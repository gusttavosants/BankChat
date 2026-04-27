# Plano de Correção de Bugs de Lógica e Conversação

Este documento detalha as ações necessárias para corrigir as inconsistências de limite, repetições de mensagens e quebras de fluxo identificadas.

## 1. Correção da Lógica de Limite vs Score
**Problema:** O agente informa que o limite máximo (ex: R$ 5.000) é menor que o atual (ex: R$ 8.000).
**Solução:** 
- Alterar o `CreditoService` e a ferramenta `verificar_score_limite` para que o "Limite Máximo Permitido" seja sempre o maior valor entre o teto do score e o limite atual do cliente.
- Ajustar o prompt para que, caso o cliente já esteja no teto, o agente explique que "seu perfil atual já atingiu o limite máximo de concessão automática, sendo necessária a análise para qualquer valor adicional".

## 2. Eliminação de Perguntas Duplicadas (Entrevista)
**Problema:** A pergunta "Qual sua renda mensal bruta?" aparece duas vezes seguidas.
**Solução:**
- Simplificar o `prompt_transferencia` no arquivo `backend/agents/entrevista/node.py`.
- Remover a instrução redundante de "perguntar imediatamente" na transferência, deixando que o System Prompt (que já tem essa regra como prioridade 1) gerencie a primeira pergunta naturalmente.

## 3. Suavização de Transições e Redirecionamento
**Problema:** Mensagens de "Você será redirecionado" seguidas imediatamente por menus de opções.
**Solução:**
- No `agente_credito_node`, adicionar uma verificação: se o `agente_atual` anterior era `entrevista` e a `analise_realizada` é `True`, o agente não deve reapresentar o menu de opções, mas sim dar continuidade ao resultado da análise (ex: "Agora que atualizamos seu perfil, como deseja prosseguir com seu novo limite?").
- Ajustar o `router` no `graph.py` para garantir que a transição seja silenciosa quando houver dados novos de score.

## 4. Próximos Passos (Implementação)
1. Modificar `backend/services/credito_service.py` (Lógica de validação).
2. Modificar `backend/agents/entrevista/node.py` (Ajuste de prompt e repetição).
3. Modificar `backend/agents/credito/node.py` (Lógica de reapresentação de menu).
