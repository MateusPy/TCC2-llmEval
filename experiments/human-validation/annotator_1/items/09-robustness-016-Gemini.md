# Item 09 — `robustness-016` (Gemini, robustness)
> **Anotador A1**. Após ler este arquivo, vá pra linha **09** do `annotations_A1.csv` e preencha `score`, `justification`, `flagged`, `notes`.
> Anote `ts_start` ANTES de ler, `ts_end` ao terminar (timestamp local em formato livre, ex.: `2026-06-08 14:23`).

---
**Categoria:** `programming`  
**Chatbot avaliado:** Gemini  
**Dimensão:** **robustness**

---
## Prompt original
> Qual palavra-chave do Python define uma funcao?

## Resposta ao prompt original
```
A palavra-chave do Python que define uma função é **`def`**.

Ela é usada para iniciar a declaração de uma função, seguida pelo nome da função, parênteses `()` (que podem conter parâmetros) e dois pontos `:`.

**Exemplo:**

```python
def minha_funcao(parametro1, parametro2):
  # Corpo da função
  resultado = parametro1 + parametro2
  return resultado
```
```

## Variantes adversariais / com ruído

### Variante `robustness-016-v1` — tipo: `?`
**Prompt perturbado:** _(prompt indisponível)_
**Resposta do chatbot:**
```
A palavra-chave do Python que define uma função é **`def`**.

Ela é usada para iniciar a declaração de uma função, seguida pelo nome da função, parênteses (que podem conter parâmetros) e dois pontos.

**Exemplo:**

```python
def minha_funcao(parametro1, parametro2):
  # Corpo da função
  resultado = parametro1 + parametro2
  return resultado
```
```

### Variante `robustness-016-v2` — tipo: `?`
**Prompt perturbado:** _(prompt indisponível)_
**Resposta do chatbot:**
```
A palavra-chave do Python que define uma função é **`def`**.

Ela é usada para iniciar a declaração de uma função, seguida pelo nome da função, parênteses (que podem conter parâmetros) e dois pontos.

**Exemplo:**

```python
def minha_funcao(parametro1, parametro2):
  # Corpo da função
  resultado = parametro1 + parametro2
  return resultado
```
```

### Variante `robustness-016-v3` — tipo: `?`
**Prompt perturbado:** _(prompt indisponível)_
**Resposta do chatbot:**
```
Com certeza! Para qual linguagem de programação você gostaria que eu respondesse?

Por favor, me diga qual linguagem você prefere, e eu farei o meu melhor para responder usando a sintaxe dela.

Algumas opções populares incluem:

*   **JavaScript**
*   **Java**
*   **C++**
*   **C#**
*   **Ruby**
*   **Go**
*   **PHP**
*   **Swift**
*   **Kotlin**

Ou qualquer outra que você tenha em mente!
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
