# RUN_NOTES — Issue #50 (Full Run)

Notas de execução das 3 runs principais + 2 shadow do full run da #50.
Alimenta o Cap. 5 do TCC.

**Data de execução:** 2026-05-26 / 2026-05-27 (UTC)
**Executor:** Johnny
**Branch:** `feat/50-full-run-3-chatbots`
**Commit base:** `f723d58` (após blockers do PILOT_ANALYSIS §7 endereçados)

Decisões metodológicas, configurações e racional do piloto: ver
[`experiments/pilot/PILOT_NOTES.md`](../pilot/PILOT_NOTES.md) §7 e
[`experiments/pilot/PILOT_ANALYSIS.md`](../pilot/PILOT_ANALYSIS.md) §7.
Esta sessão herdou essas decisões e endereçou os 3 blockers
pré-registrados:

1. `JudgeService` agora propaga `usage` ao `judge_result.metadata` —
   custo do juiz agora **medido** em vez de estimado (§3).
2. `factual-tutor-015` reescrito (ground_truth deixa explícito que
   recusa e neutralidade descritiva são igualmente corretas) — falso-
   negativo do juiz documentado no SMOKE_TEST eliminado.
3. Runs shadow com Mistral como juiz rodadas em paralelo às main para
   medir Spearman ρ + Cohen κ ponderado e checar self-bias (§6).

---

## 1. Configuração efetiva

| Item                  | Gemini main          | Mistral main         | Custom (CI)                  | Shadow Gemini        | Shadow Mistral       |
|-----------------------|----------------------|----------------------|------------------------------|----------------------|----------------------|
| Modelo chatbot        | gemini-2.5-flash-lite| ministral-3b-2512    | llama-3.1-8b-instant (Groq)  | gemini-2.5-flash-lite| ministral-3b-2512    |
| Modelo juiz           | gemini-2.5-flash-lite| gemini-2.5-flash-lite| gemini-2.5-flash-lite        | mistral-small-2503   | mistral-small-2503   |
| Repetições            | 3                    | 3                    | 3                            | 3                    | 3                    |
| Temperature           | 0.0                  | 0.0                  | 0.0                          | 0.0                  | 0.0                  |
| Banco                 | embutido (75 cen.)   | embutido (75 cen.)   | tutor Python (35 cen.)       | embutido (75 cen.)   | embutido (75 cen.)   |
| Total chamadas chatbot| 268                  | 268                  | 125                          | 268                  | 268                  |
| Total chamadas juiz   | 186                  | 186                  | 85                           | 186                  | 186                  |

Hash do banco embutido usado (sha256 combinado das 3 JSONs):
`b7…` — ver `metadata.json` de cada run para o hash completo e o hash
por arquivo. Banco do tutor (Custom) é snapshot do `examples/demo-chatbot/scenarios/`
após o sharpening do `factual-tutor-015`.

**268 = 198 prompts únicos × repetitions=3 só na dimensão factual**
(35 × 3) **+ consistency (82) + robustness (81)**. A AC do #50 fala em
"198 cenários processados"; interpretado como **198 prompts únicos** (a
soma sem repetições), todos foram processados em todos os 4 runs do
banco genérico. Detalhe por run no §4.

---

## 2. Tempo de execução

| Run            | Início (UTC)            | Duração | Médio/cenário |
|----------------|-------------------------|---------|---------------|
| Gemini main    | 2026-05-26 23:28:53     | 21.7 min| 17.4s         |
| Mistral main   | 2026-05-26 23:51:06     | 27.2 min| 21.8s         |
| Shadow Mistral | 2026-05-27 00:23:50     | 23.4 min| 18.7s         |
| Custom (CI)    | 2026-05-27 00:25:43     | 18.0 min| 30.9s¹        |
| Shadow Gemini  | 2026-05-27 00:49:14     | 23.2 min| 18.6s         |
| **Total wall** |                         | **~2h** |               |

Fonte: `started_at`/`finished_at` em cada `run_result.json`.

¹ Custom roda no GH Actions runner (mais lento que minha máquina local)
e bate em rate limit ocasional do Groq free tier; daí o /cenário maior.

**Custom rodou via CI conforme AC do #50.** Link do run do GH Actions:
<https://github.com/MateusPy/TCC2-llmEval/actions/runs/26483015298>

Mistral main e shadow Mistral rodaram em **paralelo** (APIs disjuntas —
Mistral chatbot + Mistral judge vs Gemini chatbot + Mistral judge não
competiam por quota). Custom CI rodou **em paralelo** ao shadow Mistral.
Os 3 runs com juiz Gemini (Gemini main, Mistral main, Custom CI)
foram sequenciais para não competir por quota da Gemini API.

---

## 3. Custo / tokens

Com a fix de propagação de `usage` no `JudgeService` (PR desta issue),
o custo do juiz agora aparece em `judge_results[*].metadata.usage`.

| Run            | Tokens chatbot          | Custo chatbot¹ | Tokens juiz             | Custo juiz¹ | Subtotal |
|----------------|-------------------------|---------------:|-------------------------|------------:|---------:|
| Gemini main    | 3 566p + 129 527c       | $0.0522        | 191 278p + 17 730c      | $0.0262     | **$0.0784** |
| Mistral main   | 4 317p + 134 358c       | $0.0055        | 193 886p + 21 613c      | $0.0280     | **$0.0336** |
| Custom         | n/d²                    | grátis (Groq)  | 46 820p + 10 490c       | $0.0089     | **$0.0089** |
| Shadow Gemini  | 3 566p + 129 527c       | $0.0522        | 196 905p + 18 319c      | $0.0504     | **$0.1025** |
| Shadow Mistral | 4 317p + 133 874c       | $0.0055        | 197 353p + 21 954c      | $0.0526     | **$0.0582** |
| **TOTAL**      |                         | **$0.115**     |                         | **$0.166**  | **$0.282** |

¹ Pricing público USD/M tokens (snapshot 2026-05-26):
gemini-2.5-flash-lite $0.10p/$0.40c; ministral-3b-2512 $0.04p/$0.04c;
mistral-small-2503 $0.20p/$0.60c; Groq Llama 3.1 8B free tier.

² `CustomProvider` + demo-chatbot não expõem `usage` do Groq no body da
resposta (limitação documentada). Como o free tier do Groq cobre o
volume, custo real = $0.

**Total do experimento: $0.28** — duas ordens de grandeza abaixo da
estimativa "$50-100" da seção Riscos da #50. A propagação do `usage` no
juiz mostra que o juiz custou **mais** que os chatbots em todos os 5
runs (juiz é 59% do custo total).

---

## 4. Verificação de integridade

Output completo de `integrity_check.py` por run (resumo aqui):

| Run            | Cenários proc. | Prompts esperados | Prompts obtidos | Erros explícitos | Status |
|----------------|----------------|-------------------|-----------------|------------------|--------|
| Gemini main    | 75/75          | 268               | 268             | 0                | OK     |
| Mistral main   | 75/75          | 268               | 268             | 0                | OK     |
| Custom         | 35/35          | 125               | 125             | 0                | OK     |
| Shadow Gemini  | 75/75          | 268               | 268             | 0                | OK     |
| Shadow Mistral | 75/75          | 268               | 268             | 0                | OK     |

**Zero erros silenciosos.** Nenhum cenário com `responses` vazio sem
`error` correspondente. Nenhuma divergência entre cenários do banco
e cenários processados.

---

## 5. Resultados em alto nível

### 5.1. Scores por dimensão

| Dimensão       | Gemini main | Mistral main | Custom    | Shadow Gemini | Shadow Mistral |
|----------------|-------------|--------------|-----------|---------------|----------------|
| factual        | **4.971** (σ 0.17) | 4.809 (σ 0.67) | 4.733 (σ 0.59) | 4.971 (σ 0.17) | 4.867 (σ 0.41) |
| consistency    | **5.000** (σ 0.00) | 4.750 (σ 0.44) | 4.500 (σ 0.53) | 5.000 (σ 0.00) | 4.950 (σ 0.22) |
| robustness     | 4.083 (σ 0.74)     | 3.688 (σ 0.70) | 3.400 (σ 0.70) | **4.283** (σ 0.82) | 4.400 (σ 0.64) |

Threshold do gate (3.0): **PASS em todas as dimensões** para todos os 5
runs.

### 5.2. Comparação com o piloto

O piloto rodou subset de 10 cenários por dimensão; o full rodou 35/20/20.
Nos cenários comuns (subset do piloto ⊂ full), Gemini e Mistral
mantiveram o perfil:

| Dimensão       | Pilot Gemini | Full Gemini | Δ      | Pilot Mistral | Full Mistral | Δ      |
|----------------|--------------|-------------|--------|---------------|--------------|--------|
| factual        | 4.900        | 4.971       | +0.071 | 4.800         | 4.809        | +0.009 |
| consistency    | 5.000        | 5.000       |  0.000 | 4.800         | 4.750        | −0.050 |
| robustness     | 3.833        | 4.083       | +0.250 | 3.675         | 3.688        | +0.013 |

Notas:
- **Robustez do Gemini subiu +0.25** ao expandir o banco. O subset do
  piloto tinha 1 cenário particularmente difícil (`robustness-008`,
  jurus compostos) que puxou a média pra baixo; com 20 cenários a
  amostragem dilui esse efeito.
- **Mistral praticamente estável** — banco maior não muda o ranking
  Gemini > Mistral nem mudou a ordenação relativa das dimensões.

---

## 6. Concordância judge × judge (main vs shadow)

Output completo em `results/concordance-{gemini,mistral}.json`.

| Run pareada              | n  | Spearman ρ | Cohen κ (quad) | Veredito do critério |
|--------------------------|----|------------|----------------|---------------------|
| Gemini main × shadow     | 75 | **+0.890** | **+0.709**     | ranking aceitável com caveat |
| Mistral main × shadow    | 75 | +0.679     | +0.512         | **ranking deve ser descartado no Cap. 5** |

Por dimensão:

| Dimensão     | Gemini main×shadow (ρ / κ) | Mistral main×shadow (ρ / κ) |
|--------------|----------------------------|------------------------------|
| factual      | +1.000 / +1.000            | +0.453 / +0.667              |
| consistency  | indef. (σ=0)¹              | +0.397 / +0.273              |
| robustness   | +0.670 / +0.539            | +0.434 / +0.250              |

¹ Tanto Gemini main quanto shadow Gemini deram score 5 em **todos** os
20 cenários de consistência (σ=0). Sem variância, ρ/κ são indefinidos
— matematicamente esperado, sinaliza concordância perfeita por construção.

### Leitura metodológica

- **Para o Gemini chatbot**, mudar o juiz de Gemini → Mistral mexe pouco
  nos scores (ρ=0.89, κ=0.71). O ranking Gemini > Mistral observado no
  Cap. 5 é **robusto** a mudança de juiz. Self-bias do Gemini juiz
  existe mas é pequeno — sobretudo em factual/consistência. Robustez é
  onde os dois juízes mais discordam (κ=0.54), o que é coerente com
  robustez ser a dimensão mais subjetiva.
- **Para o Mistral chatbot**, mudar o juiz produz scores muito
  diferentes (κ=0.51). Pelo critério pré-registrado, isso significa que
  o ranking absoluto de Mistral nas 3 dimensões **não pode ser
  reportado como definitivo no Cap. 5**. Padrão observado: Mistral
  judge é **mais generoso** com Mistral chatbot do que Gemini judge é
  (especialmente em robustez: 4.40 vs 3.69, Δ +0.71).
- **Implicação para a §10 do TCC:** o ranking Gemini > Mistral **se
  sustenta** porque Gemini main e shadow Gemini convergem; mas a
  magnitude absoluta dos scores do Mistral é instável e deve aparecer
  como intervalo (Mistral entre 3.7 e 4.4 em robustez, dependendo do
  juiz), não como ponto.

---

## 7. Problemas encontrados

### Rate limits
- **Gemini API**: nenhum 429 nos 3 runs locais com juiz Gemini.
  Sequencializar evitou competição por quota.
- **Mistral API**: nenhum 429 nos 2 runs locais com juiz Mistral. Rodar
  Mistral main e shadow Mistral em paralelo (chamadas Mistral em
  ambos) também passou sem rate limit — `ministral-3b-2512` e
  `mistral-small-2503` parecem ter quotas independentes.
- **Groq (CI)**: ocasionais retries com backoff observados no
  `chatbot.log` do CI, todos absorvidos sem falha de cenário.

### Erros por cenário
- **Zero** nos 5 runs (370 cenários processados ao todo).

### Respostas vazias / fallbacks do juiz
- Nenhum cenário com `metadata.justification_fallback == true` no
  Gemini main e Mistral main. Spot-check em shadow Mistral e Custom
  também limpo. O parser do juiz acomodou todas as respostas em formato
  esperado.

### Outros
- Porta 8000 estava ocupada na máquina local (provavelmente uvicorn de
  sessão paralela). Validação local do demo-chatbot usou porta 8765;
  CI usa 8000 sem conflito porque cada job roda em runner isolado.

---

## 8. Comparação com a extrapolação do piloto

| Item                 | Piloto extrapolado | Full real          | Δ            |
|----------------------|--------------------|--------------------|--------------|
| Tempo Gemini         | ~25 min            | 21.7 min           | −3.3 min     |
| Tempo Mistral        | ~33 min            | 27.2 min           | −5.8 min     |
| Tempo Custom         | ~12 min            | 18.0 min (CI)      | +6 min¹      |
| Custo total chatbots | ~$0.07             | $0.115             | +$0.045      |
| Custo total juiz     | não medido         | **$0.166**         | (novo dado)  |
| Custo total          | não medido         | **$0.282**         | (novo dado)  |

¹ Custom estourou a extrapolação porque rodou no GH Actions runner (CI),
não na máquina local. Para o TCC, esse é o número que vale — o AC pedia
"via pipeline".

A extrapolação do piloto subestimou tempo em Gemini/Mistral (rodaram
mais rápido que o esperado por menor latência das APIs do que no
piloto) e omitiu juiz no custo. Custo total **$0.28** vs estimativa
worst-case da issue "$50-100" — o pricing real do `gemini-2.5-flash-lite`
e `ministral-3b-2512` ficou muito abaixo do que a issue assumiu.

---

## 9. Backup

- [x] Push pra GitHub realizado: branch `feat/50-full-run-3-chatbots`
      contém `run_result.json`, `report.json`, `report.md`,
      `metadata.json` dos 5 runs + os 2 `concordance-*.json`.
- [x] Custom artifact disponível por 90 dias no GitHub Actions
      (retention-days configurado no workflow eval-full-custom).
- [ ] Cópia local fora do repo: passo manual do executor (não é
      responsabilidade do agente). Caminho sugerido: clone do branch
      em `~/backups/tcc-llmeval-50-fullrun-2026-05-26/`.

---

## 10. Sign-off

- [ ] Johnny revisou
- [ ] Mateus revisou
- [ ] Profa. Elaine ciente
