# Instalação

## Requisitos

- **Python 3.11 ou superior**
- Uma **chave de API** de pelo menos um provider (Google Gemini, Mistral AI ou um
  endpoint HTTP próprio)
- Uma chave de API para o **LLM-as-a-Judge** — pode ser o mesmo provider do chatbot

## Instalar via pip

```bash
pip install llm-eval-unb
```

!!! note "Nome de instalação × import × comando"
    O pacote é distribuído como **`llm-eval-unb`** no PyPI (o nome `llm-eval` já
    estava ocupado). Depois de instalado, o **import** é `import llm_eval` e o
    **comando** é `llm-eval` — como `pip install scikit-learn` → `import sklearn`.

Isso instala a biblioteca e o comando de linha de comando `llm-eval`. Confirme:

```bash
llm-eval --version
```

## Instalação para desenvolvimento

**Para apenas rodar a partir do código** (ler o fonte, testar a versão mais recente),
clone o repositório direto:

```bash
git clone https://github.com/MateusPy/TCC2-llmEval.git
cd TCC2-llmEval

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -e ".[dev]"
```

**Para contribuir** (abrir pull requests), você não tem permissão de push no
repositório principal — então comece pelo **fork**:

```bash
# 1. Faça o fork em github.com/MateusPy/TCC2-llmEval e clone o SEU fork
git clone https://github.com/<seu-usuario>/TCC2-llmEval.git
cd TCC2-llmEval

# 2. Ambiente e instalação editável
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# 3. Crie a branch da sua mudança e abra o PR contra MateusPy/TCC2-llmEval
git checkout -b feat/minha-mudanca
```

O passo a passo completo (padrões de código, testes, revisão) está em
[Contribuindo](contribuindo.md).

O extra `[dev]` traz `pytest`, `ruff` e `mypy`. Há também os extras `[analysis]`
(matplotlib) e `[docs]` (MkDocs).

## Chaves de API por variável de ambiente

As chaves **nunca** ficam no `config.yaml` em texto puro — você as referencia por
`${VAR}` no YAML e o framework resolve a partir do ambiente:

=== "Linux / macOS"

    ```bash
    export GEMINI_API_KEY="sua-chave-aqui"
    export MISTRAL_API_KEY="sua-chave-aqui"   # se for usar Mistral
    ```

=== "Windows (PowerShell)"

    ```powershell
    $env:GEMINI_API_KEY = "sua-chave-aqui"
    $env:MISTRAL_API_KEY = "sua-chave-aqui"
    ```

No `config.yaml`:

```yaml
provider:
  type: gemini
  api_key: ${GEMINI_API_KEY}   # resolvido a partir do ambiente
  model: gemini-2.0-flash
```

!!! warning "Variável não definida falha cedo"
    Se um `${VAR}` referenciado no YAML não estiver no ambiente, o carregamento da
    configuração falha com erro explícito — antes de qualquer chamada à API.

## Próximos passos

- [Guia rápido](quickstart.md) — rode sua primeira avaliação em 2 minutos
- [Configuração](configuracao.md) — referência completa do `config.yaml`
- [Providers](providers.md) — Gemini, Mistral e o provider HTTP customizado
