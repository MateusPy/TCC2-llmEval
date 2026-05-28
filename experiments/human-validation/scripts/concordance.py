"""Concordância LLM-as-a-Judge × consenso humano (issue #52).

Calcula:
- Cohen κ quadrático **A1 × A2** (concordância intra-anotadores), com IC 95% bootstrap.
- Cohen κ quadrático **judge × consenso humano**, com IC 95% bootstrap.
- Pearson r e MAE judge × consenso humano (sobre `consensus_mean` contínuo).
- Tudo também desagregado por dimensão (factual, consistency, robustness).
- Lista de "high disagreements" — itens com `|judge_score − consensus_mean| ≥ 2`.
- Análise de sensibilidade: refaz tudo trocando `consensus_mean` por
  `consensus_after_discussion` nos 4 itens revisados na sessão de discussão
  (ver `DISCUSSION_NOTES.md`).

Métricas em stdlib (mesmo padrão de `experiments/full/scripts/concordance.py`).
Figuras em matplotlib (dependência opcional `analysis` em pyproject.toml).

Uso:
    python3 experiments/human-validation/scripts/concordance.py

Outputs:
    experiments/human-validation/concordance_results.json
    experiments/human-validation/figures/*.png
"""

from __future__ import annotations

import csv
import json
import math
import random
from pathlib import Path
from statistics import fmean

REPO = Path(__file__).resolve().parents[3]
HV = REPO / "experiments/human-validation"

CONSOLIDATED_CSV = HV / "annotations_consolidated.csv"
OUT_JSON = HV / "concordance_results.json"
FIG_DIR = HV / "figures"

JUDGE_RUNS = {
    "Gemini": REPO / "experiments/full/results/gemini/run_result.json",
    "Mistral": REPO / "experiments/full/results/mistral/run_result.json",
    "Custom": REPO / "experiments/full/results/custom/run_result.json",
}

BOOTSTRAP_N = 1000
BOOTSTRAP_SEED = 42
HIGH_DISAGREEMENT_THRESHOLD = 2.0
QUALITATIVE_TOP_N = 5  # mínimo de casos para inspeção qualitativa (AC do #52)

DIMENSIONS = ("factual", "consistency", "robustness")


# ----- métricas em stdlib -----


def cohen_kappa_quadratic(xs: list[int], ys: list[int]) -> float:
    """Cohen κ com pesos quadráticos sobre escala discreta 1-5.

    Idêntico a `experiments/full/scripts/concordance.py:_cohen_kappa_quadratic`
    (mantido por dependência local — sem módulo compartilhado entre experimentos).
    """
    if len(xs) < 2:
        return float("nan")
    n = 5
    obs = [[0.0] * n for _ in range(n)]
    for x, y in zip(xs, ys):
        if 1 <= x <= 5 and 1 <= y <= 5:
            obs[x - 1][y - 1] += 1
    total = sum(sum(row) for row in obs)
    if total == 0:
        return float("nan")
    row_marg = [sum(row) for row in obs]
    col_marg = [sum(obs[i][j] for i in range(n)) for j in range(n)]
    exp = [[row_marg[i] * col_marg[j] / total for j in range(n)] for i in range(n)]
    w = [[((i - j) ** 2) / ((n - 1) ** 2) for j in range(n)] for i in range(n)]
    num = sum(w[i][j] * obs[i][j] for i in range(n) for j in range(n))
    den = sum(w[i][j] * exp[i][j] for i in range(n) for j in range(n))
    if den == 0:
        return float("nan")
    return 1.0 - num / den


def pearson_r(xs: list[float], ys: list[float]) -> float:
    if len(xs) < 2:
        return float("nan")
    mx, my = fmean(xs), fmean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if dx == 0 or dy == 0:
        return float("nan")
    return num / (dx * dy)


def mae(xs: list[float], ys: list[float]) -> float:
    if not xs:
        return float("nan")
    return fmean(abs(x - y) for x, y in zip(xs, ys))


def bootstrap_ci(
    metric_fn,
    xs: list,
    ys: list,
    n: int = BOOTSTRAP_N,
    seed: int = BOOTSTRAP_SEED,
    alpha: float = 0.05,
) -> tuple[float, float]:
    """IC bootstrap percentil 95% para uma métrica pareada."""
    if len(xs) < 2:
        return (float("nan"), float("nan"))
    rng = random.Random(seed)
    estimates: list[float] = []
    indices = list(range(len(xs)))
    for _ in range(n):
        sample_idx = [rng.choice(indices) for _ in range(len(xs))]
        sxs = [xs[i] for i in sample_idx]
        sys = [ys[i] for i in sample_idx]
        v = metric_fn(sxs, sys)
        if not math.isnan(v):
            estimates.append(v)
    if not estimates:
        return (float("nan"), float("nan"))
    estimates.sort()
    lo = estimates[int(len(estimates) * (alpha / 2))]
    hi = estimates[int(len(estimates) * (1 - alpha / 2))]
    return (lo, hi)


# ----- carregamento dos dados -----


def judge_score_per_item() -> dict[tuple[str, str], dict[str, object]]:
    """Para cada (scenario_id, chatbot), retorna mean dos judge_results + sample de justificativas."""
    out: dict[tuple[str, str], dict[str, object]] = {}
    for chatbot, path in JUDGE_RUNS.items():
        run = json.loads(path.read_text(encoding="utf-8"))
        for sr in run["scenario_results"]:
            jr = sr.get("judge_results") or []
            if not jr:
                continue
            scores = [j["score"] for j in jr]
            out[(sr["scenario_id"], chatbot)] = {
                "judge_mean": fmean(scores),
                "judge_scores": scores,
                "judge_justifications": [j.get("justification", "") for j in jr],
            }
    return out


def load_consolidated() -> list[dict[str, object]]:
    with CONSOLIDATED_CSV.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def to_int(s: str) -> int:
    return int(s.strip())


def to_float(s: str) -> float:
    return float(s.strip())


# ----- pipeline -----


def compute_block(
    items: list[dict[str, object]],
    judge: dict[tuple[str, str], dict[str, object]],
    consensus_key: str,
) -> dict[str, object]:
    """Calcula todas as métricas para um conjunto de itens usando `consensus_key`.

    `consensus_key` ∈ {'consensus_mean', 'consensus_after_discussion_or_mean'}.
    """
    a1_scores: list[int] = []
    a2_scores: list[int] = []
    judge_means: list[float] = []
    judge_rounded: list[int] = []
    consensus_means: list[float] = []
    consensus_rounded: list[int] = []
    per_item: list[dict[str, object]] = []

    for it in items:
        sid = it["scenario_id"]  # type: ignore[index]
        chatbot = it["chatbot"]  # type: ignore[index]
        jkey = (sid, chatbot)
        if jkey not in judge:
            continue

        s1 = to_int(it["score_A1"])  # type: ignore[arg-type]
        s2 = to_int(it["score_A2"])  # type: ignore[arg-type]
        j_mean = float(judge[jkey]["judge_mean"])  # type: ignore[arg-type]
        c_mean = to_float(it[consensus_key])  # type: ignore[arg-type]
        c_round = round(c_mean)
        j_round = round(j_mean)

        a1_scores.append(s1)
        a2_scores.append(s2)
        judge_means.append(j_mean)
        judge_rounded.append(j_round)
        consensus_means.append(c_mean)
        consensus_rounded.append(c_round)

        per_item.append(
            {
                "item_id": it["item_id"],
                "dimension": it["dimension"],
                "chatbot": chatbot,
                "score_A1": s1,
                "score_A2": s2,
                "judge_mean": j_mean,
                "consensus_mean": c_mean,
                "abs_error_judge_vs_consensus": abs(j_mean - c_mean),
            }
        )

    # Cohen κ A1 × A2 (escala discreta)
    kappa_a1a2 = cohen_kappa_quadratic(a1_scores, a2_scores)
    kappa_a1a2_ci = bootstrap_ci(cohen_kappa_quadratic, a1_scores, a2_scores)

    # Cohen κ judge × consenso (escala discreta — usa rounded)
    kappa_jh = cohen_kappa_quadratic(judge_rounded, consensus_rounded)
    kappa_jh_ci = bootstrap_ci(cohen_kappa_quadratic, judge_rounded, consensus_rounded)

    # Pearson e MAE (contínuos)
    r_jh = pearson_r(judge_means, consensus_means)
    mae_jh = mae(judge_means, consensus_means)

    return {
        "n": len(per_item),
        "kappa_A1_A2": {
            "point": kappa_a1a2,
            "ci95_bootstrap": list(kappa_a1a2_ci),
        },
        "kappa_judge_human": {
            "point": kappa_jh,
            "ci95_bootstrap": list(kappa_jh_ci),
        },
        "pearson_judge_human": r_jh,
        "mae_judge_human": mae_jh,
        "per_item": per_item,
    }


def compute_by_dimension(
    items: list[dict[str, object]],
    judge: dict[tuple[str, str], dict[str, object]],
    consensus_key: str,
) -> dict[str, dict[str, object]]:
    out: dict[str, dict[str, object]] = {}
    for dim in DIMENSIONS:
        subset = [it for it in items if it["dimension"] == dim]
        if not subset:
            continue
        block = compute_block(subset, judge, consensus_key)
        block.pop("per_item")  # not needed at dim level (already in overall)
        out[dim] = block
    return out


# ----- figuras -----


def generate_figures(items_overall: list[dict[str, object]]) -> list[Path]:
    """Scatter, matriz de confusão e distribuição de erros — salvas em FIG_DIR."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []

    dim_color = {"factual": "#1f77b4", "consistency": "#2ca02c", "robustness": "#d62728"}

    # 1. Scatter judge × consensus_mean
    fig, ax = plt.subplots(figsize=(6.5, 6))
    for dim in DIMENSIONS:
        xs = [it["consensus_mean"] for it in items_overall if it["dimension"] == dim]
        ys = [it["judge_mean"] for it in items_overall if it["dimension"] == dim]
        ax.scatter(xs, ys, c=dim_color[dim], alpha=0.7, label=dim, s=60, edgecolors="white")
    ax.plot([1, 5], [1, 5], "k--", alpha=0.4, label="concordância perfeita")
    ax.set_xlim(0.5, 5.5)
    ax.set_ylim(0.5, 5.5)
    ax.set_xlabel("Consenso humano (mean A1, A2)")
    ax.set_ylabel("Juiz Gemini (mean dos judge_results)")
    ax.set_title("Juiz × consenso humano (n=30)")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower right")
    p = FIG_DIR / "scatter_judge_vs_human.png"
    fig.tight_layout()
    fig.savefig(p, dpi=150)
    plt.close(fig)
    paths.append(p)

    # 2. Matriz de confusão (judge_rounded × consensus_rounded)
    fig, ax = plt.subplots(figsize=(6, 5.5))
    mat = [[0] * 5 for _ in range(5)]
    for it in items_overall:
        j = round(float(it["judge_mean"]))  # type: ignore[arg-type]
        c = round(float(it["consensus_mean"]))  # type: ignore[arg-type]
        if 1 <= j <= 5 and 1 <= c <= 5:
            mat[j - 1][c - 1] += 1
    im = ax.imshow(mat, cmap="Blues", aspect="equal")
    ax.set_xticks(range(5))
    ax.set_yticks(range(5))
    ax.set_xticklabels([1, 2, 3, 4, 5])
    ax.set_yticklabels([1, 2, 3, 4, 5])
    ax.set_xlabel("Consenso humano (rounded)")
    ax.set_ylabel("Juiz Gemini (rounded)")
    ax.set_title("Matriz de confusão judge × consenso humano")
    for i in range(5):
        for j in range(5):
            if mat[i][j] > 0:
                ax.text(j, i, str(mat[i][j]), ha="center", va="center",
                        color="white" if mat[i][j] >= 6 else "black", fontsize=11)
    fig.colorbar(im, ax=ax, label="contagem")
    p = FIG_DIR / "confusion_matrix.png"
    fig.tight_layout()
    fig.savefig(p, dpi=150)
    plt.close(fig)
    paths.append(p)

    # 3. Distribuição de erros (judge - consensus_mean) por dimensão
    fig, ax = plt.subplots(figsize=(7, 4.5))
    bins = [-4.5, -3.5, -2.5, -1.5, -0.5, 0.5, 1.5, 2.5, 3.5, 4.5]
    for dim in DIMENSIONS:
        errs = [
            float(it["judge_mean"]) - float(it["consensus_mean"])  # type: ignore[arg-type]
            for it in items_overall
            if it["dimension"] == dim
        ]
        if errs:
            ax.hist(errs, bins=bins, alpha=0.6, label=f"{dim} (n={len(errs)})", color=dim_color[dim])
    ax.axvline(0, color="black", linestyle="--", alpha=0.5)
    ax.set_xlabel("Erro (judge − consenso humano)")
    ax.set_ylabel("Itens")
    ax.set_title("Distribuição de erros do juiz por dimensão")
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")
    p = FIG_DIR / "error_distribution.png"
    fig.tight_layout()
    fig.savefig(p, dpi=150)
    plt.close(fig)
    paths.append(p)

    return paths


# ----- main -----


def main() -> None:
    items = load_consolidated()
    judge = judge_score_per_item()

    # campo derivado: usa consensus_after_discussion onde existir, senão consensus_mean
    for it in items:
        cad = (it.get("consensus_after_discussion") or "").strip()
        it["consensus_after_discussion_or_mean"] = cad if cad else it["consensus_mean"]

    primary = compute_block(items, judge, "consensus_mean")
    primary_by_dim = compute_by_dimension(items, judge, "consensus_mean")

    # high disagreements: lista estrita (AC #52) + relaxada (≥ 5 itens para análise qualitativa)
    per_item_sorted = sorted(
        primary["per_item"],  # type: ignore[arg-type]
        key=lambda x: -float(x["abs_error_judge_vs_consensus"]),  # type: ignore[arg-type]
    )
    strict = [pi for pi in per_item_sorted if pi["abs_error_judge_vs_consensus"] >= HIGH_DISAGREEMENT_THRESHOLD]
    relaxed = per_item_sorted[: max(QUALITATIVE_TOP_N, len(strict))]

    # análise de sensibilidade
    sensitivity = compute_block(items, judge, "consensus_after_discussion_or_mean")
    sensitivity_by_dim = compute_by_dimension(items, judge, "consensus_after_discussion_or_mean")
    sensitivity.pop("per_item")

    figures = generate_figures(primary["per_item"])  # type: ignore[arg-type]

    result = {
        "config": {
            "judge": "Gemini (main, gemini-2.5-flash-lite)",
            "consensus_primary": "consensus_mean (média A1, A2)",
            "consensus_sensitivity": "consensus_after_discussion onde definido, senão consensus_mean",
            "bootstrap_n": BOOTSTRAP_N,
            "bootstrap_seed": BOOTSTRAP_SEED,
            "high_disagreement_threshold": HIGH_DISAGREEMENT_THRESHOLD,
            "qualitative_top_n": QUALITATIVE_TOP_N,
        },
        "primary": {
            "overall": primary,
            "by_dimension": primary_by_dim,
        },
        "sensitivity": {
            "overall": sensitivity,
            "by_dimension": sensitivity_by_dim,
        },
        "high_disagreements": {
            "strict_threshold": HIGH_DISAGREEMENT_THRESHOLD,
            "at_or_above_strict": strict,
            "top_n_for_qualitative": relaxed,
        },
        "figures": [str(p.relative_to(REPO)) for p in figures],
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # resumo no stdout
    print("=" * 72)
    print(f"Juiz: Gemini main  |  n=30 itens  |  bootstrap n={BOOTSTRAP_N} seed={BOOTSTRAP_SEED}")
    print("-" * 72)
    o = primary
    print(
        f"κ A1×A2          = {o['kappa_A1_A2']['point']:+.3f}  "
        f"IC95% [{o['kappa_A1_A2']['ci95_bootstrap'][0]:+.3f}, {o['kappa_A1_A2']['ci95_bootstrap'][1]:+.3f}]"
    )
    print(
        f"κ judge×humano   = {o['kappa_judge_human']['point']:+.3f}  "
        f"IC95% [{o['kappa_judge_human']['ci95_bootstrap'][0]:+.3f}, {o['kappa_judge_human']['ci95_bootstrap'][1]:+.3f}]"
    )
    print(f"Pearson r        = {o['pearson_judge_human']:+.3f}")
    print(f"MAE              = {o['mae_judge_human']:.3f}")
    print("-" * 72)
    print("Por dimensão (judge × humano, primary):")
    for dim, d in primary_by_dim.items():
        print(
            f"  {dim:11s}: n={d['n']:2d}  κ={d['kappa_judge_human']['point']:+.3f}  "  # type: ignore[index]
            f"r={d['pearson_judge_human']:+.3f}  MAE={d['mae_judge_human']:.3f}"
        )
    print("-" * 72)
    print(
        f"High disagreements (|judge − consenso| ≥ {HIGH_DISAGREEMENT_THRESHOLD}): {len(strict)}  "
        f"|  top-{len(relaxed)} para análise qualitativa:"
    )
    for h in relaxed:
        marker = "  ≥ strict" if h["abs_error_judge_vs_consensus"] >= HIGH_DISAGREEMENT_THRESHOLD else ""  # type: ignore[index]
        print(
            f"  {h['item_id']:<42} judge={h['judge_mean']:.2f}  cons={h['consensus_mean']:.2f}  "  # type: ignore[index]
            f"|Δ|={h['abs_error_judge_vs_consensus']:.2f}{marker}"
        )
    print("-" * 72)
    print("Sensibilidade (consensus_after_discussion onde definido):")
    s = sensitivity
    print(
        f"  κ judge×humano = {s['kappa_judge_human']['point']:+.3f}  "  # type: ignore[index]
        f"IC95% [{s['kappa_judge_human']['ci95_bootstrap'][0]:+.3f}, {s['kappa_judge_human']['ci95_bootstrap'][1]:+.3f}]  "
        f"r={s['pearson_judge_human']:+.3f}  MAE={s['mae_judge_human']:.3f}"
    )
    print("=" * 72)
    print(f"Resultados completos: {OUT_JSON}")
    print(f"Figuras: {len(figures)} em {FIG_DIR}/")


if __name__ == "__main__":
    main()
