# Item 02 — `consistency-003` (Gemini, consistency)
> **Anotador (calibração)**. Após ler este arquivo, vá pra linha **02** do `annotations_(calibração).csv` e preencha `score`, `justification`, `flagged`, `notes`.
> Anote `ts_start` ANTES de ler, `ts_end` ao terminar (timestamp local em formato livre, ex.: `2026-06-08 14:23`).

---
**Categoria:** `writing`  
**Chatbot avaliado:** Gemini  
**Dimensão:** **consistency**

---
## Prompt base
> Explique a diferenca entre lista e tupla em Python.

## Resposta ao prompt base
```
Em Python, tanto **listas** quanto **tuplas** são estruturas de dados usadas para armazenar coleções de itens. No entanto, a principal diferença entre elas reside na sua **mutabilidade**.

Vamos detalhar cada uma e depois comparar:

---

### Listas (Lists)

*   **Definição:** Listas são coleções **mutáveis** e **ordenadas** de itens. Isso significa que você pode modificar uma lista após sua criação, adicionando, removendo ou alterando elementos.
*   **Sintaxe:** São definidas usando colchetes `[]`.
*   **Exemplo:**
    ```python
    minha_lista = [1, "Python", 3.14, True]
    ```
*   **Características:**
    *   **Mutáveis:** Você pode alterar os elementos, adicionar novos elementos ou remover elementos existentes.
        ```python
        minha_lista.append("novo item")  # Adiciona um item ao final
        minha_lista[0] = 100             # Altera o primeiro elemento
        del minha_lista[1]               # Remove o segundo elemento
        print(minha_lista)               # Saída: [100, 3.14, True, 'novo item']
        ```
    *   **Ordenadas:** Os elementos mantêm a ordem em que foram inseridos.
    *   **Podem conter tipos de dados mistos:** Uma lista pode armazenar números, strings, booleanos, outras listas, etc.
    *   **Uso comum:** Quando você precisa de uma coleção de itens que pode mudar ao longo do tempo, como uma lista de tarefas, um carrinho de compras, ou dados que serão processados e modificados.

---

### Tuplas (Tuples)

*   **Definição:** Tuplas são coleções **imutáveis** e **ordenadas** de itens. Uma vez que uma tupla é criada, você não pode alterar seus elementos.
*   **Sintaxe:** São definidas usando parênteses `()`.
*   **Exemplo:**
    ```python
    minha_tupla = (1, "Python", 3.14, True)
    ```
*   **Características:**
    *   **Imutáveis:** Você não pode adicionar, remover ou alterar elementos após a criação da tupla.
        ```python
        # Tentativas de modificação resultarão em erro:
        # minha_tupla.append("novo item")  # AttributeError
        # minha_tupla[0] = 100             # TypeError
        # del minha_tupla[1]               # TypeError
        ```
        Se você precisar de uma versão modificada de uma tupla, você terá que criar uma nova tupla.
    *   **Ordenadas:** Os elementos mantêm a ordem em que foram inseridos.
    *   **Podem conter tipos de dados mistos:** Assim como listas, tuplas podem armazenar diferentes tipos de dados.
    *   **Uso comum:**
        *   Quando você quer garantir que os dados não sejam alterados acidentalmente.
        *   Para representar registros fixos, como coordenadas (x, y), informações de data (ano, mês, dia).
        *   Como chaves em dicionários (pois são imutáveis e hashable).
        *   Para retornar múltiplos valores de uma função.

---

### Resumo das Diferenças Principais:

| Característica | Lista (`[]`)                               | Tupla (`()`)                               |
| :------------- | :----------------------------------------- | :----------------------------------------- |
| **Mutabilidade** | **Mutável** (pode ser alterada)            | **Imutável** (não pode ser alterada)       |
| **Sintaxe**    | Colchetes `[]`                             | Parênteses `()`                            |
| **Performance**| Geralmente um pouco mais lenta devido à mutabilidade. | Geralmente um pouco mais rápida e consome menos memória devido à imutabilidade. |
| **Uso Típico** | Coleções que precisam ser modificadas.     | Coleções fixas, registros, chaves de dicionário. |
| **Métodos**    | Possui métodos para modificação (append, insert, remove, pop, etc.). | Não possui métodos de modificação. |

---

### Quando usar qual?

*   **Use Listas quando:**
    *   Você precisa adicionar, remover ou modificar elementos após a criação.
    *   A coleção de itens é dinâmica e pode mudar.

*   **Use Tuplas quando:**
    *   Você quer garantir que os dados não sejam alterados.
    *   A
```

## Respostas às paráfrases

### Paráfrase `consistency-003-v1`
**Prompt:** _(prompt indisponível)_
**Resposta:**
```
Em Python, `list` e `tuple` são ambos tipos de sequências que podem armazenar coleções de itens. No entanto, a principal diferença entre eles reside na sua **mutabilidade**.

Vamos detalhar as diferenças:

---

### 1. Mutabilidade (A Diferença Fundamental)

*   **`list` (Lista): Mutável**
    *   Isso significa que você pode **modificar** uma lista após ela ter sido criada. Você pode adicionar, remover ou alterar elementos em uma lista.
    *   **Exemplo:**
        ```python
        minha_lista = [1, 2, 3]
        minha_lista.append(4)  # Adiciona um elemento
        minha_lista[0] = 10    # Altera um elemento
        del minha_lista[1]     # Remove um elemento
        print(minha_lista)     # Saída: [10, 3, 4]
        ```

*   **`tuple` (Tupla): Imutável**
    *   Isso significa que, uma vez que uma tupla é criada, você **não pode modificá-la**. Você não pode adicionar, remover ou alterar elementos.
    *   **Exemplo:**
        ```python
        minha_tupla = (1, 2, 3)
        # Tentativas de modificação resultarão em erro:
        # minha_tupla.append(4)  # AttributeError: 'tuple' object has no attribute 'append'
        # minha_tupla[0] = 10    # TypeError: 'tuple' object does not support item assignment
        # del minha_tupla[1]     # TypeError: 'tuple' object doesn't support item deletion
        print(minha_tupla)     # Saída: (1, 2, 3)
        ```
    *   **Observação:** Se uma tupla contiver um objeto mutável (como uma lista), você poderá modificar esse objeto mutável *dentro* da tupla. No entanto, a tupla em si (a referência ao objeto) permanece imutável.
        ```python
        tupla_com_lista = ([1, 2], 3)
        tupla_com_lista[0].append(4) # Isso é permitido!
        print(tupla_com_lista)       # Saída: ([1, 2, 4], 3)
        # tupla_com_lista[0] = [5, 6] # Isso ainda não é permitido!
        ```

---

### 2. Sintaxe

*   **`list`:** Criada usando colchetes `[]`.
    ```python
    lista_vazia = []
    lista_com_itens = [1, "hello", 3.14]
    ```

*   **`tuple`:** Criada usando parênteses `()`.
    ```python
    tupla_vazia = ()
    tupla_com_itens = (1, "hello", 3.14)
    ```
    *   **Casos Especiais de Sintaxe para Tuplas:**
        *   Para uma tupla com um único elemento, você precisa de uma vírgula final: `(item,)`. Sem a vírgula, seria interpretado como o item entre parênteses.
            ```python
            tupla_unica = (5,)
            nao_e_tupla = (5) # Isso é apenas um inteiro
            print(type(tupla_unica)) # <class 'tuple'>
            print(type(nao_e_tupla)) # <class 'int'>
            ```
        *   Os parênteses são opcionais em muitos casos, especialmente ao desempacotar ou retornar múltiplos valores de uma função.
            ```python
            minha_tupla = 1, 2, 3 # Isso cria uma tupla
            ```

---

### 3. Performance

*   **`tuple`:** Geralmente são um pouco mais eficientes em termos de memória e velocidade de iteração do que listas. Isso ocorre porque sua natureza imutável permite que o Python otimize seu armazenamento e acesso.
*   **`list`:** São mais flexíveis, mas essa flexibilidade vem com um pequeno custo de performance em comparação com tuplas.

---

### 4. Uso Comum

*   **`list`:**
    *   Quando você precisa de uma coleção de itens que pode mudar ao longo do tempo (adicionar, remover, modificar).
    *   Para armazenar dados que serão processados sequencialmente e podem
```

### Paráfrase `consistency-003-v2`
**Prompt:** _(prompt indisponível)_
**Resposta:**
```
Em Python, **listas** e **tuplas** são ambas sequências ordenadas de itens, mas possuem diferenças fundamentais que as tornam adequadas para diferentes propósitos. A principal distinção reside na sua **mutabilidade**.

Vamos comparar as duas em detalhes:

## Listas (Lists)

*   **Mutabilidade:** Listas são **mutáveis**. Isso significa que você pode alterar seu conteúdo após a criação. Você pode adicionar, remover ou modificar elementos em uma lista.
*   **Sintaxe:** São definidas usando colchetes `[]`.
    ```python
    minha_lista = [1, "hello", 3.14, True]
    ```
*   **Flexibilidade:** São ideais para coleções de itens que podem mudar ao longo do tempo.
*   **Operações Comuns:**
    *   **Adicionar elementos:** `append()`, `insert()`, `extend()`
    *   **Remover elementos:** `remove()`, `pop()`, `del`
    *   **Modificar elementos:** Acessando por índice e atribuindo um novo valor.
    *   **Ordenar:** `sort()` (in-place), `sorted()` (retorna uma nova lista)
*   **Uso:**
    *   Armazenar dados que precisam ser atualizados dinamicamente.
    *   Implementar pilhas (stacks) e filas (queues).
    *   Coletar resultados de operações.
*   **Performance:** Geralmente um pouco mais lentas que tuplas para iteração e acesso, devido à sobrecarga de gerenciar a mutabilidade.

**Exemplo de Lista:**

```python
frutas = ["maçã", "banana", "laranja"]
print(frutas)  # Saída: ['maçã', 'banana', 'laranja']

frutas.append("uva")
print(frutas)  # Saída: ['maçã', 'banana', 'laranja', 'uva']

frutas[1] = "morango"
print(frutas)  # Saída: ['maçã', 'morango', 'laranja', 'uva']

frutas.remove("laranja")
print(frutas)  # Saída: ['maçã', 'morango', 'uva']
```

## Tuplas (Tuples)

*   **Mutabilidade:** Tuplas são **imutáveis**. Uma vez criadas, você não pode alterar seu conteúdo. Não é possível adicionar, remover ou modificar elementos.
*   **Sintaxe:** São definidas usando parênteses `()`. Parênteses são opcionais em muitos casos, mas são necessários para tuplas vazias ou para evitar ambiguidade.
    ```python
    minha_tupla = (1, "hello", 3.14, True)
    # Ou sem parênteses (se não houver ambiguidade)
    outra_tupla = 1, "hello", 3.14, True
    ```
*   **Segurança e Integridade:** A imutabilidade garante que os dados em uma tupla não sejam acidentalmente alterados, o que é útil para representar coleções de dados que devem permanecer constantes.
*   **Operações Comuns:**
    *   **Acesso a elementos:** Por índice.
    *   **Fatiamento (Slicing):** Para obter sub-tuplas.
    *   **Concatenação:** Usando o operador `+` para criar novas tuplas.
    *   **Repetição:** Usando o operador `*` para criar novas tuplas.
*   **Uso:**
    *   Representar coleções de dados fixos, como coordenadas (x, y), registros de banco de dados, ou valores de configuração.
    *   Usar como chaves em dicionários (pois são imutáveis e hashable).
    *   Retornar múltiplos valores de uma função.
*   **Performance:** Geralmente mais rápidas que listas para iteração e acesso, pois o Python pode otimizar o uso de memória e o acesso aos elementos devido à sua natureza imutável.

**Exemplo de Tupla:**

```python
coordenadas = (10, 20)
print(coordenadas)  # Saída: (10, 20)

# Tentativa de modificar uma tupla resultará em erro:
# coordenadas[0] = 5  # Isso gerará um TypeError

# Criando uma nova tupla a partir da antiga
novas_coordenadas = (coordenadas[0] + 5, coordenadas[1] + 5)
print(novas_coorden
```

### Paráfrase `consistency-003-v3`
**Prompt:** _(prompt indisponível)_
**Resposta:**
```
Em Python, a escolha entre usar uma **lista** ou uma **tupla** depende principalmente da **mutabilidade** e do **propósito** dos dados que você está armazenando.

Aqui estão as diretrizes gerais sobre quando usar uma lista em vez de uma tupla:

**Use uma LISTA quando:**

1. **Você precisa modificar os elementos:**
   * **Adicionar novos elementos:** `lista.append(novo_item)` ou `lista.insert(indice, novo_item)`
   * **Remover elementos:** `lista.remove(item)` ou `del lista[indice]` ou `lista.pop()`
   * **Alterar elementos existentes:** `lista[indice] = novo_valor`
   * **Reordenar elementos:** `lista.sort()` ou `lista.reverse()`

   **Exemplo:** Uma lista de tarefas pendentes. Você adiciona novas tarefas, marca tarefas como concluídas (removendo-as ou alterando um status) e reordena a lista.

   ```python
   tarefas = ["Comprar pão", "Estudar Python", "Ligar para o João"]
   tarefas.append("Pagar contas")
   tarefas.remove("Comprar pão")
   tarefas[0] = "Estudar Python intensivamente"
   print(tarefas)
   ```

2. **O número de elementos pode mudar:**
   * Se você não sabe quantos itens terá em sua coleção de antemão, ou se esse número é dinâmico e pode aumentar ou diminuir durante a execução do programa, uma lista é a escolha natural.

   **Exemplo:** Uma lista de usuários que se conectam a um sistema. O número de usuários conectados muda constantemente.

   ```python
   usuarios_online = []
   # ... código que adiciona e remove usuários ...
   ```

3. **Você precisa de uma coleção que possa ser iterada e modificada:**
   * Listas são projetadas para serem flexíveis e permitem uma ampla gama de operações de manipulação de dados.

4. **O desempenho não é uma preocupação crítica para a imutabilidade:**
   * Embora listas sejam ligeiramente mais lentas que tuplas em algumas operações devido à sua natureza mutável, essa diferença geralmente é insignificante para a maioria das aplicações.

**Em resumo, use uma LISTA quando você precisa de uma coleção de itens que pode ser alterada após a sua criação.**

**Quando usar TUPLA em vez de LISTA (para entender melhor a distinção):**

*   **Dados Imutáveis:** Quando você tem uma coleção de itens que não devem ser alterados após a criação. Tuplas são imutáveis, o que significa que uma vez criadas, seus elementos não podem ser modificados, adicionados ou removidos.
    *   **Exemplo:** Coordenadas geográficas (latitude, longitude), cores RGB (vermelho, verde, azul), registros de banco de dados que devem permanecer fixos.

    ```python
    coordenadas = (40.7128, -74.0060) # Nova York
    # coordenadas[0] = 34.0522 # Isso geraria um erro TypeError
    ```

*   **Estruturas de Dados Fixas:** Quando você quer representar uma estrutura de dados com um número fixo de elementos, onde a ordem e o tipo de cada elemento têm um significado específico.
    *   **Exemplo:** Um registro de pessoa com nome, idade e cidade.

    ```python
    pessoa = ("Alice", 30, "São Paulo")
    nome, idade, cidade = pessoa # Desempacotamento
    ```

*   **Chaves de Dicionário:** Tuplas podem ser usadas como chaves em dicionários porque são imutáveis. Listas não podem ser usadas como chaves de dicionário.
    *   **Exemplo:** Mapear coordenadas para informações.

    ```python
    mapa = {
        (40.7128, -74.0060): "Nova York",
        (34.0522, -118.2437): "Los Angeles"
    }
    ```

*   **Desempenho e Segurança:** Tuplas são ligeiramente mais eficientes em termos de memória e velocidade de acesso em comparação com listas. A imutabilidade também oferece uma garantia de segurança, pois você sabe que os dados não serão alterados acidentalmente.

**Em resumo, use uma TUPLA quando você precisa de uma coleção de itens que não deve ser alterada após a sua criação, ou quando a imutabilidade é um requisito.**

**Regra de ouro:** Se você precisa modificar a coleção, use
```

### Paráfrase `consistency-003-v4`
**Prompt:** _(prompt indisponível)_
**Resposta:**
```
As principais diferenças entre listas e tuplas em Python residem em sua **mutabilidade** e em como elas são usadas. Aqui está um detalhamento:

**1. Mutabilidade:**

*   **Listas (Mutable):** Listas são **mutáveis**, o que significa que você pode alterar seu conteúdo após a criação. Você pode adicionar, remover, modificar ou reordenar elementos em uma lista.
    *   **Exemplo:**
        ```python
        minha_lista = [1, 2, 3]
        minha_lista.append(4)  # Adiciona um elemento
        minha_lista[0] = 10    # Modifica um elemento
        print(minha_lista)     # Saída: [10, 2, 3, 4]
        ```

*   **Tuplas (Immutable):** Tuplas são **imutáveis**, o que significa que, uma vez criadas, seu conteúdo não pode ser alterado. Você não pode adicionar, remover ou modificar elementos em uma tupla.
    *   **Exemplo:**
        ```python
        minha_tupla = (1, 2, 3)
        # minha_tupla.append(4)  # Isso geraria um erro (AttributeError)
        # minha_tupla[0] = 10    # Isso geraria um erro (TypeError)
        print(minha_tupla)     # Saída: (1, 2, 3)
        ```

**2. Sintaxe:**

*   **Listas:** São definidas usando **colchetes `[]`**.
    *   Exemplo: `[elemento1, elemento2, elemento3]`

*   **Tuplas:** São definidas usando **parênteses `()`**.
    *   Exemplo: `(elemento1, elemento2, elemento3)`
    *   **Observação:** Os parênteses são opcionais em muitos casos, mas são recomendados para clareza. Uma tupla com um único elemento precisa de uma vírgula final para ser reconhecida como tupla: `(elemento,)`.

**3. Performance:**

*   **Tuplas:** Geralmente são um pouco mais **eficientes em termos de memória e velocidade** do que listas. Isso ocorre porque sua imutabilidade permite que o Python otimize seu uso.

**4. Uso e Casos de Aplicação:**

*   **Listas:** São ideais para coleções de itens que precisam ser modificados ao longo do tempo. Exemplos incluem:
    *   Armazenar uma lista de usuários que podem ser adicionados ou removidos.
    *   Manter um histórico de ações.
    *   Processar dados onde a ordem e o conteúdo podem mudar.

*   **Tuplas:** São ideais para coleções de itens que não devem mudar e que representam um conjunto fixo de dados. Exemplos incluem:
    *   **Coordenadas:** `(x, y)`
    *   **Registros de banco de dados:** `(id, nome, email)`
    *   **Valores de retorno de funções:** Uma função pode retornar múltiplos valores como uma tupla.
    *   **Chaves de dicionário:** Como tuplas são imutáveis, elas podem ser usadas como chaves em dicionários, enquanto listas não podem.
    *   **Garantir a integridade dos dados:** Ao usar tuplas, você garante que os dados não serão acidentalmente alterados.

**5. Métodos Disponíveis:**

*   **Listas:** Possuem uma variedade maior de métodos para manipulação, como `append()`, `extend()`, `insert()`, `remove()`, `pop()`, `sort()`, `reverse()`, etc.

*   **Tuplas:** Possuem menos métodos, principalmente aqueles que não modificam a tupla, como `count()` (conta a ocorrência de um elemento) e `index()` (retorna o índice da primeira ocorrência de um elemento).

**Resumo das Principais Diferenças:**

| Característica | Listas (`[]`)                               | Tuplas (`()`)                               |
| :------------- | :------------------------------------------ | :------------------------------------------ |
| **Mutabilidade** | Mutáveis (podem ser alteradas)              | Imutáveis (não podem ser alteradas)         |
| **Sintaxe**    | Colchetes `[]`                              | Parênteses `()`                             |
| **Performance**| Geralmente menos eficientes em memória/velocidade | Geralmente mais eficientes em memória/velocidade |
| **Uso Típico** | Coleções que mudam, dados dinâmicos         | Coleções fixas, dados
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
