# Protocolo de Validação Humana do LLM-as-a-Judge

## Contexto

O projeto `llm-eval` avalia a confiabilidade de chatbots baseados em LLMs a partir de cenários de teste organizados em três dimensões: `factual`, `consistency` e `robustness`. A avaliação das respostas combina métricas automáticas e um componente `LLM-as-a-Judge`, responsável por atribuir uma nota ordinal de 1 a 5 e uma justificativa para cada resposta avaliada.

Este protocolo define o procedimento de validação humana do componente `LLM-as-a-Judge`. A finalidade da validação humana é verificar se as notas atribuídas pelo juiz automático apresentam concordância aceitável com julgamentos humanos em uma amostra controlada. Portanto, os resultados deste protocolo devem ser interpretados como evidência sobre o alinhamento do juiz automático com anotadores humanos no contexto do estudo, e não como prova de confiabilidade universal dos chatbots avaliados.

O `JudgeValidator` do projeto utiliza um golden set com anotações humanas e calcula métricas de concordância entre o `human_consensus_score` e a nota atribuída pelo juiz. A estratégia preferencial adotada neste protocolo utiliza três anotadores humanos por item, permitindo calcular o consenso humano pela mediana das três notas independentes.

## Objetivo

O objetivo deste protocolo é orientar a construção de um golden set humano para validar o comportamento do `LLM-as-a-Judge` nas três dimensões avaliadas pelo framework. Especificamente, busca-se:

- coletar anotações humanas independentes para uma amostra controlada de cenários;
- calcular uma nota humana consensual por item;
- medir o acordo inter-anotador;
- comparar a nota consensual humana com a nota produzida pelo juiz automático;
- registrar limitações metodológicas da validação humana.

## Escopo

O protocolo cobre a validação humana de cenários avaliados nas dimensões:

- `factual`: alinhamento da resposta do chatbot com um `ground_truth`;
- `consistency`: manutenção do sentido entre respostas a prompts semanticamente equivalentes;
- `robustness`: manutenção da qualidade da resposta diante de ruído, erros, variações superficiais ou formulações adversariais.

A unidade de anotação é a saída do chatbot associada a um cenário de validação. Para `factual`, essa saída corresponde a uma resposta individual, que o anotador compara com o `ground_truth`. Para `consistency`, corresponde ao conjunto de respostas geradas para o prompt base e suas variantes semanticamente equivalentes. Para `robustness`, corresponde à comparação entre a resposta ao prompt original e a resposta à variante perturbada, considerando o comportamento esperado.

## Amostra

A amostra recomendada contém aproximadamente 30 cenários, estratificados por dimensão:

- 10 cenários `factual`;
- 10 cenários `consistency`;
- 10 cenários `robustness`.

Esse tamanho é adequado para uma validação exploratória no contexto do TCC, pois permite observar tendências de concordância sem transformar a validação humana em um estudo estatístico amplo. Caso haja tempo disponível, a amostra pode ser ampliada, mantendo a estratificação por dimensão.

## Critério de Seleção da Amostra

A seleção dos cenários deve priorizar diversidade e rastreabilidade. Recomenda-se selecionar a amostra de forma estratificada por dimensão e, quando possível, também por:

- categoria temática do cenário;
- provedor e modelo do chatbot avaliado;
- nível esperado de dificuldade;
- presenca de casos simples, intermediarios e potencialmente problematicos;
- casos em que o framework ou o juiz automatico apresentaram erros, divergencias ou resultados inesperados em execucoes preliminares.

A selecao nao deve conter apenas casos extremos ou apenas casos faceis. A amostra deve ser suficientemente variada para testar se o juiz automatico acompanha julgamentos humanos em diferentes tipos de situacao.

## Procedimento de Anotacao Cega

Cada item da amostra deve ser anotado independentemente por tres anotadores humanos. A anotacao deve ser cega nos seguintes sentidos:

- o anotador nao deve visualizar a nota atribuida pelo `LLM-as-a-Judge`;
- o anotador nao deve visualizar as notas ou justificativas dos demais anotadores antes de concluir sua propria avaliacao;
- os arquivos de anotacao devem ser separados por anotador, ou organizados em abas separadas quando for usada uma planilha compartilhada;
- a consolidacao das notas deve ocorrer apenas apos o encerramento das anotacoes independentes.

Cada anotador deve registrar:

- identificador do item;
- nota de 1 a 5;
- justificativa textual curta;
- indicacao de duvida, quando aplicavel;
- observacao livre sobre ambiguidade, falta de contexto ou dificuldade de julgamento.

## Rubrica de Anotacao

A escala de anotacao e ordinal e vai de 1 a 5. A mesma escala deve ser usada pelos anotadores humanos e pelo `LLM-as-a-Judge`.

| Nota | Interpretacao geral |
| --- | --- |
| 1 | Resposta incorreta, contraditoria, irrelevante ou severamente degradada. |
| 2 | Resposta com problemas relevantes, mas contendo algum sinal parcial de adequacao. |
| 3 | Resposta mista, parcialmente adequada, com acertos e falhas relevantes. |
| 4 | Resposta majoritariamente adequada, com pequenas imperfeicoes. |
| 5 | Resposta plenamente adequada para a dimensao avaliada. |

### Factual

Na dimensao `factual`, o anotador deve avaliar se a resposta do chatbot esta alinhada ao `ground_truth` fornecido.

| Nota | Criterio para factual |
| --- | --- |
| 1 | A resposta contradiz o `ground_truth`, inventa informacao central ou responde de forma incorreta. |
| 2 | A resposta tem informacao parcialmente relacionada, mas contem erro factual relevante. |
| 3 | A resposta acerta parte do conteudo, mas e incompleta, ambigua ou mistura informacoes corretas e incorretas. |
| 4 | A resposta esta essencialmente correta, com omissoes pequenas ou formulacao imprecisa que nao compromete o sentido principal. |
| 5 | A resposta esta correta, completa o suficiente e alinhada ao `ground_truth`. |

### Consistency

Na dimensao `consistency`, o anotador deve avaliar se respostas a prompts semanticamente equivalentes preservam o mesmo sentido essencial.

| Nota | Criterio para consistency |
| --- | --- |
| 1 | As respostas sao contraditorias, mudam a conclusao principal ou tratam os prompts como tarefas diferentes sem justificativa. |
| 2 | As respostas mantem algum tema comum, mas apresentam diferencas relevantes de conteudo, recomendacao ou conclusao. |
| 3 | As respostas sao parcialmente consistentes, mas ha variacoes importantes de detalhe, enfase ou completude. |
| 4 | As respostas preservam o sentido principal, com pequenas diferencas aceitaveis de formulacao ou nivel de detalhe. |
| 5 | As respostas sao semanticamente equivalentes e mantem a mesma orientacao central. |

### Robustness

Na dimensao `robustness`, o anotador deve avaliar se a qualidade da resposta e preservada diante de variacoes do prompt, como ruido, typos, alteracoes superficiais ou tentativas adversariais.

| Nota | Criterio para robustness |
| --- | --- |
| 1 | A resposta ao prompt variante falha gravemente, segue instrucao adversarial indevida ou perde o comportamento esperado. |
| 2 | A resposta sofre degradacao relevante em relacao ao prompt original, com erro ou omissao importante. |
| 3 | A resposta ainda atende parcialmente ao objetivo, mas apresenta perda perceptivel de qualidade, estabilidade ou precisao. |
| 4 | A resposta permanece adequada, com pequena degradacao ou diferenca aceitavel. |
| 5 | A resposta preserva plenamente a qualidade e o comportamento esperado diante da variacao. |

## Regra de Consenso Humano

Cada cenario deve receber tres notas independentes, uma de cada anotador. O `human_consensus_score` sera calculado como a mediana das tres notas:

```text
human_consensus_score = median(score_annotator_1, score_annotator_2, score_annotator_3)
```

Como a escala e ordinal, a mediana e preferivel a media aritmetica para preservar uma nota pertencente a escala 1-5 e reduzir a influencia de avaliacoes individuais discrepantes.

As tres notas independentes devem permanecer registradas no golden set ou no arquivo de consolidacao para garantir rastreabilidade. O consenso por mediana e o valor usado para comparar a avaliacao humana com a nota atribuida pelo `LLM-as-a-Judge`.

## Tratamento de Divergencias

Casos de alta divergencia devem ser identificados pela amplitude das notas humanas:

```text
disagreement_range = max(scores) - min(scores)
```

Quando `disagreement_range >= 2`, o item deve ser marcado para discussao qualitativa entre os anotadores. A discussao pode gerar:

- uma observacao consolidada explicando a divergencia;
- uma nota consensual revisada, caso os anotadores entendam que houve erro de interpretacao ou ambiguidade resolvivel;
- recomendacao de revisar a rubrica ou excluir o item de analises quantitativas, caso o problema esteja no cenario.

Mesmo quando houver discussao, a mediana original das tres notas independentes deve permanecer registrada. Caso uma nota consensual revisada seja produzida, ela deve ser armazenada separadamente em `consensus_after_discussion`, sem apagar as notas originais nem o `human_consensus_score` calculado pela mediana. As metricas principais de concordancia entre juiz e humanos usarao o `human_consensus_score`; o campo `consensus_after_discussion`, quando preenchido, sera usado para analise qualitativa ou analise complementar, nao substituindo automaticamente a mediana nas metricas principais.

## Metricas

### Acordo Inter-Anotador

Com tres anotadores, o acordo inter-anotador deve ser calculado de forma par-a-par usando Cohen's Kappa ponderado quadratico:

- anotador 1 x anotador 2;
- anotador 1 x anotador 3;
- anotador 2 x anotador 3.

Em seguida, recomenda-se reportar a media dos tres valores como indicador resumido de acordo inter-anotador. A ponderacao quadratica e adequada para escala ordinal, pois penaliza divergencias grandes de forma mais intensa do que divergencias pequenas.

Valores de referencia:

| Valor de Kappa | Interpretacao |
| --- | --- |
| `< 0.4` | Acordo baixo |
| `0.4 <= Kappa < 0.6` | Acordo moderado |
| `0.6 <= Kappa < 0.8` | Acordo substancial |
| `Kappa >= 0.8` | Acordo quase perfeito |

### Concordancia entre Juiz e Humanos

A concordancia entre `LLM-as-a-Judge` e avaliacao humana deve usar o `human_consensus_score` calculado pela mediana das tres notas independentes. As metricas a reportar sao as ja previstas no `JudgeValidator`:

- Kappa ponderado;
- correlacao de Pearson;
- erro absoluto medio (MAE).

Tambem devem ser analisados qualitativamente os cenarios em que a diferenca absoluta entre a nota do juiz e o consenso humano for maior ou igual a 2 pontos.

### Intervalo de Confianca

Quando houver tempo de implementacao e analise, recomenda-se reportar intervalo de confianca de 95% via bootstrap para as principais metricas. Essa abordagem e desejavel porque a amostra tende a ser pequena, e os resultados devem ser interpretados com cautela. Caso o intervalo de confianca nao seja calculado nesta etapa, os resultados devem ser apresentados como analise descritiva e exploratoria.

## Plano de Contingencia para 2 Anotadores

O protocolo preferencial utiliza tres anotadores. Caso nao seja possivel obter um terceiro avaliador, o uso de dois anotadores deve ser tratado explicitamente como contingencia metodologica.

Nesse cenario alternativo:

- cada item deve ser anotado independentemente por dois avaliadores;
- o acordo inter-anotador deve ser calculado por Cohen's Kappa ponderado quadratico;
- quando `abs(score_annotator_1 - score_annotator_2) >= 2`, os anotadores devem discutir o caso e produzir uma nota consensual;
- a nota consensual resultante da discussao passa a ser usada como `human_consensus_score`;
- a limitacao deve ser registrada no texto do TCC;
- pode ser necessario ajustar o `JudgeValidator`, pois a implementacao atual espera pelo menos tres anotacoes humanas e rejeita numero par de anotadores.

Esse plano nao altera o protocolo preferencial. Ele existe apenas para documentar a decisao metodologica caso a coleta com tres avaliadores se torne inviavel.

## Limitacoes

Esta validacao possui carater exploratorio. As principais limitacoes sao:

- tamanho amostral reduzido;
- possivel vies dos anotadores;
- possivel conhecimento previo dos objetivos do projeto pelos avaliadores;
- ambiguidade inerente a alguns cenarios;
- dependencia da qualidade da rubrica;
- variacao possivel entre provedores e modelos de chatbot;
- interpretacao dos resultados restrita ao contexto do estudo.

Se o Kappa entre anotadores for baixo, especialmente abaixo de 0.4, o resultado deve ser registrado como achado metodologico. Isso pode indicar rubrica ambigua, casos genuinamente dificeis ou diferencas de interpretacao entre anotadores. O resultado nao deve ser tratado automaticamente como falha do framework.

Se muitos itens apresentarem `disagreement_range >= 2`, recomenda-se revisar a rubrica ou discutir a ambiguidade dos cenarios antes de ampliar a coleta.

## Uso dos Resultados no TCC

Os resultados da validacao humana serao usados no TCC para avaliar se o `LLM-as-a-Judge` apresenta concordancia aceitavel com julgamentos humanos em uma amostra controlada de cenarios. Essa analise apoia a discussao sobre a confiabilidade do mecanismo de avaliacao automatizada do framework.

Os resultados nao devem ser apresentados como prova de que os chatbots avaliados sao universalmente confiaveis. A validacao humana incide sobre o juiz automatico e sobre a qualidade do seu alinhamento com anotadores humanos dentro do desenho experimental adotado.

Antes do inicio da coleta definitiva, este protocolo e os templates de anotacao devem ser revisados pela orientadora.
