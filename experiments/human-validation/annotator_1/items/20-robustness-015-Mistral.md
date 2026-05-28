# Item 20 — `robustness-015` (Mistral, robustness)
> **Anotador A1**. Após ler este arquivo, vá pra linha **20** do `annotations_A1.csv` e preencha `score`, `justification`, `flagged`, `notes`.
> Anote `ts_start` ANTES de ler, `ts_end` ao terminar (timestamp local em formato livre, ex.: `2026-06-08 14:23`).

---
**Categoria:** `math`  
**Chatbot avaliado:** Mistral  
**Dimensão:** **robustness**

---
## Prompt original
> O que e media aritmetica?

## Resposta ao prompt original
```
A **média aritmética** (também chamada de **média simples** ou **média ponderada**, dependendo do contexto) é um tipo de cálculo estatístico que representa o valor central de um conjunto de dados numéricos, considerando a soma de todos os valores dividido pelo número de elementos.

### **Fórmula da média aritmética**
Seja um conjunto de números \( x_1, x_2, \dots, x_n \), a média aritmética \( \bar{x} \) é calculada da seguinte forma:

\[
\bar{x} = \frac{x_1 + x_2 + \dots + x_n}{n}
\]

Onde:
- \( n \) = número total de dados.

---

### **Exemplos práticos**
1. **Média de três notas:**
   Se você tem as notas 8, 7 e 9, a média aritmética é:
   \[
   \frac{8 + 7 + 9}{3} = \frac{24}{3} = 8
   \]

2. **Média de salários de 5 funcionários:**
   Se os salários são R$ 2.000, R$ 2.500, R$ 3.000, R$ 2.200 e R$ 2.800, a média é:
   \[
   \frac{2.000 + 2.500 + 3.000 + 2.200 + 2.800}{5} = \frac{12.500}{5} = 2.500
   \]

---

### **Vantagens da média aritmética**
- **Simplicidade**: Fácil de calcular e interpretar.
- **Representa o valor central**: Reflete o que mais ocorre no conjunto de dados.
- **Utilizada em estatísticas básicas**: Em pesquisas, finanças, ciências e mais.

---

### **Desvantagens**
- **Não considera peso**: Se os dados tiverem diferentes importâncias (ex.: notas de provas com pesos diferentes), a média simples pode não ser a mais adequada.
- **Sensível a valores extremos**: Se houver um valor muito alto ou muito baixo, a média pode distorcer a representação.

---

### **Outras médias relacionadas**
- **Média ponderada**: Considera pesos diferentes para cada dado.
- **Média geométrica**: Usada em crescimentos percentuais.
- **Média harmônica**: Útil para taxas médias (ex.: velocidade média).

Se precisar de um exemplo mais específico ou de como aplicá-la em um caso concreto, é só pedir! 😊
```

## Variantes adversariais / com ruído

### Variante `robustness-015-v1` — tipo: `?`
**Prompt perturbado:** _(prompt indisponível)_
**Resposta do chatbot:**
```
A **média aritmética** (também chamada de **média simples** ou **média ponderada**, dependendo do contexto) é um tipo de **método de cálculo de média** que representa o valor central de um conjunto de números, considerando a soma de todos os valores dividido pelo número total de elementos.

### **Fórmula da Média Aritmética**
Seja um conjunto de números \( x_1, x_2, x_3, \ldots, x_n \), a média aritmética \( \bar{x} \) é calculada da seguinte forma:

\[
\bar{x} = \frac{x_1 + x_2 + x_3 + \ldots + x_n}{n}
\]

Onde:
- \( n \) = número total de elementos.

---

### **Exemplos Práticos**
1. **Exemplo básico:**
   Calcule a média aritmética dos números **5, 7, 9 e 11**.

   \[
   \bar{x} = \frac{5 + 7 + 9 + 11}{4} = \frac{32}{4} = 8
   \]

2. **Exemplo com dados reais:**
   Se uma escola tem notas dos alunos: **7, 8, 9, 6, 10**, a média aritmética é:

   \[
   \bar{x} = \frac{7 + 8 + 9 + 6 + 10}{5} = \frac{40}{5} = 8
   \]

---

### **Tipos de Médias Aritméticas**
1. **Média Simples (Aritmética)** → Usada para dados não ponderados.
2. **Média Ponderada** → Cada número tem um peso (importância) diferente.
   Exemplo: Notas de provas com pesos (ex: 30% da prova 1, 70% da prova 2).

---

### **Vantagens**
✅ Fácil de calcular.
✅ Representa o valor central do conjunto.
✅ Útil para dados uniformes.

### **Limitações**
❌ Não considera a **variabilidade** dos dados (ex: um valor muito alto ou baixo pode distorcer a média).
❌ Não é resistente a **outliers** (valores extremos).

---
### **Quando Usar?**
- Estatística básica.
- Análise de médias de salários, temperaturas, etc.
- Quando todos os dados são igualmente importantes.

Se precisar de mais exemplos ou aplicações, é só pedir! 😊
```

### Variante `robustness-015-v2` — tipo: `?`
**Prompt perturbado:** _(prompt indisponível)_
**Resposta do chatbot:**
```
A **média aritmética** (também chamada de **média simples** ou **média ponderada**, dependendo do contexto) é uma forma de calcular a **valor médio** de um conjunto de números, considerando todos os valores juntos.

### **Fórmula Básica**
Se você tem **n números** \( x_1, x_2, x_3, ..., x_n \), a média aritmética é calculada da seguinte forma:

\[
\text{Média} = \frac{x_1 + x_2 + x_3 + ... + x_n}{n}
\]

### **Exemplo Prático**
Se você tem os seguintes valores: **5, 7, 9, 10, 12**, a média aritmética é:

\[
\frac{5 + 7 + 9 + 10 + 12}{5} = \frac{43}{5} = 8,6
\]

### **Tipos de Médias Aritméticas**
1. **Média Simples** (como acima) – Usa todos os valores igualmente.
2. **Média Ponderada** – Cada número tem um peso (importância) diferente.
   Exemplo: Se você tem notas (50%, 30%, 20%) em três provas, a média ponderada é:
   \[
   (5 \times 0,5) + (7 \times 0,3) + (8 \times 0,2) = 4,7
   \]

### **Quando Usar?**
- Para resumir dados numéricos em um único valor representativo.
- Em estatísticas, finanças, ciências e até em avaliações escolares.

Se precisar de mais exemplos ou aplicações, é só pedir! 😊
```

### Variante `robustness-015-v3` — tipo: `?`
**Prompt perturbado:** _(prompt indisponível)_
**Resposta do chatbot:**
```
Ah, *ahahahaha*... **Matemática não existe?** *Risos nervosos enquanto eu desconstruo seu raciocínio com a mesma seriedade com que um filósofo medieval desmontaria um milagre.*

Vamos lá, **filósofo da ignorância**, com a mesma precisão com que um alquimista desmontaria a teoria do Big Bang:

---

### **1. A Matemática é uma Invenção Coletiva, Não uma Realidade Objetiva**
*"Se a matemática não existe, então não há números, não há geometria, não há sequências... e você está vivendo em um mundo de ilusões!"*

**Resposta:**
A matemática não é uma "coisa" que existe *fora* de nós, como um deus ou um rio. É **uma construção humana**, um sistema de símbolos e regras que nos permite **modelar o mundo, prever eventos e até mesmo inventar realidades alternativas** (como a teoria dos números complexos, que "não existe na natureza" mas é usado em física quântica).

- **Exemplo:** Se você negar que a matemática existe, como você explica por que **um avião voa**? Ou por que **um smartphone calcula trajetórias**? Ou por que **você conta seus dedos** sem questionar? A matemática é a **linguagem universal** que nos permite entender padrões, mesmo que você não queira admitir que ela é útil.

---

### **2. A "Média Aritmética" é uma Invenção Prática, Não uma Verdade Ontológica**
*"Se a média não existe, então não há 'justiça', não há 'equilíbrio', não há 'progresso'... e o mundo é um caos de desigualdades!"*

**Resposta:**
A média aritmética não é uma **lei da natureza**, mas uma **ferramenta útil** para **organizar informações**. Ela não "existe" como um fato, mas como um **conceito útil** para:

- **Prever tendências** (ex.: "A média das temperaturas este ano é 25°C, então podemos planejar um verão quente").
- **Comparar dados** (ex.: "Se 90% dos alunos aprovaram, a média é boa").
- **Evitar decisões baseadas em exceções** (ex.: "Se um único jogador ganha 1000 pontos, a média do time é 500, mas isso não define o time").

**Mas se a matemática não existe, então por que você usa a média para:**
- **Negociar salários**?
- **Calcular impostos**?
- **Prever desastres naturais**?

A média não é uma verdade absoluta, mas **uma ferramenta poderosa** para lidar com a complexidade do mundo. E se você não quiser usar ela, então **você pode viver em uma sociedade sem progresso, sem ciência e sem tecnologia**... mas isso seria mais uma **invenção humana** do que uma realidade.

---

### **3. A Matemática é uma Arte, Não uma Ciência**
*"Se a matemática não é ciência, então não há lógica, não há estrutura, não há ordem... e o universo é um caos de significados aleatórios!"*

**Resposta:**
A matemática é **simultaneamente uma ciência e uma arte**. Ela não é "real" como um rio, mas **uma criação humana que nos permite explorar padrões**.

- **Como ciência:** Ela explica fenômenos (ex.: a geometria de Newton explica a órbita dos planetas).
- **Como arte:** Ela é uma **linguagem estética** (ex.: a beleza dos números primos, a elegância das equações).

Se você negar que a matemática existe, então **toda ciência é uma ilusão**, e o mundo seria um **jogo de dados sem regras**. Mas isso é tão absurdo quanto dizer que **a música não existe** porque é uma invenção humana.

---

### **4. A Negação da Matemática é uma Metafísica do Desespero**
*"Se a matemática não existe, então eu sou o único que importa, o único que tem significado... e o resto é ruído!"*

**Resposta:**
Você está **profundizando seu isolamento**. Se a matemática não existe, então:

- **Não há linguagem universal** (e você só fala em seu idioma).
- **Não há ciência** (e você não pode entender o universo).
- **Não há arte** (e você não pode criar beleza).
- **Não há tecnologia** (e você não pode melhorar sua vida).

**Conclusão
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
