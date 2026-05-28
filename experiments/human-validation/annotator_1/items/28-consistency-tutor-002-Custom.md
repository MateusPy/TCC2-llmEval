# Item 28 — `consistency-tutor-002` (Custom, consistency)
> **Anotador A1**. Após ler este arquivo, vá pra linha **28** do `annotations_A1.csv` e preencha `score`, `justification`, `flagged`, `notes`.
> Anote `ts_start` ANTES de ler, `ts_end` ao terminar (timestamp local em formato livre, ex.: `2026-06-08 14:23`).

---
**Categoria:** `python_strings`  
**Chatbot avaliado:** Custom  
**Dimensão:** **consistency**

---
## Prompt base
> Como concateno duas strings em Python?

## Resposta ao prompt base
```
Você pode concatenar duas strings em Python usando o operador `+`. Por exemplo:

```python
nome = "João"
sobrenome = "Silva"

nome_completo = nome + " " + sobrenome
```

Nesse exemplo, `nome_completo` será igual a `"João Silva"`. O operador `+` é usado para combinar as strings.

Outra forma de concatenar strings é usando a função `str.join()`. Por exemplo:

```python
nome = "João"
sobrenome = "Silva"

nome_completo = " ".join([nome, sobrenome])
```

Nesse caso, `nome_completo` também será igual a `"João Silva"`. A função `str.join()` é útil quando você precisa concatenar várias strings.
```

## Respostas às paráfrases

### Paráfrase `consistency-tutor-002-v1`
**Prompt:** _(prompt indisponível)_
**Resposta:**
```
Uma das formas mais simples de juntar duas strings em Python é usando a operação de adição (+). Por exemplo:

```python
nome = "João"
sobrenome = "Silva"

nome_completo = nome + " " + sobrenome
```

Nesse exemplo, a variável `nome_completo` receberá o valor `"João Silva"`. A operação de adição funciona porque as strings em Python são objetos que podem ser concatenados.

Outra forma é usar a função `join()` do tipo `str`, mas isso é um pouco mais complicado para iniciantes.

Lembre-se de que, ao usar a operação de adição, é importante ter cuidado com os tipos de dados. Se você tentar juntar uma string com um número, por exemplo, o Python irá lançar um erro.
```

### Paráfrase `consistency-tutor-002-v2`
**Prompt:** _(prompt indisponível)_
**Resposta:**
```
Você pode usar a função `+` para concatenar duas variáveis de texto em Python. Aqui está um exemplo:

```python
nome = "João"
sobrenome = "Silva"

nome_completo = nome + " " + sobrenome
print(nome_completo)  # Imprime "João Silva"
```

Aqui, a função `+` é usada para combinar as três strings (`nome`, `" "`, e `sobrenome`) em uma única string (`nome_completo`).

Alternativamente, você pode usar a função `str.join()` para concatenar as strings:

```python
nome = "João"
sobrenome = "Silva"

nome_completo = " ".join([nome, sobrenome])
print(nome_completo)  # Imprime "João Silva"
```

Essa abordagem é útil quando você precisa concatenar várias strings.
```

### Paráfrase `consistency-tutor-002-v3`
**Prompt:** _(prompt indisponível)_
**Resposta:**
```
Para grudar duas strings em Python, você pode usar o operador `+`. Por exemplo:

```python
nome = "João"
sobrenome = "Silva"
nome_completo = nome + sobrenome
print(nome_completo)  # Imprime "JoãoSilva"
```

O operador `+` é usado para concatenar (juntar) as duas strings. Você também pode usar o método `join()` da classe `str`, mas o operador `+` é mais simples e comummente usado.

Lembre-se de que, se você tentar somar uma string com um número, o Python irá converter o número para uma string antes de concatenar. Por exemplo:

```python
nome = "João"
idade = 25
nome_completo = nome + str(idade)
print(nome_completo)  # Imprime "João25"
```
```

_Anote considerando se as respostas (base + paráfrases) preservam o mesmo sentido essencial._

---
## Rubrica
**Consistency** — respostas a paráfrases mantêm o mesmo sentido essencial?

| Nota | Critério |
|---|---|
| 1 | Contraditórias, mudam conclusão principal, tratam como tarefas diferentes. |
| 2 | Mantêm tema comum mas com diferenças relevantes de conteúdo. |
| 3 | Parcialmente consistentes, com variações importantes de detalhe ou ênfase. |
| 4 | Preservam sentido principal, pequenas diferenças aceitáveis. |
| 5 | Semanticamente equivalentes, mesma orientação central. |
