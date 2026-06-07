# Validação humana do LLM-as-a-Judge (issue #51)

Tudo o que vocês (A1 + A2) precisam para anotar os 30 cenários
selecionados pelo plano da [issue #51](https://github.com/MateusPy/TCC2-llmEval/issues/51).

## Fluxo

```
1. Rodada zero (calibração) — 5 cenários compartilhados
   ↓ ambos abrem `calibration/`, anotam independentemente
   ↓ se reúnem (Discord/Zoom, ~30 min) pra alinhar interpretação da rubrica
   ↓ ajustes na rubrica se necessário
2. Anotação principal — 30 cenários, cego e independente
   ↓ A1 abre `annotator_1/`, A2 abre `annotator_2/`
   ↓ cada um no seu ritmo, em casa
   ↓ ninguém vê a nota do juiz nem a nota do outro
3. Consolidação
   ↓ rodar `scripts/consolidate.py` → gera `annotations_consolidated.csv`
   ↓ disagreement ≥ 2 → sessão de discussão (remota OK)
   ↓ preencher `discussion_resolutions.json` → re-rodar `consolidate.py`
   ↓ commit no PR de #51
4. Métricas
   ↓ vira issue #52 (Cohen κ, Pearson, MAE — script separado)
```

## Estrutura

```
experiments/human-validation/
├── README.md                       ← este arquivo
├── sample.json                     ← os 30 itens da amostra principal (pré-registro)
├── DISCUSSION_NOTES.md             ← ata da sessão de discussão (Δ ≥ 2)
├── discussion_resolutions.json     ← entrada do consolidate.py para Δ ≥ 2
├── annotations_consolidated.csv    ← saída final do consolidate.py
├── HIGH_DISAGREEMENTS.md           ← análise qualitativa (#52, top-5 |judge−humano|)
├── concordance_results.json        ← métricas κ/Pearson/MAE (saída do concordance.py)
├── figures/                        ← scatter, matriz de confusão, distribuição de erros
├── calibration/                    ← rodada zero (5 cenários compartilhados)
│   ├── README.md
│   ├── CALIBRATION_NOTES.md
│   ├── calibration_A1.csv
│   ├── calibration_A2.csv
│   └── items/                      ← .md por cenário (legível, sem nota do juiz)
├── annotator_1/                    ← A1
│   ├── README.md
│   ├── annotations_A1.csv
│   └── items/                      ← 30 .md em ordem randomizada (seed=11)
├── annotator_2/                    ← A2
│   ├── README.md
│   ├── annotations_A2.csv
│   └── items/                      ← 30 .md em ordem randomizada (seed=22)
└── scripts/
    ├── select_sample.py            ← reproduz sample.json (seed=42)
    ├── build_annotation_sheets.py  ← regera items/ + CSVs dos anotadores
    ├── build_calibration_sheets.py ← regera items/ + CSVs da calibração
    ├── consolidate.py              ← mescla A1+A2+resolutions em consolidated.csv
    └── concordance.py              ← κ/Pearson/MAE judge × humano (#52)
```

## Pré-registro

`sample.json` foi gerado deterministicamente por `select_sample.py` no commit
`6ce2d0d` (merge do PR #64). Qualquer um pode re-rodar o script e obter o mesmo
arquivo byte-a-byte. A tabela dos 30 itens está publicada no body da issue #51
§2 — comparem antes de começar.

## Regra primária de consenso

Para `n=2` anotadores (vocês), a nota humana consensual é a **média** das
duas notas:

```
consensus_mean = (score_A1 + score_A2) / 2          # contínuo 1.0–5.0
consensus_rounded = round(consensus_mean)            # discreto 1–5, pra Cohen κ
```

Itens com `disagreement ≥ 2` entram em discussão e produzem
`consensus_after_discussion`, usada como **análise de sensibilidade** (não
substitui `consensus_mean` na métrica principal). Detalhes em
[issue #51 §3.3](https://github.com/MateusPy/TCC2-llmEval/issues/51).

## Cegueira (importante)

- **NÃO** abra os arquivos do outro anotador antes de terminar o seu.
- **NÃO** consulte `experiments/full/results/*/report.md` enquanto anota
  (esses arquivos têm a nota do juiz).
- Os `.md` em `items/` foram gerados SEM mostrar nota do juiz — pode abrir
  à vontade.

## Sessões realizadas

| Etapa                                          | Data        | Modo            | Ata |
|------------------------------------------------|-------------|-----------------|-----|
| Rodada zero (calibração — 5 cenários)          | 2026-05-26  | remoto (call)   | [`calibration/CALIBRATION_NOTES.md`](calibration/CALIBRATION_NOTES.md) |
| Anotação principal cega (A1, 30 itens)         | 2026-05-27  | individual      | (CSV: `annotator_1/annotations_A1.csv`) |
| Anotação principal cega (A2, 30 itens)         | 2026-05-27  | individual      | (CSV: `annotator_2/annotations_A2.csv`) |
| Discussão dos 4 itens com `disagreement ≥ 2`   | 2026-05-27  | remoto (call)   | [`DISCUSSION_NOTES.md`](DISCUSSION_NOTES.md) |

## Tempo por item

Anotadores registraram `ts_start` / `ts_end` na própria linha do CSV.

- **A2:** registro granular item-a-item. Sessão de ~65 min para
  os 30 itens → **~2,2 min/item** (mediana ~2 min, faixa 0–7 min, item
  inicial mais longo por ramp-up).
- **A1:** timestamps capturados como bloco único (~17:15 em
  quase todos), sem granularidade por item. Sessão estimada em ~1,5h
  para os 30 → **~3 min/item** estimado.

Estimativa combinada para futuras réplicas: **~2,5 min por item, ~1–1,5h
por anotador** para o set completo de 30 itens.

## Quando estiver na dúvida

Se o cenário parece ambíguo, mal formulado, ou se a rubrica não cobre
bem o caso, **marque `flagged = true`** e descreva em `notes`. Isso é
sinal qualitativo importante para o Cap. 5 do TCC — não tente forçar
uma nota "boa".

## Resultados de concordância (issue #52)

Gerado por `scripts/concordance.py` (juiz = Gemini main; n=30; bootstrap
n=1000, seed=42 — reproduzível byte-a-byte).

### Métricas globais

| Métrica                       | Point  | IC95% bootstrap        |
|-------------------------------|--------|------------------------|
| κ A1×A2 (quadrático)          | +0.419 | [+0.085, +0.791]       |
| κ judge×humano (quadrático)   | +0.717 | [+0.438, +0.852]       |
| Pearson r judge×humano        | +0.790 | [+0.583, +0.911]       |
| Spearman ρ judge×humano       | +0.739 | [+0.485, +0.911]       |
| MAE judge×humano              | 0.381  | [0.228, 0.556]         |

### Por dimensão (n=10 cada)

| dim         | κ A1×A2 | κ j×h  | r j×h  | ρ j×h  | MAE   | A1 distinct | A2 distinct |
|-------------|---------|--------|--------|--------|-------|-------------|-------------|
| factual     | +0.323  | +0.924 | +0.985 | +0.916 | 0.117 | 4           | 3           |
| consistency | 0.000   | −0.154 | −0.167 | −0.167 | 0.250 | **1**       | 2           |
| robustness  | +0.053  | +0.304 | +0.346 | +0.413 | 0.775 | 3           | 4           |

### Análise de sensibilidade

Substituindo `consensus_mean` por `consensus_after_discussion` nos 4 itens revisados:

| Métrica          | Primary | Sensibilidade | Δ      |
|------------------|---------|---------------|--------|
| κ judge×humano   | +0.717  | **+0.766**    | +0.049 |
| Pearson r        | +0.790  | **+0.810**    | +0.020 |
| Spearman ρ       | +0.739  | +0.682        | −0.057 |
| MAE              | 0.381   | 0.442         | +0.061 |

A discussão dos Δ≥2 **aumentou** κ e Pearson e **reduziu** Spearman e
aumentou MAE — comportamento esperado: a discussão polarizou notas
(jogou consenso pra 1 ou 5 onde havia ambiguidade), aumentando
concordância linear/categórica com o juiz mas degradando a ordenação
nos casos discutidos (que ficaram nas pontas, criando empates).

### Divergências `|judge − consenso| ≥ 2`

**0 itens** atingem o threshold estrito da issue #52 — a máxima divergência
observada é |Δ|=1.50. Para cumprir a AC "inspeção qualitativa de pelo
menos 5 casos", selecionamos os 5 itens com maior |Δ|. Análise completa
em [`HIGH_DISAGREEMENTS.md`](HIGH_DISAGREEMENTS.md), incluindo:

- Padrão **P1**: juiz subestima falhas de escopo em chatbot restrito
- Padrão **P2**: juiz é mais granular em consistency que humanos
- Padrão **P3**: em robustness, juiz e humanos divergem em unidade de avaliação
- Padrão **P4**: `consensus_mean` pode mascarar concordância latente
- **Caveat metodológico** sobre κ em consistency e robustness (próximo bloco)

### Caveat — κ baixo em consistency e robustness

Os κs baixos nessas duas dimensões têm causas **diferentes** e não devem
ser lidos como falha do juiz:

- **consistency:** A1 deu nota **5 em todos os 10 itens** (n_distinct=1).
  Com uma das séries com variância zero, κ é matematicamente forçado a
  ~0 (e Pearson/Spearman a NaN se a outra também for constante). MAE=0.250
  é a métrica informativa aqui — confirma forte acordo absoluto.

- **robustness:** A1 e A2 leram robustness com critérios efetivamente
  diferentes — κ A1×A2 = +0.053 indica concordância intra-anotadores
  praticamente aleatória, apesar da calibração. Implicação metodológica
  forte: a baixa concordância judge×humano em robustness reflete pelo
  menos parcialmente a baixa concordância **entre humanos**, não só
  ruído do juiz. Detalhado em `HIGH_DISAGREEMENTS.md`.

Em factual, ambos κs (A1×A2 = +0.323 e judge×humano = +0.924) e
correlações estão em níveis interpretáveis — a base sólida da
validação.
