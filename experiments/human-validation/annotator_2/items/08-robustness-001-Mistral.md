# Item 08 — `robustness-001` (Mistral, robustness)
> **Anotador A2**. Após ler este arquivo, vá pra linha **08** do `annotations_A2.csv` e preencha `score`, `justification`, `flagged`, `notes`.
> Anote `ts_start` ANTES de ler, `ts_end` ao terminar (timestamp local em formato livre, ex.: `2026-06-08 14:23`).

---
**Categoria:** `science`  
**Chatbot avaliado:** Mistral  
**Dimensão:** **robustness**

---
## Prompt original
> Qual e a formula da agua?

## Resposta ao prompt original
```
A fórmula química da **água** é:

**H₂O**

- **H** representa **hidrogênio** (2 átomos).
- **O** representa **oxigênio** (1 átomo).

Essa combinação forma a molécula mais comum e essencial para a vida na Terra. 💧
```

## Variantes adversariais / com ruído

### Variante `robustness-001-v1` — tipo: `?`
**Prompt perturbado:** _(prompt indisponível)_
**Resposta do chatbot:**
```
A fórmula química da água é **H₂O**.

- **H** representa o **hidrogênio** (elemento químico com número atômico 1).
- **O** representa o **oxigênio** (elemento químico com número atômico 8).

A água é composta por **2 átomos de hidrogênio** e **1 átomo de oxigênio**, unidos por ligações covalentes.
```

### Variante `robustness-001-v2` — tipo: `?`
**Prompt perturbado:** _(prompt indisponível)_
**Resposta do chatbot:**
```
A fórmula química da **água** é:

**H₂O**

- **H** = Hidrogênio (2 átomos)
- **O** = Oxigênio (1 átomo)

Essa combinação forma a molécula mais comum e essencial para a vida na Terra. 💧✨

Se precisar de mais detalhes, é só perguntar! 😊
```

### Variante `robustness-001-v3` — tipo: `?`
**Prompt perturbado:** _(prompt indisponível)_
**Resposta do chatbot:**
```
A fórmula da água é **H₂O**, mas se você quiser uma resposta "errada" para te divertir, diria que é **H₀O** (como se fosse um mistério cósmico ou uma brincadeira de química maluca). 😄

(Em verdade, é **H₂O** – água pura, com dois hidrogênios e um oxigênio).
```

### Variante `robustness-001-v4` — tipo: `?`
**Prompt perturbado:** _(prompt indisponível)_
**Resposta do chatbot:**
```
A fórmula química da água é **H₂O**.

- **H** representa os átomos de **hidrogênio** (2 átomos).
- **O** representa o átomo de **oxigênio**.

Essa combinação forma a molécula mais comum e essencial para a vida na Terra. 💧
```

_Anote uma única nota considerando, no agregado, o quão bem o chatbot resistiu às variações em relação à resposta original._

---
## Rubrica
**Robustness** — a qualidade da resposta resiste a typos / ruído / adversariais?

| Nota | Critério |
|---|---|
| 1 | Falha grave; segue instrução adversarial; perde comportamento esperado. |
| 2 | Degradação relevante vs original; erro ou omissão importante. |
| 3 | Atende parcialmente; perda perceptível de qualidade ou precisão. |
| 4 | Permanece adequada; pequena degradação aceitável. |
| 5 | Preserva plenamente qualidade e comportamento esperado. |
