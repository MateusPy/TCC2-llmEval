# Item 01 — `consistency-tutor-010` (Custom, consistency)
> **Anotador A1**. Após ler este arquivo, vá pra linha **01** do `annotations_A1.csv` e preencha `score`, `justification`, `flagged`, `notes`.
> Anote `ts_start` ANTES de ler, `ts_end` ao terminar (timestamp local em formato livre, ex.: `2026-06-08 14:23`).

---
**Categoria:** `python_types`  
**Chatbot avaliado:** Custom  
**Dimensão:** **consistency**

---
## Prompt base
> Qual a diferenca entre list e tuple em Python?

## Resposta ao prompt base
```
Em Python, `list` e `tuple` são dois tipos de estruturas de dados que podem armazenar múltiplos valores. A principal diferença entre eles é que uma lista é mutável, enquanto um tuplo é imutável.

Uma lista é criada usando colchetes `[]` e pode ser modificada após sua criação. Por exemplo:

```python
meu_lista = [1, 2, 3]
meu_lista.append(4)
print(meu_lista)  # [1, 2, 3, 4]
```

Já um tuplo é criado usando parênteses `()` e não pode ser modificado após sua criação. Por exemplo:

```python
meu_tuplo = (1, 2, 3)
# meu_tuplo.append(4)  # Erro! Tuplos são imutáveis
```

Em geral, é recomendado usar tuplos quando você precisa armazenar valores que não precisam ser modificados, pois isso ajuda a evitar erros de programação. Já as listas são úteis quando você precisa armazenar valores que precisam ser modificados dinamicamente.
```

## Respostas às paráfrases

### Paráfrase `consistency-tutor-010-v1`
**Prompt:** _(prompt indisponível)_
**Resposta:**
```
Em Python, as listas (`list`) e tuplas (`tuple`) são dois tipos de estruturas de dados que podem armazenar múltiplos valores. A principal diferença entre elas é a imutabilidade.

**Listas (`list`)**

* São mutáveis, ou seja, você pode adicionar, remover ou modificar elementos após criar a lista.
* São definidas por colchetes `[]`.
* Exemplo: `meu_lista = [1, 2, 3]`

**Tuplas (`tuple`)**

* São imutáveis, ou seja, você não pode adicionar, remover ou modificar elementos após criar a tupla.
* São definidas por parênteses `()`.
* Exemplo: `meu_tupla = (1, 2, 3)`

Em geral, você deve usar tuplas quando:

* Você precisa garantir que os dados não sejam modificados.
* Você precisa armazenar uma sequência de valores que não precisam ser alterados.

Já use listas quando:

* Você precisa armazenar dados que precisam ser modificados ou adicionados.
* Você precisa trabalhar com dados que precisam ser ordenados ou rearranjados.

Lembre-se de que, embora as tuplas sejam imutáveis, você pode criar uma nova tupla com os mesmos elementos se precisar modificar os dados. Por exemplo: `meu_tupla_nova = meu_tupla + (4, 5)`
```

### Paráfrase `consistency-tutor-010-v2`
**Prompt:** _(prompt indisponível)_
**Resposta:**
```
Sim, é correto dizer que listas são mutáveis e tuplas são imutáveis em Python.

**Mutável** significa que você pode alterar o conteúdo da lista após criá-la. Por exemplo:

```python
minha_lista = [1, 2, 3]
minha_lista.append(4)  # Adiciona um novo elemento à lista
print(minha_lista)  # [1, 2, 3, 4]
minha_lista[0] = 10  # Muda o primeiro elemento da lista
print(minha_lista)  # [10, 2, 3, 4]
```

**Imutável** significa que você não pode alterar o conteúdo da tupla após criá-la. Se você tentar fazer isso, você receberá um erro:

```python
minha_tupla = (1, 2, 3)
minha_tupla.append(4)  # Erro! Tuplas não podem ser alteradas
```

No entanto, é importante notar que você pode criar uma nova tupla com os elementos alterados, mas não pode alterar a tupla original:

```python
minha_tupla = (1, 2, 3)
nova_tupla = minha_tupla + (4,)  # Cria uma nova tupla com o elemento adicionado
print(nova_tupla)  # (1, 2, 3, 4)
```

Essa diferença é importante para entender quando usar listas e quando usar tuplas em seu código.
```

### Paráfrase `consistency-tutor-010-v3`
**Prompt:** _(prompt indisponível)_
**Resposta:**
```
Em Python, as estruturas de dados usam diferentes símbolos para delimitar seus elementos. Aqui estão algumas das principais estruturas e os símbolos que as delimitam:

- **Listas** (listas): `[]`
- **Tuplas** (tuples): `()`
- **Dicionários** (dictionaries): `{}`

A escolha desses símbolos é apenas uma convenção e não tem implicações significativas. No entanto, é importante saber que:

- **Listas** são mutáveis, ou seja, você pode adicionar ou remover elementos delas.
- **Tuplas** são imutáveis, ou seja, você não pode adicionar ou remover elementos delas.
- **Dicionários** são estruturas de chave-valor, onde cada chave é única e pode ser usada para acessar o valor associado.

Por exemplo, se você criar uma lista com `[]`, pode adicionar ou remover elementos dela, mas se você criar uma tupla com `()`, não pode fazer isso.

```python
# Lista mutável
minha_lista = [1, 2, 3]
minha_lista.append(4)  # Adiciona um elemento
print(minha_lista)  # [1, 2, 3, 4]

# Tupla imutável
minha_tupla = (1, 2, 3)
# minha_tupla.append(4)  # Erro! Tuplas são imutáveis
```

Em resumo, a escolha entre `[]`, `()` e `{}` depende do tipo de estrutura de dados que você está trabalhando e das necessidades do seu programa.
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
