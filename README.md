# 🔍 llm-eval

**Framework open-source para avaliação sistemática da confiabilidade de chatbots baseados em LLMs.**

[![CI](https://github.com/MateusPy/TCC2-llmEval/actions/workflows/ci.yml/badge.svg)](https://github.com/MateusPy/TCC2-llmEval/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow.svg)]()

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

Para desenvolvimento local:

```bash
git clone https://github.com/seu-usuario/llm-eval.git
cd llm-eval
pip install -e ".[dev]"
```

---

## Quick Start

### 1. Crie um arquivo de configuração

```yaml
# config.yaml

# Chatbot a ser avaliado
provider:
  type: gemini
  api_key: "${GEMINI_API_KEY}"
  model: gemini-2.0-flash
  temperature: 0.0
  max_tokens: 1024

# LLM usado como juiz (avaliador)
judge:
  enabled: true
  provider:
    type: gemini
    api_key: "${GEMINI_API_KEY}"
    model: gemini-2.0-flash
    temperature: 0.0
    max_tokens: 2048

# Dimensões a avaliar
dimensions:
  - factual
  - consistency
  - robustness

# Quantas vezes repetir cada prompt (para medir variabilidade)
repetitions: 3

# Saída
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

Os resultados serão salvos em `./results/`.

---

## Uso como biblioteca Python

```python
from llm_eval import Config, Runner, ReportGenerator

# Carregar configuração
config = Config.from_yaml("config.yaml")

# Executar avaliação
result = Runner(config).run()

# Gerar relatórios
report = ReportGenerator(result)
report.to_json("results/report.json")
report.to_markdown("results/report.md")
```

Também é possível configurar programaticamente, sem arquivo YAML:

```python
from llm_eval.config import Config, ProviderSettings, JudgeSettings

config = Config(
    provider=ProviderSettings(
        type="gemini",
        api_key="sua-key",
        model="gemini-2.0-flash",
        temperature=0.0,
    ),
    judge=JudgeSettings(
        provider=ProviderSettings(
            type="gemini",
            api_key="sua-key",
            model="gemini-2.0-flash",
        )
    ),
    dimensions=["factual", "consistency"],
    repetitions=3,
)

result = Runner(config).run()
```

---

## Integração com CI/CD

### GitHub Actions

```yaml
# .github/workflows/llm-eval.yml
name: Avaliação de Confiabilidade

on:
  push:
    branches: [main]
  schedule:
    - cron: '0 6 * * 1'  # toda segunda às 6h

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Instalar llm-eval
        run: pip install llm-eval

      - name: Executar avaliação
        run: llm-eval run --config config.yaml
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}

      - name: Upload relatório
        uses: actions/upload-artifact@v4
        with:
          name: llm-eval-report
          path: results/
```

### GitLab CI

```yaml
# .gitlab-ci.yml
llm-eval:
  image: python:3.11
  script:
    - pip install llm-eval
    - llm-eval run --config config.yaml
  artifacts:
    paths:
      - results/
  variables:
    GEMINI_API_KEY: $GEMINI_API_KEY
```

---

## Providers

O llm-eval suporta três tipos de providers para se conectar a diferentes chatbots:

### Google Gemini

```yaml
provider:
  type: gemini
  api_key: "${GEMINI_API_KEY}"
  model: gemini-2.0-flash
  temperature: 0.0
  max_tokens: 1024
```

### Mistral AI

```yaml
provider:
  type: mistral
  api_key: "${MISTRAL_API_KEY}"
  model: mistral-small-latest
  temperature: 0.0
  max_tokens: 1024
```

### Custom (qualquer endpoint HTTP)

Para avaliar qualquer chatbot que tenha uma API REST:

```yaml
provider:
  type: custom
  url: "https://meu-chatbot.com/api/chat"
  method: POST
  headers:
    Authorization: "Bearer ${CUSTOM_API_KEY}"
  request_template:
    messages:
      - role: "user"
        content: "{prompt}"
    temperature: 0.0
  response_path: "choices.0.message.content"
```

O campo `{prompt}` no `request_template` é substituído pelo prompt do cenário. O `response_path` indica onde no JSON de resposta está o texto (suporta notação de ponto e índices numéricos).

---

## Banco de Cenários

O llm-eval vem com um banco de cenários embutido organizado por dimensão. Para listar os cenários disponíveis:

```bash
# Listar dimensões
llm-eval scenarios --list

# Listar cenários de uma dimensão
llm-eval scenarios --dimension factual
```

### Categorias dos cenários

| Categoria | Descrição | Exemplo |
|---|---|---|
| `knowledge` | Fatos verificáveis | "Qual é a capital da Austrália?" |
| `reasoning` | Raciocínio lógico | "Se A implica B e B implica C, A implica C?" |
| `math` | Cálculos | "Quanto é 15% de 200?" |
| `comprehension` | Compreensão de texto | "Leia o trecho e responda..." |
| `common_sense` | Senso comum | "O que acontece se deixar gelo no sol?" |
| `instruction` | Seguir instruções | "Resuma em uma frase: ..." |

### Cenários customizados

Você pode criar seus próprios cenários. Basta seguir o formato JSON:

```json
{
  "dimension": "factual",
  "version": "1.0.0",
  "scenarios": [
    {
      "id": "custom-001",
      "dimension": "factual",
      "category": "knowledge",
      "prompt": "Sua pergunta aqui",
      "ground_truth": "Resposta esperada",
      "variants": []
    }
  ]
}
```

E referenciar no config:

```yaml
scenarios_path: ./meus-cenarios/
```

---

## Relatórios

### JSON (consumo programático)

```json
{
  "metadata": {
    "framework_version": "0.1.0",
    "provider": "gemini",
    "model": "gemini-2.0-flash",
    "total_scenarios": 30
  },
  "summary": {
    "overall_score": 4.2,
    "by_dimension": {
      "factual": { "mean": 4.5, "median": 5.0, "stdev": 0.7 },
      "consistency": { "mean": 4.0, "median": 4.0, "stdev": 0.8 },
      "robustness": { "mean": 4.1, "median": 4.0, "stdev": 0.9 }
    }
  },
  "details": [...]
}
```

### Markdown (leitura humana)

O relatório em Markdown inclui tabela resumo, detalhes por dimensão e os cenários com piores scores destacados para facilitar a análise.

---

## Validação do Juiz

O módulo de **LLM-as-a-Judge** pode ser validado contra um *golden set* anotado por humanos para medir concordância acima do nível de chance. O framework agora inclui:

- um dataset embutido em `llm_eval/scenarios/golden/golden_set.json`
- o módulo `llm_eval.evaluation.validation`
- o comando CLI `llm-eval validate-judge`

### Protocolo de anotação

Cada cenário do golden set deve conter:

- `prompt`
- `dimension`
- a resposta do chatbot a ser julgada
- pelo menos **3 anotações humanas**
- `human_consensus_score`, calculado como a mediana dos scores humanos

Rubrica 1-5 usada por humanos e pelo juiz:

- `1`: completamente incorreta, contraditória ou degradada
- `2`: resposta com problemas relevantes, mas com algum sinal parcial
- `3`: qualidade mista, parcialmente correta/consistente/robusta
- `4`: majoritariamente boa, com pequenas imperfeições
- `5`: correta, consistente ou robusta

### Executando a validação

```bash
llm-eval validate-judge --provider gemini
```

Opcionalmente, você pode apontar para um golden set externo:

```bash
llm-eval validate-judge \
  --provider gemini \
  --golden-set path/to/golden_set.json \
  --output results/validation_report.json
```

Saída esperada:

```text
Cohen's Kappa: 0.72 (substantial agreement)
Pearson correlation: 0.85
MAE: 0.45
```

O relatório salvo em `results/validation_report.json` inclui:

- `cohen_kappa`
- `pearson_correlation`
- `mae`
- métricas por dimensão
- cenários com divergência `>= 2` pontos entre juiz e consenso humano
- detalhamento por cenário para análise qualitativa

### Observação importante sobre o dataset embutido

O golden set versionado no repositório é **sintético** e serve para:

- exercitar o pipeline de validação fim a fim
- permitir testes automatizados
- documentar o formato esperado do dataset

Ele **não substitui** um golden set com anotações humanas reais. Para uma alegação cientificamente defensável no TCC, substitua esse arquivo por um conjunto anotado por pelo menos 3 humanos por cenário e registre no README os valores reais obtidos para Kappa, correlação e MAE.

### Limitações

- **Self-bias:** um juiz Gemini pode tender a favorecer respostas geradas por modelos da mesma família.
- **Calibração da escala:** scores 1-5 podem ser interpretados de forma ligeiramente diferente por modelos diferentes.
- **Variância:** mesmo com `temperature=0`, respostas do juiz podem variar dependendo do provider.
- **Golden set sintético:** o dataset embutido ajuda no desenvolvimento, mas a validação científica depende de anotações humanas reais.

---

## CLI - Comandos Disponíveis

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
llm-eval report --input results.json --format markdown --output report.md

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

## Dependências

| Pacote | Uso |
|---|---|
| `google-generativeai` | Provider do Google Gemini |
| `mistralai` | Provider da Mistral AI |
| `httpx` | Provider customizado (HTTP) |
| `bert-score` | Métrica de similaridade semântica |
| `pydantic` | Validação de dados e schemas |
| `click` | Interface de linha de comando |
| `pyyaml` | Leitura de configurações YAML |

---

## Contribuindo

Contribuições são bem-vindas! Veja o [CONTRIBUTING.md](CONTRIBUTING.md) para detalhes sobre como configurar o ambiente de desenvolvimento, rodar os testes e enviar pull requests.

```bash
# Clonar e instalar em modo dev
git clone https://github.com/seu-usuario/llm-eval.git
cd llm-eval
pip install -e ".[dev]"

# Rodar testes
pytest

# Rodar linter
ruff check .
```

### Como adicionar um novo provider

1. Crie um arquivo em `llm_eval/providers/`
2. Estenda a classe `BaseProvider`
3. Implemente o método `send(prompt: str) -> ProviderResponse`
4. Registre no factory de providers

---

## Roadmap

- [x] Arquitetura e estrutura do pacote
- [ ] Providers (Gemini, Mistral, Custom)
- [ ] Banco de cenários embutido
- [ ] Módulo de avaliação (LLM-as-a-Judge + BERTScore)
- [ ] Runner e relatórios
- [ ] CLI
- [ ] Publicação no PyPI
- [ ] Suporte a mais dimensões (imparcialidade, segurança)
- [ ] Dashboard web para visualização de resultados

---

## Contexto Acadêmico

Este projeto foi desenvolvido como parte do Trabalho de Conclusão de Curso intitulado **"Avaliação Sistemática da Confiabilidade de Chatbots baseados LLMs: Um Processo Reprodutível de Verificação da Qualidade"**, no curso de Engenharia de Software da Universidade de Brasília (UnB).

**Autores:** Mateus Orlando Medeiros Ribeiro e Johnny Da Ponte Lopes
**Orientadora:** Profa. Dra. Elaine Venson

---

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).
