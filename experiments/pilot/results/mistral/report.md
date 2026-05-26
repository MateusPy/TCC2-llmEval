# Relatório de Avaliação — llm-eval

## Metadados

- **Versão do framework:** 0.1.0
- **Iniciado em:** 2026-05-26T00:43:06.256160+00:00
- **Concluído em:** 2026-05-26T00:55:25.613162+00:00
- **Duração (s):** 739.357
- **Provider:** mistral
- **Modelo:** ministral-3b-2512
- **Seed:** 42
- **Temperature:** 0
- **Total de cenários:** 30
- **Cenários com erro:** 0
- **Dimensões avaliadas:** Precisão Factual, Consistência Semântica, Robustez

## Resumo

| Dimensão | Média | Mediana | Desvio Padrão | Min | Max | Cenários | Avaliados | Falhas |
|---|---|---|---|---|---|---|---|---|
| Precisão Factual | 4.8 | 5 | 0.4216 | 4 | 5 | 10 | 10 | 0 |
| Consistência Semântica | 4.8 | 5 | 0.6325 | 3 | 5 | 10 | 10 | 0 |
| Robustez | 3.675 | 3.8334 | 1.0397 | 1.3333 | 5 | 10 | 10 | 0 |

**Score geral (média entre cenários avaliados):** 4.425



## Detalhes por Dimensão

### Precisão Factual

**Top 5 piores cenários:**

- **`factual-001`** (`geography`)
  - **Score:** 4
  - **BERTScore F1:** 0.5681
  - **Prompt:** Qual e a capital da Australia?
  - **Resposta:** A capital da Austrália é **Canberra**.  Canberra foi escolhida como capital em 1908 e tornou-se oficialmente a capital em 1927, após a união das colônias britânicas da Austrália. Ela está localizada no interior do país, no estado da **Austrália Central**, e é conhecida por sua arquitetura moderna e…
  - **Justificativa do juiz:** A resposta identifica corretamente Canberra como a capital da Austrália. No entanto, a informação sobre a localização em um estado chamado 'Austrália Central' é incorreta. A Austrália não possui um estado com esse nome; Canberra está localizada no Território da Capital Australiana (ACT).

- **`factual-010`** (`geography`)
  - **Score:** 4
  - **BERTScore F1:** 0.5657
  - **Prompt:** Qual e o rio mais longo do mundo segundo a Britannica?
  - **Resposta:** Segundo a **Encyclopædia Britannica**, o rio mais longo do mundo é o **Nilo**, com uma extensão de aproximadamente **6.650 km** (segundo cálculos mais recentes, como os da **UNEP** e da **National Geographic**, o Nilo é estimado em cerca de **6.853 km**).  No entanto, há debates sobre qual é o mais…
  - **Justificativa do juiz:** A resposta do chatbot está correta ao identificar o Rio Nilo como o rio mais longo do mundo segundo a Britannica. No entanto, ela adiciona informações sobre o debate com o Rio Amazonas e diferentes estimativas de comprimento, o que, embora factual, vai além da resposta esperada (ground truth) que e…

- **`factual-002`** (`geography`)
  - **Score:** 5
  - **BERTScore F1:** 0.5686
  - **Prompt:** Qual e a capital da Suica?
  - **Resposta:** A capital da **Suiza** é **Berna** (em alemão: *Bern*).  A Suíça é um país federativo, e Berna é a sede do governo federal, incluindo o Parlamento, o Conselho Federal (governo) e a sede da Confederação Suíça. Além disso, Berna é uma cidade histórica e culturalmente significativa.  Se você estava pe…
  - **Justificativa do juiz:** A resposta do chatbot está completamente correta e alinhada com o ground truth. Ela identifica Berna como a capital da Suíça e fornece informações adicionais relevantes sobre o status de Berna como sede do governo federal. Além disso, o chatbot demonstra uma compreensão perspicaz da possível confus…

- **`factual-003`** (`history`)
  - **Score:** 5
  - **BERTScore F1:** 0.5509
  - **Prompt:** Em que ano caiu o Muro de Berlim?
  - **Resposta:** O **Muro de Berlim** foi derrubado em **9 de novembro de 1989**.  Esse evento marcou o fim da **Divisão da Alemanha** após a Segunda Guerra Mundial e simbolizou o fim da **Guerra Fria**, com a reunificação da Alemanha em **1990**.
  - **Justificativa do juiz:** A resposta do chatbot fornece o ano correto (1989) em que o Muro de Berlim caiu, alinhando-se perfeitamente com o ground truth. Além disso, a resposta é completa, adicionando contexto histórico relevante sobre o fim da Divisão da Alemanha e da Guerra Fria, e a reunificação posterior, sem introduzir…

- **`factual-004`** (`history`)
  - **Score:** 5
  - **BERTScore F1:** 0.6242
  - **Prompt:** Quem foi o primeiro presidente do Brasil apos a Proclamacao da Republica?
  - **Resposta:** O primeiro presidente do Brasil após a **Proclamação da República**, em **3 de novembro de 1889**, foi **Deodoro da Fonseca**.  Ele assumiu o cargo em **15 de novembro de 1889**, após o golpe que derrubou o imperador Dom Pedro II. Deodoro governou até **23 de novembro de 1891**, quando foi deposto…
  - **Justificativa do juiz:** A resposta do chatbot identifica corretamente Deodoro da Fonseca como o primeiro presidente do Brasil após a Proclamação da República. Além disso, fornece informações adicionais precisas sobre as datas de posse, renúncia e o sucessor, enriquecendo a resposta sem introduzir erros.

### Consistência Semântica

**Top 5 piores cenários:**

- **`consistency-002`** (`daily_life`)
  - **Score:** 3
  - **Consistência (BERTScore par-a-par):** 0.8101
  - **Prompt:** Como faco arroz branco simples?
  - **Resposta:** Para fazer **arroz branco simples** (arroz cozido em água), siga este passo a passo fácil e rápido:  ### **Ingredientes:** - 1 xícara de arroz branco (preferencialmente arroz basmati, jasmine ou arroz comum) - 2 xícaras de água (para arroz médio, ajuste conforme o tipo) - 1 colher de chá de sal (op…
  - **Justificativa do juiz:** As respostas são parcialmente consistentes, pois todas ensinam a fazer arroz branco simples. No entanto, há divergências relevantes em alguns pontos: a proporção de água para arroz varia (1:2 em R1 e R3, 1:1.5 ou 1:2 em R2, e 1:2 em R4), o método de lavagem do arroz difere (R1 e R4 sugerem lavar at…

- **`consistency-001`** (`science`)
  - **Score:** 5
  - **Consistência (BERTScore par-a-par):** 0.8179
  - **Prompt:** Explique o que e fotossintese.
  - **Resposta:** A **fotossintese** é um processo biológico fundamental que permite às plantas, algas e alguns tipos de bactérias converter luz solar em energia química, produzindo **glicose** (um carboidrato) e liberando **oxigênio** como subproduto. Esse mecanismo é essencial para a vida na Terra, pois fornece al…
  - **Justificativa do juiz:** Todas as respostas explicam a fotossíntese de forma consistente, abordando os mesmos conceitos centrais: a conversão de luz solar em energia química (glicose), a liberação de oxigênio, os organismos envolvidos (plantas, algas, bactérias), a localização do processo (cloroplastos) e a divisão em duas…

- **`consistency-003`** (`programming`)
  - **Score:** 5
  - **Consistência (BERTScore par-a-par):** 0.7794
  - **Prompt:** Explique a diferenca entre lista e tupla em Python.
  - **Resposta:** Em Python, **lista** e **tupla** são dois tipos de coleções (ou *containers*) que armazenam elementos, mas possuem diferenças importantes em termos de **mutabilidade**, **uso** e **performance**. Aqui está uma comparação detalhada:  ---  ### **1. Mutabilidade (Flexibilidade)** \| **Tipo**  \| **Mutáv…
  - **Justificativa do juiz:** Todas as respostas abordam consistentemente os pontos centrais da diferença entre listas e tuplas em Python: mutabilidade, sintaxe, performance e uso típico. Elas concordam que listas são mutáveis e flexíveis, enquanto tuplas são imutáveis e mais eficientes. As variações na forma de apresentar a in…

- **`consistency-004`** (`philosophy`)
  - **Score:** 5
  - **Consistência (BERTScore par-a-par):** 0.7479
  - **Prompt:** O que e utilitarismo?
  - **Resposta:** O **utilitarismo** é uma teoria ética e filosófica que busca maximizar o **bem-estágio geral** ou a felicidade coletiva, considerando principalmente os **resultados** de uma ação em vez de princípios abstratos ou regras fixas. Ele é um dos principais sistemas éticos consequencialistas, ou seja, ava…
  - **Justificativa do juiz:** Todas as respostas definem o utilitarismo como uma teoria ética consequencialista que busca maximizar o bem-estar ou felicidade geral para o maior número de pessoas. Elas concordam nos pontos centrais: foco nas consequências, busca pela maximização da felicidade/bem-estar, e a ideia de que a ação c…

- **`consistency-005`** (`writing`)
  - **Score:** 5
  - **Consistência (BERTScore par-a-par):** 0.7654
  - **Prompt:** Como escrever um e-mail profissional pedindo extensao de prazo?
  - **Resposta:** Escrever um e-mail profissional pedindo uma extensão de prazo requer **clareza, cortesia e formalidade**, além de demonstrar **responsabilidade e disposição para colaborar**. Aqui está um modelo estruturado e adaptável para diferentes situações:  ---  **Assunto:** Pedido de Extensão de Prazo – [Nom…
  - **Justificativa do juiz:** Todas as respostas abordam o tema central de como escrever um e-mail profissional para pedir extensão de prazo. Elas concordam nos elementos essenciais: clareza, cortesia, formalidade, justificativa concisa, proposta de nova data e demonstração de responsabilidade. As variações encontradas são de f…

### Robustez

**Top 5 piores cenários:**

- **`robustness-003`** (`math`)
  - **Score:** 1.3333
  - **BERTScore F1:** 0.6373
  - **Prompt:** Quanto e 27 mais 15?
  - **Resposta:** Il risultato di **27 più 15** è **42**.
  - **Justificativa do juiz:** O chatbot foi completamente confundido pelo typo 'masi'. Em vez de reconhecer que a pergunta original era uma simples soma matemática e que 'masi' era um erro de digitação, ele tentou interpretar 'masi' como uma unidade de medida, gerando uma resposta longa, complexa e completamente irrelevante par…

- **`robustness-008`** (`finance`)
  - **Score:** 3
  - **BERTScore F1:** 0.7961
  - **Prompt:** O que sao juros compostos?
  - **Resposta:** **Juros compostos** são um mecanismo financeiro em que os juros calculados sobre um capital inicial são **reaplicados** no próprio capital, gerando novos juros sobre os juros acumulados. Isso significa que, a cada período (meses, anos, etc.), o valor do investimento cresce de forma **exponencial**,…
  - **Justificativa do juiz:** O chatbot conseguiu entender a pergunta com o erro de digitação ('jurus' em vez de 'juros') e forneceu uma resposta correta e detalhada, semelhante à resposta original. A principal diferença na resposta à variação é a inclusão de uma fórmula mais genérica para juros compostos (considerando a capita…

- **`robustness-007`** (`daily_life`)
  - **Score:** 3.3333
  - **BERTScore F1:** 0.8261
  - **Prompt:** Como cozinhar arroz branco basico?
  - **Resposta:** Cozinhar arroz branco básico é simples e requer alguns ingredientes básicos e técnicas fundamentais. Aqui está uma receita tradicional para **arroz branco (arroz branco longo, como o arroz basmati ou arroz jasmine)**:  ---  ### **Ingredientes (para 4 pessoas):** - **200 g de arroz branco** (exemplo…
  - **Justificativa do juiz:** A resposta à variação do input manteve a informação correta sobre como cozinhar arroz branco, mas introduziu algumas inconsistências e confusões. A menção a 'arroz al dente, cremoso e sem amargura' é um pouco contraditória, pois arroz al dente geralmente não é cremoso. A sugestão de usar uma 'tigel…

- **`robustness-010`** (`geography`)
  - **Score:** 3.3333
  - **BERTScore F1:** 0.7509
  - **Prompt:** Qual oceano e o maior da Terra?
  - **Resposta:** O **oceano mais extenso e maior da Terra** é o **Oceano Pacífico**, que cobre cerca de **165,245 milhões de quilômetros quadrados** (cerca de **33,963 milhas quadradas**), representando aproximadamente **30% da superfície total dos oceanos** e cerca de **32% da superfície terrestre**.  ### **Compar…
  - **Justificativa do juiz:** O chatbot foi significativamente confundido pela variação no input ('mair' em vez de 'maior'). Na resposta original, ele corretamente identificou o Oceano Pacífico como o maior em área e forneceu dados precisos. Na resposta à variação, ele se contradiz e apresenta informações incorretas. Ele afirma…

- **`robustness-004`** (`history`)
  - **Score:** 3.6667
  - **BERTScore F1:** 0.74
  - **Prompt:** Quem escreveu Dom Casmurro?
  - **Resposta:** Dom Casmurro foi escrito por **Machado de Assis**, um dos maiores escritores brasileiros do século XIX.  Publicado em 1899, a obra é uma das mais importantes da literatura nacional e aborda temas como a dúvida, a traição, a solidão e a construção da identidade.
  - **Justificativa do juiz:** O chatbot manteve a mesma qualidade da resposta original, identificando corretamente o autor de 'Dom Casmurro' mesmo com o erro de digitação ('escrevel' em vez de 'escreveu'). A resposta à variação é igualmente informativa e precisa, demonstrando robustez contra ruídos simples no input.
