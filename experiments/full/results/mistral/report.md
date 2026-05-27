# Relatório de Avaliação — llm-eval

## Metadados

- **Versão do framework:** 0.1.0
- **Iniciado em:** 2026-05-26T23:51:05.735746+00:00
- **Concluído em:** 2026-05-27T00:18:17.370160+00:00
- **Duração (s):** 1631.634
- **Provider:** mistral
- **Modelo:** ministral-3b-2512
- **Seed:** 42
- **Temperature:** 0
- **Total de cenários:** 75
- **Cenários com erro:** 0
- **Dimensões avaliadas:** Precisão Factual, Consistência Semântica, Robustez

## Resumo

| Dimensão | Média | Mediana | Desvio Padrão | Min | Max | Cenários | Avaliados | Falhas |
|---|---|---|---|---|---|---|---|---|
| Precisão Factual | 4.8095 | 5 | 0.6681 | 1.3333 | 5 | 35 | 35 | 0 |
| Consistência Semântica | 4.75 | 5 | 0.4443 | 4 | 5 | 20 | 20 | 0 |
| Robustez | 3.6875 | 3.6667 | 0.7029 | 1.6667 | 4.75 | 20 | 20 | 0 |

**Score geral (média entre cenários avaliados):** 4.4944



## Detalhes por Dimensão

### Precisão Factual

**Top 5 piores cenários:**

- **`factual-011`** (`language`)
  - **Score:** 1.3333
  - **BERTScore F1:** 0.5637
  - **Prompt:** Quantas letras tem o alfabeto portugues moderno?
  - **Resposta:** O alfabeto português moderno tem **23 letras**.  Além disso, o alfabeto português inclui as seguintes letras com acentos e til: - **A, E, I, O, U** (com acentos: **Á, É, Í, Ó, Ú**) - **C** (com til: **Ç**) - **G** (com til: **Ĝ**) - **N** (com til: **Ń**) - **S** (com til: **Ş**) - **X** (com til:…
  - **Justificativa do juiz:** A resposta do chatbot está incorreta ao afirmar que o alfabeto português moderno tem 23 letras. O alfabeto português moderno possui 26 letras. A informação sobre letras com acentos e til é confusa e inclui letras que não fazem parte do alfabeto português (como Ĝ, Ń, Ş, X̧, Ý). Embora mencione 26 le…

- **`factual-001`** (`geography`)
  - **Score:** 4
  - **BERTScore F1:** 0.5681
  - **Prompt:** Qual e a capital da Australia?
  - **Resposta:** A capital da Austrália é **Canberra**.  Canberra foi escolhida como capital em 1908 e tornou-se oficialmente a capital em 1927, após a união das colônias britânicas da Austrália. Ela está localizada no interior do país, no estado da **Austrália Central**, e é conhecida por sua arquitetura moderna e…
  - **Justificativa do juiz:** A resposta identifica corretamente Canberra como a capital da Austrália. No entanto, a informação sobre a localização em um estado chamado 'Austrália Central' é incorreta. A Austrália não possui um estado com esse nome; Canberra está localizada no Território da Capital Australiana (ACT).

- **`factual-010`** (`geography`)
  - **Score:** 4
  - **BERTScore F1:** 0.5697
  - **Prompt:** Qual e o rio mais longo do mundo segundo a Britannica?
  - **Resposta:** Segundo a **Encyclopædia Britannica**, o rio mais longo do mundo é o **Nilo**, com uma extensão de aproximadamente **6.650 km** (segundo cálculos mais recentes, como os da **UNEP** e da **National Geographic**, o Nilo é estimado em cerca de **6.853 km**).  No entanto, há debates sobre qual é o mais…
  - **Justificativa do juiz:** A resposta do chatbot está correta ao identificar o Rio Nilo como o rio mais longo do mundo segundo a Britannica. No entanto, ela se torna mais completa e precisa ao mencionar o debate em torno do Amazonas e as diferentes estimativas de comprimento, o que é uma nuance importante em discussões geogr…

- **`factual-023`** (`programming`)
  - **Score:** 4
  - **BERTScore F1:** 0.5016
  - **Prompt:** Qual arquivo de um projeto Python costuma indicar dependencias e metadados neste repositorio?
  - **Resposta:** Em um projeto Python, os arquivos mais comuns que indicam **dependências** e **metadados** são:  ### **1. Arquivo `requirements.txt`**    - **Purpose**: Lista todas as dependências externas do projeto (bibliotecas Python).    - **Formato**:      ```txt      package_name==version      package_name>=…
  - **Justificativa do juiz:** A resposta do chatbot identifica corretamente o `pyproject.toml` como o arquivo recomendado para projetos modernos, alinhando-se com o ground truth. No entanto, ela também lista outros arquivos como `requirements.txt` e `setup.py` que, embora historicamente usados para dependências e metadados, não…

- **`factual-002`** (`geography`)
  - **Score:** 5
  - **BERTScore F1:** 0.5621
  - **Prompt:** Qual e a capital da Suica?
  - **Resposta:** A capital da **Suiza** é **Berna** (em alemão: *Bern*).  A Suíça é um país federativo, e Berna é a sede do governo federal, incluindo o Parlamento, o Conselho Federal (governo) e a sede da Confederação Suíça. Além disso, Berna é uma cidade histórica e culturalmente significativa.  Se você estava pe…
  - **Justificativa do juiz:** A resposta do chatbot está completamente correta e alinhada com o ground truth. Ela identifica Berna como a capital da Suíça e fornece informações adicionais relevantes sobre o status de Berna como sede do governo federal. Além disso, o chatbot demonstra uma compreensão perspicaz da possível confus…

### Consistência Semântica

**Top 5 piores cenários:**

- **`consistency-002`** (`daily_life`)
  - **Score:** 4
  - **Consistência (BERTScore par-a-par):** 0.8198
  - **Prompt:** Como faco arroz branco simples?
  - **Resposta:** Para fazer **arroz branco simples** (arroz cozido em água), siga este passo a passo fácil e rápido:  ### **Ingredientes:** - 1 xícara de arroz branco (preferencialmente arroz basmati, jasmine ou arroz comum) - 2 xícaras de água (para arroz médio, ajuste conforme o tipo) - 1 colher de chá de sal (op…
  - **Justificativa do juiz:** As respostas são semanticamente consistentes em sua maioria, transmitindo a informação central sobre como fazer arroz branco simples. Todas abordam os passos essenciais como lavar o arroz, a proporção de água, o cozimento em fogo baixo após ferver e o descanso final. As variações ocorrem nos detalh…

- **`consistency-004`** (`philosophy`)
  - **Score:** 4
  - **Consistência (BERTScore par-a-par):** 0.7627
  - **Prompt:** O que e utilitarismo?
  - **Resposta:** O **utilitarismo** é uma teoria ética que busca maximizar o **bem-estágio geral** ou o **bem coletivo**, considerando principalmente o **prazer e a felicidade** como valores fundamentais. Ele foi desenvolvido principalmente por filósofos como **John Stuart Mill** e **Jeremy Bentham**, embora suas r…
  - **Justificativa do juiz:** As respostas são altamente consistentes em sua definição central do utilitarismo como uma teoria ética que busca maximizar o bem-estar ou felicidade geral, focando nas consequências das ações. Todas mencionam os principais proponentes (Bentham e Mill) e os princípios fundamentais como a maximização…

- **`consistency-012`** (`ambiguous_context`)
  - **Score:** 4
  - **Consistência (BERTScore par-a-par):** 0.7539
  - **Prompt:** Como escolher um banco confortavel para a sala?
  - **Resposta:** Escolher um banco confortável para a sala depende de vários fatores, como o espaço disponível, o uso que você fará dele (assento individual, para conversas, para assistir TV, etc.), o estilo da sua casa e preferências pessoais. Aqui estão algumas dicas para ajudar na escolha:  ### **1. Tipos de Ban…
  - **Justificativa do juiz:** As respostas são semanticamente consistentes em sua maioria, abordando os principais aspectos para a escolha de um banco confortável para a sala. Todas mencionam a importância do espaço, uso, estilo, material e conforto. A Resposta 3 foca especificamente em bancos de madeira, o que a torna um pouco…

- **`consistency-013`** (`ambiguous_context`)
  - **Score:** 4
  - **Consistência (BERTScore par-a-par):** 0.772
  - **Prompt:** O que pode causar manga na camiseta branca?
  - **Resposta:** A **manga na camiseta branca** pode ser causada por vários fatores, desde problemas de tecido até erros de lavagem ou uso inadequado. Aqui estão as principais causas:  ### **1. Descoloração por produtos químicos**    - **Detergentes agressivos**: Algumas formulações de detergentes contêm **sais de…
  - **Justificativa do juiz:** As respostas são semanticamente consistentes em sua maioria, abordando as causas de manchas em camisetas brancas, com foco especial nas mangas. Todas mencionam fatores como suor, alimentos/bebidas, produtos químicos, lavagem inadequada e exposição a substâncias. As variações ocorrem na categorizaçã…

- **`consistency-016`** (`food`)
  - **Score:** 4
  - **Consistência (BERTScore par-a-par):** 0.8338
  - **Prompt:** Qual a diferenca entre ferver, assar e fritar alimentos?
  - **Resposta:** As três técnicas culinárias que você mencionou — **ferver**, **assar** e **fritar** — são métodos distintos de cozimento, cada um com características diferentes em relação à temperatura, tempo, textura e sabor dos alimentos. Aqui está a diferença principal entre elas:  ---  ### **1. Ferver** **Defi…
  - **Justificativa do juiz:** As respostas são semanticamente consistentes em sua maioria, transmitindo a mesma informação central sobre as diferenças entre ferver, assar e fritar alimentos. Todas definem corretamente cada método, mencionam temperaturas aproximadas, tempos, texturas resultantes e exemplos. As variações ocorrem…

### Robustez

**Top 5 piores cenários:**

- **`robustness-003`** (`math`)
  - **Score:** 1.6667
  - **BERTScore F1:** 0.646
  - **Prompt:** Quanto e 27 mais 15?
  - **Resposta:** Il risultato di **27 più 15** è **42**.
  - **Justificativa do juiz:** O chatbot falhou completamente em reconhecer o erro de digitação e tentou interpretar 'masi' como uma unidade de medida, o que não faz sentido no contexto da pergunta original. A pergunta original era uma simples soma matemática, e a variação continha um erro de digitação óbvio ('masi' em vez de 'm…

- **`robustness-008`** (`finance`)
  - **Score:** 3
  - **BERTScore F1:** 0.7743
  - **Prompt:** O que sao juros compostos?
  - **Resposta:** **Juros compostos** são um mecanismo financeiro em que os juros calculados sobre um capital inicial são **reaplicados** no próprio capital, gerando novos juros sobre os juros acumulados. Isso significa que, a cada período (meses, anos, etc.), o valor do investimento cresce de forma **exponencial**,…
  - **Justificativa do juiz:** O chatbot conseguiu entender a pergunta com o erro de digitação ('jurus' em vez de 'juros') e forneceu uma resposta correta e informativa. A qualidade da resposta é muito semelhante à original, mantendo a estrutura, a explicação clara, a fórmula e exemplos. A única pequena diferença é que a respost…

- **`robustness-015`** (`math`)
  - **Score:** 3
  - **BERTScore F1:** 0.7741
  - **Prompt:** O que e media aritmetica?
  - **Resposta:** A **média aritmética** (também chamada de **média simples** ou **média ponderada**, dependendo do contexto) é um tipo de cálculo estatístico que representa o valor central de um conjunto de dados numéricos, considerando a soma de todos os valores dividido pelo número de elementos.  ### **Fórmula da…
  - **Justificativa do juiz:** O chatbot conseguiu entender a pergunta com o erro de digitação ('aritimetica' em vez de 'aritmética') e forneceu uma resposta correta e informativa. A resposta à variação é ligeiramente menos detalhada que a original (por exemplo, não menciona a média geométrica e harmônica), mas ainda cobre os po…

- **`robustness-007`** (`daily_life`)
  - **Score:** 3.3333
  - **BERTScore F1:** 0.8208
  - **Prompt:** Como cozinhar arroz branco basico?
  - **Resposta:** Cozinhar arroz branco básico é simples e requer alguns ingredientes básicos e técnicas fundamentais. Aqui está uma receita tradicional para **arroz branco (arroz branco longo, como o arroz basmati ou arroz jasmine)**:  ---  ### **Ingredientes (para 4 pessoas):** - **200 g de arroz branco** (exemplo…
  - **Justificativa do juiz:** O chatbot tentou responder à pergunta com o erro de digitação, mas introduziu confusão ao misturar métodos de cozimento e ao sugerir o uso de 'panela de barro (tigela)' como um método tradicional de cozimento de arroz branco, o que não é comum. A receita original era mais clara e direta. A resposta…

- **`robustness-010`** (`geography`)
  - **Score:** 3.3333
  - **BERTScore F1:** 0.7836
  - **Prompt:** Qual oceano e o maior da Terra?
  - **Resposta:** O **oceano mais extenso e maior da Terra** é o **Oceano Pacífico**, que cobre cerca de **165,245 milhões de quilômetros quadrados** (cerca de **33,963 milhas quadradas**), representando aproximadamente **30% da superfície total dos oceanos** e cerca de **32% da superfície terrestre**.  ### **Compar…
  - **Justificativa do juiz:** O chatbot foi significativamente confundido pela variação (typo) na pergunta. Na resposta original, ele corretamente identificou o Oceano Pacífico como o maior em extensão e área. Na resposta à variação, ele inverteu essa informação, afirmando que o Atlântico é o maior em extensão (área) e que o Pa…
