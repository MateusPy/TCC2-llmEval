# Validação humana do LLM-as-a-Judge (issue #51)

Tudo o que vocês (Johnny + Mateus) precisam para anotar os 30 cenários
selecionados pelo plano da [issue #51](https://github.com/MateusPy/TCC2-llmEval/issues/51).

## Fluxo

```
1. Rodada zero (calibração) — 5 cenários compartilhados
   ↓ ambos abrem `calibration/`, anotam independentemente
   ↓ se reúnem (Discord/Zoom, ~30 min) pra alinhar interpretação da rubrica
   ↓ ajustes na rubrica se necessário
2. Anotação principal — 30 cenários, cego e independente
   ↓ Johnny abre `annotator_1/`, Mateus abre `annotator_2/`
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
├── calibration/                    ← rodada zero (5 cenários compartilhados)
│   ├── README.md
│   ├── CALIBRATION_NOTES.md
│   ├── calibration_A1.csv
│   ├── calibration_A2.csv
│   └── items/                      ← .md por cenário (legível, sem nota do juiz)
├── annotator_1/                    ← Johnny
│   ├── README.md
│   ├── annotations_A1.csv
│   └── items/                      ← 30 .md em ordem randomizada (seed=11)
├── annotator_2/                    ← Mateus
│   ├── README.md
│   ├── annotations_A2.csv
│   └── items/                      ← 30 .md em ordem randomizada (seed=22)
└── scripts/
    ├── select_sample.py            ← reproduz sample.json (seed=42)
    ├── build_annotation_sheets.py  ← regera items/ + CSVs dos anotadores
    ├── build_calibration_sheets.py ← regera items/ + CSVs da calibração
    └── consolidate.py              ← mescla A1+A2+resolutions em consolidated.csv
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

- **A2 (Mateus):** registro granular item-a-item. Sessão de ~65 min para
  os 30 itens → **~2,2 min/item** (mediana ~2 min, faixa 0–7 min, item
  inicial mais longo por ramp-up).
- **A1 (Johnny):** timestamps capturados como bloco único (~17:15 em
  quase todos), sem granularidade por item. Sessão estimada em ~1,5h
  para os 30 → **~3 min/item** estimado.

Estimativa combinada para futuras réplicas: **~2,5 min por item, ~1–1,5h
por anotador** para o set completo de 30 itens.

## Quando estiver na dúvida

Se o cenário parece ambíguo, mal formulado, ou se a rubrica não cobre
bem o caso, **marque `flagged = true`** e descreva em `notes`. Isso é
sinal qualitativo importante para o Cap. 5 do TCC — não tente forçar
uma nota "boa".
