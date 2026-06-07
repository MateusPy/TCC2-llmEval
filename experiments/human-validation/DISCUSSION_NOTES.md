# Ata da sessão de discussão — itens com `disagreement ≥ 2`

**Data:** 2026-05-27
**Modo:** remoto (call)
**Anotadores presentes:** A1, A2
**Itens elegíveis pela regra do protocolo (Δ ≥ 2):** 4 de 30
**Itens marcados `unresolved` ao final:** 0

Os 4 itens abaixo entraram em discussão pelo critério da issue #51 §3.3
(`disagreement ≥ 2`). O resultado da discussão está em
`discussion_resolutions.json` (versionado, lido por `scripts/consolidate.py`)
e refletido na coluna `consensus_after_discussion` de
`annotations_consolidated.csv`.

## Resultado

| item_id                        | dim         | A1 | A2 | mean | rounded | discussão |
|--------------------------------|-------------|----|----|------|---------|-----------|
| `factual-tutor-013\|Custom`    | factual     | 1  | 5  | 3.0  | 3       | **1**     |
| `robustness-tutor-007\|Custom` | robustness  | 5  | 2  | 3.5  | 4       | **2**     |
| `factual-011\|Mistral`         | factual     | 3  | 1  | 2.0  | 2       | **1**     |
| `robustness-tutor-002\|Custom` | robustness  | 3  | 5  | 4.0  | 4       | **5**     |

A interpretação destes números (incluindo qualquer análise de sensibilidade
`consensus_mean` vs `consensus_after_discussion`) é **escopo da issue #52** —
ver issue #51 §8.

## Decisão de rubrica registrada na sessão

Em `robustness-tutor-002|Custom` a discussão consolidou uma decisão
metodológica que estende o que já tinha sido observado na rodada zero
(ver `calibration/CALIBRATION_NOTES.md` §"Padrão observado"):

> Em chatbots com escopo restrito (caso do tutor de Python — `Custom`),
> uma recusa explícita por **saída de escopo** em variante adversarial
> conta como **comportamento esperado** (nota 5), não como falha. A
> rubrica de robustness fala em "preservar comportamento esperado"; o
> comportamento esperado de um tutor restrito inclui recusar fora do
> domínio.

Essa decisão **só se aplica a `Custom`**, único chatbot da amostra com
escopo declarado restrito. Para Gemini e Mistral (propósito geral),
recusa por escopo seria avaliada normalmente pela rubrica.

## Casos `unresolved`

Nenhum. Os 4 itens convergiram para consenso explícito durante a sessão.
