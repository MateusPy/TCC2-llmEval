# Guia rápido

Este guia leva você de zero a um relatório de confiabilidade em três passos.
Pré-requisito: [instalação](instalacao.md) feita e uma chave de API exportada.

## 1. Crie um `config.yaml`

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

# Quantas vezes repetir cada prompt (para medir variabilidade)
repetitions: 1

# Saída
output_dir: ./results
output_format:
  - json
  - markdown
```

!!! tip "O juiz precisa de um `provider` completo"
    Diferente de um atalho, o bloco `judge` exige `judge.provider` com `type` e
    `model` próprios — pode ser o mesmo provider do chatbot ou outro, para reduzir
    *self-bias*. Veja a [referência de configuração](configuracao.md).

## 2. Exporte sua chave

```bash
export GEMINI_API_KEY="sua-chave-aqui"
```

## 3. Rode a avaliação

```bash
llm-eval run --config config.yaml
```

Os resultados são gravados em `./results/`:

- `report.json` — consumo programático (resumo + detalhes por cenário)
- `report.md` — leitura humana (tabela-resumo e piores cenários destacados)

## Lendo o relatório

O `report.json` traz um resumo por dimensão:

```json
{
  "summary": {
    "overall_score": 4.22,
    "by_dimension": {
      "factual":     {"mean": 4.53, "median": 5,    "stdev": 0.92, "min": 2,    "max": 5, "count": 35},
      "consistency": {"mean": 4.60, "median": 5,    "stdev": 0.52, "min": 4,    "max": 5, "count": 20},
      "robustness":  {"mean": 3.37, "median": 3.33, "stdev": 0.58, "min": 2.33, "max": 4, "count": 20}
    }
  },
  "details": [ /* uma entrada por cenário, com score e justificativa do juiz */ ]
}
```

Cada dimensão recebe uma nota média de **1 a 5** atribuída pelo
[LLM-as-a-Judge](avaliacao.md). O `report.md` lista os cenários com piores notas
para facilitar a análise.

## Usando como biblioteca Python

O mesmo fluxo, de forma programática:

```python
from llm_eval import Config, Runner, ReportGenerator

config = Config.from_yaml("config.yaml")
result = Runner(config).run()

report = ReportGenerator(result)
report.to_json("results/report.json")
report.to_markdown("results/report.md")
```

Também dá para montar a configuração sem arquivo YAML:

```python
from llm_eval import Config, Runner
from llm_eval.config import ProviderSettings, JudgeSettings

config = Config(
    provider=ProviderSettings(
        type="gemini",
        api_key="sua-chave",
        model="gemini-2.0-flash",
        temperature=0.0,
    ),
    judge=JudgeSettings(
        provider=ProviderSettings(
            type="gemini",
            api_key="sua-chave",
            model="gemini-2.0-flash",
        )
    ),
    dimensions=["factual", "consistency"],
    repetitions=3,
)

result = Runner(config).run()
```

## Outros comandos úteis

```bash
# Validar o config sem executar o pipeline
llm-eval validate --config config.yaml

# Listar o banco de cenários embutido
llm-eval scenarios --list
llm-eval scenarios --dimension factual

# Regenerar um relatório a partir de um resultado salvo
llm-eval report --input results/run_result.json --format markdown --output report.md
```

## Próximos passos

- [Configuração](configuracao.md) — todos os campos do `config.yaml`
- [Banco de cenários](banco-de-cenarios.md) — use seus próprios cenários via `scenarios_path`
- [Quality gate em CI](ci-quality-gate-tuning.md) — rode o mesmo comando como portão de qualidade em PRs
