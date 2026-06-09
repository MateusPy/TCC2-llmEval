# Changelog

Todas as mudanças notáveis deste projeto são documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e o projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Não lançado]

## [0.1.0] - 2026-06-09

Primeira versão pública do `llm-eval`, framework open-source para avaliação de
confiabilidade de chatbots baseados em LLMs.

### Adicionado
- Pipeline de avaliação de confiabilidade com as dimensões de **consistência**,
  **factualidade** e **robustez**.
- **LLM-as-a-judge**: avaliação das respostas do chatbot por um LLM juiz configurável.
- Métrica de similaridade semântica via **BERTScore**.
- Bancos de cenários embutidos (`bank/`) e *golden set* (`golden/`) distribuídos
  junto do pacote.
- Providers integrados: **Google Gemini**, **Mistral AI** e endpoint HTTP **custom**.
- CLI `llm-eval` com os comandos `run`, `validate`, `scenarios`, `validate-judge`
  e `report`.
- Relatórios em **JSON** (consumo programático) e **Markdown** (leitura humana).
- *Quality gate* para CI/CD com falha em regressão (GitHub Actions e GitLab CI).
- Validação do juiz contra anotações humanas (concordância judge × humano).
- Configuração declarativa via arquivo YAML.

[Não lançado]: https://github.com/MateusPy/TCC2-llmEval/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/MateusPy/TCC2-llmEval/releases/tag/v0.1.0
