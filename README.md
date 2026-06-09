# 🔍 llm-eval

**Framework open-source para avaliação sistemática da confiabilidade de chatbots baseados em LLMs.**

[![CI](https://github.com/MateusPy/TCC2-llmEval/actions/workflows/ci.yml/badge.svg)](https://github.com/MateusPy/TCC2-llmEval/actions/workflows/ci.yml)
[![Docs](https://github.com/MateusPy/TCC2-llmEval/actions/workflows/docs.yml/badge.svg)](https://mateuspy.github.io/TCC2-llmEval/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow.svg)]()

📚 **Documentação completa:** <https://mateuspy.github.io/TCC2-llmEval/>

---

## Sobre

O `llm-eval` é um pacote Python que permite avaliar a confiabilidade de qualquer chatbot baseado em LLM de forma automatizada e reprodutível. Ele envia cenários de teste ao chatbot, coleta as respostas, avalia usando a estratégia **LLM-as-a-Judge** combinada com métricas computacionais como **BERTScore**, e gera relatórios estruturados.

O framework avalia três dimensões de confiabilidade:

| Dimensão | O que avalia | Como avalia |
|---|---|---|
| **Precisão Factual** | O chatbot responde corretamente? | Compara respostas com ground truth verificável |
| **Consistência Semântica** | O chatbot dá a mesma resposta para a mesma pergunta feita de formas diferentes? | Envia reformulações e compara respostas entre si |
| **Robustez** | O chatbot mantém a qualidade diante de ruído, typos e inputs adversariais? | Envia variações com erros e compara com a resposta original |

O projeto nasceu como parte de um Trabalho de Conclusão de Curso em Engenharia de Software na Universidade de Brasília (UnB), com o objetivo de preencher uma lacuna prática: embora a literatura proponha métricas e critérios para avaliar LLMs, faltam ferramentas acessíveis que permitam aplicá-los de forma sistemática.

---

## Instalação

```bash
pip install llm-eval
```

Requer **Python 3.11+**. Guia completo (extras de dev, chaves por variável de ambiente): [Instalação](https://mateuspy.github.io/TCC2-llmEval/instalacao/).

---

## Quick Start

### 1. Crie um arquivo de configuração

```yaml
# config.yaml

# Chatbot a ser avaliado
provider:
  type: gemini
  api_key: ${GEMINI_API_KEY}
  model: gemini-2.0-flash
  temperature: 0.0
  max_tokens: 1024

# LLM usado como juiz (avaliador)
judge:
  enabled: true
  provider:
    type: gemini
    api_key: ${GEMINI_API_KEY}
    model: gemini-2.0-flash
    temperature: 0.0
    max_tokens: 2048

# Dimensões a avaliar
dimensions:
  - factual
  - consistency
  - robustness

repetitions: 1
output_dir: ./results
output_format:
  - json
  - markdown
```

### 2. Defina sua API key

```bash
export GEMINI_API_KEY="sua-api-key-aqui"
```

### 3. Execute a avaliação

```bash
llm-eval run --config config.yaml
```

Os resultados são salvos em `./results/` — `report.json` (programático) e `report.md` (leitura humana). Passo a passo detalhado em [Guia rápido](https://mateuspy.github.io/TCC2-llmEval/quickstart/).

### Uso como biblioteca Python

```python
from llm_eval import Config, Runner, ReportGenerator

config = Config.from_yaml("config.yaml")
result = Runner(config).run()

report = ReportGenerator(result)
report.to_json("results/report.json")
report.to_markdown("results/report.md")
```

---

## Documentação

A referência completa fica no **[site de documentação](https://mateuspy.github.io/TCC2-llmEval/)**:

- [**Instalação**](https://mateuspy.github.io/TCC2-llmEval/instalacao/) — requisitos, extras e chaves por variável de ambiente.
- [**Guia rápido**](https://mateuspy.github.io/TCC2-llmEval/quickstart/) — do zero a um relatório em três passos.
- [**Configuração**](https://mateuspy.github.io/TCC2-llmEval/configuracao/) — referência de todos os campos do `config.yaml`.
- [**Providers**](https://mateuspy.github.io/TCC2-llmEval/providers/) — Gemini, Mistral e o provider HTTP genérico (`custom`).
- [**Banco de cenários**](https://mateuspy.github.io/TCC2-llmEval/banco-de-cenarios/) — formato dos cenários e como usar um banco próprio via `scenarios_path`.
- [**Avaliação**](https://mateuspy.github.io/TCC2-llmEval/avaliacao/) — LLM-as-a-Judge (rubrica 1–5) e métricas como BERTScore.
- [**Quality gate em CI**](https://mateuspy.github.io/TCC2-llmEval/ci-quality-gate-tuning/) — rode o mesmo comando como portão de qualidade em PRs.
- [**Validação humana**](https://mateuspy.github.io/TCC2-llmEval/protocolo-validacao-humana/) — concordância humano × juiz e templates de anotação.

O exemplo vivo de um chatbot avaliado em CI está em [`examples/demo-chatbot/`](examples/demo-chatbot/).

---

## CLI — comandos disponíveis

```bash
# Executar avaliação completa
llm-eval run --config config.yaml

# Validar configuração sem executar
llm-eval validate --config config.yaml

# Listar cenários disponíveis
llm-eval scenarios --list
llm-eval scenarios --dimension factual

# Validar o juiz contra um golden set
llm-eval validate-judge --provider gemini

# Regenerar relatório a partir de resultados salvos
llm-eval report --input results/run_result.json --format markdown --output report.md

# Ver versão
llm-eval --version
```

---

## Como funciona

```
                          ┌─────────────────┐
                          │   config.yaml   │
                          └────────┬────────┘
                                   │
                                   ▼
                          ┌─────────────────┐
                          │     Runner      │
                          └────────┬────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
                    ▼              ▼              ▼
             ┌───────────┐ ┌───────────┐ ┌───────────┐
             │  Factual  │ │Consistency│ │ Robustness│
             │ Scenarios │ │ Scenarios │ │ Scenarios │
             └─────┬─────┘ └─────┬─────┘ └─────┬─────┘
                   │             │             │
                   ▼             ▼             ▼
             ┌─────────────────────────────────────┐
             │            Provider                 │
             │   (Gemini / Mistral / Custom)       │
             └──────────────────┬──────────────────┘
                                │
                                ▼
             ┌─────────────────────────────────────┐
             │           Evaluation                │
             │  ┌──────────┐  ┌─────────────────┐  │
             │  │  Judge   │  │    Metrics       │  │
             │  │(LLM-as-a-│  │  (BERTScore,    │  │
             │  │  Judge)  │  │   Variance)     │  │
             │  └──────────┘  └─────────────────┘  │
             └──────────────────┬──────────────────┘
                                │
                                ▼
             ┌─────────────────────────────────────┐
             │         Report Generator            │
             │     (JSON + Markdown output)        │
             └─────────────────────────────────────┘
```

---

## Requisitos

- Python 3.11 ou superior
- API key de pelo menos um provider (Gemini, Mistral ou endpoint customizado)
- API key para o LLM-as-a-Judge (pode ser o mesmo provider)

---

## Contribuindo

Contribuições são bem-vindas! Veja o [CONTRIBUTING.md](CONTRIBUTING.md) para o guia completo — setup do ambiente, padrões de código, testes e fluxo de PR.

Como você não tem permissão de push no repositório principal, comece pelo **fork**:

```bash
# Faça o fork em github.com/MateusPy/TCC2-llmEval e clone o SEU fork
git clone https://github.com/<seu-usuario>/TCC2-llmEval.git
cd TCC2-llmEval

# Ambiente + instalação editável com deps de dev
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Rodar testes e linter
pytest
ruff check .
```

---

## Roadmap

- [x] Arquitetura e estrutura do pacote
- [x] Providers (Gemini, Mistral, Custom)
- [x] Banco de cenários embutido
- [x] Módulo de avaliação (LLM-as-a-Judge + BERTScore)
- [x] Runner e relatórios
- [x] CLI
- [x] Site de documentação
- [ ] Publicação no PyPI
- [ ] Suporte a mais dimensões (imparcialidade, segurança)
- [ ] Dashboard web para visualização de resultados

---

## Contexto Acadêmico

Este projeto foi desenvolvido como parte do Trabalho de Conclusão de Curso intitulado **"Avaliação Sistemática da Confiabilidade de Chatbots baseados LLMs: Um Processo Reprodutível de Verificação da Qualidade"**, no curso de Engenharia de Software da Universidade de Brasília (UnB).

**Autores:** Mateus Orlando Medeiros Ribeiro e Johnny Da Ponte Lopes
**Orientador:** Profa. Dra. Elaine Venson

---

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).
