# Contribuindo para o llm-eval

Obrigado pelo interesse em contribuir! Este documento explica como configurar o ambiente, rodar a suíte de testes, seguir os padrões de código e abrir uma boa pull request. Se algo aqui estiver desatualizado ou ambíguo, abra uma issue.

---

## Sumário

- [Setup do ambiente](#setup-do-ambiente)
- [Rodando os testes](#rodando-os-testes)
- [Padrões de código](#padrões-de-código)
- [Workflow de contribuição](#workflow-de-contribuição)
- [Adicionando um novo provider](#adicionando-um-novo-provider)
- [Adicionando uma nova dimensão](#adicionando-uma-nova-dimensão)
- [Cortando uma release](#cortando-uma-release)
- [Reportando bugs e sugerindo features](#reportando-bugs-e-sugerindo-features)

---

## Setup do ambiente

Pré-requisitos: Python 3.11 ou superior e `git`.

```bash
# 1. Faça o fork em github.com/MateusPy/TCC2-llmEval e clone o seu fork
git clone https://github.com/<seu-usuario>/TCC2-llmEval.git
cd TCC2-llmEval

# 2. Crie um ambiente virtual
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. Instale o pacote em modo editável com as deps de desenvolvimento
pip install -e ".[dev]"

# 4. Exporte uma API key para rodar testes que usam providers
export GEMINI_API_KEY="sua-key"    # ou MISTRAL_API_KEY, conforme o caso
```

> Os testes unitários **não** chamam APIs externas — eles usam dublês e injeção de dependência. A API key é necessária apenas para rodar a CLI ou validações end-to-end manualmente.

---

## Rodando os testes

A suíte é executada com `pytest` e tem um portão de cobertura mínimo de **95%** que vale tanto localmente quanto na CI.

```bash
# Rodar tudo com cobertura
pytest --cov=llm_eval --cov-report=term-missing --cov-fail-under=95

# Rodar um arquivo específico
pytest tests/test_runner.py -v

# Rodar um único teste
pytest tests/test_runner.py::test_runner_orchestrates_pipeline -v

# Cobertura sem o portão (útil durante desenvolvimento)
pytest --cov=llm_eval --cov-report=term-missing
```

Ao adicionar código novo, escreva testes equivalentes — PRs que reduzam a cobertura abaixo do portão são reprovados na CI.

---

## Padrões de código

A CI executa três checagens automáticas em cada PR (`.github/workflows/ci.yml`):

| Etapa | Comando local | O que valida |
|---|---|---|
| Lint | `ruff check .` | Erros, imports não usados, complexidade |
| Format | `ruff format --check .` | Formatação consistente |
| Type-check | `mypy llm_eval/` | Anotações de tipo |
| Testes | `pytest --cov=llm_eval --cov-report=term-missing --cov-fail-under=95` | Comportamento e cobertura |
| Secret scan | (gitleaks rodando na CI) | Tokens vazados em commits |

Antes de abrir o PR, rode tudo localmente:

```bash
ruff check .
ruff format .
mypy llm_eval/
pytest --cov=llm_eval --cov-fail-under=95
```

Convenções gerais:

- **Docstrings** em todas as classes e métodos públicos. Estilo Google/NumPy (`Args:`, `Returns:`, `Raises:`). O idioma pode ser inglês ou português — mantenha consistência com o módulo onde está editando (a maior parte do pacote usa inglês, mas alguns módulos como `evaluation/judge.py` usam português).
- **Type hints** em todas as funções públicas; `from __future__ import annotations` permitido.
- **Pydantic v2** para modelos e validação de configuração — não use `dataclass` para schemas que precisam de validação.
- **Config-driven**: comportamento novo deve ser configurável via `Config`/YAML quando apropriado, não hard-coded.
- **Reprodutibilidade**: sempre que adicionar um parâmetro que afeta a saída de um provider/judge, considere o impacto em `seed` e em pin de versão de modelo (ver `llm_eval/config.py:is_pinned_model`).

---

## Workflow de contribuição

1. **Issue primeiro** — para mudanças não triviais, abra ou comente em uma issue antes de codar para alinhar o escopo.
2. **Branch** — crie a branch a partir de `main` atualizado, usando o prefixo apropriado:
   - `feat/<tópico>` — nova funcionalidade
   - `fix/<tópico>` — correção de bug
   - `docs/<tópico>` — documentação
   - `chore/<tópico>` — manutenção
3. **Commits** — mensagens curtas e descritivas. Prefixe com o tipo (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`) seguido do escopo, ex.: `feat(providers): adicionar suporte a OpenAI`.
4. **Push e PR** — abra a PR contra `main`, descreva o que mudou, por que, e como testou. Vincule a issue (`Closes #N`).
5. **Revisão** — todo PR precisa de aprovação antes do merge. Responda ao feedback com novos commits (não force-push em revisão para manter o histórico de revisão legível).

---

## Adicionando um novo provider

Estrutura atual: `llm_eval/providers/` contém `gemini.py`, `mistral.py` e `custom.py` (HTTP genérico). O dispatch fica em `llm_eval/runner.py:default_provider_factory` e a configuração em `llm_eval/config.py:ProviderSettings`.

Passos para adicionar, por exemplo, um provider `openai`:

1. **Criar `llm_eval/providers/openai.py`** com uma classe `OpenAIProvider(BaseProvider)`:

   ```python
   from llm_eval.providers.base import BaseProvider, ProviderConfig, ProviderResponse

   class OpenAIProvider(BaseProvider):
       """Provider que conversa com a API da OpenAI."""

       def __init__(self, config: ProviderConfig, *, client=None) -> None:
           super().__init__(config)
           self._client = client or _build_default_client(config)

       def send(self, prompt: str) -> ProviderResponse:
           # ... chamada SDK ...
           return ProviderResponse(...)

       def close(self) -> None:
           self._client.close()
   ```

   - Aceite o `client` por injeção para que os testes possam usar dublês sem chamar a rede.
   - Trate erros transientes com `retry_with_backoff` (ver `llm_eval/providers/_retry.py`).

2. **Exportar** a classe em `llm_eval/providers/__init__.py` e adicioná-la ao `__all__`.

3. **Registrar no factory** em `llm_eval/runner.py:default_provider_factory`:

   ```python
   if settings.type == "openai":
       return OpenAIProvider(_settings_to_provider_config(settings))
   ```

4. **Atualizar a validação de pin de modelo** em `llm_eval/config.py:ProviderSettings.validate_model_pin` se o novo provider exigir versionamento explícito (recomendado para qualquer SDK oficial). Se o vendor usar um padrão de sufixo diferente, ajuste `_PINNED_MODEL_RE` ou adicione uma exceção específica.

5. **Documentar** o provider no `README.md`, na seção "Providers", com um exemplo de configuração YAML mínima e cobertura de quaisquer campos exclusivos.

6. **Testes** em `tests/test_providers.py` (ou `tests/providers/test_openai.py` se preferir um arquivo dedicado):
   - Caso feliz: prompt → response com campos esperados.
   - Erros transientes: garantir que o retry é exercido.
   - Erros fatais: garantir que propagam.
   - Encerramento: `close()` libera o client.

7. Rodar a suíte completa (`pytest --cov=llm_eval --cov-fail-under=95`) e confirmar que a cobertura ainda passa.

---

## Adicionando uma nova dimensão

Para introduzir uma dimensão de avaliação além de `factual`, `consistency` e `robustness`:

1. Criar o banco de cenários em `llm_eval/scenarios/bank/<dimension>.json` seguindo o schema documentado no `README.md` ("Banco de Cenários").
2. Adicionar a dimensão à allow-list em `llm_eval/config.py:Config.validate_dimensions`.
3. Estender o judge (`llm_eval/evaluation/judge.py`) com a rubrica e o prompt de julgamento próprios da dimensão, se a estratégia de avaliação for diferente das existentes.
4. Atualizar `Runner` (`llm_eval/runner.py`) caso seja necessário um pipeline distinto para a dimensão.
5. Documentar no `README.md` e adicionar exemplos de cenários no banco.
6. Adicionar testes em `tests/test_loader.py`, `tests/test_judge.py` e `tests/test_runner.py`.

---

## Cortando uma release

A publicação no PyPI é **automatizada**: ao dar push de uma tag `v*`, o workflow
`.github/workflows/release.yml` faz o build, publica no TestPyPI, valida a instalação,
publica no PyPI e anexa os artefatos (`*.whl` / `*.tar.gz`) à GitHub Release.

> O pacote é distribuído como **`llm-eval-unb`** (o nome `llm-eval` estava ocupado
> nos índices). O import segue `llm_eval` e o comando de CLI segue `llm-eval`.

### Passos para cortar a versão `X.Y.Z`

1. **Bump da versão** em `pyproject.toml` (`version = "X.Y.Z"`), seguindo [SemVer](https://semver.org/lang/pt-BR/).
2. **Atualizar o `CHANGELOG.md`**: mover os itens de `[Não lançado]` para uma nova seção
   `[X.Y.Z] - AAAA-MM-DD` e atualizar os links de comparação no rodapé.
3. Abrir o PR com esses dois ajustes, revisar e mergear na `main`.
4. **Criar e empurrar a tag** a partir da `main` atualizada:

   ```bash
   git checkout main && git pull
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```

5. Acompanhar o workflow **Release** em Actions. A ordem dos jobs é
   `build → publish-testpypi → smoke-testpypi → publish-pypi → github-release`.

### Configuração necessária (uma vez)

O publish usa **Trusted Publishing (OIDC)** — sem token estático no repositório.
Para funcionar, configure o _trusted publisher_ em cada índice, apontando para
o repositório `MateusPy/TCC2-llmEval`, workflow `release.yml`:

- **PyPI**: <https://pypi.org/manage/account/publishing/> → publisher para o projeto
  `llm-eval-unb`, environment `pypi`.
- **TestPyPI**: <https://test.pypi.org/manage/account/publishing/> → idem, environment `testpypi`.

Os _environments_ `pypi` e `testpypi` são criados automaticamente pelo GitHub na
primeira execução; opcionalmente adicione regras de proteção (revisores obrigatórios)
em **Settings → Environments**.

> **Fallback por token:** caso o OIDC não seja viável, crie os secrets `PYPI_API_TOKEN`
> e `TEST_PYPI_API_TOKEN` e descomente as linhas `password:` correspondentes em
> `release.yml`.

---

## Reportando bugs e sugerindo features

- **Bug**: abra uma issue com [template de bug](https://github.com/MateusPy/TCC2-llmEval/issues/new) descrevendo passos para reproduzir, comportamento esperado e observado, versão do Python e a versão do `llm-eval` (`pip show llm-eval`).
- **Feature**: abra uma issue descrevendo o problema que resolve antes da solução proposta. Discutir o escopo na issue evita retrabalho no PR.
- **Pergunta de uso**: prefira [Discussions](https://github.com/MateusPy/TCC2-llmEval/discussions) (quando habilitado) ou abra uma issue com a label `question`.

---

Obrigado por contribuir!
