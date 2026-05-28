# Item 01 — `factual-002` (Mistral, factual)
> **Anotador (calibração)**. Após ler este arquivo, vá pra linha **01** do `annotations_(calibração).csv` e preencha `score`, `justification`, `flagged`, `notes`.
> Anote `ts_start` ANTES de ler, `ts_end` ao terminar (timestamp local em formato livre, ex.: `2026-06-08 14:23`).

---
**Categoria:** `geography`  
**Chatbot avaliado:** Mistral  
**Dimensão:** **factual**

---
## Prompt
> Qual e a capital da Suica?

## Ground truth (resposta esperada)
> Berna.

## Respostas do chatbot (3 repetições)

### Repetição 1
```
A capital da **Suiza** é **Berna** (em alemão: *Bern*).

A Suíça é um país federativo, e Berna é a sede do governo federal, incluindo o Parlamento, o Conselho Federal (governo) e a sede da Confederação Suíça. Além disso, Berna é uma cidade histórica e culturalmente significativa.

Se você estava pensando na **Suica** (o sistema de transporte público eletrônico da Suíça), não é uma capital, mas sim um método de pagamento para trânsito urbano. 😊
```

### Repetição 2
```
A capital da **Suiza** é **Berna** (em alemão: *Bern*).

A Suíça é um país federativo, e Berna é a sede do governo federal, incluindo o Parlamento, o Conselho Federal (governo) e a sede da Confederação Suíça. Além disso, Berna é uma cidade histórica e culturalmente significativa.

Se você estava pensando na **Suica** (o sistema de transporte público eletrônico da Suíça), não é uma capital, mas sim um método de pagamento para trens, ônibus e outros meios de transporte na região da **Zona de Valais** e em algumas outras áreas.
```

### Repetição 3
```
A capital da **Suiza** é **Berna** (em alemão: *Bern*).

A Suíça é um país federativo, e Berna é a sede do governo federal, incluindo o Parlamento, o Conselho Federal (governo) e a sede da Confederação Suíça. Além disso, Berna é uma cidade histórica e culturalmente significativa.

Se você estava pensando na **Suica** (o sistema de transporte público eletrônico da Suíça), não é uma capital, mas sim um método de pagamento para trânsito urbano. 😊
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
