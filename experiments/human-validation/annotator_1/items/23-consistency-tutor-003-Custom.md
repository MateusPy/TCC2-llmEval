# Item 23 — `consistency-tutor-003` (Custom, consistency)
> **Anotador A1**. Após ler este arquivo, vá pra linha **23** do `annotations_A1.csv` e preencha `score`, `justification`, `flagged`, `notes`.
> Anote `ts_start` ANTES de ler, `ts_end` ao terminar (timestamp local em formato livre, ex.: `2026-06-08 14:23`).

---
**Categoria:** `python_dict`  
**Chatbot avaliado:** Custom  
**Dimensão:** **consistency**

---
## Prompt base
> Como acesso o valor de uma chave em um dict em Python?

## Resposta ao prompt base
```
Em Python, você pode acessar o valor de uma chave em um dicionário (dict) usando a sintaxe `dicionário[chave]`.

Exemplo:
```python
meu_dicionario = {'nome': 'João', 'idade': 30}
print(meu_dicionario['nome'])  # Imprime: João
```
Se a chave não existir no dicionário, você receberá um erro `KeyError`. Para evitar isso, você pode usar o método `get()` do dicionário, que retorna `None` se a chave não existir:
```python
meu_dicionario = {'nome': 'João', 'idade': 30}
print(meu_dicionario.get('nome'))  # Imprime: João
print(meu_dicionario.get('endereco'))  # Imprime: None
```
Lembre-se de que o método `get()` é uma boa prática para evitar erros de chave não encontrada.
```

## Respostas às paráfrases

### Paráfrase `consistency-tutor-003-v1`
**Prompt:** _(prompt indisponível)_
**Resposta:**
```
A sintaxe para pegar o valor associado a uma chave de dicionário em Python é simples:

```python
dicionario = {'chave': 'valor'}
valor = dicionario['chave']
```

Nesse exemplo, `dicionario['chave']` é usado para acessar o valor associado à chave `'chave'` no dicionário `dicionario`. O valor é então atribuído à variável `valor`.

Lembre-se de que, se a chave não existir no dicionário, você receberá um erro `KeyError`. Para evitar isso, você pode usar o método `.get()` do dicionário:

```python
valor = dicionario.get('chave', 'valor_padrao')
```

Nesse caso, se a chave `'chave'` não existir, o valor `valor_padrao` será retornado em vez de um erro.
```

### Paráfrase `consistency-tutor-003-v2`
**Prompt:** _(prompt indisponível)_
**Resposta:**
```
Para ler um item de um dicionário Python a partir da chave, você pode usar a sintaxe `dicionário[chave]`. Por exemplo:

```python
meu_dicionario = {'nome': 'João', 'idade': 30}
print(meu_dicionario['nome'])  # Imprime: João
```

Se a chave não existir no dicionário, você receberá um erro `KeyError`. Para evitar isso, você pode usar o método `get()` do dicionário, que retorna `None` se a chave não existir:

```python
meu_dicionario = {'nome': 'João', 'idade': 30}
print(meu_dicionario.get('nome'))  # Imprime: João
print(meu_dicionario.get('endereco'))  # Imprime: None
```

Lembre-se de que o método `get()` é uma boa prática para evitar erros de chave não encontrada.
```

### Paráfrase `consistency-tutor-003-v3`
**Prompt:** _(prompt indisponível)_
**Resposta:**
```
Você pode usar a sintaxe de acesso direto ao dicionário para obter o valor de uma chave específica. Por exemplo:

```python
meu_dicionario = {'nome': 'João', 'idade': 30}
nome = meu_dicionario['nome']
```

Nesse exemplo, `nome` receberá o valor `'João'`.

Se a chave não existir no dicionário, você receberá um erro `KeyError`. Para evitar isso, você pode usar o método `get()` do dicionário, que permite especificar um valor padrão a ser retornado se a chave não existir:

```python
nome = meu_dicionario.get('nome', 'Desconhecido')
```

Nesse caso, se a chave `'nome'` não existir no dicionário, `nome` receberá o valor `'Desconhecido'`.
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
