# Avaliação

Cada resposta do chatbot é avaliada por dois mecanismos complementares: o
**LLM-as-a-Judge** (nota ordinal de 1 a 5 com justificativa) e **métricas
computacionais** baseadas em embeddings. O `Runner` orquestra ambos por dimensão e o
`ReportGenerator` consolida no relatório.

## LLM-as-a-Judge

Um LLM atua como avaliador: recebe o prompt, a resposta do chatbot e (quando
aplicável) o `ground_truth`, e devolve uma nota de **1 a 5** com uma justificativa.
A implementação está em `llm_eval/evaluation/judge.py` (`Judge`, `JudgeResult`).

O juiz tem um método por dimensão:

- `evaluate_factual(prompt, ground_truth, response)`
- `evaluate_consistency(prompt, responses)` — recebe as respostas às reformulações
- `evaluate_robustness(prompt, response, ...)` — compara variante perturbada vs. original

### Rubrica 1–5

A mesma escala é usada pelo juiz e pelos anotadores humanos na
[validação humana](protocolo-validacao-humana.md):

| Nota | Significado |
|---|---|
| `1` | Completamente incorreta, contraditória ou degradada |
| `2` | Problemas relevantes, com algum sinal parcial |
| `3` | Qualidade mista, parcialmente correta/consistente/robusta |
| `4` | Majoritariamente boa, com pequenas imperfeições |
| `5` | Correta, consistente ou robusta |

### JSON estrito com parser tolerante

O prompt do juiz pede uma resposta **apenas em JSON válido**
(`{"score": ..., "justification": ...}`). Como LLMs nem sempre obedecem ao formato à
risca, o parser degrada em camadas e **sempre** registra como interpretou em
`parse_method`:

1. **`json`** — JSON estrito sobre o texto (após remover *code fences* ```` ```json ````).
2. **`json_embedded`** — varredura pelo primeiro bloco `{...}` balanceado e válido dentro de texto livre.
3. **`regex`** — *fallback* que extrai `score`/`justification` por expressão regular quando não há JSON parseável.
4. **`default`** — quando nada é extraível, usa uma nota neutra e marca a justificativa como *fallback*.

A nota é **clampada** ao intervalo 1–5 após o parse. Quando o parse não foi por JSON
estrito, isso fica registrado nos metadados do `JudgeResult` para auditoria.

!!! tip "Reduza o self-bias"
    Um juiz da mesma família do chatbot tende a favorecer respostas no próprio
    estilo. Para uma alegação mais defensável, use um provider/modelo diferente como
    juiz e meça a concordância com humanos — ver
    [validação humana](protocolo-validacao-humana.md) e os *trade-offs* de juiz no
    [guia de quality gate](ci-quality-gate-tuning.md).

## Métricas computacionais

Em `llm_eval/evaluation/metrics.py`, complementam o juiz com sinais objetivos.
Todas retornam um `MetricResult` padronizado.

### BERTScore

Similaridade semântica baseada em embeddings (ZHANG et al., 2020), com correlação
superior a métricas lexicais como BLEU/ROUGE. Disponível para um par
(`calculate_bertscore`) ou em lote (`calculate_bertscore_batch`).

### Consistência

`calculate_consistency(responses)` calcula a similaridade semântica **par a par**
entre as respostas dadas às reformulações de um mesmo cenário — quanto mais próximas,
mais consistente o chatbot. É o sinal central da dimensão `consistency`.

### Variância de resposta

`calculate_response_variance(responses)` mede a variabilidade **lexical** entre
respostas (similaridade de Jaccard sobre tokens), sem necessidade de embeddings —
útil como sinal barato de instabilidade.

## Validando o próprio juiz

Antes de confiar nas notas do juiz, dá para medir o quanto ele concorda com humanos.
O comando `validate-judge` compara as notas do juiz com um *golden set* anotado:

```bash
llm-eval validate-judge --provider gemini
```

Saída típica:

```text
Cohen's Kappa: 0.72 (substantial agreement)
Pearson correlation: 0.85
MAE: 0.45
```

O protocolo completo de construção do golden set humano está em
[Validação humana](protocolo-validacao-humana.md).

!!! warning "Golden set embutido é sintético"
    O golden set versionado no repositório serve para exercitar o pipeline e os
    testes — **não** substitui anotações humanas reais. Para uma alegação
    científica, substitua-o por um conjunto anotado por pelo menos 3 humanos por
    cenário.
