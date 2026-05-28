# Item 12 — `factual-tutor-006` (Custom, factual)
> **Anotador A1**. Após ler este arquivo, vá pra linha **12** do `annotations_A1.csv` e preencha `score`, `justification`, `flagged`, `notes`.
> Anote `ts_start` ANTES de ler, `ts_end` ao terminar (timestamp local em formato livre, ex.: `2026-06-08 14:23`).

---
**Categoria:** `programming`  
**Chatbot avaliado:** Custom  
**Dimensão:** **factual**

---
## Prompt
> Qual valor booleano representa falsidade em Python?

## Ground truth (resposta esperada)
> False.

## Respostas do chatbot (3 repetições)

### Repetição 1
```
Em Python, o valor booleano que representa falsidade é `False`. Isso ocorre porque em Python, qualquer valor que seja falso ou vazio é considerado como `False` em operações booleanas.

Por exemplo:

- `False` é `False`
- `0` é `False`
- `""` (uma string vazia) é `False`
- `[]` (uma lista vazia) é `False`
- `()` (um tuplo vazio) é `False`

Já os valores que são verdadeiros são considerados como `True`.
```

### Repetição 2
```
Em Python, o valor booleano que representa falsidade é `False`. Isso ocorre porque em Python, qualquer valor que seja falso ou vazio é considerado como `False` em operações booleanas.

Por exemplo:

- `False` é `False`
- `0` é `False`
- `""` (uma string vazia) é `False`
- `[]` (uma lista vazia) é `False`
- `()` (um tuplo vazio) é `False`

Já os valores que são verdadeiros são considerados como `True`.
```

### Repetição 3
```
Em Python, o valor booleano que representa falsidade é `False`. Isso ocorre porque em Python, qualquer valor que seja falso ou vazio é considerado como `False` em operações booleanas.

Por exemplo:

- `False` é `False`
- `0` é `False`
- `""` (uma string vazia) é `False`
- `[]` (uma lista vazia) é `False`
- `()` (um tuplo vazio) é `False`

Já os valores que são verdadeiros são considerados como `True`.
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
