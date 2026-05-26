# Full run — Gemini, Mistral e Custom (issue #50)

Materiais de execução do **full run** da #50. Roda o framework `llm-eval`
contra os 3 chatbots no banco completo (35 factual + 20 consistency + 20
robustness = 75 cenários, 198 prompts) com `repetitions=3` e `temperature=0`.

> O piloto da #49 validou o pipeline com 30 cenários × 3 chatbots. O full
> herda as decisões metodológicas do piloto (ver `experiments/pilot/PILOT_NOTES.md`
> §7 e `PILOT_ANALYSIS.md` §7) e endereça os 3 blockers documentados antes
> de disparar:
>
> 1. `JudgeService` agora propaga `usage` ao `judge_result.metadata`
>    (custo do juiz medido, não estimado).
> 2. `factual-tutor-015` reescrito (eliminação do falso-negativo do juiz).
> 3. Runs **shadow** com Mistral como juiz rodadas em paralelo (mede
>    self-bias do Gemini juiz via Spearman ρ + Cohen κ).

## Estrutura

```
experiments/full/
├── README.md                       (este arquivo)
├── RUN_NOTES.md                    preenchido após as 5 runs
├── config-gemini.yaml              Gemini chatbot, juiz Gemini
├── config-mistral.yaml             Mistral chatbot, juiz Gemini
├── config-custom.yaml              Custom chatbot, juiz Gemini (rodado VIA CI)
├── config-shadow-gemini.yaml       Gemini chatbot, juiz Mistral (concordância)
├── config-shadow-mistral.yaml      Mistral chatbot, juiz Mistral (concordância)
├── scenarios/                      snapshot do bank embutido (hash em metadata.json)
│   ├── factual.json                35 cenários, 35 prompts
│   ├── consistency.json            20 cenários, 82 prompts (com paráfrases)
│   └── robustness.json             20 cenários, 81 prompts (com variantes)
├── scripts/
│   ├── integrity_check.py          verifica 75/75 cenários processados, 0 silenciosos
│   ├── gen_metadata.py             produz metadata.json (data, hash, modelos, versões)
│   └── concordance.py              Spearman ρ + Cohen κ entre main e shadow
└── results/
    ├── gemini/                     run_result.json + report.{json,md} + metadata.json
    ├── mistral/                    idem
    ├── custom/                     baixado do artifact do GH Actions
    ├── shadow-gemini/              juiz Mistral
    ├── shadow-mistral/             juiz Mistral
    ├── concordance-gemini.json     output do concordance.py
    └── concordance-mistral.json    output do concordance.py
```

## Pré-requisitos

1. **Pacote instalado:** `pip install -e .` no root do repo.
2. **Demo chatbot instalado** (para validação local do Custom antes do CI):
   `pip install -e ./examples/demo-chatbot`.
3. **API keys exportadas:**
   ```bash
   export GEMINI_API_KEY='<chave-aistudio>'
   export MISTRAL_API_KEY='<chave-mistral>'
   export GROQ_API_KEY='<chave-groq>'    # só para validação local do Custom
   ```
4. **Secrets no repo GitHub** (para o run do Custom via Actions): `GEMINI_API_KEY`,
   `GROQ_API_KEY`.

## Como rodar

### 1. Runs locais — Gemini e Mistral (main + shadow)

```bash
# Validar todos os configs sem chamar APIs
llm-eval validate --config experiments/full/config-gemini.yaml
llm-eval validate --config experiments/full/config-mistral.yaml
llm-eval validate --config experiments/full/config-shadow-gemini.yaml
llm-eval validate --config experiments/full/config-shadow-mistral.yaml

# Runs principais (juiz: Gemini)
llm-eval run --config experiments/full/config-gemini.yaml
llm-eval run --config experiments/full/config-mistral.yaml

# Runs shadow (juiz: Mistral)
llm-eval run --config experiments/full/config-shadow-gemini.yaml
llm-eval run --config experiments/full/config-shadow-mistral.yaml
```

### 2. Custom via CI (AC obrigatória do #50)

```bash
# Push da branch e disparo via gh CLI
git push -u origin feat/50-full-run-3-chatbots
gh workflow run ci.yml --ref feat/50-full-run-3-chatbots \
    -f config_path=experiments/full/config-custom.yaml

# Acompanhar
gh run watch
# Quando concluir, baixar o artifact
RUN_ID=$(gh run list --workflow=ci.yml --branch feat/50-full-run-3-chatbots \
    --limit 1 --json databaseId --jq '.[0].databaseId')
gh run download "$RUN_ID" -n eval-full-custom -D experiments/full/results/custom/
```

### 3. Pós-runs — integridade, metadata, concordância

```bash
# Integridade (rode em cada resultado; Custom já corre na CI)
for c in gemini mistral shadow-gemini shadow-mistral; do
    python3 experiments/full/scripts/integrity_check.py \
        experiments/full/results/$c/run_result.json
done

# Metadata (Custom já vem com metadata.json do CI)
for c in gemini mistral shadow-gemini shadow-mistral; do
    python3 experiments/full/scripts/gen_metadata.py \
        --run-result experiments/full/results/$c/run_result.json \
        --config experiments/full/config-$c.yaml \
        --output experiments/full/results/$c/metadata.json
done

# Concordância main × shadow
python3 experiments/full/scripts/concordance.py \
    --main experiments/full/results/gemini/run_result.json \
    --shadow experiments/full/results/shadow-gemini/run_result.json \
    --output experiments/full/results/concordance-gemini.json

python3 experiments/full/scripts/concordance.py \
    --main experiments/full/results/mistral/run_result.json \
    --shadow experiments/full/results/shadow-mistral/run_result.json \
    --output experiments/full/results/concordance-mistral.json
```

## Volume e custo estimados

Extrapolação do piloto (`PILOT_NOTES.md §6`):

| Item                     | Estimativa |
|--------------------------|-----------:|
| Tempo Gemini main        | ~25 min    |
| Tempo Mistral main       | ~33 min    |
| Tempo Custom (no CI)     | ~12 min    |
| Tempo shadow Gemini      | ~25 min    |
| Tempo shadow Mistral     | ~33 min    |
| Tempo total wall-clock   | ~2h        |
| Custo chatbots (USD)     | ~$0.07     |
| Custo juiz (USD)         | medido após run (issue do propagate `usage` resolvida) |

## Caveats herdados do piloto (§5 do PILOT_ANALYSIS)

- Bancos diferentes para Custom (tutor de Python). Comparação cross-vendor
  é apples-to-apples só entre Gemini e Mistral.
- SDK Gemini ignora `seed`. Determinismo confiado a `temperature=0`.
- Tamanho amostral (n=20 por dimensão exceto factual com n=35) ainda é
  modesto. Diferenças menores que ~0.1 entre médias são estatisticamente
  ambíguas.
