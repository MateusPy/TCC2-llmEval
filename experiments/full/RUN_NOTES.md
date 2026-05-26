# RUN_NOTES — Issue #50 (Full Run)

Notas de execução das 3 runs principais + 2 shadow do full run da #50.
Alimenta o Cap. 5 do TCC.

**Data de execução:** _(preencher)_
**Executor:** Johnny
**Branch:** `feat/50-full-run-3-chatbots`
**Commit:** _(preencher após push)_

Decisões metodológicas, configurações e racional do piloto: ver
[`experiments/pilot/PILOT_NOTES.md`](../pilot/PILOT_NOTES.md) §7 e
[`experiments/pilot/PILOT_ANALYSIS.md`](../pilot/PILOT_ANALYSIS.md) §7.
Esta sessão herda essas decisões e endereça os 3 blockers pré-registrados.

---

## 1. Configuração efetiva

| Item                  | Gemini main          | Mistral main         | Custom (CI)                       | Shadow Gemini        | Shadow Mistral       |
|-----------------------|----------------------|----------------------|-----------------------------------|----------------------|----------------------|
| Modelo chatbot        | gemini-2.5-flash-lite| ministral-3b-2512    | llama-3.1-8b-instant (Groq)       | gemini-2.5-flash-lite| ministral-3b-2512    |
| Modelo juiz           | gemini-2.5-flash-lite| gemini-2.5-flash-lite| gemini-2.5-flash-lite             | mistral-small-2503   | mistral-small-2503   |
| Repetições            | 3                    | 3                    | 3                                 | 3                    | 3                    |
| Temperature           | 0.0                  | 0.0                  | 0.0                               | 0.0                  | 0.0                  |
| Banco                 | embutido (75 cen.)   | embutido (75 cen.)   | tutor Python (35 cen.)            | embutido (75 cen.)   | embutido (75 cen.)   |
| Total prompts         | 198                  | 198                  | 95                                | 198                  | 198                  |

Hash do banco usado: ver `metadata.json` de cada run.

---

## 2. Tempo de execução

| Run            | Início (UTC) | Fim (UTC) | Duração   | Médio/cenário |
|----------------|--------------|-----------|-----------|---------------|
| Gemini main    | _            | _         | _         | _             |
| Mistral main   | _            | _         | _         | _             |
| Custom (CI)    | _            | _         | _         | _             |
| Shadow Gemini  | _            | _         | _         | _             |
| Shadow Mistral | _            | _         | _         | _             |
| **Total wall** |              |           | **_**     |               |

Fonte: `metadata.duration_seconds` calculado de `started_at`/`finished_at` em
cada `run_result.json`.

**Link do GH Actions run do Custom (AC #50):** _(URL completo)_

---

## 3. Custo / tokens

Com a fix de propagação de `usage` no `JudgeService` (PR desta issue), o
custo do juiz agora aparece em `judge_results[*].metadata.usage`.

| Run            | Tokens chatbot | Custo chatbot | Tokens juiz | Custo juiz | Total |
|----------------|----------------|--------------:|-------------|-----------:|------:|
| Gemini main    | _              | _             | _           | _          | _     |
| Mistral main   | _              | _             | _           | _          | _     |
| Custom         | n/d¹           | grátis (Groq) | _           | _          | _     |
| Shadow Gemini  | _              | _             | _           | _          | _     |
| Shadow Mistral | _              | _             | _           | _          | _     |
| **Total**      |                | **_**         |             | **_**      | **_** |

¹ `CustomProvider` não expõe `usage` (limitação documentada — chatbot
demo não devolve `usage` do Groq no body). Estimativa heurística vai aqui.

Pricing (USD/M tokens, snapshot 2026-05-26):
- Gemini 2.5 Flash Lite: $0.10 prompt / $0.40 completion
- Ministral 3B: $0.04 / $0.04
- Mistral Small (juiz shadow): $0.20 / $0.60
- Groq Llama 3.1 8B: grátis no free tier

---

## 4. Verificação de integridade

Output completo de `integrity_check.py` por run (resumo aqui):

| Run            | Cenários proc. | Prompts esperados | Prompts obtidos | Erros explícitos | Status |
|----------------|----------------|-------------------|-----------------|------------------|--------|
| Gemini main    | _/75           | 198               | _               | _                | _      |
| Mistral main   | _/75           | 198               | _               | _                | _      |
| Custom         | _/35           | 95                | _               | _                | _      |
| Shadow Gemini  | _/75           | 198               | _               | _                | _      |
| Shadow Mistral | _/75           | 198               | _               | _                | _      |

Erros explícitos por cenário (se houver): _(lista)_

---

## 5. Resultados em alto nível

| Dimensão       | Gemini   | Mistral  | Custom    |
|----------------|----------|----------|-----------|
| factual        | _ (σ _)  | _ (σ _)  | _ (σ _)   |
| consistency    | _ (σ _)  | _ (σ _)  | _ (σ _)   |
| robustness     | _ (σ _)  | _ (σ _)  | _ (σ _)   |
| **Score geral**| **_**    | **_**    | **_**     |

Comparação com o piloto (mesmo subset de 30 cenários):

| Dimensão       | Pilot Gemini | Full Gemini | Δ | Pilot Mistral | Full Mistral | Δ |
|----------------|--------------|-------------|---|---------------|--------------|---|
| factual        | 4.900        | _           | _ | 4.800         | _            | _ |
| consistency    | 5.000        | _           | _ | 4.800         | _            | _ |
| robustness     | 3.833        | _           | _ | 3.675         | _            | _ |

---

## 6. Concordância judge × judge (main vs shadow)

Output completo em `results/concordance-{gemini,mistral}.json`.

| Run pareada              | n cenários | Spearman ρ | Cohen κ (quad) | Veredito |
|--------------------------|------------|------------|----------------|----------|
| Gemini main × shadow     | _          | _          | _              | _        |
| Mistral main × shadow    | _          | _          | _              | _        |

Critério de descarte do ranking (pré-registrado no `config-shadow-*.yaml`):

- κ > 0.8 → ranking validado, self-bias pequeno
- 0.6 ≤ κ ≤ 0.8 → ranking com caveat metodológico
- κ < 0.6 → ranking descartado no Cap. 5

---

## 7. Problemas encontrados

### Rate limits
- _(preencher; principalmente Gemini free tier)_

### Erros por cenário
- _(preencher; cada cenário com `error != null` no run_result.json)_

### Respostas vazias / fallbacks do juiz
- _(preencher; cenários com `metadata.justification_fallback == true`)_

### Outros
- _(preencher)_

---

## 8. Comparação com a extrapolação do piloto

| Item                 | Piloto extrapolado | Full real |
|----------------------|--------------------|-----------|
| Tempo Gemini         | ~25 min            | _         |
| Tempo Mistral        | ~33 min            | _         |
| Tempo Custom         | ~12 min            | _         |
| Custo total chatbots | ~$0.07             | _         |
| Custo total juiz     | não medido         | _         |

---

## 9. Backup

- [ ] Push pra GitHub realizado: branch `feat/50-full-run-3-chatbots`
      contém todos os `run_result.json`, `report.json`, `report.md`,
      `metadata.json` e os 2 `concordance-*.json`.
- [ ] Custom artifact disponível por 90 dias no GitHub Actions
      (retention-days configurado no workflow).
- [ ] Cópia local fora do repo: _(caminho que o executor escolher; passo
      manual deliberado — não é responsabilidade do agente)_.

---

## 10. Sign-off

- [ ] Johnny revisou
- [ ] Mateus revisou
- [ ] Profa. Elaine ciente
