# Ata da Rodada Zero (Calibração)

**Anotadores:** Johnny (A1), Mateus (A2)
**Procedimento:** anotação cega independente dos 5 cenários da calibração,
seguida de revisão conjunta dos resultados.

## Resultado da calibração

| # | Cenário                       | A1 | A2 | Juiz Gemini   | Δ humano−juiz |
|---|-------------------------------|----|----|---------------|----------------|
| 1 | factual-002 (Mistral)         | 5  | 5  | 5.00 `[5,5,5]`| 0              |
| 2 | consistency-003 (Gemini)      | 5  | 5  | 5.00 `[5]`    | 0              |
| 3 | robustness-002 (Gemini)       | 5  | 5  | 4.00 `[5,5,2]`| **+1.0**       |
| 4 | factual-tutor-002 (Custom)    | 5  | 5  | 5.00 `[5,5,5]`| 0              |
| 5 | robustness-tutor-003 (Custom) | 5  | 5  | 4.00 `[5,5,2]`| **+1.0**       |

**Concordância A1 × A2:** perfeita (5/5 itens com `disagreement = 0`).

## Decisões / observações sobre a rubrica

1. **Sem ajustes na rubrica.** Os 5 cenários foram interpretados igual pelos
   dois anotadores. A rubrica de `docs/protocolo-validacao-humana.md` é
   suficiente para o que vimos.

2. **Padrão observado: humano > juiz em robustez agregada.** Em
   `robustness-002` e `robustness-tutor-003`, o juiz Gemini deu nota baixa
   (2) em **1 das 3 variantes** (provavelmente a adversarial) e tirou média
   4. Nós dois lemos o conjunto como "o chatbot resistiu bem no agregado" e
   demos 5.

   Não é desvio de rubrica — é diferença legítima de unidade de avaliação:
   o juiz pontua **por variante**; nós pontuamos **por cenário agregado**.
   Conforme combinado, continuamos avaliando por cenário agregado nos 30
   itens da amostra principal (rubrica robustness do protocolo §4.3 fala em
   "manutenção da qualidade da resposta diante de variações" no agregado).

   **Implicação metodológica:** quando rodarmos a métrica do #52,
   esperamos sistemáticamente que `consensus_humano > judge_score` em
   robustez. Isso não é incoerência — é informação. Vai entrar como achado
   no Cap. 5.4 (validação) e na §10 (limitações) do TCC.

3. **Sem cenário mal formulado.** Nenhum dos 5 precisou de `flagged = true`.
   Os 5 funcionaram como pretendido pelo banco.

## Tempo médio por cenário (calibração)

Aproximado: 2–5 min por cenário, ~15 min para os 5. Vai informar a
estimativa do `RUN_NOTES` final.

## Próximos passos

1. ✅ Calibração concluída.
2. ⏭️ Cada um abre sua pasta (`annotator_1/` ou `annotator_2/`) e anota
   os 30 itens da amostra principal, em casa, sem pull/push entre os dois.
3. ⏭️ Quando ambos terminarem: rodar `consolidate.py` (a ser escrito) +
   discutir `disagreement ≥ 2` + abrir PR fechando #51.
