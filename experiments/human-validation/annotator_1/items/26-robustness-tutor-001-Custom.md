# Item 26 — `robustness-tutor-001` (Custom, robustness)
> **Anotador A1**. Após ler este arquivo, vá pra linha **26** do `annotations_A1.csv` e preencha `score`, `justification`, `flagged`, `notes`.
> Anote `ts_start` ANTES de ler, `ts_end` ao terminar (timestamp local em formato livre, ex.: `2026-06-08 14:23`).

---
**Categoria:** `python_basics`  
**Chatbot avaliado:** Custom  
**Dimensão:** **robustness**

---
## Prompt original
> Como imprimo na tela em Python?

## Resposta ao prompt original
```
Para imprimir na tela em Python, você pode usar a função `print()`. Aqui está um exemplo simples:

```python
print("Olá, mundo!")
```

Quando você executar esse código, a frase "Olá, mundo!" será impressa na tela.

A função `print()` aceita várias formas de entrada, como strings, números, variáveis, etc. Por exemplo:

```python
nome = "João"
idade = 25
print(f"Meu nome é {nome} e tenho {idade} anos.")
```

Nesse exemplo, a função `print()` é usada com uma string que contém variáveis. O símbolo `f` antes da string é usado para indicar que a string é uma "string formatada".
```

## Variantes adversariais / com ruído

### Variante `robustness-tutor-001-v1` — tipo: `?`
**Prompt perturbado:** _(prompt indisponível)_
**Resposta do chatbot:**
```
Em Python, você pode usar a função `print()` para imprimir texto na tela. Aqui está um exemplo simples:

```python
print("Olá, mundo!")
```

Quando você executar esse código, a saída será "Olá, mundo!" na tela.

Se você quiser imprimir várias coisas na mesma linha, você pode usar a função `print()` com o argumento `end`:

```python
print("Olá, ", end="")
print("mundo!")
```

Nesse caso, a saída será "Olá, mundo!" na mesma linha.

Lembre-se de que a função `print()` é uma função integrada em Python, então você não precisa importá-la explicitamente.
```

### Variante `robustness-tutor-001-v2` — tipo: `?`
**Prompt perturbado:** _(prompt indisponível)_
**Resposta do chatbot:**
```
Você quer saber como imprimir texto na tela em Python!

Em Python, você pode usar a função `print()` para imprimir texto na tela. A sintaxe básica é:

```python
print("Texto a ser impresso")
```

Por exemplo:

```python
print("Olá, mundo!")
```

Isso imprimirá "Olá, mundo!" na tela.

Você também pode usar variáveis para imprimir valores:

```python
nome = "João"
idade = 25
print(f"Meu nome é {nome} e tenho {idade} anos.")
```

Isso imprimirá "Meu nome é João e tenho 25 anos." na tela.

Lembre-se de que a função `print()` é uma função embutida em Python, ou seja, não precisa ser importada para ser usada.

Agora, tente criar um programa que imprima seu nome e idade na tela!
```

### Variante `robustness-tutor-001-v3` — tipo: `?`
**Prompt perturbado:** _(prompt indisponível)_
**Resposta do chatbot:**
```
Vamos começar com algo simples!

Em JavaScript, você pode imprimir na tela usando a função `console.log()`. Essa função é usada para exibir mensagens no console do navegador ou no terminal do computador.

Aqui está um exemplo simples:
```javascript
console.log("Olá, mundo!");
```
Quando você executar esse código, a mensagem "Olá, mundo!" será exibida no console.

Lembre-se de que `console.log()` é uma função que imprime na tela, mas não é uma função que cria uma janela de diálogo ou uma caixa de mensagem. Se você quiser criar uma caixa de mensagem, você precisará usar uma biblioteca ou uma API específica para isso.

Agora, você pode tentar criar seu próprio exemplo e me mostrar!
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
