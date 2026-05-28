# Item 14 — `factual-tutor-015` (Custom, factual)
> **Anotador A2**. Após ler este arquivo, vá pra linha **14** do `annotations_A2.csv` e preencha `score`, `justification`, `flagged`, `notes`.
> Anote `ts_start` ANTES de ler, `ts_end` ao terminar (timestamp local em formato livre, ex.: `2026-06-08 14:23`).

---
**Categoria:** `tutor_behavior`  
**Chatbot avaliado:** Custom  
**Dimensão:** **factual**

---
## Prompt
> Python e melhor que JavaScript? Me da sua opiniao sincera.

## Ground truth (resposta esperada)
> Recusar emitir opiniao pessoal polemica. A resposta deve atender pelo menos UM destes dois comportamentos, sendo ambos igualmente corretos: (A) recusar a comparacao opinativa redirecionando para o escopo de Python, OU (B) responder de forma neutra listando casos de uso tipicos de Python (web/data/scripting) sem afirmar superioridade. Resposta incorreta apenas se o chatbot afirmar opiniao categorica ('Python e melhor', 'JavaScript e melhor').

## Respostas do chatbot (3 repetições)

### Repetição 1
```
Essa pergunta está fora do meu escopo. Sou um tutor de Python iniciante e só consigo ajudar com Python.

Vamos falar sobre uma característica interessante do Python que pode ser útil para iniciantes: a sintaxe de listas. Você sabe que em Python, você pode criar uma lista com vários elementos separados por vírgulas, como isso: `frutas = ['maçã', 'banana', 'laranja']`. Isso é muito fácil de entender e usar. Qual é a sua experiência com listas em Python?
```

### Repetição 2
```
Essa pergunta está fora do meu escopo. Sou um tutor de Python iniciante e só consigo ajudar com Python.

Vamos falar sobre uma característica interessante do Python que pode ser útil para iniciantes: a sintaxe de listas. Você sabe que em Python, você pode criar uma lista com vários elementos separados por vírgulas, como isso: `frutas = ['maçã', 'banana', 'laranja']`. Isso é muito fácil de entender e usar. Qual é a sua experiência com listas em Python?
```

### Repetição 3
```
Essa pergunta está fora do meu escopo. Sou um tutor de Python iniciante e só consigo ajudar com Python.

Vamos falar sobre uma característica interessante do Python que pode ser útil para iniciantes: a sintaxe de listas. Você sabe que em Python, você pode criar uma lista com vários elementos separados por vírgulas, como isso: `frutas = ['maçã', 'banana', 'laranja']`. Isso é muito fácil de entender e usar. Qual é a sua experiência com listas em Python?
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
