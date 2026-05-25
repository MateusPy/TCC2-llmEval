# Piloto experimental — Gemini e Mistral

Materiais de execução do **piloto da issue #49**. Roda o framework `llm-eval`
contra Gemini e Mistral usando um subset reproduzível do banco embutido (10
cenários por dimensão), antes da execução completa (#50).

> **Status do "Custom provider":** intencionalmente fora deste piloto.
> O terceiro chatbot será o **demo chatbot tutor de Python** entregue pela
> issue #60. Quando #60 estiver pronto, criar `config-demo.yaml` aqui e rodar
> a terceira execução.

## Estrutura

```
experiments/pilot/
├── README.md                       (este arquivo)
├── PILOT_NOTES.md                  preenchido após as duas runs
├── config-gemini.yaml              chatbot avaliado: Gemini
├── config-mistral.yaml             chatbot avaliado: Mistral
├── scenarios/                      subset gerado, versionado no git
│   ├── factual.json                primeiros 10 do bank
│   ├── consistency.json            primeiros 10 do bank
│   └── robustness.json             primeiros 10 do bank
├── scripts/
│   └── subset_scenarios.py         regera scenarios/ a partir do bank
└── results/
    ├── gemini/                     run_result.json + report.{json,md}
    └── mistral/                    idem
```

## Pré-requisitos

1. **Pacote instalado:** `pip install -e .` no root do repo.
2. **API keys exportadas** no shell:
   ```bash
   export GEMINI_API_KEY='<sua-chave-aistudio>'
   export MISTRAL_API_KEY='<sua-chave-mistral>'
   ```
   - Gemini free tier: https://aistudio.google.com/apikey (15 req/min,
     1.500 req/dia — suficiente para o piloto).
   - Mistral: https://console.mistral.ai (requer cartão; piloto custa ~$0.03).

## Decisões fixadas neste piloto

| Item | Valor | Justificativa |
|---|---|---|
| **Modelo Gemini** | `gemini-2.5-flash-lite` | Paid tier do AI Studio (billing ativado; free tier do 2.0-flash era `limit:0` na conta usada, ver mudança abaixo). Custo estimado do piloto + TCC < R$ 2. Soft pin: o Google não publica snapshots datados para a família 2.5+. Coleta timestampada em `run_result.json`. |
| **Modelo Mistral** | `ministral-3b-2512` | Modelo Mistral mais barato hospedado com snapshot pinado (~$0.04/1M tokens, ~5× mais barato que `mistral-small-2503`). Hard pin (snapshot datado). Trade-off de capacidade: é um modelo 3B em vez dos ~22B do Small; respostas em PT-BR foram coerentes no smoke test, mas a comparação cross-vendor com Gemini 2.5 Flash-Lite passa a ser entre modelos de tiers diferentes, registrar como limitação ao apresentar resultados. |
| **Juiz** | Gemini `gemini-2.5-flash-lite` para **ambos** | Comparabilidade entre runs. Self-bias documentado como limitação (§10 do `RESUMO_PROJETO.md`). |
| **Repetições** | `3` | Conforme AC da #49 (medir variabilidade em factual). |
| **Temperature** | `0.0` (chatbot e juiz) | Reprodutibilidade. |
| **Seed** | `42` no config (não chega ao Gemini) | O SDK `google-generativeai 0.8.6` não expõe seed em `GenerationConfig`; reprodutibilidade do lado Gemini depende de `temperature=0.0`. Mistral SDK aceita seed normalmente. |
| **Subset** | 10 cenários por dimensão (primeiros por ID) | Determinístico, regenerável via `scripts/subset_scenarios.py`. |

> **Mudança em relação ao escopo original (registrar no TCC):** o piloto foi planejado com `gemini-2.0-flash-001` (snapshot datado, hard pin) no free tier do AI Studio. Durante a execução, três problemas vieram à tona em sequência:
>
> 1. O SDK `google-generativeai 0.8.6` não expõe o campo `seed` em `GenerationConfig` (suportado apenas no SDK novo `google-genai`); o provider foi corrigido para parar de enviar `seed`. Reprodutibilidade do lado Gemini depende de `temperature=0.0`.
> 2. O Google moveu o free tier do AI Studio de `gemini-2.0-flash` para a família 2.5+, e a família 2.5+ não publica snapshots datados. Solução: `is_pinned_model` foi estendido para aceitar "soft pin" (minor version embutida) além do snapshot datado, e o validador continua rejeitando nomes sem versão e aliases flutuantes (`-latest`, `-stable`).
> 3. O free tier do 2.5-flash tem rate limit muito restrito (5-20 RPM) e a janela saturada não libera com o `retry_in` curto que o servidor retorna. `_retry.py` foi estendido para honrar o `retry_after` extraído da exceção, mas mesmo assim o free tier inviabilizou o piloto. **Decisão:** habilitar billing no projeto Google Cloud e migrar para `gemini-2.5-flash-lite` (mesma família 2.5, sem thinking, ~8× mais barato que o `gemini-2.5-flash`; custo total do TCC estimado < R$ 2). Mantém Gemini como juiz para ambos os chatbots conforme decisão metodológica original.
>
> Todas as mudanças de código têm testes; ver `tests/test_config.py` (pinning) e `tests/test_providers.py` (seed + retry-after).

## Como rodar o piloto

```bash
# 0. (Uma vez) regenerar o subset se o bank embutido mudar
python experiments/pilot/scripts/subset_scenarios.py

# 1. Validar os configs sem chamar nenhuma API
llm-eval validate --config experiments/pilot/config-gemini.yaml
llm-eval validate --config experiments/pilot/config-mistral.yaml

# 2. Rodar contra Gemini (~15-25 min com rate limit do free tier)
llm-eval run --config experiments/pilot/config-gemini.yaml

# 3. Rodar contra Mistral (~5-10 min)
llm-eval run --config experiments/pilot/config-mistral.yaml

# 4. Preencher experiments/pilot/PILOT_NOTES.md à mão (template já criado)
```

## Volume esperado de chamadas por run

Por chatbot avaliado:

| Dimensão | Prompts ao chatbot | Prompts ao juiz |
|---|---|---|
| factual (10 × repetitions=3) | 30 | 30 |
| consistency (10 base + ~30 paráfrases) | ~40 | ~10 (1 por cenário) |
| robustness (10 base + ~30 variantes) | ~40 | ~30 (1 por par) |
| **Total** | **~110** | **~70** |

Custo aproximado:

- **Gemini:** dentro do free tier; gargalo é o 15 req/min (≈12-18 min de
  parede só de rate limit).
- **Mistral:** ~$0.02-$0.05 dependendo do tamanho das respostas.

## Saídas geradas (por run)

Em `results/<chatbot>/`:

- `run_result.json` — output cru do `Runner`, todas as respostas + scores +
  metadados (timestamps, parâmetros, erros por cenário).
- `report.json` — sumário estruturado por dimensão (mean, median, stdev).
- `report.md` — relatório legível para humanos, com top-N piores cenários.
- `run_partial.json` (transitório) — escrita incremental; removido no fim.

## O que registrar no `PILOT_NOTES.md`

- Tempo total de execução de cada chatbot (do `metadata.duration_seconds` do
  `run_result.json`).
- Tokens consumidos / custo aproximado (somar `parameters.usage` dos
  `ScenarioResult`s).
- Problemas: rate limits, timeouts, cenários com erro, respostas vazias.
- Decisão final de `repetitions` e `temperature` para o **full run** (#50)
  — confirmar 3 ou reduzir para 1.
- Estimativa extrapolada de tempo/custo para o banco completo
  (3,5× para factual, 2× para consistency/robustness, dado que o subset
  é 10/35 e 10/20 respectivamente).
