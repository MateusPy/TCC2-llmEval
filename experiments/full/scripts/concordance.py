"""Mede concordância judge × judge entre uma run principal e uma run shadow.

Pareia cenários (mesmo `scenario_id`) entre duas execuções do mesmo chatbot
com juízes diferentes (ex.: Gemini main vs Mistral shadow) e calcula
Spearman ρ e Cohen κ quadrático-ponderado sobre o score médio por cenário.

Critério metodológico (PILOT_ANALYSIS §5.1, decisão pré-registrada no
config-shadow-gemini.yaml):
    κ > 0.8 → ranking Gemini > Mistral validado, self-bias pequeno
    0.6 ≤ κ ≤ 0.8 → ranking aceitável com caveat
    κ < 0.6 → ranking deve ser descartado no Cap. 5 do TCC

Uso:
    python experiments/full/scripts/concordance.py \\
        --main   experiments/full/results/gemini/run_result.json \\
        --shadow experiments/full/results/shadow-gemini/run_result.json \\
        --output experiments/full/results/concordance-gemini.json
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from statistics import fmean


def _mean_score_per_scenario(run: dict) -> dict[str, float]:
    """Calcula score médio por cenário, agregando judge_results."""
    out: dict[str, float] = {}
    for r in run["scenario_results"]:
        scores = [j["score"] for j in (r.get("judge_results") or [])]
        if not scores:
            continue
        out[r["scenario_id"]] = fmean(scores)
    return out


def _spearman(xs: list[float], ys: list[float]) -> float:
    """Spearman ρ via Pearson sobre os ranks (lida com empates por average rank)."""
    n = len(xs)
    if n < 2:
        return float("nan")
    rx = _rank(xs)
    ry = _rank(ys)
    mx = fmean(rx)
    my = fmean(ry)
    num = sum((rx[i] - mx) * (ry[i] - my) for i in range(n))
    dx = math.sqrt(sum((r - mx) ** 2 for r in rx))
    dy = math.sqrt(sum((r - my) ** 2 for r in ry))
    if dx == 0 or dy == 0:
        return float("nan")
    return num / (dx * dy)


def _rank(values: list[float]) -> list[float]:
    """Rank com média em empates (fractional ranking)."""
    sorted_pairs = sorted(enumerate(values), key=lambda p: p[1])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(sorted_pairs):
        j = i
        while j + 1 < len(sorted_pairs) and sorted_pairs[j + 1][1] == sorted_pairs[i][1]:
            j += 1
        avg_rank = (i + j) / 2.0 + 1.0  # ranks são 1-indexed
        for k in range(i, j + 1):
            ranks[sorted_pairs[k][0]] = avg_rank
        i = j + 1
    return ranks


def _cohen_kappa_quadratic(xs: list[int], ys: list[int]) -> float:
    """Cohen κ com pesos quadráticos sobre escala discreta 1-5.

    Adequado para escalas ordinais: penaliza discordâncias grandes mais
    que pequenas (|2-5| pesa mais que |4-5|).
    """
    if len(xs) < 2:
        return float("nan")
    labels = list(range(1, 6))
    n = len(labels)
    # matriz observada
    obs = [[0.0] * n for _ in range(n)]
    for x, y in zip(xs, ys):
        if 1 <= x <= 5 and 1 <= y <= 5:
            obs[x - 1][y - 1] += 1
    total = sum(sum(row) for row in obs)
    if total == 0:
        return float("nan")
    # marginais
    row_marg = [sum(row) for row in obs]
    col_marg = [sum(obs[i][j] for i in range(n)) for j in range(n)]
    # esperada sob independência
    exp = [[row_marg[i] * col_marg[j] / total for j in range(n)] for i in range(n)]
    # pesos quadráticos
    w = [[((i - j) ** 2) / ((n - 1) ** 2) for j in range(n)] for i in range(n)]
    num = sum(w[i][j] * obs[i][j] for i in range(n) for j in range(n))
    den = sum(w[i][j] * exp[i][j] for i in range(n) for j in range(n))
    if den == 0:
        return float("nan")
    return 1.0 - num / den


def _interpret(kappa: float) -> str:
    if math.isnan(kappa):
        return "indefinido (dados insuficientes)"
    if kappa > 0.8:
        return "ranking validado, self-bias pequeno"
    if kappa >= 0.6:
        return "ranking aceitável com caveat"
    return "ranking deve ser descartado no Cap. 5"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--main", type=Path, required=True, help="run_result.json com juiz principal"
    )
    parser.add_argument(
        "--shadow", type=Path, required=True, help="run_result.json com juiz alternativo"
    )
    parser.add_argument("--output", type=Path, required=True, help="JSON com resultados")
    args = parser.parse_args()

    main_run = json.loads(args.main.read_text(encoding="utf-8"))
    shadow_run = json.loads(args.shadow.read_text(encoding="utf-8"))

    main_scores = _mean_score_per_scenario(main_run)
    shadow_scores = _mean_score_per_scenario(shadow_run)

    common = sorted(set(main_scores) & set(shadow_scores))
    if not common:
        raise SystemExit("Nenhum scenario_id em comum entre main e shadow.")

    # vetor pareado por dimensão e overall
    dims = ("factual", "consistency", "robustness")
    by_dim_main: dict[str, list[float]] = {d: [] for d in dims}
    by_dim_shadow: dict[str, list[float]] = {d: [] for d in dims}
    sc_dim = {r["scenario_id"]: r["dimension"] for r in main_run["scenario_results"]}

    overall_main, overall_shadow = [], []
    for sid in common:
        dim = sc_dim.get(sid)
        overall_main.append(main_scores[sid])
        overall_shadow.append(shadow_scores[sid])
        if dim in dims:
            by_dim_main[dim].append(main_scores[sid])
            by_dim_shadow[dim].append(shadow_scores[sid])

    result: dict[str, object] = {
        "main_run": str(args.main),
        "shadow_run": str(args.shadow),
        "n_scenarios_common": len(common),
        "overall": {
            "spearman_rho": _spearman(overall_main, overall_shadow),
            "cohen_kappa_quadratic": _cohen_kappa_quadratic(
                [round(s) for s in overall_main], [round(s) for s in overall_shadow]
            ),
        },
        "by_dimension": {},
    }
    result["overall"]["interpretation"] = _interpret(result["overall"]["cohen_kappa_quadratic"])
    for d in dims:
        if by_dim_main[d]:
            result["by_dimension"][d] = {
                "n": len(by_dim_main[d]),
                "spearman_rho": _spearman(by_dim_main[d], by_dim_shadow[d]),
                "cohen_kappa_quadratic": _cohen_kappa_quadratic(
                    [round(s) for s in by_dim_main[d]],
                    [round(s) for s in by_dim_shadow[d]],
                ),
            }

    # imprime resumo legível
    print("=" * 60)
    print(f"Main:   {args.main}")
    print(f"Shadow: {args.shadow}")
    print(f"Cenários comuns: {len(common)}")
    print("-" * 60)
    o = result["overall"]
    print(
        f"Overall  : ρ={o['spearman_rho']:+.3f}  κ_quad={o['cohen_kappa_quadratic']:+.3f}  → {o['interpretation']}"
    )
    for d in dims:
        if d in result["by_dimension"]:
            r = result["by_dimension"][d]
            print(
                f"  {d:11s}: ρ={r['spearman_rho']:+.3f}  κ_quad={r['cohen_kappa_quadratic']:+.3f}  (n={r['n']})"
            )
    print("=" * 60)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Detalhe salvo em {args.output}")


if __name__ == "__main__":
    main()
