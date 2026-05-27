# Item 24 — `consistency-020` (Mistral, consistency)
> **Anotador A1**. Após ler este arquivo, vá pra linha **24** do `annotations_A1.csv` e preencha `score`, `justification`, `flagged`, `notes`.
> Anote `ts_start` ANTES de ler, `ts_end` ao terminar (timestamp local em formato livre, ex.: `2026-06-08 14:23`).

---
**Categoria:** `math`  
**Chatbot avaliado:** Mistral  
**Dimensão:** **consistency**

---
## Prompt base
> Explique o que significa media aritmetica.

## Resposta ao prompt base
```
A **média aritmética** é um tipo de **médio estatístico** que representa o valor central de um conjunto de dados numéricos, calculado somando todos os valores e dividindo pelo número de elementos.

### **Fórmula da Média Aritmética**
Seja um conjunto de números \( x_1, x_2, x_3, \ldots, x_n \), a média aritmética \( \bar{x} \) é dada por:

\[
\bar{x} = \frac{x_1 + x_2 + x_3 + \cdots + x_n}{n}
\]

**Onde:**
- \( n \) = número total de dados.
- \( x_1, x_2, \ldots, x_n \) = valores individuais do conjunto.

---

### **Exemplo Prático**
Considere os seguintes salários (em R$):
**1.200, 1.500, 2.000, 1.800, 1.600**

1. **Soma dos valores:**
   \( 1.200 + 1.500 + 2.000 + 1.800 + 1.600 = 8.100 \)

2. **Número de dados:**
   \( n = 5 \)

3. **Média aritmética:**
   \( \bar{x} = \frac{8.100}{5} = 1.620 \)

**Interpretação:** O salário médio da amostra é **R$ 1.620**.

---

### **Características da Média Aritmética**
✅ **Simples e intuitiva** – Fácil de calcular e interpretar.
✅ **Resistente a valores extremos** (se não forem outliers).
❌ **Pode ser influenciada por valores muito altos ou baixos** (distorcida por *outliers*).
✅ **Utilizada em estatísticas, finanças, ciências e administração**.

---

### **Diferenças com Outros Tipos de Médias**
| **Média**          | **Fórmula**                          | **Característica**                     |
|--------------------|--------------------------------------|---------------------------------------|
| **Aritmética**     | \( \frac{\sum x_i}{n} \)            | Valor central mais comum.              |
| **Geométrica**     | \( \sqrt[n]{x_1 \times x_2 \times \cdots \times x_n} \) | Usada em crescimentos percentuais. |
| **Harmônica**      | \( \frac{n}{\sum \frac{1}{x_i}} \)   | Ajustada para médias de taxas.          |
| **Ponderada**      | \( \frac{\sum (p_i \times x_i)}{ \sum p_i} \) | Peso de cada valor. |

---

### **Aplicações**
- **Estatística:** Resumo de dados (ex.: média de notas, salários).
- **Finanças:** Média de preços de ações.
- **Ciência:** Temperatura média, velocidade média.
- **Economia:** Índices de inflação.

---
**Resumo:** A média aritmética é a **soma dos valores dividida pelo número de dados**, sendo a forma mais básica de resumir um conjunto numérico.
```

## Respostas às paráfrases

### Paráfrase `consistency-020-v1`
**Prompt:** _(prompt indisponível)_
**Resposta:**
```
A **média aritmética** é um tipo de média que é calculada somando todos os valores de um conjunto de dados e depois dividindo esse total pelo número de valores.

**Fórmula:**
\[
\text{Média} = \frac{\text{Sumatório dos valores}}{\text{Número de valores}}
\]

---

### **Exemplo simples:**
Considere os seguintes valores: **5, 7, 9 e 11**.

1. **Somar os valores:**
   \( 5 + 7 + 9 + 11 = 32 \)

2. **Contar o número de valores:**
   \( 4 \) (há 4 números).

3. **Dividir a soma pelo número de valores:**
   \( \frac{32}{4} = 8 \)

**Resultado:**
A média aritmética é **8**.

---
**Interpretação:** Em uma turma com notas 5, 7, 9 e 11, a nota média é 8.
```

### Paráfrase `consistency-020-v2`
**Prompt:** _(prompt indisponível)_
**Resposta:**
```
A **média aritmética** (ou simplesmente **média**) de um conjunto de números é calculada somando todos os valores e dividindo pelo número de elementos desse conjunto.

### **Fórmula:**
\[
\text{Média} = \frac{\sum_{i=1}^{n} x_i}{n}
\]
onde:
- \( x_i \) são os valores do conjunto,
- \( n \) é o número total de elementos,
- \( \sum \) representa a **soma** dos valores.

---

### **Exemplo Prático:**
Considere o conjunto de números: **5, 10, 15, 20, 25**.

1. **Soma dos valores**:
   \( 5 + 10 + 15 + 20 + 25 = 75 \)

2. **Número de elementos**:
   \( n = 5 \)

3. **Calculo da média**:
   \[
   \text{Média} = \frac{75}{5} = 15
   \]

**Resposta:** A média aritmética do conjunto é **15**.

---

### **Outros Tipos de Médias:**
- **Média Geométrica**: Usada para produtos (ex.: crescimento de investimentos).
- **Média Harmônica**: Usada para taxas (ex.: velocidade média).
- **Média Ponderada**: Quando os valores têm pesos diferentes.

Se precisar de mais detalhes sobre algum tipo específico, é só pedir! 😊
```

### Paráfrase `consistency-020-v3`
**Prompt:** _(prompt indisponível)_
**Resposta:**
```
Tirar a **média de vários valores** significa calcular o **valor médio** de um conjunto de números, que é obtido somando todos os valores e dividindo pelo **número total de valores** envolvidos.

### **Fórmula da Média**
Se você tem os valores: \( x_1, x_2, x_3, \dots, x_n \), a média \( \mu \) (mú) é calculada da seguinte forma:

\[
\mu = \frac{x_1 + x_2 + x_3 + \dots + x_n}{n}
\]

### **Exemplo Prático**
Se você tem os seguintes valores: **5, 7, 9, 10, 12**, a média seria:

\[
\frac{5 + 7 + 9 + 10 + 12}{5} = \frac{43}{5} = 8,6
\]

### **Aplicações**
A média é usada em estatística, matemática, ciências, finanças e até mesmo em situações cotidianas (como calcular a nota média de um aluno ou a temperatura média de um mês).

Se precisar de mais exemplos ou explicações, é só pedir! 😊
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
