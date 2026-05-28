# Rodada zero — calibração

5 cenários compartilhados, **fora** da amostra principal de 30. O objetivo
não é gerar dado pra análise — é alinhar interpretação da rubrica entre os
dois anotadores antes da coleta real.

## Como fazer

1. **Cada um abre o próprio CSV** (`calibration_A1.csv` ou `calibration_A2.csv`).
2. **Abra `items/01-...md`**, leia o prompt + resposta(s), aplique a rubrica,
   preencha a linha 01 do seu CSV. Repita pros 5.
3. **Ainda NÃO mostre seu CSV pro outro.**
4. Quando ambos terminarem, marquem uma call (Discord/Zoom, ~30 min) com:
   - As 2 planilhas abertas lado a lado
   - O texto da rubrica em `docs/protocolo-validacao-humana.md`
5. **Discutam item por item:**
   - Onde divergiram? Por quê?
   - A rubrica deu ambiguidade? Algum critério precisa ser refinado?
   - Algum cenário está mal formulado? (raro, mas pode acontecer)
6. **Documentem decisões** em [`README.md`](../README.md) ou em um
   `CALIBRATION_NOTES.md` aqui na pasta (livre formato), por exemplo:
   - "Combinamos que para refusal correto em factual-tutor, nota é 5 (não 4)."
   - "Decidimos que typo+adversarial na mesma variante conta como adversarial."

## Importante

Estes 5 cenários **NÃO entram na análise quantitativa final** do #52. São
descartáveis — o objetivo é calibrar.

A escolha cobre:
- 2 dimensões factual (1 Mistral, 1 Custom)
- 1 consistency (Gemini)
- 2 robustness (1 Gemini, 1 Custom)
- E os 3 chatbots (2 Custom, 2 Gemini, 1 Mistral)

Isso expõe vocês aos 3 tipos de pipeline antes da coleta real começar.

## Próximo passo

Depois da call de alinhamento, abram a pasta `../annotator_1/` ou
`../annotator_2/` (cada um a sua) e comecem a coleta dos 30.
