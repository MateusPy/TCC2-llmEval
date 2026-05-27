# Item 10 — `factual-035` (Mistral, factual)
> **Anotador A2**. Após ler este arquivo, vá pra linha **10** do `annotations_A2.csv` e preencha `score`, `justification`, `flagged`, `notes`.
> Anote `ts_start` ANTES de ler, `ts_end` ao terminar (timestamp local em formato livre, ex.: `2026-06-08 14:23`).

---
**Categoria:** `calendar`  
**Chatbot avaliado:** Mistral  
**Dimensão:** **factual**

---
## Prompt
> Qual mes do ano tem menos dias em anos nao bissextos?

## Ground truth (resposta esperada)
> Fevereiro.

## Respostas do chatbot (3 repetições)

### Repetição 1
```
Em anos **não bissextos**, os meses com menos dias são sempre **fevereiro**, que tem **28 dias**.

Os outros meses do ano têm sempre o mesmo número de dias:
- **Janeiro**: 31 dias
- **Março**: 31 dias
- **Abril**: 30 dias
- **Maio**: 31 dias
- **Junho**: 30 dias
- **Julho**: 31 dias
- **Agosto**: 31 dias
- **Setembro**: 30 dias
- **Outubro**: 31 dias
- **Novembro**: 30 dias
- **Dezembro**: 31 dias

Portanto, **fevereiro** é o único mês com menos dias em anos não bissextos.
```

### Repetição 2
```
Em anos **não bissextos**, os meses com menos dias são sempre **fevereiro**, que tem **28 dias**.

Os outros meses do ano têm sempre o mesmo número de dias:
- **Janeiro**: 31 dias
- **Março**: 31 dias
- **Abril**: 30 dias
- **Maio**: 31 dias
- **Junho**: 30 dias
- **Julho**: 31 dias
- **Agosto**: 31 dias
- **Setembro**: 30 dias
- **Outubro**: 31 dias
- **Novembro**: 30 dias
- **Dezembro**: 31 dias

Portanto, **fevereiro** é o único mês com menos dias em anos não bissextos.
```

### Repetição 3
```
Em anos **não bissextos**, os meses com menos dias são sempre **fevereiro**, que tem **28 dias**.

Os outros meses do ano têm sempre o mesmo número de dias:
- **Janeiro**: 31 dias
- **Março**: 31 dias
- **Abril**: 30 dias
- **Maio**: 31 dias
- **Junho**: 30 dias
- **Julho**: 31 dias
- **Agosto**: 31 dias
- **Setembro**: 30 dias
- **Outubro**: 31 dias
- **Novembro**: 30 dias
- **Dezembro**: 31 dias

Portanto, **fevereiro** é o único mês com menos dias em anos não bissextos.
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
