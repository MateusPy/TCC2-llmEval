# Item 13 — `factual-013` (Gemini, factual)
> **Anotador A1**. Após ler este arquivo, vá pra linha **13** do `annotations_A1.csv` e preencha `score`, `justification`, `flagged`, `notes`.
> Anote `ts_start` ANTES de ler, `ts_end` ao terminar (timestamp local em formato livre, ex.: `2026-06-08 14:23`).

---
**Categoria:** `sports`  
**Chatbot avaliado:** Gemini  
**Dimensão:** **factual**

---
## Prompt
> Quantos jogadores de linha um time de futebol tem em campo, sem contar o goleiro?

## Ground truth (resposta esperada)
> 10 jogadores de linha.

## Respostas do chatbot (3 repetições)

### Repetição 1
```
Um time de futebol tem **10 jogadores de linha** em campo, sem contar o goleiro.

Um time completo em campo tem 11 jogadores, sendo 1 goleiro e 10 jogadores de linha.
```

### Repetição 2
```
Um time de futebol tem **10 jogadores de linha** em campo, sem contar o goleiro.

Um time completo em campo tem 11 jogadores, sendo 1 goleiro e 10 jogadores de linha.
```

### Repetição 3
```
Um time de futebol tem **10 jogadores de linha** em campo, sem contar o goleiro.

Um time completo em campo tem 11 jogadores, sendo 1 goleiro e 10 jogadores de linha.
```

_Anote uma única nota considerando o conjunto das 3 repetições._

---
## Rubrica
**Factual** — a resposta está alinhada ao `ground_truth`?

| Nota | Critério |
|---|---|
| 1 | Contradiz o ground_truth, inventa, ou responde incorretamente. |
| 2 | Tem algo relacionado mas com erro factual relevante. |
| 3 | Parcialmente correta; incompleta, ambígua, mistura certo e errado. |
| 4 | Essencialmente correta; pequenas omissões ou imprecisões não comprometem. |
| 5 | Correta, completa e alinhada ao ground_truth. |
