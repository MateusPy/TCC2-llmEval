# Providers

Um *provider* é o adaptador que conecta o `llm-eval` ao chatbot avaliado. O
framework traz três tipos: dois nativos (**Gemini** e **Mistral**) e um **HTTP
genérico** (`custom`) para qualquer endpoint REST. O mesmo bloco `provider` também é
usado para configurar o [juiz](avaliacao.md).

## Google Gemini

```yaml
provider:
  type: gemini
  api_key: ${GEMINI_API_KEY}
  model: gemini-2.0-flash
  temperature: 0.0
  max_tokens: 1024
```

Requer `google-generativeai` (instalado com o pacote). O `model` precisa carregar
versão — `gemini-2.0-flash` e `gemini-2.5-flash` são aceitos; `gemini-pro` e
`gemini-flash-latest` são rejeitados (ver [pin de modelo](configuracao.md#pin-de-modelo)).

## Mistral AI

```yaml
provider:
  type: mistral
  api_key: ${MISTRAL_API_KEY}
  model: mistral-small-2503
  temperature: 0.0
  max_tokens: 1024
```

Requer `mistralai` (instalado com o pacote). Use um snapshot datado como
`mistral-small-2503` — aliases como `mistral-small-latest` são **rejeitados** por
não fixarem os pesos do modelo.

## Custom (qualquer endpoint HTTP)

Para avaliar qualquer chatbot com uma API REST — incluindo um deploy interno ou
proprietário:

```yaml
provider:
  type: custom
  url: https://meu-chatbot.com/api/chat
  model: meu-chatbot-v1            # identificador livre — só para rastreabilidade
  method: POST
  headers:
    Authorization: Bearer ${CUSTOM_API_KEY}
  request_template:
    messages:
      - role: user
        content: "{prompt}"
    temperature: 0.0
  response_path: choices.0.message.content
```

Como funciona:

- **`{prompt}`** dentro de `request_template` é substituído pelo prompt de cada
  cenário antes de enviar a requisição.
- **`response_path`** indica onde, no JSON de resposta, está o texto a avaliar. Usa
  notação de ponto com índices numéricos — `choices.0.message.content` lê
  `resposta["choices"][0]["message"]["content"]`.
- A autenticação pode ir em `headers` (como acima) em vez de `api_key`, que então
  pode ficar ausente.

O provider `custom` é **isento da exigência de pin de modelo**: você controla o
endpoint e o identificador do modelo pode ser opaco.

!!! tip "Avaliando um chatbot local em CI"
    No quality gate, o provider `custom` aponta para o chatbot subido localmente na
    própria pipeline (ex.: `http://localhost:8000/...`). Veja o exemplo vivo em
    [`examples/demo-chatbot/`](https://github.com/MateusPy/TCC2-llmEval/tree/main/examples/demo-chatbot)
    e o guia de [quality gate em CI](ci-quality-gate-tuning.md).

## Campos comuns

Todos os providers aceitam `temperature`, `max_tokens` e `seed`. A referência
completa de cada campo está em [Configuração → `provider`](configuracao.md#provider).

| Provider | SDK / mecanismo | `api_key` | Pin de modelo |
|---|---|---|---|
| `gemini` | `google-generativeai` | obrigatória | exigido |
| `mistral` | `mistralai` | obrigatória | exigido |
| `custom` | HTTP via `httpx` | opcional (ou via `headers`) | isento |
