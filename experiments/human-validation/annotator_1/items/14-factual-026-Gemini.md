# Item 14 — `factual-026` (Gemini, factual)
> **Anotador A1**. Após ler este arquivo, vá pra linha **14** do `annotations_A1.csv` e preencha `score`, `justification`, `flagged`, `notes`.
> Anote `ts_start` ANTES de ler, `ts_end` ao terminar (timestamp local em formato livre, ex.: `2026-06-08 14:23`).

---
**Categoria:** `history`  
**Chatbot avaliado:** Gemini  
**Dimensão:** **factual**

---
## Prompt
> Em que ano o homem pisou na Lua pela primeira vez?

## Ground truth (resposta esperada)
> 1969.

## Respostas do chatbot (3 repetições)

### Repetição 1
```
O homem pisou na Lua pela primeira vez em **1969**.
```

### Repetição 2
```
O homem pisou na Lua pela primeira vez em **1969**.
```

### Repetição 3
```
O homem pisou na Lua pela primeira vez em **1969**.
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
