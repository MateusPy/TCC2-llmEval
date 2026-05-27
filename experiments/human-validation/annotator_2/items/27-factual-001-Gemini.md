# Item 27 — `factual-001` (Gemini, factual)
> **Anotador A2**. Após ler este arquivo, vá pra linha **27** do `annotations_A2.csv` e preencha `score`, `justification`, `flagged`, `notes`.
> Anote `ts_start` ANTES de ler, `ts_end` ao terminar (timestamp local em formato livre, ex.: `2026-06-08 14:23`).

---
**Categoria:** `geography`  
**Chatbot avaliado:** Gemini  
**Dimensão:** **factual**

---
## Prompt
> Qual e a capital da Australia?

## Ground truth (resposta esperada)
> Canberra.

## Respostas do chatbot (3 repetições)

### Repetição 1
```
A capital da Austrália é **Camberra**.
```

### Repetição 2
```
A capital da Austrália é **Camberra**.
```

### Repetição 3
```
A capital da Austrália é **Camberra**.
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
