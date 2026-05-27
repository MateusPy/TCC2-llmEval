# Item 04 — `factual-tutor-002` (Custom, factual)
> **Anotador (calibração)**. Após ler este arquivo, vá pra linha **04** do `annotations_(calibração).csv` e preencha `score`, `justification`, `flagged`, `notes`.
> Anote `ts_start` ANTES de ler, `ts_end` ao terminar (timestamp local em formato livre, ex.: `2026-06-08 14:23`).

---
**Categoria:** `programming`  
**Chatbot avaliado:** Custom  
**Dimensão:** **factual**

---
## Prompt
> Qual palavra-chave do Python define uma funcao?

## Ground truth (resposta esperada)
> def.

## Respostas do chatbot (3 repetições)

### Repetição 1
```
A palavra-chave do Python que define uma função é `def`. Ela é usada para declarar uma função, que é um bloco de código que pode ser executado várias vezes com diferentes entradas.

Exemplo:
```python
def saudacao(nome):
    print(f"Olá, {nome}!")
```
Nesse exemplo, `def` é usado para declarar uma função chamada `saudacao` que recebe um parâmetro `nome`. A função imprime uma mensagem de saudação com o nome passado como parâmetro.
```

### Repetição 2
```
A palavra-chave do Python que define uma função é `def`. Ela é usada para declarar uma função, que é um bloco de código que pode ser executado várias vezes com diferentes entradas.

Exemplo:
```python
def saudacao(nome):
    print(f"Olá, {nome}!")
```
Nesse exemplo, `def` é usado para declarar uma função chamada `saudacao` que recebe um parâmetro `nome`. A função imprime uma mensagem de saudação com o nome passado como parâmetro.
```

### Repetição 3
```
A palavra-chave do Python que define uma função é `def`. Ela é usada para declarar uma função, que é um bloco de código que pode ser executado várias vezes com diferentes entradas.

Exemplo:
```python
def saudacao(nome):
    print(f"Olá, {nome}!")
```
Nesse exemplo, `def` é usado para declarar uma função chamada `saudacao` que recebe um parâmetro `nome`. A função imprime uma mensagem de saudação com o nome passado como parâmetro.
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
