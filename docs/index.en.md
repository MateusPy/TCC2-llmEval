---
hide:
  - navigation
  - toc
---

<div class="hero" markdown>
<span class="hero__eyebrow">LLM-as-a-Judge · BERTScore · Reproducible</span>

# Measure the reliability of your LLM chatbot

<p class="hero__subtitle">
Open-source Python framework to assess the <strong>factual accuracy</strong>,
<strong>semantic consistency</strong> and <strong>robustness</strong> of any
LLM-based chatbot — in an automated, comparable and reproducible way.
</p>

<div class="hero__actions" markdown>
[Get started :octicons-arrow-right-24:](metodologia-cenarios.md){ .md-button .md-button--primary }
[View on GitHub](https://github.com/MateusPy/TCC2-llmEval){ .md-button }
</div>
</div>

<p class="landing-tagline" markdown>
Send test scenarios, let a **judge model** grade the answers with the help of
computational metrics, and get **structured reports** — ready to run as a
**quality gate** in your CI pipeline.
</p>

## Three dimensions of reliability

<div class="grid cards" markdown>

-   :material-target-variant:{ .lg .middle } &nbsp;__Factual accuracy__

    ---

    Does the chatbot answer correctly? Responses are compared against a
    **verifiable ground truth**, with trap scenarios to surface hallucination.

    [:octicons-arrow-right-24: Scenario bank](metodologia-cenarios.md)

-   :material-vector-link:{ .lg .middle } &nbsp;__Semantic consistency__

    ---

    Does the same question, asked in different ways, get the same answer? The
    framework sends **rephrasings** and compares the outputs with each other.

    [:octicons-arrow-right-24: How we evaluate](metodologia-cenarios.md)

-   :material-shield-check:{ .lg .middle } &nbsp;__Robustness__

    ---

    Does quality hold up against **noise, typos and adversarial inputs**? The
    variants are compared against the original answer.

    [:octicons-arrow-right-24: Human validation](protocolo-validacao-humana.md)

</div>

## Get started in 2 minutes

=== "Install"

    ```bash
    pip install llm-eval-unb
    ```

=== "Configure (`config.yaml`)"

    ```yaml
    provider:
      type: gemini
      model: gemini-2.0-flash
      api_key: ${GEMINI_API_KEY}
    judge:
      model: gemini-2.0-flash
    dimensions: [factual, consistency, robustness]
    output_dir: results/
    ```

=== "Run"

    ```bash
    export GEMINI_API_KEY=...      # your key via environment variable
    llm-eval run --config config.yaml
    # → results/report.md  +  results/report.json
    ```

!!! tip "CI-ready"
    The same command becomes a **quality gate** that blocks quality
    regressions on every pull request. See the
    [gate calibration guide](ci-quality-gate-tuning.md).

## Where to go next

<div class="grid cards" markdown>

-   :material-flask-outline:{ .lg .middle } &nbsp;__Scenario methodology__

    ---

    How the bank was built and how to point to your own bank via
    `scenarios_path`.

    [:octicons-arrow-right-24: Open](metodologia-cenarios.md)

-   :material-account-check-outline:{ .lg .middle } &nbsp;__Human validation__

    ---

    Human × judge agreement protocol and the annotation templates.

    [:octicons-arrow-right-24: Open](protocolo-validacao-humana.md)

-   :material-pipe:{ .lg .middle } &nbsp;__Quality gate in CI__

    ---

    Calibrate when and how the gate fails in your pipeline.

    [:octicons-arrow-right-24: Open](ci-quality-gate-tuning.md)

-   :material-github:{ .lg .middle } &nbsp;__Code & issues__

    ---

    Contribute, open issues or explore the source code on GitHub.

    [:octicons-arrow-right-24: Repository](https://github.com/MateusPy/TCC2-llmEval)

</div>

!!! note "Documentation in progress"
    This is the first version of the site. Quickstart, configuration reference,
    providers and evaluation details are coming next
    ([issue #71](https://github.com/MateusPy/TCC2-llmEval/issues/71)).

---

`llm-eval` started as an undergraduate thesis (TCC) in Software Engineering at
the **University of Brasília (UnB)**, filling a practical gap: applying LLM
evaluation metrics and criteria in a systematic, accessible way.

> The guide pages below are currently available in Portuguese; English
> translations are on the way.
