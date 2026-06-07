# llm-eval

**Framework open-source para avaliação sistemática da confiabilidade de chatbots
baseados em LLMs.**

O `llm-eval` é um pacote Python que avalia a confiabilidade de qualquer chatbot
baseado em LLM de forma automatizada e reprodutível. Ele envia cenários de teste
ao chatbot, coleta as respostas, avalia usando a estratégia
**LLM-as-a-Judge** combinada com métricas computacionais como **BERTScore**, e
gera relatórios estruturados.

## Dimensões avaliadas

| Dimensão | O que avalia | Como avalia |
|---|---|---|
| **Precisão factual** | O chatbot responde corretamente? | Compara respostas com ground truth verificável |
| **Consistência semântica** | O chatbot dá a mesma resposta para a mesma pergunta feita de formas diferentes? | Envia reformulações e compara respostas entre si |
| **Robustez** | O chatbot mantém a qualidade diante de ruído, typos e inputs adversariais? | Envia variações com erros e compara com a resposta original |

## Instalação

```bash
pip install llm-eval
```

## Como navegar

- **[Metodologia dos cenários](metodologia-cenarios.md)** — como o banco de
  cenários foi construído e como apontar um banco próprio.
- **[Validação humana](protocolo-validacao-humana.md)** — protocolo de
  concordância humano × juiz e os templates de anotação.
- **[Quality gate em CI](ci-quality-gate-tuning.md)** — como calibrar o gate
  que barra regressões de qualidade na pipeline.

!!! note "Documentação em evolução"
    Esta é a estrutura inicial do site. As páginas de guia rápido,
    configuração, providers e avaliação serão adicionadas em seguida
    (issue [#71](https://github.com/MateusPy/TCC2-llmEval/issues/71)).

O projeto nasceu como parte de um Trabalho de Conclusão de Curso em Engenharia
de Software na Universidade de Brasília (UnB). Código-fonte e issues em
[github.com/MateusPy/TCC2-llmEval](https://github.com/MateusPy/TCC2-llmEval).
