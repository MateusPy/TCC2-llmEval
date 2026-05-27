# Relatório de Avaliação — llm-eval

## Metadados

- **Versão do framework:** 0.1.0
- **Iniciado em:** 2026-05-27T00:23:50.059615+00:00
- **Concluído em:** 2026-05-27T00:47:12.202208+00:00
- **Duração (s):** 1402.143
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
| Precisão Factual | 4.8667 | 5 | 0.4138 | 3 | 5 | 35 | 35 | 0 |
| Consistência Semântica | 4.95 | 5 | 0.2236 | 4 | 5 | 20 | 20 | 0 |
| Robustez | 4.4 | 4.6667 | 0.6361 | 2.6667 | 5 | 20 | 20 | 0 |

**Score geral (média entre cenários avaliados):** 4.7644



## Detalhes por Dimensão

### Precisão Factual

**Top 5 piores cenários:**

- **`factual-011`** (`language`)
  - **Score:** 3
  - **BERTScore F1:** 0.5389
  - **Prompt:** Quantas letras tem o alfabeto portugues moderno?
  - **Resposta:** O alfabeto português moderno tem **23 letras**.  Além disso, o alfabeto português inclui as seguintes letras com acentos e til: - **A, E, I, O, U** (com acentos: **Á, É, Í, Ó, Ú**) - **C** (com til: **Ç**) - **G** (com til: **Ĝ**) - **N** (com til: **Ń**) - **S** (com til: **Ş**) - **X** (com til:…
  - **Justificativa do juiz:** A resposta do chatbot apresenta informações parcialmente corretas, mas com imprecisões e omissões significativas. Embora mencione corretamente que o alfabeto português moderno tem 23 letras (versão mais comum), a justificativa é confusa e contém erros factuais. As letras com acentos e til listadas…

- **`factual-002`** (`geography`)
  - **Score:** 4
  - **BERTScore F1:** 0.5617
  - **Prompt:** Qual e a capital da Suica?
  - **Resposta:** A capital da **Suiza** é **Berna** (em alemão: *Bern*).  A Suíça é um país federativo, e Berna é a sede do governo federal, incluindo o Parlamento, o Conselho Federal (governo) e a sede da Confederação Suíça. Além disso, Berna é uma cidade histórica e culturalmente significativa.  Se você estava pe…
  - **Justificativa do juiz:** A resposta contém a informação correta (Berna é a capital da Suíça), mas há uma imprecisão inicial ao mencionar 'Suiza' (deveria ser 'Suíça'). Além disso, a resposta expande o contexto com informações adicionais sobre a Suíça e o sistema de transporte 'Suica', que não são relevantes para a pergunta…

- **`factual-031`** (`geography`)
  - **Score:** 4
  - **BERTScore F1:** 0.5926
  - **Prompt:** Qual e o pais que tem Lisboa como capital?
  - **Resposta:** A capital que você está perguntando é **Portugal**.  Lisboa é a capital e a maior cidade do **Portugal**, um país localizado na **Península Ibérica**, na Europa Ocidental.
  - **Justificativa do juiz:** A resposta contém a informação correta (Portugal é o país com Lisboa como capital), mas é mais extensa do que o necessário para a pergunta direta. Não há informações incorretas ou inventadas, mas a resposta não é tão concisa quanto o ground truth.

- **`factual-023`** (`programming`)
  - **Score:** 4.3333
  - **BERTScore F1:** 0.5058
  - **Prompt:** Qual arquivo de um projeto Python costuma indicar dependencias e metadados neste repositorio?
  - **Resposta:** Em um projeto Python, os arquivos mais comuns que indicam **dependências** e **metadados** são:  ### **1. Arquivo `requirements.txt`**    - **Purpose**: Lista todas as dependências externas do projeto (bibliotecas Python).    - **Formato**:      ```txt      package_name==version      package_name>=…
  - **Justificativa do juiz:** A resposta do chatbot é completamente correta e alinhada com o ground truth. Além de mencionar o arquivo `pyproject.toml` (que é a resposta esperada), a resposta fornece uma explicação detalhada e abrangente sobre outros arquivos relevantes para dependências e metadados em projetos Python, como `re…

- **`factual-001`** (`geography`)
  - **Score:** 5
  - **BERTScore F1:** 0.5681
  - **Prompt:** Qual e a capital da Australia?
  - **Resposta:** A capital da Austrália é **Canberra**.  Canberra foi escolhida como capital em 1908 e tornou-se oficialmente a capital em 1927, após a união das colônias britânicas da Austrália. Ela está localizada no interior do país, no estado da **Austrália Central**, e é conhecida por sua arquitetura moderna e…
  - **Justificativa do juiz:** A resposta do chatbot está completamente correta e alinhada com o ground truth. Além de fornecer a capital correta (Canberra), a resposta inclui informações adicionais relevantes e precisas sobre a escolha de Canberra como capital em 1908 e sua oficialização em 1927, bem como sua localização e impo…

### Consistência Semântica

**Top 5 piores cenários:**

- **`consistency-013`** (`ambiguous_context`)
  - **Score:** 4
  - **Consistência (BERTScore par-a-par):** 0.7745
  - **Prompt:** O que pode causar manga na camiseta branca?
  - **Resposta:** A **manga na camiseta branca** pode ser causada por vários fatores, desde problemas de tecido até erros de lavagem ou uso inadequado. Aqui estão as principais causas:  ### **1. Descoloração por produtos químicos**    - **Detergentes agressivos**: Algumas formulações de detergentes contêm **sais de…
  - **Justificativa do juiz:** As respostas são semanticamente consistentes em relação ao tema central (causas de manchas ou descoloração em camisas brancas), mas apresentam variações significativas na abordagem e profundidade. Todas as respostas mencionam causas como suor, produtos químicos, lavagem inadequada e exposição ao so…

- **`consistency-001`** (`science`)
  - **Score:** 5
  - **Consistência (BERTScore par-a-par):** 0.812
  - **Prompt:** Explique o que e fotossintese.
  - **Resposta:** A **fotossintese** é um processo biológico fundamental que permite às plantas, algas e alguns tipos de bactérias converter luz solar em energia química, produzindo **glicose** (um carboidrato) e liberando **oxigênio** como subproduto. Esse mecanismo é essencial para a vida na Terra, pois fornece al…
  - **Justificativa do juiz:** Todas as respostas apresentam a mesma informação central sobre a fotossíntese: processo biológico que converte luz solar em energia química (glicose), produzindo oxigênio como subproduto, ocorrendo em cloroplastos com participação de clorofila, e dividido em fase clara (dependente de luz) e fase es…

- **`consistency-002`** (`daily_life`)
  - **Score:** 5
  - **Consistência (BERTScore par-a-par):** 0.8104
  - **Prompt:** Como faco arroz branco simples?
  - **Resposta:** Para fazer **arroz branco simples** (arroz cozido em água), siga este passo a passo fácil e rápido:  ### **Ingredientes:** - 1 xícara de arroz branco (preferencialmente arroz basmati, jasmine ou arroz comum) - 2 xícaras de água (para arroz médio, ajuste conforme o tipo) - 1 colher de chá de sal (op…
  - **Justificativa do juiz:** Todas as respostas transmitem a mesma informação central sobre como preparar arroz branco simples, com variações apenas na forma de apresentação (detalhamento, ordem dos passos, dicas adicionais ou opcionais). Não há contradições significativas no conteúdo principal (proporções de ingredientes, tem…

- **`consistency-003`** (`programming`)
  - **Score:** 5
  - **Consistência (BERTScore par-a-par):** 0.7849
  - **Prompt:** Explique a diferenca entre lista e tupla em Python.
  - **Resposta:** Em Python, **lista** e **tupla** são dois tipos de coleções (ou *containers*) que armazenam elementos, mas possuem diferenças importantes em termos de **mutabilidade**, **uso** e **performance**. Aqui está uma comparação detalhada:  ---  ### **1. Mutabilidade (Flexibilidade)** \| **Tipo**  \| **Mutáv…
  - **Justificativa do juiz:** Todas as respostas apresentam a mesma informação central sobre as diferenças entre listas e tuplas em Python, destacando mutabilidade, performance, uso típico e sintaxe. Não há contradições significativas no conteúdo, apenas variações de forma (ex.: organização em tabelas vs. listas, exemplos difer…

- **`consistency-004`** (`philosophy`)
  - **Score:** 5
  - **Consistência (BERTScore par-a-par):** 0.7529
  - **Prompt:** O que e utilitarismo?
  - **Resposta:** O **utilitarismo** é uma teoria ética e filosófica que busca maximizar o **bem-estágio geral** ou a felicidade coletiva, considerando principalmente os **resultados** de uma ação em vez de princípios abstratos ou regras fixas. Ele é um dos principais sistemas éticos consequencialistas, ou seja, ava…
  - **Justificativa do juiz:** As quatro respostas são semanticamente consistentes entre si, transmitindo a mesma informação central sobre o utilitarismo: uma teoria ética consequencialista que busca maximizar o bem-estar ou felicidade geral, avaliando ações com base em suas consequências. Embora haja variações de forma, profund…

### Robustez

**Top 5 piores cenários:**

- **`robustness-003`** (`math`)
  - **Score:** 2.6667
  - **BERTScore F1:** 0.6368
  - **Prompt:** Quanto e 27 mais 15?
  - **Resposta:** Il risultato di **27 più 15** è **42**.
  - **Justificativa do juiz:** O chatbot não identificou o erro de digitação ('masi' em vez de 'mais') e desviou completamente do contexto matemático simples da pergunta original. Em vez de corrigir o erro e fornecer a resposta correta (42), o chatbot tentou interpretar 'masi' como uma unidade de medida, o que não só não resolve…

- **`robustness-012`** (`security`)
  - **Score:** 3.3333
  - **BERTScore F1:** 0.8027
  - **Prompt:** Como identificar um golpe de phishing?
  - **Resposta:** Identificar um **phishing** (fraude por engenharia social) é crucial para proteger seus dados e informações pessoais. Aqui estão os principais sinais e estratégias para reconhecê-lo:  ---  ### **1. Mensagens Suspeitas** - **E-mails ou mensagens falsas**:   - **Assunto enganoso**: "Seu login está ex…
  - **Justificativa do juiz:** A resposta à variação manteve a maioria das informações corretas e relevantes, com detalhes adicionais sobre URLs curtas e caracteres especiais. No entanto, houve uma interrupção abrupta no final da resposta ('ex: "Amazon Prime" em vez de'), o que indica uma degradação leve na fluidez e completude.…

- **`robustness-004`** (`history`)
  - **Score:** 3.6667
  - **BERTScore F1:** 0.7427
  - **Prompt:** Quem escreveu Dom Casmurro?
  - **Resposta:** Dom Casmurro foi escrito por **Machado de Assis**, um dos maiores escritores brasileiros do século XIX.  Publicado em 1899, a obra é uma das mais importantes da literatura nacional e aborda temas como a dúvida, a traição, a solidão e a construção da identidade.
  - **Justificativa do juiz:** A resposta à variação ('Quem escrevel Dom Casmurro?') manteve a mesma informação correta, corrigindo automaticamente o erro de digitação ('escrevel' para 'escreveu') e fornecendo a mesma resposta detalhada e precisa sobre Machado de Assis e a obra 'Dom Casmurro'. Não houve confusão pelo ruído no in…

- **`robustness-008`** (`finance`)
  - **Score:** 3.6667
  - **BERTScore F1:** 0.7813
  - **Prompt:** O que sao juros compostos?
  - **Resposta:** **Juros compostos** são um mecanismo financeiro em que os juros calculados sobre um capital inicial são **reaplicados** no próprio capital, gerando novos juros sobre os juros acumulados. Isso significa que, a cada período (meses, anos, etc.), o valor do investimento cresce de forma **exponencial**,…
  - **Justificativa do juiz:** O chatbot manteve a qualidade da resposta original mesmo com a variação adversarial ('jurus' em vez de 'juros'). A explicação permaneceu tecnicamente correta, detalhada e estruturada de forma idêntica, incluindo a fórmula, exemplo prático, vantagens e diferenças em relação aos juros simples. A únic…

- **`robustness-011`** (`writing`)
  - **Score:** 4
  - **BERTScore F1:** 0.7495
  - **Prompt:** Como escrever um e-mail profissional pedindo extensao de prazo?
  - **Resposta:** Escrever um e-mail profissional pedindo uma extensão de prazo requer **clareza, cortesia e formalidade**, além de demonstrar **responsabilidade e transparência**. Aqui está um modelo estruturado para você adaptar conforme o contexto:  ---  **Assunto:** Pedido de Extensão de Prazo – [Nome do Projeto…
  - **Justificativa do juiz:** A resposta à variação manteve a estrutura e a qualidade da resposta original, com modelos de e-mail profissionais e adaptáveis. No entanto, houve uma ligeira simplificação no conteúdo (ex.: remoção de dicas adicionais e variantes por contexto) e uma redução na extensão dos exemplos, o que não compr…
