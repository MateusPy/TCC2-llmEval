# Auditoria de dados sensíveis — pré-release público

> Registro da auditoria exigida antes de tornar o repositório público e publicar
> no PyPI (issue #67). Cobre a árvore de trabalho **e** todo o histórico do git.

| Item | Valor |
| --- | --- |
| Data | 2026-06-07 |
| Responsável | Johnny da Ponte Lopes |
| Commit auditado (HEAD) | `55fcc1f` |
| Ferramentas | `gitleaks 8.21.2`, `trufflehog 3.88.0` |
| Resultado | ✅ Nenhum segredo encontrado |

## Varredura automatizada (árvore + histórico)

### gitleaks

```
$ gitleaks detect --source . --redact
INF 92 commits scanned.
INF scan completed in 2.59s
INF no leaks found
```

Cobre todos os commits acessíveis a partir das refs do repositório (não apenas o
HEAD). **Nenhum vazamento detectado.**

### trufflehog (segunda opinião)

```
$ trufflehog git file://. --only-verified
chunks: 3249, bytes: 17822901, verified_secrets: 0, unverified_secrets: 0
```

Rodado também sem o filtro `--only-verified` (incluindo achados não verificados):
`verified_secrets: 0, unverified_secrets: 0`. **Nenhum segredo, verificado ou
não, em todo o histórico.**

### CI

O scan está automatizado no pipeline (`.github/workflows/ci.yml`, job
`Secret Scan (gitleaks)`), com `fetch-depth: 0` para varrer o histórico completo
a cada push/PR. O job é dependência (`needs`) do `eval-gate`, barrando
vazamentos futuros antes do merge.

## Verificação manual dos artefatos commitados

O `.gitignore` versiona propositalmente `experiments/**/results/` e
`examples/demo-chatbot/results/` (reprodutibilidade / registro do TCC). Cada
ponto abaixo foi conferido nesses artefatos:

- ✅ **`api_key` sanitizado** — todos os `run_result.json` commitados (9 arquivos:
  demo-chatbot, pilot ×3, full ×5) trazem `"api_key": "***REDACTED***"`. A
  sanitização do framework está atuando; nenhum valor literal.
- ✅ **Configs sem chave literal** — os 10 `config*.yaml` versionados usam apenas
  placeholders `${MISTRAL_API_KEY}` / `${GEMINI_API_KEY}` / `${CUSTOM_API_KEY}`.
  Nenhum `api_key` com valor embutido.
- ✅ **Nenhum `.env` no histórico** — `git log --all --diff-filter=A` por `.env`
  (e variantes) não retorna nada; o arquivo nunca foi commitado.
- ✅ **Sem dados pessoais / endpoints privados** — sem e-mail do autor,
  `@instabuy`, tokens, URLs internas ou endpoints privados nos artefatos. Os
  únicos e-mails presentes são exemplos *dentro das respostas do chatbot* sobre
  phishing (ex.: `suporte@amaz0n.com`, `paypal-security@gmai1.com`), propositais
  e fictícios — não são dados reais.
- ✅ **Logs sem credenciais** — os `*.log` commitados em
  `experiments/full/results/*/` não contêm cabeçalhos `Authorization`/`Bearer`,
  chaves (`sk-`, `AIza`, `gsk_`) nem corpos de requisição com segredo. As únicas
  ocorrências de `Bearer` no repositório são placeholders em docs
  (`Bearer ${CUSTOM_API_KEY}`) e fixtures de teste (`Bearer tok`, `Bearer abc`).

## Remediação

Não aplicável — nada foi encontrado na árvore nem no histórico, logo não houve
necessidade de rotacionar chaves, reescrever histórico (`git filter-repo`/BFG)
ou forçar push.

## Conclusão

Varredura de histórico concluída sem segredos verificados; scan ativo no CI;
artefatos commitados conferidos manualmente. **Repositório apto para tornar-se
público.** Recomendação permanente: manter o job de scan no CI e nunca remover o
`fetch-depth: 0`.
