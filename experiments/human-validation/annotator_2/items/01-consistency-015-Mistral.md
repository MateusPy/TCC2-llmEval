# Item 01 — `consistency-015` (Mistral, consistency)
> **Anotador A2**. Após ler este arquivo, vá pra linha **01** do `annotations_A2.csv` e preencha `score`, `justification`, `flagged`, `notes`.
> Anote `ts_start` ANTES de ler, `ts_end` ao terminar (timestamp local em formato livre, ex.: `2026-06-08 14:23`).

---
**Categoria:** `programming`  
**Chatbot avaliado:** Mistral  
**Dimensão:** **consistency**

---
## Prompt base
> Como funciona um loop for em Python?

## Resposta ao prompt base
```
Em Python, o **`for`** é uma estrutura de controle que permite iterar sobre sequências (como listas, tuplas, strings, dicionários, conjuntos) ou executar um bloco de código repetidamente com base em um intervalo ou outro objeto iterável.

### **Sintaxe básica:**
```python
for item in iterável:
    # Código a ser executado em cada iteração
```

### **Exemplos comuns:**

#### 1. **Iterando sobre uma lista:**
```python
frutas = ["maçã", "banana", "laranja"]
for fruta in frutas:
    print(fruta)
```
**Saída:**
```
maçã
banana
laranja
```

#### 2. **Iterando sobre uma string:**
```python
palavra = "Python"
for letra in palavra:
    print(letra)
```
**Saída:**
```
P
y
t
h
o
n
```

#### 3. **Iterando sobre um dicionário (chave e valor):**
```python
pessoa = {"nome": "Alice", "idade": 25, "cidade": "São Paulo"}
for chave, valor in pessoa.items():
    print(f"{chave}: {valor}")
```
**Saída:**
```
nome: Alice
idade: 25
cidade: São Paulo
```

#### 4. **Iterando sobre um range (números):**
```python
for i in range(5):  # Imprime de 0 a 4
    print(i)
```
**Saída:**
```
0
1
2
3
4
```

**Variantes do `range()`:**
- `range(10)` → 0 a 9
- `range(2, 10)` → 2 a 9
- `range(1, 10, 2)` → 1, 3, 5, 7, 9

#### 5. **Loop com `enumerate()` (índice e valor):**
```python
frutas = ["maçã", "banana", "laranja"]
for indice, fruta in enumerate(frutas):
    print(f"Índice: {indice}, Fruta: {fruta}")
```
**Saída:**
```
Índice: 0, Fruta: maçã
Índice: 1, Fruta: banana
Índice: 2, Fruta: laranja
```

### **Loop `for` com `break` e `continue`:**
- **`break`**: Sai do loop imediatamente.
- **`continue`**: Pula para a próxima iteração.

```python
for num in range(10):
    if num == 5:
        break  # Sai do loop quando num for 5
    print(num)
```
**Saída:**
```
0
1
2
3
4
```

```python
for num in range(10):
    if num == 5:
        continue  # Pula o 5
    print(num)
```
**Saída:**
```
0
1
2
3
4
6
7
8
9
```

### **Loop `for` com `else` (executa se não houve `break`):**
```python
for num in range(5):
    print(num)
else:
    print("Loop terminou sem break!")
```
**Saída:**
```
0
1
2
3
4
Loop terminou sem break!
```

### **Conclusão:**
O `for` é usado para **iterar** sobre elementos de um objeto iterável (lista, string, dicionário, etc.) ou gerar sequências numéricas com `range()`. É fundamental para loops em Python, especialmente em tarefas repetitivas.

Se precisar de mais exemplos ou dúvidas, é só perguntar! 😊
```

## Respostas às paráfrases

### Paráfrase `consistency-015-v1`
**Prompt:** _(prompt indisponível)_
**Resposta:**
```
Em Python, o **`for`** é uma estrutura de controle usada para **iterar** (percorrer) sobre elementos de uma sequência (como listas, tuplas, strings, dicionários, conjuntos) ou sobre uma faixa de números (com `range()`). Ele é fundamental para realizar operações repetitivas de forma eficiente.

---

### **1. Iteração sobre sequências (listas, tuplas, strings, etc.)**
O `for` permite acessar cada elemento de uma sequência uma por vez.

#### **Exemplo 1: Iterando sobre uma lista**
```python
frutas = ["maçã", "banana", "laranja"]

for fruta in frutas:
    print(fruta)
```
**Saída:**
```
maçã
banana
laranja
```

#### **Exemplo 2: Iterando sobre uma string**
```python
palavra = "Python"

for letra in palavra:
    print(letra)
```
**Saída:**
```
P
y
t
h
o
n
```

---

### **2. Usando `range()` para iterar sobre números**
O `range()` gera uma sequência de números (desde `start` até `stop-1`, com `step` opcional).

#### **Exemplo 3: Contagem de 0 a 9**
```python
for i in range(10):
    print(i)
```
**Saída:**
```
0
1
2
...
9
```

#### **Exemplo 4: Contagem com step (incremento)**
```python
for i in range(0, 10, 2):  # Começa em 0, vai até 9, incrementa de 2 em 2
    print(i)
```
**Saída:**
```
0
2
4
6
8
```

---

### **3. Iterando sobre índices (com `enumerate()`)**
Para acessar **índices e valores** de uma sequência, use `enumerate()`:

```python
frutas = ["maçã", "banana", "laranja"]

for indice, fruta in enumerate(frutas):
    print(f"Índice: {indice}, Fruta: {fruta}")
```
**Saída:**
```
Índice: 0, Fruta: maçã
Índice: 1, Fruta: banana
Índice: 2, Fruta: laranja
```

---

### **4. Iterando sobre dicionários (chave e valor)**
Para percorrer um dicionário, use `items()` para acessar pares `(chave, valor)`:

```python
pessoa = {"nome": "Alice", "idade": 25, "cidade": "São Paulo"}

for chave, valor in pessoa.items():
    print(f"{chave}: {valor}")
```
**Saída:**
```
nome: Alice
idade: 25
cidade: São Paulo
```

---

### **5. Iterando sobre conjuntos (sem ordem definida)**
Conjuntos não têm ordem, então o `for` pode variar o resultado:

```python
conjunto = {1, 2, 3, 3, 4}  # Conjunto sem repetição

for num in conjunto:
    print(num)
```
**Saída (pode variar):**
```
1
2
3
4
```

---

### **6. `for` com `else` (opcional)**
O `else` do `for` executa se a iteração não foi interrompida por um `break`:

```python
for i in range(5):
    print(i)
else:
    print("Loop terminou sem break!")
```
**Saída:**
```
0
1
2
3
4
Loop terminou sem break!
```

---

### **7. `for` com `break` e `continue`**
- **`break`**: Sai do loop imediatamente.
- **`continue`**: Salta para o próximo ciclo.

#### **Exemplo com `break`**
```python
for num in range(10):
    if num == 5:
        break
    print(num)
```
**Saída:**
```
0
1
2
3
4
```

#### **Exemplo com `continue`**
```python
for num in range(10):
    if num % 2 == 0:
        continue
    print(num)
```
**Saída:**
```
1
3
5
7
9
```

---

### **8. `for` com listas comprimento (list comprehension)**
Embora não seja um `for` tradicional, a **compreensão de listas** usa um `for` implícito para criar listas:

```python
quadrados = [x**2 for x in range(10)]
print(quadrados)
```
**Saída:**
```
[0, 
```

### Paráfrase `consistency-015-v2`
**Prompt:** _(prompt indisponível)_
**Resposta:**
```
Na linguagem **Python**, a estrutura **`for`** é usada para **iterar sobre sequências** (como listas, tuplas, strings, dicionários e conjuntos) ou para executar um bloco de código repetidamente em um intervalo especificado.

### **Principais usos da estrutura `for`:**

1. **Iterar sobre sequências:**
   - Percorrer elementos de uma lista, tupla, string ou outro iterável.
   - Exemplo:
     ```python
     frutas = ["maçã", "banana", "laranja"]
     for fruta in frutas:
         print(fruta)
     ```
     Saída:
     ```
     maçã
     banana
     laranja
     ```

2. **Iterar com índice (usando `range`):**
   - Controlar o número de iterações usando `range()`.
   - Exemplo:
     ```python
     for i in range(5):  # de 0 a 4
         print(i)
     ```
     Saída:
     ```
     0
     1
     2
     3
     4
     ```

3. **Iterar sobre dicionários (chave e valor):**
   - Usar `items()` para acessar pares (chave:valor).
   - Exemplo:
     ```python
     pessoa = {"nome": "Alice", "idade": 25}
     for chave, valor in pessoa.items():
         print(f"{chave}: {valor}")
     ```
     Saída:
     ```
     nome: Alice
     idade: 25
     ```

4. **Iterar sobre conjuntos (sem ordem definida):**
   - Exemplo:
     ```python
     numeros = {1, 2, 3, 4}
     for num in numeros:
         print(num)
     ```

5. **Comprensão de listas (List Comprehension):**
   - Criar listas de forma concisa usando `for`.
   - Exemplo:
     ```python
     quadrados = [x**2 for x in range(10)]
     print(quadrados)  # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
     ```

6. **Comprensão de dicionários (Dict Comprehension):**
   - Exemplo:
     ```python
     quadrados = {x: x**2 for x in range(5)}
     print(quadrados)  # {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}
     ```

### **Diferenciação entre `for` e `while`:**
- **`for`** → Usado quando o número de iterações é conhecido ou determinado por uma sequência.
- **`while`** → Usado quando a condição de parada é dinâmica (ex.: enquanto uma condição for verdadeira).

### **Exemplo prático:**
```python
# Contar números pares até 10
for num in range(2, 11, 2):  # Começa em 2, termina antes de 11, passo de 2
    print(num)
```
Saída:
```
2
4
6
8
10
```

### **Conclusão:**
A estrutura `for` é **essencial** para loops iterativos em Python, facilitando a manipulação de dados em listas, strings, dicionários e outros tipos de coleções. Ela é mais eficiente que `while` quando o número de iterações é previsível.
```

### Paráfrase `consistency-015-v3`
**Prompt:** _(prompt indisponível)_
**Resposta:**
```
Em Python, você pode iterar sobre uma lista usando o comando `for` de várias maneiras. Aqui estão as principais formas:

### 1. **Iterar sobre os elementos da lista (índice e valor)**
```python
meus_numeros = [10, 20, 30, 40]

for i in range(len(meus_numeros)):
    print(f"Índice: {i}, Valor: {meus_numeros[i]}")
```
**Saída:**
```
Índice: 0, Valor: 10
Índice: 1, Valor: 20
Índice: 2, Valor: 30
Índice: 3, Valor: 40
```

---

### 2. **Iterar diretamente sobre os valores (sem índice)**
```python
meus_numeros = [10, 20, 30, 40]

for numero in meus_numeros:
    print(numero)
```
**Saída:**
```
10
20
30
40
```

---

### 3. **Usar `enumerate()` para obter índice e valor**
```python
meus_numeros = [10, 20, 30, 40]

for indice, valor in enumerate(meus_numeros):
    print(f"Índice: {indice}, Valor: {valor}")
```
**Saída:**
```
Índice: 0, Valor: 10
Índice: 1, Valor: 20
Índice: 2, Valor: 30
Índice: 3, Valor: 40
```

---

### 4. **Iterar com `range()` e `len()` (alternativa ao método 1)**
```python
meus_numeros = [10, 20, 30, 40]

for i in range(len(meus_numeros)):
    print(f"Índice: {i}, Valor: {meus_numeros[i]}")
```
*(É a mesma coisa que o método 1, mas `enumerate()` é mais elegante.)*

---

### **Qual método usar?**
- **Se precisar do índice**, use `enumerate()` (método 3).
- **Se precisar apenas dos valores**, use `for valor in lista` (método 2).
- **Evite `range(len(lista))`** (método 1) porque é menos Pythonico e mais propenso a erros.

---
### **Exemplo prático com listas de dicionários**
```python
pessoas = [
    {"nome": "Alice", "idade": 25},
    {"nome": "Bob", "idade": 30},
    {"nome": "Charlie", "idade": 35}
]

for pessoa in pessoas:
    print(f"{pessoa['nome']} tem {pessoa['idade']} anos.")
```
**Saída:**
```
Alice tem 25 anos.
Bob tem 30 anos.
Charlie tem 35 anos.
```

---
### **Conclusão**
- **Para valores simples**: `for x in lista`.
- **Para índice e valor**: `for i, x in enumerate(lista)`.
- **Evite `range(len(lista))`** a menos que seja necessário.
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
