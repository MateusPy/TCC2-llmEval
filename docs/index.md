---
hide:
  - navigation
  - toc
---

<div class="hero" markdown>
<span class="hero__eyebrow">LLM-as-a-Judge · BERTScore · Reprodutível</span>

# Avalie a confiabilidade do seu chatbot LLM

<p class="hero__subtitle">
Framework open-source em Python para medir <strong>precisão factual</strong>,
<strong>consistência semântica</strong> e <strong>robustez</strong> de qualquer
chatbot baseado em LLM — de forma automatizada, comparável e reprodutível.
</p>

<div class="hero__actions" markdown>
[Começar agora :octicons-arrow-right-24:](quickstart.md){ .md-button .md-button--primary }
[Ver no GitHub](https://github.com/MateusPy/TCC2-llmEval){ .md-button }
</div>
</div>

<p class="landing-tagline" markdown>
Envie cenários de teste, deixe um **modelo-juiz** avaliar as respostas com apoio
de métricas computacionais e receba **relatórios estruturados** — pronto para
rodar como _quality gate_ na sua pipeline de CI.
</p>

## Três dimensões de confiabilidade

<div class="grid cards" markdown>

-   :material-target-variant:{ .lg .middle } &nbsp;__Precisão factual__

    ---

    O chatbot responde corretamente? As respostas são comparadas com um
    **ground truth verificável**, com cenários-armadilha para flagrar
    alucinação.

    [:octicons-arrow-right-24: Banco de cenários](metodologia-cenarios.md)

-   :material-vector-link:{ .lg .middle } &nbsp;__Consistência semântica__

    ---

    A mesma pergunta, feita de formas diferentes, recebe a mesma resposta? O
    framework envia **reformulações** e compara as saídas entre si.

    [:octicons-arrow-right-24: Como avaliamos](metodologia-cenarios.md)

-   :material-shield-check:{ .lg .middle } &nbsp;__Robustez__

    ---

    A qualidade se mantém diante de **ruído, typos e inputs adversariais**? As
    variantes são comparadas com a resposta original.

    [:octicons-arrow-right-24: Validação humana](protocolo-validacao-humana.md)

</div>

## Comece em 2 minutos

=== "Instalar"

    ```bash
    pip install llm-eval-unb
    ```

=== "Configurar (`config.yaml`)"

    ```yaml
    provider:
      type: gemini
      model: gemini-2.0-flash
      api_key: ${GEMINI_API_KEY}
    judge:
      provider:
        type: gemini
        model: gemini-2.0-flash
        api_key: ${GEMINI_API_KEY}
    dimensions: [factual, consistency, robustness]
    output_dir: results/
    ```

=== "Rodar"

    ```bash
    export GEMINI_API_KEY=...      # sua chave por variável de ambiente
    llm-eval run --config config.yaml
    # → results/report.md  +  results/report.json
    ```

!!! tip "Pronto para CI"
    O mesmo comando vira um **quality gate** que barra regressões de qualidade
    em cada pull request. Veja o guia de
    [calibração do gate](ci-quality-gate-tuning.md).

## Por onde seguir

<div class="grid cards" markdown>

-   :material-rocket-launch-outline:{ .lg .middle } &nbsp;__Guia rápido__

    ---

    Do zero a um relatório de confiabilidade em três passos.

    [:octicons-arrow-right-24: Abrir](quickstart.md)

-   :material-tune:{ .lg .middle } &nbsp;__Configuração__

    ---

    Referência completa do `config.yaml`: provider, juiz, dimensões e saída.

    [:octicons-arrow-right-24: Abrir](configuracao.md)

-   :material-connection:{ .lg .middle } &nbsp;__Providers__

    ---

    Gemini, Mistral e o provider HTTP genérico para qualquer endpoint.

    [:octicons-arrow-right-24: Abrir](providers.md)

-   :material-scale-balance:{ .lg .middle } &nbsp;__Avaliação__

    ---

    LLM-as-a-Judge (rubrica 1–5) e métricas computacionais como o BERTScore.

    [:octicons-arrow-right-24: Abrir](avaliacao.md)

-   :material-pipe:{ .lg .middle } &nbsp;__Quality gate em CI__

    ---

    Calibre quando e como o gate falha na sua pipeline.

    [:octicons-arrow-right-24: Abrir](ci-quality-gate-tuning.md)

-   :material-account-check-outline:{ .lg .middle } &nbsp;__Validação humana__

    ---

    Protocolo de concordância humano × juiz e os templates de anotação.

    [:octicons-arrow-right-24: Abrir](protocolo-validacao-humana.md)

</div>

---

O `llm-eval` nasceu como Trabalho de Conclusão de Curso em Engenharia de Software
na **Universidade de Brasília (UnB)**, preenchendo uma lacuna prática: aplicar,
de forma sistemática e acessível, métricas e critérios de avaliação de LLMs.
