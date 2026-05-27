# Item 24 — `factual-018` (Mistral, factual)
> **Anotador A2**. Após ler este arquivo, vá pra linha **24** do `annotations_A2.csv` e preencha `score`, `justification`, `flagged`, `notes`.
> Anote `ts_start` ANTES de ler, `ts_end` ao terminar (timestamp local em formato livre, ex.: `2026-06-08 14:23`).

---
**Categoria:** `programming`  
**Chatbot avaliado:** Mistral  
**Dimensão:** **factual**

---
## Prompt
> Qual estrutura de dados do Python armazena pares chave-valor mutaveis?

## Ground truth (resposta esperada)
> dict.

## Respostas do chatbot (3 repetições)

### Repetição 1
```
No Python, a estrutura de dados que armazena **pares chave-valor mutáveis** de forma eficiente é o **`dict` (dicionário)**.

### Características do `dict`:
- **Mutável**: Permite alterações após a criação (adicionar, modificar ou remover pares chave-valor).
- **Chaves únicas**: Cada chave deve ser **imutável** (exemplos: `str`, `int`, `tuple`, `frozenset`).
- **Acesso rápido**: Operações de busca, inserção e exclusão são **O(1)** em média (graças à implementação baseada em hash).
- **Flexível**: Chaves e valores podem ser de qualquer tipo imutável.

### Exemplo:
```python
meu_dicionario = {
    "chave1": "valor1",
    123: [1, 2, 3],  # Valor mutável (lista)
    ("tupla",): "outro valor"  # Chave imutável (tupla)
}

meu_dicionario["nova_chave"] = "novo_valor"  # Adiciona um novo par
print(meu_dicionario["chave1"])  # Acesso ao valor
```

### Outras estruturas mutáveis (menos recomendadas para pares chave-valor):
- **`list`**: Não é ideal para pares chave-valor (só índices numéricos).
- **`set`**: Armazena elementos únicos, não pares.

Se precisar de um **conjunto de pares ordenados**, use `dict` ou `collections.OrderedDict` (para preservar ordem de inserção).

### Alternativa para chaves dinâmicas (Python 3.7+):
Em versões recentes do Python, o `dict` mantém a **ordem de inserção** (como `OrderedDict`), mas não é necessário importar explicitamente.
```

### Repetição 2
```
No Python, a estrutura de dados que armazena **pares chave-valor mutáveis** de forma eficiente é o **`dict` (dicionário)**.

### Características do `dict`:
- **Mutável**: Permite alterações após a criação (adicionar, modificar ou remover pares chave-valor).
- **Chaves únicas**: Cada chave deve ser **imutável** (exemplos: `str`, `int`, `tuple`, `frozenset`).
- **Acesso rápido**: Operações de busca, inserção e exclusão são **O(1)** em média (graças à implementação baseada em hash).
- **Flexível**: Chaves e valores podem ser de qualquer tipo imutável.

### Exemplo:
```python
meu_dicionario = {
    "chave1": "valor1",
    123: [1, 2, 3],  # Valor mutável (lista)
    ("tupla",): "outro valor"  # Chave imutável (tupla)
}

meu_dicionario["nova_chave"] = "novo_valor"  # Adiciona um novo par
meu_dicionario[123].append(4)  # Modifica um valor mutável
del meu_dicionario["chave1"]  # Remove uma chave
```

### Outras estruturas mutáveis (menos recomendadas para pares chave-valor):
- **`list`**: Não é ideal para pares chave-valor (usado para sequências ordenadas).
- **`set`**: Armazena elementos únicos, não pares.
- **`collections.OrderedDict`**: Versão ordenada do `dict`, mas ainda é um `dict` com funcionalidades adicionais.

### Quando usar `dict`?
- Para **associar dados com identificadores únicos**.
- Quando precisar de **acesso rápido por chave** e **mutabilidade**.

Se precisar de um dicionário ordenado ou com prioridades, pode usar `collections.OrderedDict` ou `defaultdict` (para valores padrão).
```

### Repetição 3
```
No Python, a estrutura de dados que armazena **pares chave-valor mutáveis** de forma eficiente é o **`dict` (dicionário)**.

### Características do `dict`:
- **Mutável**: Permite alterações após a criação (adicionar, modificar ou remover pares chave-valor).
- **Chaves únicas**: Cada chave deve ser **imutável** (exemplos: `str`, `int`, `tuple`, `frozenset`).
- **Acesso rápido**: Operações de busca, inserção e exclusão são **O(1)** em média (graças à implementação baseada em hash).
- **Flexível**: Chaves e valores podem ser de qualquer tipo imutável.

### Exemplo:
```python
meu_dicionario = {
    "chave1": "valor1",
    123: [1, 2, 3],  # Valor mutável (lista)
    ("tupla",): "outro valor"  # Chave imutável (tupla)
}

meu_dicionario["nova_chave"] = "novo_valor"  # Adiciona um novo par
meu_dicionario[123].append(4)  # Modifica valor mutável
```

### Outras estruturas mutáveis (menos recomendadas para pares chave-valor):
- **`list`**: Armazena elementos em ordem, mas não é ideal para mapear chaves a valores (exige indexação).
- **`set`**: Armazena elementos únicos, não é adequado para pares chave-valor.

### Alternativas menos comuns:
- **`defaultdict`** (do módulo `collections`): Similar ao `dict`, mas com comportamento padrão para chaves inexistentes.
- **`OrderedDict`** (do `collections`): Preserva a ordem de inserção (útil em casos específicos).

O **`dict` é a escolha padrão** para pares chave-valor mutáveis em Python.
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
