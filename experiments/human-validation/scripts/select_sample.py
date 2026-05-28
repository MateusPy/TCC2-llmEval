"""Seleção determinística da amostra de 30 outputs para anotação humana (#51).

Reproduz a tabela publicada no issue #51. Seed fixo (42), ordem dos buckets
fixa. Pode ser re-rodada por qualquer um a qualquer momento — deve produzir
o mesmo sample.json byte-a-byte (módulo timestamps, que não existem aqui).

Critério resumido (detalhes no body do issue #51 §9):
- 10 itens por dimensão (factual/consistency/robustness).
- 10 itens por chatbot (Gemini/Mistral/Custom).
- Dentro de cada célula (dim × chatbot), preferir 1 caso de divergência
  judge × shadow (|main − shadow| ≥ 1.0); restantes por percentis de score.

Uso:
    python3 experiments/human-validation/scripts/select_sample.py
"""

from __future__ import annotations

import json
import random
from pathlib import Path
from statistics import fmean

REPO = Path(__file__).resolve().parents[3]
SEED = 42


def per_scenario(run: dict) -> dict[str, dict]:
    out = {}
    for sr in run["scenario_results"]:
        judge = sr.get("judge_results") or []
        if not judge:
            continue
        out[sr["scenario_id"]] = {
            "dimension": sr["dimension"],
            "category": sr.get("category", ""),
            "prompt": sr["prompt"][:120],
            "mean": fmean(j["score"] for j in judge),
        }
    return out


def main() -> None:
    g = per_scenario(
        json.loads((REPO / "experiments/full/results/gemini/run_result.json").read_text())
    )
    m = per_scenario(
        json.loads((REPO / "experiments/full/results/mistral/run_result.json").read_text())
    )
    c = per_scenario(
        json.loads((REPO / "experiments/full/results/custom/run_result.json").read_text())
    )
    gs = per_scenario(
        json.loads((REPO / "experiments/full/results/shadow-gemini/run_result.json").read_text())
    )
    ms = per_scenario(
        json.loads((REPO / "experiments/full/results/shadow-mistral/run_result.json").read_text())
    )

    pool: list[dict] = []
    for sid, info in g.items():
        sh = gs.get(sid, {}).get("mean")
        pool.append(
            {
                **info,
                "scenario_id": sid,
                "chatbot": "Gemini",
                "main": info["mean"],
                "shadow": sh,
                "div": abs(info["mean"] - sh) if sh is not None else None,
            }
        )
    for sid, info in m.items():
        sh = ms.get(sid, {}).get("mean")
        pool.append(
            {
                **info,
                "scenario_id": sid,
                "chatbot": "Mistral",
                "main": info["mean"],
                "shadow": sh,
                "div": abs(info["mean"] - sh) if sh is not None else None,
            }
        )
    for sid, info in c.items():
        pool.append(
            {
                **info,
                "scenario_id": sid,
                "chatbot": "Custom",
                "main": info["mean"],
                "shadow": None,
                "div": None,
            }
        )

    targets = {
        "factual": {"Gemini": 4, "Mistral": 3, "Custom": 3},
        "consistency": {"Gemini": 3, "Mistral": 4, "Custom": 3},
        "robustness": {"Gemini": 3, "Mistral": 3, "Custom": 4},
    }

    def stratified_pick(items: list[dict], n: int) -> list[dict]:
        # Lógica preservada exatamente como produzida no script original que
        # gerou a tabela publicada no issue #51 (commit base: 6ce2d0d). A
        # tabela é o registro público da amostra; qualquer mudança aqui
        # tem que casar com a tabela.
        if not items or n == 0:
            return []
        by_score = sorted(items, key=lambda x: x["main"])
        if n == 3:
            idxs_choice = [0, len(by_score) // 2, len(by_score) - 1]
        elif n == 4:
            idxs_choice = [0, len(by_score) // 3, 2 * len(by_score) // 3, len(by_score) - 1]
        elif n > 1:
            idxs_choice = [int(i * (len(by_score) - 1) / (n - 1)) for i in range(n)]
        else:
            idxs_choice = [len(by_score) // 2]
        chosen: list[dict] = []
        by_score_filt = list(by_score)
        high_div = [x for x in by_score_filt if x.get("div") is not None and x["div"] >= 1.0]
        if high_div:
            pick = sorted(high_div, key=lambda x: x["main"])[0]
            chosen.append(pick)
            by_score_filt = [x for x in by_score_filt if x["scenario_id"] != pick["scenario_id"]]
            idxs_choice = idxs_choice[1:]
        for idx in idxs_choice:
            if not by_score_filt:
                break
            idx = min(idx, len(by_score_filt) - 1)
            chosen.append(by_score_filt[idx])
            by_score_filt.pop(idx)
        return chosen

    random.seed(SEED)
    sample: list[dict] = []
    for dim in ("factual", "consistency", "robustness"):
        for chatbot in ("Gemini", "Mistral", "Custom"):
            items = [x for x in pool if x["dimension"] == dim and x["chatbot"] == chatbot]
            sample.extend(stratified_pick(items, targets[dim][chatbot]))

    out = REPO / "experiments/human-validation/sample.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(
            {"seed": SEED, "targets": targets, "items": sample}, indent=2, ensure_ascii=False
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Sample gerado: {out} ({len(sample)} itens)")


if __name__ == "__main__":
    main()
