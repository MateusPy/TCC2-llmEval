# PILOT_NOTES — Issue #49

> Preencher após as duas runs (`config-gemini.yaml` e `config-mistral.yaml`).
> Este documento alimenta as decisões do **full run** (#50) e o Cap. 5.1
> (Setup experimental).

**Data de execução:** _(YYYY-MM-DD)_
**Executor:** _(quem rodou)_
**Commit do repo:** _(`git rev-parse --short HEAD` antes da run)_

---

## 1. Configuração efetiva

| Item | Gemini | Mistral |
|---|---|---|
| Modelo do chatbot | `gemini-2.0-flash-001` | `mistral-small-2503` |
| Modelo do juiz | `gemini-2.0-flash-001` | `gemini-2.0-flash-001` |
| Repetições | 3 | 3 |
| Temperature | 0.0 | 0.0 |
| Seed | 42 | 42 |
| Cenários por dimensão | 10 (primeiros por ID) | idem |

---

## 2. Tempo de execução

| Run | Início | Fim | Duração total | Wall-clock por cenário (média) |
|---|---|---|---|---|
| Gemini | | | | |
| Mistral | | | | |

> Fonte: `metadata.duration_seconds` no `run_result.json` (se o campo existir)
> ou diferença entre primeiro e último `timestamp` em `details[]`.

---

## 3. Custo / tokens consumidos

| Run | Prompt tokens | Completion tokens | Total tokens | Custo USD estimado |
|---|---|---|---|---|
| Gemini (chatbot) | | | | |
| Gemini (juiz) | | | | |
| Mistral (chatbot) | | | | |

> Como calcular: somar `parameters.usage.{prompt,completion,total}_tokens`
> nos `ScenarioResult`s. Pricing de referência (verificar atual):
> - Gemini 2.0 Flash: $0.10/M input, $0.40/M output
> - Mistral Small: $0.20/M input, $0.60/M output

---

## 4. Problemas encontrados

### Rate limits
- [ ] Nenhum
- [ ] Gemini hit 15 req/min — runs atrasaram em _N_ minutos
- [ ] Mistral hit limit — _detalhes_

### Erros por cenário
| Cenário | Dimensão | Erro | Causa provável |
|---|---|---|---|

### Respostas vazias / fallbacks do juiz
| Cenário | Dimensão | Sintoma | `justification_fallback`? |
|---|---|---|---|

### Outros
_(timeout, erro de parser, comportamento inesperado, etc.)_

---

## 5. Resultados em alto nível

| Dimensão | Gemini score médio | Mistral score médio | Observação |
|---|---|---|---|
| factual | | | |
| consistency | | | |
| robustness | | | |

> Fonte: `summary.by_dimension.*.mean` em `report.json`.

---

## 6. Extrapolação para o full run (#50)

Multiplicadores:

| Dimensão | Cenários no piloto | Cenários no full | Multiplicador |
|---|---|---|---|
| factual | 10 | 35 | 3.5× |
| consistency | 10 (+ ~30 paráfrases) | 20 (+ ~62 paráfrases) | 2.0× |
| robustness | 10 (+ ~30 variantes) | 20 (+ ~61 variantes) | 2.0× |

| Item | Piloto | Full run extrapolado |
|---|---|---|
| Tempo Gemini | | |
| Tempo Mistral | | |
| Custo total USD | | |
| Calls totais | | |

---

## 7. Decisões para o full run

- [ ] `repetitions` = _N_ (confirmar 3 ou reduzir)
- [ ] `temperature` = _X_ (manter 0.0 ou variar?)
- [ ] Juiz = _qual?_ (manter Gemini ou trocar?)
- [ ] Inclusão do chatbot demo (#60) como 3º provider — _sim/não, justificar_

---

## 8. Sign-off

- [ ] Johnny revisou
- [ ] Mateus revisou
- [ ] Profa. Elaine ciente
