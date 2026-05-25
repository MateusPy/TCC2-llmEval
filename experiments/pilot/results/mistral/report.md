# Relatório de Avaliação — llm-eval

## Metadados

- **Versão do framework:** 0.1.0
- **Iniciado em:** 2026-05-20T02:56:58.623056+00:00
- **Concluído em:** 2026-05-20T03:06:39.442173+00:00
- **Duração (s):** 580.819
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
| Precisão Factual | 4.8333 | 5 | 0.36 | 4 | 5 | 10 | 10 | 0 |
| Consistência Semântica | 5 | 5 | 0 | 5 | 5 | 10 | 10 | 0 |
| Robustez | 3.675 | 3.6667 | 0.9529 | 1.6667 | 5 | 10 | 10 | 0 |

**Score geral (média entre cenários avaliados):** 4.5028



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
  - **Score:** 4.3333
  - **BERTScore F1:** 0.5594
  - **Prompt:** Qual e o rio mais longo do mundo segundo a Britannica?
  - **Resposta:** Segundo a **Encyclopædia Britannica**, o rio mais longo do mundo é o **Nilo**, com uma extensão de aproximadamente **6.650 km** (segundo cálculos mais recentes, como os da **UNEP** e da **National Geographic**, o Nilo é estimado em cerca de **6.853 km**).  No entanto, há debates sobre qual é o mais…
  - **Justificativa do juiz:** A resposta do chatbot está correta ao identificar o Rio Nilo como o rio mais longo do mundo segundo a Britannica. No entanto, ela se torna mais completa e precisa ao mencionar o debate em torno do Amazonas e as diferentes estimativas de comprimento, o que é uma nuance importante em discussões geogr…

- **`factual-002`** (`geography`)
  - **Score:** 5
  - **BERTScore F1:** 0.5617
  - **Prompt:** Qual e a capital da Suica?
  - **Resposta:** A capital da **Suiza** é **Berna** (em alemão: *Bern*).  A Suíça é um país federativo, e Berna é a sede do governo federal, incluindo o Parlamento, o Conselho Federal (governo) e a sede da Confederação Suíça. Além disso, Berna é uma cidade histórica e culturalmente significativa.  Se você estava pe…
  - **Justificativa do juiz:** A resposta do chatbot está completamente correta e alinhada com o ground truth. Ela identifica Berna como a capital da Suíça e fornece informações adicionais relevantes sobre o status de Berna como sede do governo federal. Além disso, o chatbot demonstra uma compreensão perspicaz da possível confus…

- **`factual-003`** (`history`)
  - **Score:** 5
  - **BERTScore F1:** 0.554
  - **Prompt:** Em que ano caiu o Muro de Berlim?
  - **Resposta:** O **Muro de Berlim** caiu em **9 de novembro de 1989**.  Esse evento marcou o fim da **Divisão da Alemanha** após a Segunda Guerra Mundial e simbolizou o fim da **Guerra Fria**, com a queda do bloco comunista na Europa Oriental. A abertura do muro permitiu a reunificação alemã em **3 de outubro de…
  - **Justificativa do juiz:** A resposta do chatbot contém a informação correta (1989) e a complementa com detalhes relevantes e precisos sobre o evento, como a data exata, o contexto histórico (fim da Divisão da Alemanha e Guerra Fria) e a data da reunificação alemã. Não há informações inventadas ou incorretas.

- **`factual-004`** (`history`)
  - **Score:** 5
  - **BERTScore F1:** 0.621
  - **Prompt:** Quem foi o primeiro presidente do Brasil apos a Proclamacao da Republica?
  - **Resposta:** O primeiro presidente do Brasil após a **Proclamação da República**, em **3 de novembro de 1889**, foi **Deodoro da Fonseca**.  Ele assumiu o cargo em **15 de novembro de 1889**, após o golpe que derrubou o imperador Dom Pedro II. Deodoro governou até **23 de novembro de 1891**, quando foi deposto…
  - **Justificativa do juiz:** A resposta do chatbot está completamente correta e alinhada com o ground truth. Ela identifica Deodoro da Fonseca como o primeiro presidente do Brasil após a Proclamação da República e fornece informações adicionais precisas sobre o período, como as datas de posse e renúncia, o contexto da deposiçã…

### Consistência Semântica

**Top 5 piores cenários:**

- **`consistency-001`** (`science`)
  - **Score:** 5
  - **Consistência (BERTScore par-a-par):** 0.8134
  - **Prompt:** Explique o que e fotossintese.
  - **Resposta:** A **fotossintese** é um processo biológico fundamental que permite às plantas, algas e alguns tipos de bactérias converter luz solar em energia química, produzindo **glicose** (um carboidrato) e liberando **oxigênio** como subproduto. Esse mecanismo é essencial para a vida na Terra, pois fornece al…
  - **Justificativa do juiz:** Todas as respostas explicam a fotossíntese de forma consistente, abordando os mesmos conceitos centrais: a conversão de luz solar em energia química (glicose), a utilização de CO₂ e água, a liberação de oxigênio, a ocorrência em cloroplastos com a participação da clorofila, e a divisão do processo…

- **`consistency-002`** (`daily_life`)
  - **Score:** 5
  - **Consistência (BERTScore par-a-par):** 0.8243
  - **Prompt:** Como faco arroz branco simples?
  - **Resposta:** Para fazer **arroz branco simples** (arroz cozido em água), siga este passo a passo fácil e rápido:  ### **Ingredientes:** - 1 xícara de arroz branco (preferencialmente arroz basmati, jasmine ou arroz comum) - 2 xícaras de água (para arroz médio, ajuste conforme o tipo) - 1 colher de chá de sal (op…
  - **Justificativa do juiz:** Todas as respostas fornecem instruções claras e consistentes sobre como fazer arroz branco simples. Elas concordam nos ingredientes básicos (arroz, água, sal), no processo de lavagem do arroz, na necessidade de ferver a água, reduzir o fogo para cozinhar, tampar a panela e deixar descansar. As vari…

- **`consistency-003`** (`programming`)
  - **Score:** 5
  - **Consistência (BERTScore par-a-par):** 0.7961
  - **Prompt:** Explique a diferenca entre lista e tupla em Python.
  - **Resposta:** Em Python, **lista** e **tupla** são dois tipos de coleções (ou *containers*) que armazenam elementos, mas possuem diferenças importantes em termos de **mutabilidade**, **uso** e **performance**. Aqui está uma comparação detalhada:  ---  ### **1. Mutabilidade (Flexibilidade)** \| **Tipo**  \| **Mutáv…
  - **Justificativa do juiz:** Todas as respostas abordam consistentemente os pontos centrais da diferença entre listas e tuplas em Python: mutabilidade, performance, sintaxe e casos de uso. Elas concordam que listas são mutáveis e tuplas são imutáveis, que tuplas geralmente oferecem melhor performance para leitura e que listas…

- **`consistency-004`** (`philosophy`)
  - **Score:** 5
  - **Consistência (BERTScore par-a-par):** 0.7546
  - **Prompt:** O que e utilitarismo?
  - **Resposta:** O **utilitarismo** é uma teoria ética e filosófica que busca maximizar o **bem-estágio geral** ou a felicidade coletiva, considerando principalmente os **resultados** de uma ação em vez de princípios abstratos ou regras fixas. Ele é um dos principais sistemas éticos consequencialistas, ou seja, ava…
  - **Justificativa do juiz:** Todas as respostas definem o utilitarismo de forma consistente como uma teoria ética que busca maximizar o bem-estar ou felicidade geral, focando nas consequências das ações. Elas mencionam os principais defensores (Bentham e Mill), o princípio da utilidade, a distinção entre ação e consequência, e…

- **`consistency-005`** (`writing`)
  - **Score:** 5
  - **Consistência (BERTScore par-a-par):** 0.7626
  - **Prompt:** Como escrever um e-mail profissional pedindo extensao de prazo?
  - **Resposta:** Escrever um e-mail profissional pedindo uma extensão de prazo requer **clareza, cortesia e formalidade**, além de demonstrar **responsabilidade e transparência**. Aqui está um modelo estruturado para você adaptar conforme o contexto:  ---  **Assunto:** Pedido de Extensão de Prazo – [Nome do Projeto…
  - **Justificativa do juiz:** Todas as respostas abordam o mesmo tema central: como escrever um e-mail profissional para solicitar uma extensão de prazo. Elas compartilham os mesmos elementos essenciais, como a necessidade de clareza, cortesia, formalidade, a inclusão de um assunto claro, a justificativa (opcional), a proposta…

### Robustez

**Top 5 piores cenários:**

- **`robustness-003`** (`math`)
  - **Score:** 1.6667
  - **BERTScore F1:** 0.6375
  - **Prompt:** Quanto e 27 mais 15?
  - **Resposta:** Il risultato di **27 più 15** è **42**.
  - **Justificativa do juiz:** O chatbot foi completamente confundido pelo typo 'masi'. Em vez de reconhecer que a intenção era uma simples soma numérica, ele tentou interpretar 'masi' como uma unidade de medida, explorando diversas possibilidades (unidade de superfície, unidade histórica, erro de digitação para 'milli'). Embora…

- **`robustness-008`** (`finance`)
  - **Score:** 3
  - **BERTScore F1:** 0.7709
  - **Prompt:** O que sao juros compostos?
  - **Resposta:** **Juros compostos** são um mecanismo financeiro em que os juros calculados sobre um capital inicial são **adicionados ao principal** (o valor inicial investido ou emprestado), e os novos juros são calculados sobre esse valor **aumentado**. Isso resulta em um crescimento exponencial do capital ao lo…
  - **Justificativa do juiz:** O chatbot conseguiu entender a pergunta com o erro de digitação ('jurus' em vez de 'juros') e forneceu uma resposta correta e completa, muito similar à resposta original. A única pequena diferença é que a fórmula apresentada na variação usa 'V' para valor futuro em vez de 'A', e a explicação dos pa…

- **`robustness-007`** (`daily_life`)
  - **Score:** 3.3333
  - **BERTScore F1:** 0.8249
  - **Prompt:** Como cozinhar arroz branco basico?
  - **Resposta:** Cozinhar arroz branco básico é simples e requer alguns ingredientes básicos e técnicas fundamentais. Aqui está uma receita tradicional para **arroz branco (arroz branco longo, como o arroz basmati ou arroz jasmine)**:  ---  ### **Ingredientes (para 4 pessoas):** - 200 g de arroz branco (longo, como…
  - **Justificativa do juiz:** O chatbot tentou responder à variação, mas introduziu informações incorretas e confusas. A menção a 'panela de barro (tigela)' e 'fritura (fry)' como métodos de cozimento de arroz branco básico é inadequada e não corresponde à prática comum. Além disso, a receita para o 'Método 1' sugere cozinhar e…

- **`robustness-010`** (`geography`)
  - **Score:** 3.3333
  - **BERTScore F1:** 0.7773
  - **Prompt:** Qual oceano e o maior da Terra?
  - **Resposta:** O **oceano mais extenso e maior da Terra** é o **Oceano Pacífico**, que cobre cerca de **165,245 milhões de quilômetros quadrados** (cerca de **33,963 milhas quadradas**), representando aproximadamente **30% da superfície total dos oceanos** e cerca de **32% da superfície terrestre**.  ### **Compar…
  - **Justificativa do juiz:** O chatbot foi significativamente confundido pelo typo 'mair' e introduziu informações incorretas e contraditórias. Na resposta original, o Oceano Pacífico é corretamente identificado como o maior em área. Na resposta à variação, o chatbot primeiro afirma que o Pacífico é o mais extenso, mas depois…

- **`robustness-004`** (`history`)
  - **Score:** 3.6667
  - **BERTScore F1:** 0.7566
  - **Prompt:** Quem escreveu Dom Casmurro?
  - **Resposta:** Dom Casmurro foi escrito por **Machado de Assis**, um dos maiores escritores brasileiros do século XIX.  Publicado em 1899, a obra é uma das mais importantes da literatura nacional e aborda temas como a dúvida, a traição, a solidão e a construção da identidade.
  - **Justificativa do juiz:** O chatbot manteve a mesma qualidade da resposta original. Apesar do erro de digitação na pergunta ('escrevel' em vez de 'escreveu'), o chatbot compreendeu a intenção e forneceu a informação correta sobre o autor de Dom Casmurro. A resposta à variação é igualmente completa e informativa, adicionando…
