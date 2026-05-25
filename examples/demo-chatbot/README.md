# Demo Chatbot — Tutor de Python

Chatbot mínimo que serve como **template de adoção** do [llm-eval](../../README.md): mostra como integrar o framework como _quality gate_ no CI do seu próprio chatbot.

A persona é um tutor de Python para iniciantes (PT-BR), mas o ponto não é a persona — é a forma de plugá-la no `llm-eval`. Copie esta pasta para o seu repo, troque ~5 coisas óbvias (system prompt, modelo, cenários, paths) e o gate roda contra o seu chatbot.

---

## Rodando o exemplo

### Pré-requisitos

- Python 3.11+
- Conta gratuita em https://console.groq.com (chave do LLM por trás do chatbot — Llama 3.1 8B).
- Conta em https://aistudio.google.com/app/apikey (chave do juiz Gemini).
- `llm-eval` instalado no ambiente (a partir da raiz do repo: `pip install -e .`).

### 4 comandos

```bash
# 1. Instale as deps do chatbot (a partir da raiz do repo)
pip install -e ./examples/demo-chatbot

# 2. Exporte as duas chaves
export GROQ_API_KEY=gsk_...
export GEMINI_API_KEY=AI...

# 3. Suba o chatbot em background
uvicorn chatbot.main:app --app-dir examples/demo-chatbot --port 8000 &

# 4. Rode a avaliação
llm-eval run --config examples/demo-chatbot/config.yaml
```

Saídas em `examples/demo-chatbot/results/`:

- `report.md` — sumário humano (score por dimensão, exemplos de falhas).
- `report.json` — mesmo conteúdo em JSON (consumido pelo gate no CI).
- `run_result.json` — todos os 95 prompts com resposta crua e justificativa do juiz.

---

## Adaptando para o seu chatbot

A ideia é que você não precise entender o `llm-eval` por dentro — só plugar 4 coisas.

### 1. Seu endpoint HTTP

O `llm-eval` usa o `CustomProvider`, que fala HTTP com **qualquer chatbot** desde que ele responda assim:

```http
POST /chat  HTTP/1.1
Content-Type: application/json

{"prompt": "como faço um for em Python?"}

---

200 OK
Content-Type: application/json

{"response": "Em Python, o for percorre um iterável..."}
```

Se o seu endpoint já tem essa cara, vá pro passo 2. Se o shape é diferente, mexa em duas linhas do `config.yaml`:

```yaml
provider:
  type: custom
  url: "http://localhost:8000/sua-rota"
  request_template:
    user_message: "{prompt}"      # mapeia "prompt" → o campo que seu endpoint espera
    session: "default"            # campos estáticos extras vão aqui
  response_path: "data.reply"     # caminho dot-notation pro texto da resposta
```

O `{prompt}` é o único placeholder reconhecido — pode aparecer em strings aninhadas em qualquer lugar do `request_template`. O `response_path` aceita dicionários (`a.b.c`) e índices de lista (`choices.0.text`).

### 2. Seus cenários

Os cenários são onde mora a "qualidade" do seu chatbot: cada prompt tem uma resposta esperada (`ground_truth`) ou um comportamento esperado, e o juiz LLM compara.

Comece pequeno — `5 factual + 3 consistency + 3 robustness` já dá pra calibrar o gate em uma tarde. Estrutura mínima:

```json
{
  "dimension": "factual",
  "version": "0.1.0",
  "scenarios": [
    {
      "id": "factual-001",
      "dimension": "factual",
      "category": "meu_dominio",
      "prompt": "Qual é o horário de funcionamento do suporte?",
      "ground_truth": "Segunda a sexta, das 9h às 18h.",
      "variants": [],
      "source": "https://meudominio.com/faq#horarios"
    }
  ]
}
```

Os arquivos deste exemplo (`scenarios/{factual,consistency,robustness}.json`) servem de molde. Para autoração séria de cenários, leia [`docs/metodologia-cenarios.md`](../../docs/metodologia-cenarios.md) — descreve os 4 critérios de validação que um cenário precisa passar antes de virar gate.

### 3. Seu juiz

O `judge.provider` no `config.yaml` usa o mesmo schema do `provider`. Recomendações:

| Caso | Juiz recomendado | Custo aproximado por run de 95 prompts |
|---|---|---|
| **Default / CI** | `gemini-2.5-flash-lite` | grátis no free tier (60 req/min) |
| Análise empírica | `gemini-2.0-flash-001` ou Mistral pequeno | até US$ 0,10 |
| Comparação cross-provider | Use o **mesmo** juiz para todos os chatbots avaliados (controla viés) | depende do volume |

Se seu chatbot **é** Gemini, evite usar Gemini como juiz (auto-favorecimento). Esse é um trade-off documentado na §10 do `docs/metodologia-cenarios.md`.

### 4. Seu gate em CI

A peça mais importante. Veja o job `eval-gate` em [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml) (raiz do repo) — é a referência viva. Há também um snippet copy-pasteável genérico no [README principal](../../README.md#using-llm-eval-as-a-ci-quality-gate).

Pontos sensíveis:

- **Roda por último.** Use `needs: [lint, test, type-check, ...]` — se os outros falham, o gate nem queima quota.
- **Filtre por path.** Use `dorny/paths-filter` pra disparar só quando o chatbot ou o framework muda — PR de docs não precisa de gate.
- **Threshold por env var.** `EVAL_THRESHOLD: '3.0'` no job (calibrado a partir do [primeiro smoke test](SMOKE_TEST_ANALYSIS.md)). Rode o pipeline ≥3x antes de recalibrar — use `piso_observado − 0.3` como referência. Detalhes de todos os knobs que afetam o gate em [`docs/ci-quality-gate-tuning.md`](../../docs/ci-quality-gate-tuning.md).
- **Secrets.** Adicione `GROQ_API_KEY` (ou equivalente do seu LLM) e `GEMINI_API_KEY` em **Repository Settings → Secrets and variables → Actions** antes do primeiro PR.

---

## Estrutura do diretório

```
examples/demo-chatbot/
├── README.md               # este arquivo
├── pyproject.toml          # deps do chatbot (separado do llm-eval)
├── config.yaml             # config do llm-eval apontando pro chatbot
├── chatbot/                # código do chatbot (substitua pelo seu)
│   ├── main.py             # FastAPI: GET /health, POST /chat
│   ├── llm.py              # wrapper do LLM (aqui: Groq)
│   ├── retry.py            # retry minimalista para 429s
│   └── prompts.py          # SYSTEM_PROMPT versionado
├── tests/                  # testes unitários do chatbot
│   └── test_main.py
├── scenarios/              # banco de cenários do domínio
│   ├── factual.json        # 15 cenários
│   ├── consistency.json    # 10 bases × 4 paráfrases = 40 prompts
│   └── robustness.json     # 10 bases × 4 variantes = 40 prompts
├── scripts/
│   └── check_gate.py       # parser do report.json para o CI gate (Fase 4)
└── results/                # gerado pelo llm-eval (gitignored por padrão)
```

Tudo dentro de `chatbot/`, `scenarios/` e `prompts.py` é específico do tutor de Python — troque pelo seu domínio. O resto (`config.yaml`, `scripts/check_gate.py`, estrutura geral) é genérico e pode ser reaproveitado quase inalterado.

---

## Troubleshooting

| Sintoma | Causa provável | Como resolver |
|---|---|---|
| `RuntimeError: GROQ_API_KEY não está definida` | Variável não exportada antes de chamar `/chat` | `export GROQ_API_KEY=gsk_...` no mesmo shell que sobe o uvicorn |
| `[Errno 98] Address already in use` | Outro processo na porta 8000 | `lsof -i :8000` para descobrir, ou suba em outra porta e ajuste o `url` no `config.yaml` |
| 401 da API Groq | Chave inválida ou expirada | Regere em https://console.groq.com/keys |
| Judge timeout (`Gemini timeout: ...`) | Free tier estrangulou; o retry honra `retry_after` automático mas o teto é `max_retry_after` | Aumente `max_attempts` do GeminiProvider ou rode em horário com menos carga |
| Scores absurdamente baixos no primeiro run | Threshold mal-calibrado ou cenários ambíguos | Confira `report.md` cenário a cenário; ajuste `EVAL_THRESHOLD` e/ou reescreva os cenários ambíguos antes de fechar o gate |
| Gate nunca dispara em PRs | Path-filter está bloqueando | Veja `paths:` do job `changes` em `.github/workflows/ci.yml` — confirme que cobre seus arquivos |

---

## Limitações conhecidas

- **Chatbot stateless.** Sem memória entre prompts, sem RAG. Se seu chatbot tem essas camadas, suba elas junto no `uvicorn` (o `CustomProvider` não enxerga a complexidade interna).
- **Free tier do Groq.** 30 req/min. Para os 95 prompts × 1 repetição, dá pra rodar em ~2 min sem estourar. Em CI a cada PR de PR descartável você atinge o limite — daí o path-filter ser importante.
- **Self-bias do juiz.** Gemini julgando outro chatbot ainda é o estado-da-arte para juízes free-tier, mas é um viés conhecido. Para análise empírica, considere variar o juiz e medir a concordância (veja `experiments/pilot/PILOT_ANALYSIS.md`).
