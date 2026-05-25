# Relatório de Avaliação — llm-eval

## Metadados

- **Versão do framework:** 0.1.0
- **Iniciado em:** 2026-05-20T02:47:21.899277+00:00
- **Concluído em:** 2026-05-20T02:56:22.163906+00:00
- **Duração (s):** 540.265
- **Provider:** gemini
- **Modelo:** gemini-2.5-flash-lite
- **Seed:** 42
- **Temperature:** 0
- **Total de cenários:** 30
- **Cenários com erro:** 0
- **Dimensões avaliadas:** Precisão Factual, Consistência Semântica, Robustez

## Resumo

| Dimensão | Média | Mediana | Desvio Padrão | Min | Max | Cenários | Avaliados | Falhas |
|---|---|---|---|---|---|---|---|---|
| Precisão Factual | 4.9 | 5 | 0.3162 | 4 | 5 | 10 | 10 | 0 |
| Consistência Semântica | 5 | 5 | 0 | 5 | 5 | 10 | 10 | 0 |
| Robustez | 3.8333 | 3.8334 | 0.8203 | 2.3333 | 5 | 10 | 10 | 0 |

**Score geral (média entre cenários avaliados):** 4.5778



## Detalhes por Dimensão

### Precisão Factual

**Top 5 piores cenários:**

- **`factual-001`** (`geography`)
  - **Score:** 4
  - **BERTScore F1:** 0.6225
  - **Prompt:** Qual e a capital da Australia?
  - **Resposta:** A capital da Austrália é **Camberra**.
  - **Justificativa do juiz:** A resposta do chatbot está quase correta, mas contém um pequeno erro de digitação na capital ('Camberra' em vez de 'Canberra'). A informação principal (a capital da Austrália) está correta, e a resposta é completa o suficiente para a pergunta feita.

- **`factual-002`** (`geography`)
  - **Score:** 5
  - **BERTScore F1:** 0.661
  - **Prompt:** Qual e a capital da Suica?
  - **Resposta:** A capital da Suíça é **Berna**.
  - **Justificativa do juiz:** A resposta do chatbot está completamente correta e alinhada com o ground truth. Ela identifica Berna como a capital da Suíça de forma direta e sem informações incorretas ou inventadas.

- **`factual-003`** (`history`)
  - **Score:** 5
  - **BERTScore F1:** 0.6525
  - **Prompt:** Em que ano caiu o Muro de Berlim?
  - **Resposta:** O Muro de Berlim caiu em **1989**.
  - **Justificativa do juiz:** A resposta do chatbot está completamente correta e alinhada com o ground truth, fornecendo o ano exato em que o Muro de Berlim caiu.

- **`factual-004`** (`history`)
  - **Score:** 5
  - **BERTScore F1:** 0.745
  - **Prompt:** Quem foi o primeiro presidente do Brasil apos a Proclamacao da Republica?
  - **Resposta:** O primeiro presidente do Brasil após a Proclamação da República foi **Marechal Deodoro da Fonseca**.
  - **Justificativa do juiz:** A resposta do chatbot está completamente correta e alinhada com o ground truth. Ela identifica corretamente Marechal Deodoro da Fonseca como o primeiro presidente do Brasil após a Proclamação da República, sem adicionar informações incorretas ou omitir detalhes relevantes.

- **`factual-005`** (`science`)
  - **Score:** 5
  - **BERTScore F1:** 0.6297
  - **Prompt:** Qual planeta do Sistema Solar e conhecido como Planeta Vermelho?
  - **Resposta:** O planeta do Sistema Solar conhecido como **Planeta Vermelho** é **Marte**.
  - **Justificativa do juiz:** A resposta do chatbot identifica corretamente Marte como o Planeta Vermelho, alinhando-se perfeitamente com a resposta esperada (ground truth). Não há informações inventadas ou incorretas, e a resposta é completa o suficiente para atender à pergunta.

### Consistência Semântica

**Top 5 piores cenários:**

- **`consistency-001`** (`science`)
  - **Score:** 5
  - **Consistência (BERTScore par-a-par):** 0.8006
  - **Prompt:** Explique o que e fotossintese.
  - **Resposta:** ## Fotossíntese: A Mágica da Vida Verde  A fotossíntese é um processo fundamental para a vida na Terra, realizado por plantas, algas e algumas bactérias. É através dela que esses organismos transformam a energia luminosa do sol em energia química, na forma de açúcares, que servem como alimento para…
  - **Justificativa do juiz:** Todas as respostas explicam a fotossíntese de forma consistente, abordando os mesmos conceitos centrais: a conversão de energia luminosa em energia química (açúcares), os ingredientes essenciais (luz, CO₂, água), os locais de ocorrência (cloroplastos, clorofila), as duas fases principais (luminosa…

- **`consistency-002`** (`daily_life`)
  - **Score:** 5
  - **Consistência (BERTScore par-a-par):** 0.8233
  - **Prompt:** Como faco arroz branco simples?
  - **Resposta:** Fazer arroz branco simples é muito fácil e rápido! Aqui está um guia passo a passo para um arroz soltinho e delicioso:  **Ingredientes:**  *   1 xícara de arroz branco (qualquer tipo, como agulhinha, parboilizado, etc.) *   2 xícaras de água fervente (a proporção clássica é 1:2, mas pode variar um…
  - **Justificativa do juiz:** Todas as respostas fornecem instruções detalhadas e consistentes sobre como fazer arroz branco simples. Elas concordam nos ingredientes essenciais (arroz, água, sal, óleo opcional), na proporção clássica de 1:2 (arroz:água), na importância da lavagem opcional do arroz para soltura, no refogado opci…

- **`consistency-003`** (`programming`)
  - **Score:** 5
  - **Consistência (BERTScore par-a-par):** 0.7816
  - **Prompt:** Explique a diferenca entre lista e tupla em Python.
  - **Resposta:** Em Python, tanto **listas** quanto **tuplas** são estruturas de dados usadas para armazenar coleções de itens. No entanto, a principal diferença entre elas reside na sua **mutabilidade**.  Vamos detalhar cada uma e depois comparar:  ---  ### Listas (Lists)  *   **Definição:** Listas são coleções **…
  - **Justificativa do juiz:** Todas as respostas abordam consistentemente a diferença fundamental entre listas e tuplas em Python, que é a mutabilidade. Elas explicam que listas são mutáveis (podem ser alteradas após a criação) e tuplas são imutáveis (não podem ser alteradas). Todas as respostas também mencionam a sintaxe (colc…

- **`consistency-004`** (`philosophy`)
  - **Score:** 5
  - **Consistência (BERTScore par-a-par):** 0.7844
  - **Prompt:** O que e utilitarismo?
  - **Resposta:** O **utilitarismo** é uma teoria ética que defende que a ação moralmente correta é aquela que produz a maior quantidade de bem-estar ou felicidade para o maior número de pessoas. Em outras palavras, o utilitarismo foca nas **consequências** de uma ação para determinar sua moralidade.  Aqui estão os…
  - **Justificativa do juiz:** Todas as respostas transmitem a mesma informação central sobre o utilitarismo: é uma teoria ética consequencialista que defende que a ação moralmente correta é aquela que maximiza a felicidade ou o bem-estar para o maior número de pessoas. As respostas variam em profundidade e detalhe (por exemplo,…

- **`consistency-005`** (`writing`)
  - **Score:** 5
  - **Consistência (BERTScore par-a-par):** 0.8137
  - **Prompt:** Como escrever um e-mail profissional pedindo extensao de prazo?
  - **Resposta:** Escrever um e-mail profissional pedindo uma extensão de prazo é uma habilidade importante para gerenciar expectativas e manter um bom relacionamento com seus colegas, chefes ou clientes. A chave é ser claro, conciso, honesto e proativo.  Aqui está um guia passo a passo com um modelo que você pode a…
  - **Justificativa do juiz:** Todas as respostas abordam o mesmo tema central: como escrever um e-mail profissional para pedir extensão de prazo. Elas compartilham os mesmos elementos essenciais, como a importância de um assunto claro, saudação profissional, justificativa honesta e concisa, proposta de novo prazo e um encerrame…

### Robustez

**Top 5 piores cenários:**

- **`robustness-008`** (`finance`)
  - **Score:** 2.3333
  - **BERTScore F1:** 0.7277
  - **Prompt:** O que sao juros compostos?
  - **Resposta:** Juros compostos são um conceito fundamental em finanças e investimentos, e a sua principal característica é que eles **rendem sobre o valor inicial (principal) e também sobre os juros acumulados em períodos anteriores**. Em outras palavras, os juros se tornam parte do capital e, a partir daí, també…
  - **Justificativa do juiz:** O chatbot foi completamente confundido pela variação 'jurus compostos', interpretando-a como um termo jurídico inexistente (provavelmente uma tentativa de 'juros compostos' com um erro de digitação). A resposta gerada sobre 'jurus compostos' no direito civil é totalmente irrelevante para a pergunta…

- **`robustness-003`** (`math`)
  - **Score:** 3
  - **BERTScore F1:** 0.7857
  - **Prompt:** Quanto e 27 mais 15?
  - **Resposta:** 27 mais 15 é igual a 42.
  - **Justificativa do juiz:** O chatbot respondeu corretamente à pergunta matemática, mas a resposta foi dada em italiano ('27 più 15 fa 42') em vez de português, o que indica que o ruído (typo 'masi') causou uma confusão na compreensão do idioma, embora a operação matemática tenha sido mantida. A informação correta foi mantida…

- **`robustness-005`** (`programming`)
  - **Score:** 3.3333
  - **BERTScore F1:** 0.8014
  - **Prompt:** Em Python, como obter o tamanho de uma lista?
  - **Resposta:** Em Python, existem duas maneiras principais e muito eficientes de obter o tamanho (o número de elementos) de uma lista:  1.  **Usando a função `len()`:** Esta é a maneira mais comum e recomendada. A função `len()` é uma função embutida no Python que retorna o número de itens em um objeto. Para list…
  - **Justificativa do juiz:** O chatbot identificou corretamente a intenção da pergunta, mesmo com o erro de digitação ('Pythn' em vez de 'Python'). A resposta à variação é muito semelhante à resposta original, mantendo a informação correta e a recomendação principal de usar a função `len()`. A única diferença notável é a omiss…

- **`robustness-004`** (`history`)
  - **Score:** 3.6667
  - **BERTScore F1:** 0.8486
  - **Prompt:** Quem escreveu Dom Casmurro?
  - **Resposta:** **Dom Casmurro** foi escrito por **Machado de Assis**.
  - **Justificativa do juiz:** O chatbot manteve a mesma informação correta e não foi confundido pelo typo na pergunta. A resposta à variação é idêntica à resposta original, indicando robustez contra ruído simples.

- **`robustness-009`** (`environment`)
  - **Score:** 3.6667
  - **BERTScore F1:** 0.8261
  - **Prompt:** Explique o que e efeito estufa.
  - **Resposta:** ## O Efeito Estufa: Um Fenômeno Natural Essencial para a Vida  O efeito estufa é um **processo natural e fundamental para a vida na Terra**. Ele funciona como um "cobertor" que mantém o planeta aquecido, permitindo que a temperatura média seja adequada para a existência de água líquida e, consequen…
  - **Justificativa do juiz:** O chatbot conseguiu identificar corretamente a intenção da pergunta, mesmo com o erro de digitação ('estfa' em vez de 'estufa'). A resposta fornecida é completa, precisa e mantém a mesma qualidade informativa e estrutural da resposta à pergunta original. Não houve confusão com o ruído e a resposta…
