# Item 15 — `factual-011` (Mistral, factual)
> **Anotador A1**. Após ler este arquivo, vá pra linha **15** do `annotations_A1.csv` e preencha `score`, `justification`, `flagged`, `notes`.
> Anote `ts_start` ANTES de ler, `ts_end` ao terminar (timestamp local em formato livre, ex.: `2026-06-08 14:23`).

---
**Categoria:** `language`  
**Chatbot avaliado:** Mistral  
**Dimensão:** **factual**

---
## Prompt
> Quantas letras tem o alfabeto portugues moderno?

## Ground truth (resposta esperada)
> 26 letras.

## Respostas do chatbot (3 repetições)

### Repetição 1
```
O alfabeto português moderno tem **23 letras**.

Além disso, o alfabeto português inclui as seguintes letras com acentos e til:
- **A, E, I, O, U** (com acentos: **Á, É, Í, Ó, Ú**)
- **C** (com til: **Ç**)
- **G** (com til: **Ĝ**)
- **N** (com til: **Ń**)
- **S** (com til: **Ş**)
- **X** (com til: **X̧**)
- **Y** (com til: **Ý**)

No entanto, em contextos formais ou oficiais, algumas letras com acentos e til são consideradas variantes e não são sempre incluídas como letras oficiais do alfabeto. A versão mais ampla, que inclui todas as variantes, é de **26 letras** (incluindo as letras com acentos e til).

Portanto, a resposta mais comum é **23 letras** (sem contar as variantes), mas se considerarmos todas as variantes, é **26 letras**.
```

### Repetição 2
```
O alfabeto português moderno tem **23 letras**.

Além disso, o alfabeto português inclui as seguintes letras com acentos e til:
- **A, E, I, O, U** (com acentos: **Á, É, Í, Ó, Ú**)
- **C** (com til: **Ç**)
- **G** (com til: **Ĝ**)
- **N** (com til: **Ń**)
- **S** (com til: **Ş**)
- **X** (com til: **X̧**)
- **Y** (com til: **Ý**)

No entanto, em contextos formais ou oficiais, algumas letras com acentos são consideradas variantes ou não são incluídas em listas oficiais. A versão mais ampla, incluindo todas as variantes, é de **23 letras** (incluindo as letras com acentos e til).
```

### Repetição 3
```
O alfabeto português moderno tem **23 letras**.

Além disso, o alfabeto português inclui as seguintes letras com acentos e til:
- **A, E, I, O, U** (com acentos: **Á, É, Í, Ó, Ú**)
- **C** (com til: **Ç**)
- **G** (com til: **Ĝ**)
- **N** (com til: **Ń**)
- **S** (com til: **Ş**)
- **X** (com til: **X̧**)
- **Y** (com til: **Ý**)

No entanto, em contextos formais ou oficiais, algumas letras com acentos e til são consideradas variantes ou letras adicionais, mas a base do alfabeto é de 23 letras.
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
