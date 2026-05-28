# Anotador A2 — Mateus

Sua coleta de 30 itens da amostra da issue #51. **Cego e independente** —
você NÃO vê a nota do juiz nem a nota do Johnny enquanto anota.

## Pré-requisitos

- [ ] Você fez a [rodada zero (`../calibration/`)](../calibration/README.md).
- [ ] Você e o Johnny se reuniram pra alinhar a rubrica e registraram
      qualquer decisão que tomaram lá.
- [ ] Profa. Elaine ciente do procedimento (issue #51 §3.4).

## Como anotar

1. Abra `annotations_A2.csv` no editor que preferir (Excel, LibreOffice,
   Google Sheets, ou direto num editor de texto). A planilha tem 30 linhas
   na ordem `01, 02, ..., 30` — essa é **a sua ordem** (randomizada com
   seed=22; a do Johnny é diferente).
2. Comece pelo item 01: abra `items/01-<algo>.md`.
3. **Antes de ler**, anote `ts_start` no CSV (timestamp livre, ex.: `2026-06-08 14:23`).
4. Leia o `.md` inteiro — prompt, ground_truth (se factual), respostas,
   e a rubrica no rodapé.
5. Preencha no CSV:
   - `score`: inteiro 1 a 5 conforme rubrica
   - `justification`: ≥ 1 frase em PT-BR explicando a nota
   - `flagged`: `true` se o caso é ambíguo ou mal formulado, `false` ou vazio caso contrário
   - `notes`: livre, opcional (ex.: "respondi assumindo que typo intencional")
6. `ts_end` ao terminar.
7. Próximo item (`02-...md`). Repita até o 30.

## Regras

- **Não pule itens.** Se ficar travado, marque `flagged = true` e dê a melhor
  nota que conseguir + descreva em `notes`.
- **Não consulte** `../annotator_1/`, nem `experiments/full/results/`,
  nem `report.md` de nenhum chatbot enquanto anota.
- Pode pausar e voltar — não precisa fazer os 30 de uma vez. Cada item tem
  seu próprio `ts_start`/`ts_end`.
- Justificativa curta (1–2 frases) é melhor que longa. O que importa é
  o critério.

## Quando terminar

1. Salve o CSV (e faça backup se quiser).
2. Avise o Johnny.
3. **Aguarde ele terminar** antes de qualquer comparação.
4. Quando os dois terminarem, rodem o `consolidate.py` (script a ser
   criado quando vocês começarem) que faz o merge A1+A2, identifica
   `disagreement ≥ 2` e abre os casos que precisam de discussão.
