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
   ↓ rodar `scripts/consolidate.py` (a ser criado na #51 quando ambos terminarem)
   ↓ disagreement ≥ 2 → sessão de discussão (remota OK), preencher
     `consensus_after_discussion`
   ↓ commit no PR de #51
4. Métricas
   ↓ vira issue #52 (Cohen κ, Pearson, MAE — script separado)
```

## Estrutura

```
experiments/human-validation/
├── README.md                       ← este arquivo
├── sample.json                     ← os 30 itens da amostra principal (pré-registro)
├── calibration/                    ← rodada zero (5 cenários compartilhados)
│   ├── README.md
│   ├── calibration_A1.csv          ← Johnny preenche
│   ├── calibration_A2.csv          ← Mateus preenche
│   └── items/                      ← .md por cenário (legível, sem nota do juiz)
├── annotator_1/                    ← Johnny
│   ├── README.md
│   ├── annotations_A1.csv          ← Johnny preenche
│   └── items/                      ← 30 .md em ordem randomizada (seed=11)
├── annotator_2/                    ← Mateus
│   ├── README.md
│   ├── annotations_A2.csv          ← Mateus preenche
│   └── items/                      ← 30 .md em ordem randomizada (seed=22)
└── scripts/
    ├── select_sample.py            ← reproduz sample.json (seed=42)
    ├── build_annotation_sheets.py  ← regera items/ + CSVs dos anotadores
    └── build_calibration_sheets.py ← regera items/ + CSVs da calibração
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

## Tempo médio por item

Anote `ts_start` e `ts_end` (formato livre, ex.: `2026-06-08 14:23`). O
script de consolidação extrai estatísticas pra reportar no PR final
(estimativa rápida: 3–5 min por item, ~2h total para os 30).

## Quando estiver na dúvida

Se o cenário parece ambíguo, mal formulado, ou se a rubrica não cobre
bem o caso, **marque `flagged = true`** e descreva em `notes`. Isso é
sinal qualitativo importante para o Cap. 5 do TCC — não tente forçar
uma nota "boa".
