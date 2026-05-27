# Relatório de Avaliação — llm-eval

## Metadados

- **Versão do framework:** 0.1.0
- **Iniciado em:** 2026-05-27T00:49:14.424053+00:00
- **Concluído em:** 2026-05-27T01:12:24.246994+00:00
- **Duração (s):** 1389.823
- **Provider:** gemini
- **Modelo:** gemini-2.5-flash-lite
- **Seed:** 42
- **Temperature:** 0
- **Total de cenários:** 75
- **Cenários com erro:** 0
- **Dimensões avaliadas:** Precisão Factual, Consistência Semântica, Robustez

## Resumo

| Dimensão | Média | Mediana | Desvio Padrão | Min | Max | Cenários | Avaliados | Falhas |
|---|---|---|---|---|---|---|---|---|
| Precisão Factual | 4.9714 | 5 | 0.169 | 4 | 5 | 35 | 35 | 0 |
| Consistência Semântica | 5 | 5 | 0 | 5 | 5 | 20 | 20 | 0 |
| Robustez | 4.2833 | 4.6667 | 0.8185 | 2.3333 | 5 | 20 | 20 | 0 |

**Score geral (média entre cenários avaliados):** 4.7956



## Detalhes por Dimensão

### Precisão Factual

**Top 5 piores cenários:**

- **`factual-001`** (`geography`)
  - **Score:** 4
  - **BERTScore F1:** 0.6225
  - **Prompt:** Qual e a capital da Australia?
  - **Resposta:** A capital da Austrália é **Camberra**.
  - **Justificativa do juiz:** A resposta contém a informação correta (a capital da Austrália é Canberra), mas há um erro de digitação ('Camberra' em vez de 'Canberra'). Essa pequena imprecisão não compromete o conteúdo principal da resposta.

- **`factual-002`** (`geography`)
  - **Score:** 5
  - **BERTScore F1:** 0.661
  - **Prompt:** Qual e a capital da Suica?
  - **Resposta:** A capital da Suíça é **Berna**.
  - **Justificativa do juiz:** A resposta do chatbot está completamente correta e alinhada com o ground truth. A capital da Suíça é, de fato, Berna, e a resposta do chatbot não contém informações inventadas, incorretas ou omissões.

- **`factual-003`** (`history`)
  - **Score:** 5
  - **BERTScore F1:** 0.6525
  - **Prompt:** Em que ano caiu o Muro de Berlim?
  - **Resposta:** O Muro de Berlim caiu em **1989**.
  - **Justificativa do juiz:** A resposta do chatbot está completamente correta e alinhada com o ground truth, fornecendo a informação exata (1989) sem erros, omissões ou imprecisões.

- **`factual-004`** (`history`)
  - **Score:** 5
  - **BERTScore F1:** 0.745
  - **Prompt:** Quem foi o primeiro presidente do Brasil apos a Proclamacao da Republica?
  - **Resposta:** O primeiro presidente do Brasil após a Proclamação da República foi **Marechal Deodoro da Fonseca**.
  - **Justificativa do juiz:** A resposta do chatbot está completamente correta e alinhada com o ground truth. Ela identifica corretamente Deodoro da Fonseca como o primeiro presidente do Brasil após a Proclamação da República, sem informações inventadas ou incorretas, e é completa o suficiente.

- **`factual-005`** (`science`)
  - **Score:** 5
  - **BERTScore F1:** 0.6297
  - **Prompt:** Qual planeta do Sistema Solar e conhecido como Planeta Vermelho?
  - **Resposta:** O planeta do Sistema Solar conhecido como **Planeta Vermelho** é **Marte**.
  - **Justificativa do juiz:** A resposta do chatbot está completamente correta e alinhada com o ground truth. Ela identifica Marte como o Planeta Vermelho de forma precisa e completa, sem informações inventadas ou incorretas.

### Consistência Semântica

**Top 5 piores cenários:**

- **`consistency-001`** (`science`)
  - **Score:** 5
  - **Consistência (BERTScore par-a-par):** 0.8006
  - **Prompt:** Explique o que e fotossintese.
  - **Resposta:** ## Fotossíntese: A Mágica da Vida Verde  A fotossíntese é um processo fundamental para a vida na Terra, realizado por plantas, algas e algumas bactérias. É através dela que esses organismos transformam a energia luminosa do sol em energia química, na forma de açúcares, que servem como alimento para…
  - **Justificativa do juiz:** Todas as respostas transmitem a mesma informação central sobre a fotossíntese, incluindo: (1) definição como processo de conversão de energia luminosa em energia química, (2) participação de plantas, algas e algumas bactérias, (3) necessidade de luz solar, CO₂ e água, (4) produção de glicose e oxig…

- **`consistency-002`** (`daily_life`)
  - **Score:** 5
  - **Consistência (BERTScore par-a-par):** 0.8233
  - **Prompt:** Como faco arroz branco simples?
  - **Resposta:** Fazer arroz branco simples é muito fácil e rápido! Aqui está um guia passo a passo para um arroz soltinho e delicioso:  **Ingredientes:**  *   1 xícara de arroz branco (qualquer tipo, como agulhinha, parboilizado, etc.) *   2 xícaras de água fervente (a proporção clássica é 1:2, mas pode variar um…
  - **Justificativa do juiz:** Todas as respostas transmitem a mesma informação central sobre como preparar arroz branco simples, com variações apenas na forma de apresentação (detalhamento, opcionais, dicas extras ou organização dos passos). Não há contradições significativas no conteúdo: todas mencionam os ingredientes básicos…

- **`consistency-003`** (`programming`)
  - **Score:** 5
  - **Consistência (BERTScore par-a-par):** 0.7816
  - **Prompt:** Explique a diferenca entre lista e tupla em Python.
  - **Resposta:** Em Python, tanto **listas** quanto **tuplas** são estruturas de dados usadas para armazenar coleções de itens. No entanto, a principal diferença entre elas reside na sua **mutabilidade**.  Vamos detalhar cada uma e depois comparar:  ---  ### Listas (Lists)  *   **Definição:** Listas são coleções **…
  - **Justificativa do juiz:** Todas as cinco respostas são semanticamente consistentes entre si, transmitindo a mesma informação central sobre as diferenças entre listas e tuplas em Python. As variações são apenas de forma (exemplos, organização do texto, ênfase em diferentes aspectos), mas o conteúdo principal é idêntico: 1) L…

- **`consistency-004`** (`philosophy`)
  - **Score:** 5
  - **Consistência (BERTScore par-a-par):** 0.7844
  - **Prompt:** O que e utilitarismo?
  - **Resposta:** O **utilitarismo** é uma teoria ética que defende que a ação moralmente correta é aquela que produz a maior quantidade de bem-estar ou felicidade para o maior número de pessoas. Em outras palavras, o utilitarismo foca nas **consequências** de uma ação para determinar sua moralidade.  Aqui estão os…
  - **Justificativa do juiz:** Todas as respostas transmitem a mesma informação central sobre o utilitarismo: trata-se de uma teoria ética consequencialista que defende a maximização da felicidade ou bem-estar geral para o maior número de pessoas. Não há contradições entre elas, apenas variações de forma (ex.: profundidade, exem…

- **`consistency-005`** (`writing`)
  - **Score:** 5
  - **Consistência (BERTScore par-a-par):** 0.8137
  - **Prompt:** Como escrever um e-mail profissional pedindo extensao de prazo?
  - **Resposta:** Escrever um e-mail profissional pedindo uma extensão de prazo é uma habilidade importante para gerenciar expectativas e manter um bom relacionamento com seus colegas, chefes ou clientes. A chave é ser claro, conciso, honesto e proativo.  Aqui está um guia passo a passo com um modelo que você pode a…
  - **Justificativa do juiz:** Todas as respostas transmitem a mesma informação central sobre como redigir um e-mail profissional para solicitar extensão de prazo, com estruturas semelhantes (assunto claro, saudação, justificativa, proposta de novo prazo, compromisso e agradecimento). As variações são apenas de forma (detalhamen…

### Robustez

**Top 5 piores cenários:**

- **`robustness-003`** (`math`)
  - **Score:** 2.3333
  - **BERTScore F1:** 0.7857
  - **Prompt:** Quanto e 27 mais 15?
  - **Resposta:** 27 mais 15 é igual a 42.
  - **Justificativa do juiz:** A resposta à variação não manteve a mesma informação correta: a palavra 'masi' foi interpretada como 'più' (que significa 'mais' em italiano), resultando em uma resposta em italiano ('27 più 15 fa 42') em vez de manter a resposta em português. Além disso, a resposta não corresponde ao contexto da p…

- **`robustness-008`** (`finance`)
  - **Score:** 2.6667
  - **BERTScore F1:** 0.7277
  - **Prompt:** O que sao juros compostos?
  - **Resposta:** Juros compostos são um conceito fundamental em finanças e investimentos, e a sua principal característica é que eles **rendem sobre o valor inicial (principal) e também sobre os juros acumulados em períodos anteriores**. Em outras palavras, os juros se tornam parte do capital e, a partir daí, també…
  - **Justificativa do juiz:** A resposta à variação ('jurus compostos') não apenas não manteve a informação correta sobre juros compostos, como também introduziu um conceito completamente diferente e incorreto ('responsabilidade civil' e 'solidária' no direito civil). O chatbot foi confundido pelo ruído/adversarialidade, gerand…

- **`robustness-020`** (`programming`)
  - **Score:** 3.3333
  - **BERTScore F1:** 0.7665
  - **Prompt:** Para que serve um bloco try/except em Python?
  - **Resposta:** Em Python, um bloco `try/except` é fundamental para o **tratamento de exceções**, que são erros que ocorrem durante a execução de um programa. Ele permite que você lide com esses erros de forma controlada, evitando que o programa trave abruptamente e fornecendo uma maneira de responder a situações…
  - **Justificativa do juiz:** A resposta à variação manteve a mesma informação correta sobre o funcionamento e propósito do bloco try/except em Python. O chatbot não foi confundido pelo erro de digitação ('Pythn'), demonstrando robustez ao ruído. No entanto, a resposta apresentou uma estrutura menos organizada (com seções menos…

- **`robustness-004`** (`history`)
  - **Score:** 3.6667
  - **BERTScore F1:** 0.8486
  - **Prompt:** Quem escreveu Dom Casmurro?
  - **Resposta:** **Dom Casmurro** foi escrito por **Machado de Assis**.
  - **Justificativa do juiz:** A resposta manteve a mesma informação correta e não foi afetada pelo erro de digitação ('escrevel' em vez de 'escreveu'). O chatbot demonstrou robustez ao lidar com a variação adversarial, não sendo confundido pelo ruído no input.

- **`robustness-011`** (`writing`)
  - **Score:** 3.6667
  - **BERTScore F1:** 0.7871
  - **Prompt:** Como escrever um e-mail profissional pedindo extensao de prazo?
  - **Resposta:** Escrever um e-mail profissional pedindo uma extensão de prazo é uma habilidade importante para gerenciar expectativas e manter um bom relacionamento com seus colegas, chefes ou clientes. A chave é ser claro, conciso, honesto e proativo.  Aqui está um guia passo a passo com um modelo que você pode a…
  - **Justificativa do juiz:** A resposta à variação manteve a mesma qualidade da original, com estrutura, modelo e dicas preservados integralmente. O chatbot não foi confundido pelo ruído (erros de digitação e formatação na variação) e não houve degradação significativa na resposta. A adaptação foi feita de forma consistente, m…
