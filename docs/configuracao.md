# Configuração

A configuração do `llm-eval` é um arquivo YAML validado por
[Pydantic](https://docs.pydantic.dev/) (`llm_eval/config.py`). Campos inválidos ou
formatos não suportados **falham no carregamento**, antes de qualquer chamada à API.

Carregue com `llm-eval run --config config.yaml` ou, em Python, com
`Config.from_yaml("config.yaml")`.

## Estrutura geral

```yaml
provider:        # chatbot a ser avaliado            (obrigatório)
  ...
judge:           # LLM-as-a-Judge                     (obrigatório)
  ...
dimensions:      # dimensões avaliadas                (default: as três)
  - factual
  - consistency
  - robustness
scenarios_path:  # banco de cenários próprio          (default: banco embutido)
repetitions:     # repetições por prompt              (default: 1)
output_dir:      # diretório de saída                 (default: ./results)
output_format:   # formatos de relatório              (default: [json, markdown])
  - json
  - markdown
```

## Referência dos campos

### Raiz

| Campo | Tipo | Default | Descrição |
|---|---|---|---|
| `provider` | mapa | — (obrigatório) | Provider do chatbot avaliado. Ver [`provider`](#provider). |
| `judge` | mapa | — (obrigatório) | Configuração do juiz. Ver [`judge`](#judge). |
| `dimensions` | lista | `[factual, consistency, robustness]` | Dimensões a avaliar. Valores aceitos: `factual`, `consistency`, `robustness`. |
| `scenarios_path` | string | `null` | Diretório com cenários próprios. `null` usa o [banco embutido](banco-de-cenarios.md). |
| `repetitions` | inteiro | `1` | Quantas vezes cada prompt é enviado, para medir variabilidade. |
| `output_dir` | string | `./results` | Onde os relatórios são gravados. |
| `output_format` | lista | `[json, markdown]` | Formatos gerados. Valores aceitos: `json`, `markdown`. |

!!! note "Validações estritas"
    - `dimensions` só aceita `factual`, `consistency` e `robustness` — qualquer outro valor é rejeitado.
    - `output_format` só aceita `json` e `markdown` (case-insensitive). Um typo como `[jsno]` falha em vez de gerar relatório vazio.

### `provider`

Configura o chatbot avaliado. Os campos variam entre os providers nativos
(Gemini, Mistral) e o provider HTTP `custom`. Detalhes e exemplos em
[Providers](providers.md).

| Campo | Tipo | Default | Aplica a | Descrição |
|---|---|---|---|---|
| `type` | string | — (obrigatório) | todos | `gemini`, `mistral` ou `custom`. |
| `model` | string | — (obrigatório) | todos | Nome do modelo. Para `gemini`/`mistral` precisa carregar versão — ver [pin de modelo](#pin-de-modelo). |
| `api_key` | string | `null` | todos | Token de autenticação. Use `${VAR}`. Pode ser `null` no `custom` quando a auth vai por `headers`. |
| `temperature` | float | `0.0` | todos | Temperatura de amostragem. |
| `max_tokens` | inteiro | `1024` | todos | Máximo de tokens na resposta. |
| `seed` | inteiro | `null` | todos | Semente determinística, quando o SDK suporta (Mistral/Custom; Gemini ignora hoje). |
| `url` | string | `null` | custom | Endpoint HTTP do chatbot. |
| `method` | string | `POST` | custom | Método HTTP. |
| `headers` | mapa | `{}` | custom | Cabeçalhos extras (ex.: `Authorization`). |
| `request_template` | mapa | `null` | custom | Corpo da requisição; `{prompt}` é substituído pelo prompt do cenário. |
| `response_path` | string | `null` | custom | Caminho em notação de ponto até o texto da resposta no JSON (ex.: `choices.0.message.content`). |

#### Pin de modelo

Por reprodutibilidade, os providers nativos (`gemini`, `mistral`) **exigem** que o
`model` carregue informação de versão. Duas formas são aceitas:

- **Snapshot (hard pin, preferível):** sufixo datado/numérico — `gemini-2.0-flash-001`, `mistral-small-2503`.
- **Versão menor embutida (soft pin):** `gemini-2.5-flash`, `gemini-1.5-pro`.

São **rejeitados** nomes sem dígitos de versão (`gemini-pro`, `mistral-small`) e
aliases flutuantes (`-latest`, `-stable`), porque o vendor pode mudar os pesos por
trás deles silenciosamente e quebrar a reprodutibilidade.

O provider `custom` é isento — o identificador do modelo pode ser opaco (chatbot
proprietário, deploy interno).

### `judge`

Configura o avaliador LLM-as-a-Judge.

| Campo | Tipo | Default | Descrição |
|---|---|---|---|
| `provider` | mapa | — (obrigatório) | Um bloco `provider` completo (mesmos campos acima) usado como juiz. |
| `enabled` | booleano | `true` | Liga/desliga a avaliação por juiz. |

```yaml
judge:
  enabled: true
  provider:
    type: gemini
    api_key: ${GEMINI_API_KEY}
    model: gemini-2.0-flash
    temperature: 0.0
    max_tokens: 2048
```

!!! tip "Reduzir self-bias"
    Um juiz da mesma família do chatbot tende a favorecer respostas no próprio
    estilo. Para análise mais defensável, use um provider/modelo diferente como juiz
    — ver [Avaliação](avaliacao.md) e o guia de [quality gate](ci-quality-gate-tuning.md).

## Variáveis de ambiente

Qualquer string no YAML pode conter `${VAR}`, resolvido a partir do ambiente no
carregamento. Se a variável não existir, o carregamento falha com erro explícito.

```yaml
provider:
  api_key: ${GEMINI_API_KEY}
  url: ${CHATBOT_URL}
```

## Exemplo completo

```yaml
provider:
  type: gemini
  api_key: ${GEMINI_API_KEY}
  model: gemini-2.0-flash
  temperature: 0.0
  max_tokens: 1024
  seed: 42

judge:
  enabled: true
  provider:
    type: gemini
    api_key: ${GEMINI_API_KEY}
    model: gemini-2.0-flash
    temperature: 0.0
    max_tokens: 2048
    seed: 42

dimensions:
  - factual
  - consistency
  - robustness

scenarios_path: ./meus-cenarios/   # opcional; omita para usar o banco embutido
repetitions: 3
output_dir: ./results
output_format:
  - json
  - markdown
```

Valide sem executar:

```bash
llm-eval validate --config config.yaml
```
