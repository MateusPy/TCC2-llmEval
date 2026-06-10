# Contribuindo

Contribuições são bem-vindas. O guia completo — setup do ambiente, padrões de
código, fluxo de PR e como adicionar providers/dimensões — está no
[**`CONTRIBUTING.md`**](https://github.com/MateusPy/TCC2-llmEval/blob/main/CONTRIBUTING.md)
no repositório. Esta página resume o essencial.

## Setup rápido

Você não tem permissão de push no repositório principal, então comece pelo **fork**:

```bash
# 1. Faça o fork em github.com/MateusPy/TCC2-llmEval e clone o SEU fork
git clone https://github.com/<seu-usuario>/TCC2-llmEval.git
cd TCC2-llmEval

# 2. Ambiente virtual + instalação editável com deps de dev
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Antes de abrir o PR

A CI roda lint, type-check, testes (com portão de cobertura de **95%**) e *secret
scan*. Rode tudo localmente antes:

```bash
ruff check .
ruff format .
mypy llm_eval/
pytest --cov=llm_eval --cov-fail-under=95
```

## Fluxo

1. **Issue primeiro** para mudanças não triviais, alinhando o escopo.
2. **Branch** a partir de `main` com prefixo (`feat/`, `fix/`, `docs/`, `chore/`).
3. **Commits** curtos e descritivos com tipo + escopo (ex.: `feat(providers): adicionar suporte a OpenAI`).
4. **PR** contra `main` descrevendo o quê, o porquê e como testou; vincule a issue (`Closes #N`).
5. **Revisão** — todo PR precisa de aprovação antes do merge.

## Guias específicos no `CONTRIBUTING.md`

- [Adicionando um novo provider](https://github.com/MateusPy/TCC2-llmEval/blob/main/CONTRIBUTING.md#adicionando-um-novo-provider)
- [Adicionando uma nova dimensão](https://github.com/MateusPy/TCC2-llmEval/blob/main/CONTRIBUTING.md#adicionando-uma-nova-dimensão)
- [Cortando uma release](https://github.com/MateusPy/TCC2-llmEval/blob/main/CONTRIBUTING.md#cortando-uma-release)
