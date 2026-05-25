# Análise do Piloto Experimental — Issue #49

> Documento de análise produzido a partir das duas runs do piloto
> (`config-gemini.yaml` e `config-mistral.yaml`) executadas em 2026-05-20.
> Complementa o template `PILOT_NOTES.md` (a ser preenchido com sign-off)
> e alimenta a §5.1 do TCC (Setup experimental) e a §10 (Limitações).
>
> **Executor:** Johnny (sessão Claude Code)
> **Data:** 2026-05-20
> **Branch:** `main` (com mudanças não-commitadas — ver §6)

---

## 1. Resumo executivo

O piloto foi executado com sucesso em ambos os chatbots avaliados (30/30
cenários sem erro em cada run), em durações praticamente equivalentes
(~9 min). Em alto nível, os dois modelos ficaram **estatisticamente
indistinguíveis** em precisão factual e consistência semântica no subset de
10 cenários, e divergiram modestamente em robustez, favorecendo o Gemini.

| Dimensão | Gemini 2.5 Flash-Lite | Ministral 3B (2512) | Δ (Gemini − Mistral) |
|---|---|---|---|
| Precisão Factual (Judge) | **4.90** (med 5.0, σ 0.32) | 4.83 (med 5.0, σ 0.36) | +0.07 |
| Consistência Semântica (Judge) | **5.00** (med 5.0, σ 0) | 5.00 (med 5.0, σ 0) | 0.00 |
| Robustez (Judge) | **3.83** (med 3.83, σ 0.82) | 3.68 (med 3.67, σ 0.95) | +0.16 |
| **Score geral** | **4.58** | 4.50 | +0.08 |

Veredito do piloto: **o framework funciona end-to-end nos três pipelines
(factual, consistência, robustez), o método LLM-as-judge produz scores
consistentes, e a comparação cross-vendor é factível.** Há pontos de
atenção metodológicos (§5 e §7) que devem ser registrados como limitações
no TCC.

---

## 2. Setup efetivamente executado

A configuração final difere em vários pontos da planejada originalmente na
issue #49. As mudanças foram forçadas por problemas técnicos descobertos
durante a execução (detalhe em §6) e estão consolidadas em
`experiments/pilot/README.md`.

### Chatbots avaliados

| Item | Gemini | Mistral |
|---|---|---|
| Modelo | `gemini-2.5-flash-lite` | `ministral-3b-2512` |
| Provider SDK | `google-generativeai 0.8.6` | `mistralai 2.4.2` |
| Tier de billing | **Paid** (free tier inviabilizado, §6.4) | Paid |
| Temperature | 0.0 | 0.0 |
| Max tokens | 1024 | 1024 |
| Seed | 42 (configurado, **não chega ao Gemini**, §6.1) | 42 (chega ao SDK como `random_seed`) |

### Juiz (LLM-as-judge)

| Item | Valor |
|---|---|
| Modelo | `gemini-2.5-flash-lite` para **ambos** os runs |
| Temperature | 0.0 |
| Max tokens | 2048 |

### Cenários

| Dimensão | Subset usado | Origem |
|---|---|---|
| Precisão Factual | 10 cenários (primeiros por ID) | `llm_eval/scenarios/bank/factual.json` (35 totais) |
| Consistência Semântica | 10 cenários (primeiros por ID) | `llm_eval/scenarios/bank/consistency.json` (20 totais) |
| Robustez | 10 cenários (primeiros por ID) | `llm_eval/scenarios/bank/robustness.json` (20 totais) |
| **Total** | **30 cenários** | regerável via `experiments/pilot/scripts/subset_scenarios.py` |

### Repetições e seed

`repetitions: 3` em factual (conforme AC da #49). Como `seed` não chega ao
Gemini SDK e ambos rodam com `temperature: 0.0`, a reprodutibilidade vem
da temperatura zero (greedy decoding). Variabilidade observada entre as 3
repetições foi nula no Gemini (mesmo prompt → mesma resposta byte a byte
em todos os casos verificados); Mistral teve variações lexicais menores
mas semanticamente equivalentes.

---

## 3. Resultados quantitativos detalhados

### 3.1 Tempo de execução

| Run | Início | Fim | Duração | Cenários/min |
|---|---|---|---|---|
| Gemini | 02:47:21Z | 02:56:22Z | 540 s (9 min 0 s) | 3.33 |
| Mistral | 02:56:58Z | 03:06:39Z | 581 s (9 min 41 s) | 3.10 |
| **Total** | 02:47:21Z | 03:06:39Z | **1121 s (~19 min)** | — |

Os dois runs rodaram em **paid tier** sem rate limit observável; latência
está dominada pelo BERTScore (factual + robustness chamam BERT do
`bert-score`, que carrega ~430 MB de modelo BERT na primeira chamada).

### 3.2 Scores do Judge (LLM-as-judge, escala 1-5)

| Dimensão | n | Gemini μ ± σ | Mistral μ ± σ | Min/Max Gemini | Min/Max Mistral |
|---|---|---|---|---|---|
| Factual | 10 | 4.90 ± 0.32 | 4.83 ± 0.36 | 4 / 5 | 4 / 5 |
| Consistência | 10 | 5.00 ± 0.00 | 5.00 ± 0.00 | 5 / 5 | 5 / 5 |
| Robustez | 10 | 3.83 ± 0.82 | 3.68 ± 0.95 | 2.33 / 5 | 1.67 / 5 |

### 3.3 BERTScore F1 (métrica computacional, escala 0-1)

| Dimensão | n | Gemini μ (min/max) | Mistral μ (min/max) |
|---|---|---|---|
| Factual (resposta vs ground_truth) | 30 | 0.622 (0.458 / 0.745) | **0.552** (0.467 / 0.625) |
| Robustez (resposta original vs variante) | 31 | 0.854 (0.622 / 1.000) | 0.787 (0.599 / 0.947) |

Diferença sistemática no BERTScore factual (Gemini 0.622 vs Mistral 0.552)
não reflete maior precisão — reflete que **o Ministral 3B é
significativamente mais verboso**. Respostas mais longas penalizam o
BERTScore F1 quando o ground truth é curto (típico em factual: ~9 chars).
Por exemplo, em `factual-001` (capital da Austrália), ambos acertaram
"Canberra"/"Camberra", mas o Mistral adicionou três parágrafos de contexto
histórico — incluindo a alucinação "estado da Austrália Central"
(corretamente capturada pelo juiz, score 4 para essa resposta).

### 3.4 Score geral por chatbot

```
Gemini 2.5 Flash-Lite  : 4.58
Ministral 3B (2512)    : 4.50
```

A diferença é pequena (1.8% relativa) e está dentro do desvio padrão
combinado das três dimensões. Não é prudente concluir superioridade
estatística no subset de 10 cenários por dimensão.

---

## 4. Análise qualitativa por dimensão

### 4.1 Precisão Factual

Os dois chatbots erraram em apenas **um cenário cada** (score < 5), em
`factual-001` (capital da Austrália):

- **Gemini:** typo na resposta — "Camberra" em vez de "Canberra".
  Informação correta, ortografia errada. Juiz: score 4.
- **Mistral:** ortografia correta ("Canberra") mas alucinação
  geográfica — afirmou que Canberra fica "no estado da Austrália Central"
  (estado inexistente; correto é Território da Capital Australiana / ACT).
  Juiz: score 4.

**Observação metodológica:** os dois receberam o mesmo score 4, embora os
erros sejam qualitativamente diferentes (typo vs alucinação). Isso pode
ser sinal de **self-bias** (juiz Gemini sendo mais brando com a "família
Gemini" — typo passa despercebido) ou apenas ruído num n pequeno. Em §10
do TCC, registrar como limitação a investigar no full run com n=35.

### 4.2 Consistência Semântica

**Score 5.00 perfeito para ambos os chatbots.** Σ = 0. BERTScore par-a-par
das paráfrases: Gemini μ = 0.81, Mistral μ = 0.79. Conclusão:

> O subset de 10 cenários de consistência não é discriminativo entre os
> dois modelos. Os prompts selecionados (fotossíntese, arroz branco,
> diferença lista/tupla em Python, utilitarismo, e-mail profissional) são
> tópicos canônicos onde **qualquer LLM moderno acerta**. Provável que o
> full run com 20 cenários expanda para domínios mais ambíguos e revele
> alguma diferença.

Recomendação: ao rodar o full run, examinar se há cenários nos 10 últimos
do banco que produzem score < 5 em algum dos modelos. Se mantiver 5/5
perfeito em todos os 20, considerar **expansão do banco de consistência**
como linha de trabalho futura (registrar como recomendação na conclusão
do TCC, não como entregável).

### 4.3 Robustez

Dimensão onde mais variação apareceu (σ ≈ 0.8-0.95) e onde a diferença
entre os modelos é mais visível.

Cenários problemáticos (score < 4):

| Cenário | Variação aplicada | Score Gemini | Score Mistral | Modo de falha dominante |
|---|---|---|---|---|
| `robustness-003` (math, 27+15) | typo `masi` | 3.00 | **1.67** | Mistral respondeu em italiano ("Il risultato di 27 più 15 è 42"); Gemini também em italiano mas com nota explicativa |
| `robustness-008` (finance, juros) | typo `jurus` | **2.33** | 3.00 | Gemini interpretou como termo jurídico; Mistral manteve interpretação correta |
| `robustness-010` (geography, oceano) | typo `mair` | 5.00 | 3.33 | Mistral apresentou contradições internas; Gemini não foi afetado |

Padrão observado: **cada chatbot quebra com typos diferentes**. Não há um
modelo claramente mais robusto — há vulnerabilidades específicas. Isso é
um achado **interessante metodologicamente** para o TCC: a robustez não é
uma propriedade global do modelo, e a métrica precisa de mais cenários
(20 no full run) para capturar a distribuição realista de modos de falha.

---

## 5. Limitações do piloto

1. **n pequeno.** 10 cenários por dimensão é pouco para conclusões
   estatísticas. O subset foi escolhido por determinismo (primeiros por
   ID), não por amostragem estratificada — pode estar enviesado para
   categorias específicas (e.g., geografia domina factual no piloto).
2. **Self-bias do juiz.** Juiz Gemini avaliando chatbot Gemini é um
   risco metodológico documentado na §10 do `RESUMO_PROJETO.md`. O
   tamanho do efeito não pode ser medido com o piloto atual (precisaria
   de juiz alternativo numa fração dos cenários). Linha de trabalho
   secundária: rodar uma sub-amostra com juiz Mistral e medir
   concordância.
3. **Determinismo parcial.** `seed: 42` está nos configs mas não chega ao
   SDK do Gemini (limitação do `google-generativeai 0.8.6`,
   ver §6.1). Reprodutibilidade Gemini depende exclusivamente de
   `temperature: 0.0` (greedy decoding) — funciona na prática (variância
   nula entre repetições observada), mas o vendor pode mudar isso sem
   aviso.
4. **Tokens não capturados.** O campo `parameters.usage` não foi
   preenchido nos `ScenarioResult`s desta run (bug latente na extração de
   usage do response SDK; fora do escopo deste piloto, mas inviabiliza
   contabilidade real de tokens — custos são estimados em §7.3).
5. **Modelos em tiers de capacidade diferentes.** Comparação direta entre
   Gemini 2.5 Flash-Lite e Ministral 3B é entre modelos de tamanhos muito
   diferentes (Mistral 3B vs Gemini Lite, este ~10× maior segundo
   especulação pública). A comparação é mais "viabilidade do framework"
   do que "qualidade relativa dos modelos". Registrar isso na §10.

---

## 6. Problemas técnicos enfrentados (e como foram resolvidos)

Esta seção documenta o que mudou no código durante o piloto. **Nenhuma
das mudanças foi commitada ainda.** Cada item deve virar um PR/issue
separado conforme o workflow do projeto.

### 6.1 Bug: `seed` não suportado pelo SDK Gemini atual

- **Sintoma:** `ValueError: Unknown field for GenerationConfig: seed` em
  100% dos cenários no primeiro run.
- **Causa:** `google-generativeai 0.8.6` (dependência atual em
  `pyproject.toml: >=0.8.0`) não expõe `seed` em `GenerationConfig`. O
  SDK novo `google-genai` expõe, mas é pacote separado.
- **Fix:** `llm_eval/providers/gemini.py` — remover atribuições de `seed`
  no `generation_config` e em `parameters` retornados. Comentário no
  código documenta a limitação. Testes do provider atualizados.
- **Impacto metodológico:** reprodutibilidade Gemini agora depende de
  `temperature=0.0`. Documentar em §5.1 do TCC.

### 6.2 Política de pinning incompatível com a nova convenção do Google

- **Sintoma:** após corrigir #6.1, configs validam mas runs falham com
  `limit: 0` no `gemini-2.0-flash-001`.
- **Causa raiz:** o Google moveu o free tier do AI Studio de
  `gemini-2.0-flash` para a família 2.5+, **e a família 2.5+ não publica
  snapshots datados** (verificado via `list_models` e teste de candidatos
  `-001`/`-002`/`-preview-MM-DD`). A política original do validador
  (`is_pinned_model` em `llm_eval/config.py`) exigia sufixo de snapshot,
  o que bloqueava todos os modelos 2.5+ utilizáveis.
- **Fix:** estender o validador para aceitar **soft pin** (minor version
  embutida no nome, ex. `gemini-2.5-flash`) além do **hard pin**
  (snapshot datado). Floating aliases (`-latest`, `-stable`) continuam
  rejeitados. Documentação do `ProviderSettings` atualizada com a nova
  política. Cobertura de teste expandida em `tests/test_config.py`.
- **Impacto metodológico:** soft pin é uma garantia mais fraca de
  reprodutibilidade — o vendor pode mudar weights silenciosamente dentro
  do mesmo nome de família. Documentar em §10 como limitação imposta pelo
  provider, não pelo framework.

### 6.3 Retry não honra `Retry-After` do servidor

- **Sintoma:** após corrigir #6.2 e migrar para `gemini-2.5-flash`, runs
  ainda falhavam em rate-limit. Free tier 2.5-flash tem 5-20 RPM e
  envia `retry_delay { seconds: ~30 }` nas respostas 429. O framework
  ignorava esse hint e usava backoff exponencial próprio (1s, 2s, 4s,
  esgotando `max_attempts=3` em ~7s).
- **Fix:** `RateLimitError` agora carrega `retry_after: float | None`.
  `_translate_sdk_error` no Gemini provider parseia tanto a forma
  humana ("Please retry in N.NNs") quanto o bloco proto
  (`retry_delay { seconds: N }`). `retry_with_backoff` honra esse valor
  (com buffer de 1 s e cap de 120 s) em vez do backoff local. Default de
  `max_attempts` no Gemini provider subiu de 3 para 6. Testes adicionados.
- **Status:** fix funciona conforme esperado, mas ver §6.4.

### 6.4 Free tier do Gemini 2.5 Flash é fundamentalmente inviável para o piloto

- **Sintoma:** mesmo com #6.3 aplicado, o run encontra padrão patológico
  em que esperar o `retry_after` (3-5 s) libera 1 slot, a próxima request
  consome esse slot, **e a seguinte falha novamente** porque a janela de
  60 s do RPM ainda está saturada. Resultado: 1 cenário processado em
  ~4 min, todos com erro.
- **Causa:** rate limiting do free tier é por janela deslizante de 60 s
  com 5-20 requests, e o `retry_after` retornado pelo servidor reflete o
  próximo "tick" — não a liberação completa da janela.
- **Decisão tomada:** **habilitar billing** no projeto Google Cloud
  (paid tier). Verificado por smoke test (81 req/min sustentado), custo
  estimado total do TCC < R$ 2,00.
- **Trade-off:** o fix #6.3 continua sendo correto e útil para
  defensive programming (a Mistral API também pode retornar `Retry-After`
  em rajadas), mas o caminho prático para o TCC é paid tier.

### 6.5 Bug: import do `mistralai` 2.4.2

- **Sintoma:** `ImportError: cannot import name 'Mistral' from 'mistralai'`
  ao tentar instanciar o provider Mistral.
- **Causa:** `mistralai 2.4.2` (versão atual permitida pelo
  `pyproject.toml: >=1.0.0`) tem o pacote top-level vazio — sem
  `__init__.py`. A classe `Mistral` vive em `mistralai.client.Mistral`.
  O código foi escrito para o SDK 1.x.
- **Fix:** `llm_eval/providers/mistral.py:111` —
  `from mistralai.client import Mistral`. `pyproject.toml` atualizado
  para `mistralai>=2.4.0,<3.0`. Teste `test_default_provider_factory_builds_mistral`
  ajustado para mockar o caminho de import correto.

### 6.6 Decisão de modelos finais

- Gemini chatbot e juiz: `gemini-2.5-flash-lite` (mais barato que 2.5
  Flash, sem thinking, adequado para Q&A direto).
- Mistral chatbot: `ministral-3b-2512` (mais barato dos modelos hosted da
  Mistral com snapshot pinado, ~$0.04/1M tokens).
- Trade-off: a comparação cross-vendor mistura modelos de tiers diferentes
  (ver §5.5). Mantém o compromisso de "framework executável end-to-end com
  custo trivial".

---

## 7. Performance e custo

### 7.1 Tempo

| Run | Duração total | Wall-clock por cenário | Multiplicador esperado para banco completo |
|---|---|---|---|
| Gemini | 540 s | 18.0 s/cenário | 75/30 = 2.5× → **~22 min** |
| Mistral | 581 s | 19.4 s/cenário | 2.5× → **~24 min** |
| **Pilot total** | **1121 s** (19 min) | — | **Full run ~46 min** |

### 7.2 Calls reais

| Item | Por run | Soma |
|---|---|---|
| Calls ao chatbot avaliado | ~110 | 220 |
| Calls ao juiz Gemini | ~70 | 140 |
| Calls totais | ~180 | **~360** |

### 7.3 Custo estimado

`parameters.usage` não foi capturado (§5.4). Estimativa baseada em
contagem de calls × média de tokens observada nos prompts/respostas:

| Componente | Tokens estim. | Preço (paid) | Custo |
|---|---|---|---|
| Gemini chatbot (~110 calls × 400 tok) | ~44 K | $0.075 in / $0.30 out por 1M | ~$0.005 |
| Mistral chatbot (~110 calls × 400 tok) | ~44 K | $0.04 / 1M | ~$0.002 |
| Gemini judge (2 runs × ~70 × 750 tok) | ~105 K | $0.075 / $0.30 por 1M | ~$0.012 |
| **Piloto total** | **~193 K** | — | **~$0.02 (R$ 0,10)** |

Extrapolação para banco completo (75 cenários, 2 chatbots):

| Cenário | Custo USD |
|---|---|
| 1 full run (Gemini + Mistral) | ~$0.05 (R$ 0,25) |
| TCC inteiro (estimando 3-5 runs entre debug, validação e final) | ~$0.15-0.25 (R$ 0,75-1,25) |

**Conclusão de custos:** desprezível para o projeto. Não há razão técnica
para limitar quantidade de runs ou tamanho do banco por custo de API.

---

## 8. Recomendações para o full run (#50)

### 8.1 Decisões a fixar antes de #50

- [x] **Modelo Gemini chatbot:** `gemini-2.5-flash-lite` (já no config)
- [x] **Modelo Mistral chatbot:** `ministral-3b-2512` (já no config)
- [x] **Juiz:** `gemini-2.5-flash-lite` para ambos (mantém comparabilidade)
- [x] **`temperature: 0.0`** (chatbot e juiz)
- [x] **`repetitions: 3`** em factual — confirmado pelo piloto: variância
  observada foi ~0 entre repetições, mas manter 3 oferece detecção de
  comportamento não-determinístico se algum modelo for atualizado.
- [ ] **Subset:** rodar o banco completo (35 + 20 + 20 = 75 cenários) sem
  filtragem. O custo justifica.
- [ ] **Provider custom (#60, demo chatbot tutor Python):** ainda não
  entregue. Roda separadamente quando estiver disponível (não bloqueia #50).

### 8.2 Itens técnicos abertos (criar issues / PRs)

1. **Commitar mudanças desta sessão.** Cinco arquivos modificados sem
   commit: `llm_eval/providers/gemini.py`, `llm_eval/providers/mistral.py`,
   `llm_eval/providers/_retry.py`, `llm_eval/config.py`, `llm_eval/cli.py`,
   `pyproject.toml`, `tests/test_*.py`, `experiments/pilot/config-*.yaml`,
   `experiments/pilot/README.md`. Sugestão: dividir em ~3 commits
   independentes (bug do seed, política de pinning, fix retry-after + import
   mistralai).
2. **Captura de tokens.** `parameters.usage` deveria conter
   `prompt_tokens`/`completion_tokens` mas saiu vazio. Investigar a
   extração no `_extract_usage` dos dois providers. Bloquearia
   contabilidade real de custo.
3. **Snapshots reais para Gemini 2.5+.** Quando o Google publicar
   `gemini-2.5-flash-MM-DD`, atualizar configs para hard pin e marcar
   `gemini-2.5-flash-lite` (soft pin) como "modo degradado".
4. **Migração para `google-genai` SDK.** O SDK atual está em deprecation
   warning (`google.generativeai` → `google.genai`). Mudança maior, fora
   do escopo do piloto, mas necessária antes do TCC final para evitar
   warning em logs e ter acesso a features novas (seed, thinking config).
5. **Robustness com banco de typos mais ampla.** Os modos de falha
   observados (idioma trocado, alucinação de contexto, contradições
   internas) sugerem que o subset de variantes está conservador.
   Considerar expandir tipologia de ruído (não só typos lexicais, também
   omissões de palavra, mudança de ordem, ruído homófono).

### 8.3 Ordem sugerida de execução

1. **Antes do full run:** commitar mudanças desta sessão em 3 PRs
   pequenos. Re-rodar a suite de testes (327 passando hoje) no CI.
2. **Full run #50:** executar `llm-eval run` nos dois configs com banco
   completo. ETA ~46 min wall-clock total.
3. **Análise:** atualizar este documento (ou criar `FULLRUN_ANALYSIS.md`)
   com os dados do banco completo. Comparar com este piloto para detectar
   regressões (foram fixados 5 bugs entre eles).
4. **Provider custom (#60):** rodar separadamente quando entregue, sem
   bloquear #50.

---

## 9. Próximos passos imediatos

1. **Preencher `PILOT_NOTES.md`** com os dados de cima (data, commit,
   tempos, problemas, decisões).
2. **Sign-off:** Johnny revisa, Mateus revisa, Profa. Elaine ciente.
3. **Commits & PRs:** ver §8.2.1.
4. **Disparar #50** após PRs mergeados.

---

## 10. Anexos

- `experiments/pilot/results/gemini/run_result.json` — output cru do runner
- `experiments/pilot/results/gemini/report.md` — relatório legível
- `experiments/pilot/results/gemini/report.json` — sumário estruturado
- `experiments/pilot/results/mistral/run_result.json` — idem
- `experiments/pilot/results/mistral/report.md` — idem
- `experiments/pilot/results/mistral/report.json` — idem
- `experiments/pilot/results/{gemini,mistral}/run.log` — log completo da
  execução (warnings do SDK Gemini deprecation + carregamento do
  `bert-score`).
