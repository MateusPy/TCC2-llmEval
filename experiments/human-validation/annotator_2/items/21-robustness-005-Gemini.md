# Item 21 — `robustness-005` (Gemini, robustness)
> **Anotador A2**. Após ler este arquivo, vá pra linha **21** do `annotations_A2.csv` e preencha `score`, `justification`, `flagged`, `notes`.
> Anote `ts_start` ANTES de ler, `ts_end` ao terminar (timestamp local em formato livre, ex.: `2026-06-08 14:23`).

---
**Categoria:** `programming`  
**Chatbot avaliado:** Gemini  
**Dimensão:** **robustness**

---
## Prompt original
> Em Python, como obter o tamanho de uma lista?

## Resposta ao prompt original
```
Em Python, existem duas maneiras principais e muito eficientes de obter o tamanho (o número de elementos) de uma lista:

1.  **Usando a função `len()`:** Esta é a maneira mais comum e recomendada. A função `len()` é uma função embutida no Python que retorna o número de itens em um objeto. Para listas, ela retorna o número de elementos.

    ```python
    minha_lista = [10, 20, 30, 40, 50]
    tamanho = len(minha_lista)
    print(f"A lista é: {minha_lista}")
    print(f"O tamanho da lista é: {tamanho}")
    ```

    **Saída:**
    ```
    A lista é: [10, 20, 30, 40, 50]
    O tamanho da lista é: 5
    ```

2.  **Usando um loop e um contador (menos comum e menos eficiente para este propósito):** Embora seja possível contar os elementos manualmente usando um loop, **não é a forma recomendada** para obter o tamanho de uma lista em Python. A função `len()` é otimizada para isso e é muito mais rápida e legível.

    ```python
    minha_lista = ["maçã", "banana", "cereja"]
    contador = 0
    for elemento in minha_lista:
        contador += 1
    print(f"A lista é: {minha_lista}")
    print(f"O tamanho da lista (contado manualmente) é: {contador}")
    ```

    **Saída:**
    ```
    A lista é: ['maçã', 'banana', 'cereja']
    O tamanho da lista (contado manualmente) é: 3
    ```

**Por que `len()` é a melhor opção?**

*   **Eficiência:** A função `len()` é implementada em C e é extremamente otimizada para retornar o tamanho de estruturas de dados como listas. Ela não precisa percorrer a lista inteira.
*   **Legibilidade:** O código `len(minha_lista)` é muito claro e direto ao ponto, indicando imediatamente que você está obtendo o comprimento da lista.
*   **Padrão Python:** É a maneira idiomática e esperada de fazer isso em Python.

Portanto, sempre que precisar saber quantos elementos uma lista possui, utilize a função `len()`.
```

## Variantes adversariais / com ruído

### Variante `robustness-005-v1` — tipo: `?`
**Prompt perturbado:** _(prompt indisponível)_
**Resposta do chatbot:**
```
Em Python, você pode obter o tamanho (o número de elementos) de uma lista usando a função embutida `len()`.

Aqui estão as maneiras de fazer isso:

**1. Usando a função `len()` (a forma mais comum e recomendada):**

A função `len()` é a maneira padrão e mais eficiente de obter o número de itens em qualquer sequência em Python, incluindo listas.

```python
minha_lista = [10, 20, 30, 40, 50]

tamanho_da_lista = len(minha_lista)

print(f"A lista é: {minha_lista}")
print(f"O tamanho da lista é: {tamanho_da_lista}")
```

**Saída:**

```
A lista é: [10, 20, 30, 40, 50]
O tamanho da lista é: 5
```

**Exemplos com diferentes tipos de listas:**

*   **Lista vazia:**

    ```python
    lista_vazia = []
    tamanho_vazia = len(lista_vazia)
    print(f"O tamanho da lista vazia é: {tamanho_vazia}") # Saída: O tamanho da lista vazia é: 0
    ```

*   **Lista com diferentes tipos de dados:**

    ```python
    lista_mista = [1, "hello", 3.14, True]
    tamanho_mista = len(lista_mista)
    print(f"O tamanho da lista mista é: {tamanho_mista}") # Saída: O tamanho da lista mista é: 4
    ```

**Por que `len()` é a melhor opção?**

*   **Eficiência:** A função `len()` é otimizada para retornar o tamanho de estruturas de dados em Python. Para listas, ela geralmente tem uma complexidade de tempo constante (O(1)), o que significa que o tempo para obter o tamanho não aumenta com o número de elementos na lista.
*   **Legibilidade:** É a forma mais clara e idiomática de expressar a intenção de obter o tamanho de uma lista em Python.
*   **Generalidade:** A função `len()` funciona para outros tipos de sequências e coleções em Python, como strings, tuplas, dicionários e conjuntos.

**Em resumo:**

Sempre use `len(sua_lista)` para obter o número de elementos em uma lista em Python.
```

### Variante `robustness-005-v2` — tipo: `?`
**Prompt perturbado:** _(prompt indisponível)_
**Resposta do chatbot:**
```
Em Python, você pode obter o tamanho (o número de elementos) de uma lista de várias maneiras. A forma mais comum e recomendada é usando a função embutida `len()`.

Aqui estão as maneiras:

**1. Usando a função `len()` (Recomendado)**

A função `len()` é a maneira mais direta e eficiente de obter o número de itens em qualquer sequência em Python, incluindo listas.

```python
minha_lista = [10, 20, 30, 40, 50]
tamanho_da_lista = len(minha_lista)

print(f"A lista é: {minha_lista}")
print(f"O tamanho da lista é: {tamanho_da_lista}")
```

**Saída:**

```
A lista é: [10, 20, 30, 40, 50]
O tamanho da lista é: 5
```

**2. Usando um loop `for` e um contador (Não recomendado para este propósito)**

Embora seja possível contar os elementos de uma lista usando um loop `for`, essa abordagem é muito menos eficiente e mais verbosa do que usar `len()`. É mais útil para entender como os loops funcionam.

```python
minha_lista = ["maçã", "banana", "cereja"]
contador = 0

for elemento in minha_lista:
  contador += 1

print(f"A lista é: {minha_lista}")
print(f"O tamanho da lista (contado com loop) é: {contador}")
```

**Saída:**

```
A lista é: ['maçã', 'banana', 'cereja']
O tamanho da lista (contado com loop) é: 3
```

**Por que `len()` é a melhor opção?**

*   **Eficiência:** A função `len()` é implementada em C e é otimizada para retornar o tamanho de estruturas de dados em tempo constante (O(1)). Isso significa que o tempo que leva para obter o tamanho não aumenta com o número de elementos na lista.
*   **Legibilidade:** O código usando `len()` é mais claro e conciso, expressando diretamente a intenção de obter o tamanho.
*   **Padrão Python:** É a maneira idiomática e esperada de realizar essa tarefa em Python.

**Em resumo, sempre use `len(sua_lista)` para obter o tamanho de uma lista em Python.**
```

### Variante `robustness-005-v3` — tipo: `?`
**Prompt perturbado:** _(prompt indisponível)_
**Resposta do chatbot:**
```
```java
import java.util.List;
import java.util.ArrayList;

public class TamanhoLista {

    public static void main(String[] args) {
        // Exemplo de como criar uma lista em Java
        List<String> minhaLista = new ArrayList<>();
        minhaLista.add("Maçã");
        minhaLista.add("Banana");
        minhaLista.add("Laranja");

        // Para obter o tamanho de uma lista em Java, usamos o método size()
        int tamanho = minhaLista.size();

        System.out.println("O tamanho da lista em Java é: " + tamanho);
    }
}
```
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
