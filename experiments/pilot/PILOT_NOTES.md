# PILOT_NOTES — Issue #49

Notas de execução do piloto experimental dos três chatbots planejados na
issue #49. Documento alimenta as decisões do **full run** (#50) e o Cap. 5.1
(Setup experimental) do TCC.

**Data de execução:** 2026-05-26
**Executor:** Johnny (sessão Claude Code)
**Commit do repo:** `957a330` (main, após merge da #60)
**Branch:** `feat/49-pilot-three-chatbots`

Todos os três chatbots foram executados **na mesma sessão, sequencialmente**,
para que diferenças entre eles reflitam o pipeline e os modelos, não
condições externas (mudanças de quota, atualizações silenciosas dos vendors,
versões diferentes do código).

---

## 1. Configuração efetiva

| Item | Gemini | Mistral | Custom (demo-chatbot) |
|---|---|---|---|
| Modelo do chatbot | `gemini-2.5-flash-lite` | `ministral-3b-2512` | `llama-3.1-8b-instant` (Groq) |
| Modelo do juiz | `gemini-2.5-flash-lite` | `gemini-2.5-flash-lite` | `gemini-2.5-flash-lite` |
| Repetições | 3 | 3 | 3 |
| Temperature | 0.0 | 0.0 | 0.0 |
| Seed | 42 (ignorado pelo SDK Gemini, ver §6.1 do PILOT_ANALYSIS) | 42 | 42 (ignorado pelo CustomProvider — Groq não expõe seed via HTTP) |
| Cenários por dimensão | 10 (primeiros por ID, banco embutido) | 10 (idem) | 15 factual / 10 consistency / 10 robustness (banco do tutor) |
| Config | `config-gemini.yaml` | `config-mistral.yaml` | `config-custom.yaml` |

**Caveat de comparabilidade:** Gemini e Mistral foram avaliados nos mesmos 30
cenários (subset reproduzível do banco embutido). Custom usou o banco do
**próprio domínio** (tutor de Python), porque o chatbot recusa perguntas fora
do escopo — usar o banco genérico daria scores artificialmente baixos. Scores
absolutos entre os três não são diretamente comparáveis; veja
`PILOT_ANALYSIS.md §3` para a discussão completa.

---

## 2. Tempo de execução

| Run | Início (UTC) | Fim (UTC) | Duração total | Médio por cenário |
|---|---|---|---|---|
| Gemini | 2026-05-26T00:32:55 | 2026-05-26T00:42:12 | **9.3 min** | 18.6s |
| Mistral | 2026-05-26T00:43:06 | 2026-05-26T00:55:25 | **12.3 min** | 24.6s |
| Custom | 2026-05-26T00:56:02 | 2026-05-26T01:07:51 | **11.8 min** | 20.3s |
| **Total parede** | | | **~33 min** | — |

Mistral foi o mais lento — combinação de latência maior da API
(`ministral-3b` no tier free) e nenhum cache local. Custom incluiu round-trip
ao chatbot local (Groq via uvicorn em `localhost:8765`); apesar do hop extra,
o Groq é veloz e o número final ficou abaixo do Mistral.

Fonte: `metadata.duration_seconds` em cada `report.json`.

---

## 3. Custo / tokens consumidos

| Run | Chatbot tokens (prompt + completion) | Custo chatbot (≈USD)¹ | Juiz tokens | Custo juiz (≈USD) |
|---|---|---|---|---|
| Gemini | 56.199 (1.465p + 54.734c) | ~$0.022 | **não disponível** ² | — |
| Mistral | 59.493 (1.761p + 57.732c) | ~$0.002 | **não disponível** ² | — |
| Custom | **não disponível** ³ | grátis (free tier Groq) | **não disponível** ² | — |

¹ Pricing público em 2026-05-26: Gemini 2.5 Flash Lite $0.10/$0.40 por
milhão (input/output); Ministral 3B $0.04/$0.04; Llama 3.1 8B via Groq tem
free tier suficiente para o piloto. Os valores assumem tier paid; rodando
no free tier o custo é zero (ver §4).

² **Limitação conhecida do framework:** o `JudgeService` não propaga o
`usage` retornado pelo SDK do juiz para o `judge_result.metadata`. Só temos
`response_time_ms`, `judge_model` e `parse_method`. Para o full run (#50),
abrir issue para adicionar `usage` ao metadata do juiz (~5 linhas em
`llm_eval/judge.py`).

³ **Limitação do `CustomProvider`:** o provider só lê o campo configurado em
`response_path`. O body da resposta do nosso demo-chatbot devolve apenas
`{"response": "..."}`, sem tokens — porque o chatbot consome o Groq por
trás e não repassa o `usage`. Para medir, ou (a) o chatbot devolve `usage`
no próprio body e o `CustomProvider` é estendido para capturar, ou (b) os
tokens do Groq são coletados dos logs do uvicorn. Não bloqueante para o
piloto, mas registrar.

**Total estimado do piloto: ~$0,024 USD** (apenas chatbots; juiz e Custom
não contabilizados pela limitação acima).

---

## 4. Problemas encontrados

### Rate limits
- [x] **Nenhum durante esta execução.** Os três runs rodaram sequenciais,
      com gap de poucos segundos entre eles, sem nenhum 429.
- [ ] _(histórico)_ Em runs anteriores do piloto Gemini (20/05), o free tier
      do Gemini hit 429 em ~30s; mitigação foi parsear `retry_delay` do erro
      e honrar no retry loop (PR #61). Comportamento agora aceitável no free
      tier para volume do piloto (~70 calls).

### Erros por cenário
Nenhum nos três runs (0/30 Gemini, 0/30 Mistral, 0/35 Custom).

### Respostas vazias / fallbacks do juiz
Nenhum detectado — todos os `judge_results` têm `score` numérico e
`justification` preenchidos.

### Outros
- Porta 8000 estava ocupada na máquina do executor (provavelmente outro
  uvicorn de sessão paralela), forçando o uso de **porta 8765** para o
  demo-chatbot. `config-custom.yaml` aponta para `localhost:8765`. Sem
  impacto na semântica.

---

## 5. Resultados em alto nível

| Dimensão | Gemini | Mistral | Custom (tutor Python) |
|---|---|---|---|
| factual | **4.900** (σ 0.32) | 4.800 (σ 0.42) | 4.533 (σ 0.92) |
| consistency | **5.000** (σ 0.00) | 4.800 (σ 0.63) | 4.400 (σ 0.70) |
| robustness | **3.833** (σ 0.82) | 3.675 (σ 1.04) | 3.500 (σ 0.76) |
| **Score geral** | **4.578** | 4.425 | 4.200 |

Os três cumpriram o threshold default do gate (3.0) em todas as dimensões.
A ordenação dos scores absolutos é gemini > mistral > custom, mas há
**caveats de comparabilidade** discutidos em `PILOT_ANALYSIS.md §3` — em
particular, Custom foi avaliado em banco de domínio mais difícil
(adversariais especificamente projetados para a persona de tutor).

Fonte: `summary.by_dimension.*.mean` em cada `report.json`.

---

## 6. Extrapolação para o full run (#50)

Multiplicadores assumindo o banco embutido completo + dimensão Custom no
seu próprio domínio:

| Dimensão | Cenários no piloto (cada) | Cenários no full | Multiplicador |
|---|---|---|---|
| factual (Gemini/Mistral) | 10 | 35 | 3.5× |
| consistency (Gemini/Mistral) | 10 + 30 paráfrases | 20 + ~62 paráfrases | 2.0× |
| robustness (Gemini/Mistral) | 10 + 30 variantes | 20 + ~61 variantes | 2.0× |
| factual (Custom) | 15 | sem mudança planejada | 1.0× |
| consistency (Custom) | 10 + 30 paráfrases | idem | 1.0× |
| robustness (Custom) | 10 + 30 variantes | idem | 1.0× |

| Item | Piloto | Full run (estimado) |
|---|---|---|
| Tempo Gemini | 9.3 min | ~25 min (×2.7 — pesos diferentes nas dimensões) |
| Tempo Mistral | 12.3 min | ~33 min |
| Tempo Custom | 11.8 min | ~12 min (banco já é o final) |
| Tempo wall-clock total (sequencial) | 33 min | ~70 min |
| Custo Gemini (chatbot) | $0.022 | ~$0.06 |
| Custo Mistral (chatbot) | $0.002 | ~$0.006 |
| Custo Custom (chatbot) | grátis (free tier Groq) | grátis |
| Custo juiz | não medido | não medido (corrigir antes do full run) |

---

## 7. Decisões para o full run

- [x] **`repetitions` = 3** confirmado. Variância vista no piloto justifica
      manter (com 1 rep a robustez teria stdev acima de 1 para Mistral e
      Custom — média um único valor torna o gate instável).
- [x] **`temperature` = 0.0** mantido. Determinismo onde o provider permite;
      gemini ignora `seed` mas com temperatura zero a divergência observada
      foi mínima.
- [x] **Juiz = Gemini 2.5 Flash Lite** mantido para os três. Self-bias do
      Gemini quando avalia ele mesmo está documentado como limitação
      (PILOT_ANALYSIS §5). Trocar de juiz no full run quebra comparabilidade
      com o piloto — vale fazer **rodada paralela** com Mistral como juiz
      antes do full run, só para medir concordância.
- [x] **Inclusão do chatbot demo (#60) como 3º provider** confirmada — é
      este `Custom`. Decisão de manter banco próprio (tutor de Python) em
      vez do banco genérico fica.
- [ ] **Antes do full run:** ajustar `JudgeService` para propagar `usage`
      (issue follow-up) e estender `CustomProvider` ou demo-chatbot para
      surfaceabilizar tokens do Groq. Sem isso, o custo do full run será
      subestimado.

---

## 8. Sign-off

- [ ] Johnny revisou
- [ ] Mateus revisou
- [ ] Profa. Elaine ciente

---

## Como reproduzir

```bash
# pré-requisitos
export GROQ_API_KEY=...      # Custom
export GEMINI_API_KEY=...    # Gemini + juiz (todos os 3 runs)
export MISTRAL_API_KEY=...   # Mistral

# subir o chatbot demo (para Custom)
uvicorn chatbot.main:app --app-dir examples/demo-chatbot --port 8765 &

# 3 runs sequenciais
llm-eval run --config experiments/pilot/config-gemini.yaml
llm-eval run --config experiments/pilot/config-mistral.yaml
llm-eval run --config experiments/pilot/config-custom.yaml

# parar o chatbot
lsof -ti:8765 | xargs -r kill
```

Outputs ficam em `experiments/pilot/results/{gemini,mistral,custom}/`
(`run_result.json`, `report.json`, `report.md`, `run.log`).
