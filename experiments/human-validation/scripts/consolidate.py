"""Consolida annotations_A1.csv e annotations_A2.csv em annotations_consolidated.csv.

Para cada item da amostra:
- disagreement       = |score_A1 - score_A2|
- consensus_mean     = (score_A1 + score_A2) / 2
- consensus_rounded  = round(consensus_mean) com banker's rounding (half-to-even)
- consensus_after_discussion / unresolved → ficam vazios; preenchidos manualmente
  pelos anotadores após a sessão de discussão dos itens com disagreement >= 2

A ordem das linhas segue `sample.json` (ordem do pré-registro), não a ordem
randomizada de nenhum dos dois anotadores.

Uso:
    python3 experiments/human-validation/scripts/consolidate.py
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
HV = REPO / "experiments/human-validation"

A1_CSV = HV / "annotator_1/annotations_A1.csv"
A2_CSV = HV / "annotator_2/annotations_A2.csv"
SAMPLE_JSON = HV / "sample.json"
RESOLUTIONS_JSON = HV / "discussion_resolutions.json"
OUT_CSV = HV / "annotations_consolidated.csv"

DISCUSSION_THRESHOLD = 2  # disagreement >= 2 entra em discussão


def load_resolutions() -> dict[str, dict[str, object]]:
    """Lê as resoluções da sessão de discussão (se existirem)."""
    if not RESOLUTIONS_JSON.exists():
        return {}
    data = json.loads(RESOLUTIONS_JSON.read_text(encoding="utf-8"))
    out: dict[str, dict[str, object]] = {}
    for r in data.get("resolutions", []):
        out[r["item_id"]] = r
    return out


def load_annotations(path: Path) -> dict[str, dict[str, str]]:
    """Lê um CSV de anotação e retorna {item_id: row}."""
    with path.open(encoding="utf-8") as f:
        return {row["item_id"]: row for row in csv.DictReader(f)}


def parse_score(raw: str) -> int:
    s = raw.strip()
    if not s:
        raise ValueError("score vazio")
    return int(s)


def main() -> None:
    sample = json.loads(SAMPLE_JSON.read_text(encoding="utf-8"))
    sample_items = sample["items"]

    a1 = load_annotations(A1_CSV)
    a2 = load_annotations(A2_CSV)
    resolutions = load_resolutions()

    rows: list[dict[str, object]] = []
    missing: list[str] = []
    needs_discussion: list[dict[str, object]] = []
    unresolved_used: set[str] = set()

    for item in sample_items:
        item_id = f"{item['scenario_id']}|{item['chatbot']}"
        r1 = a1.get(item_id)
        r2 = a2.get(item_id)
        if r1 is None or r2 is None:
            missing.append(item_id)
            continue

        s1 = parse_score(r1["score"])
        s2 = parse_score(r2["score"])
        diff = abs(s1 - s2)
        mean = (s1 + s2) / 2
        rounded = round(mean)  # Python usa banker's rounding por padrão

        resolution = resolutions.get(item_id)
        if resolution is not None:
            cad: object = resolution["consensus_after_discussion"]
            unresolved = "true" if resolution.get("unresolved") else "false"
            unresolved_used.add(item_id)
        else:
            cad = ""
            unresolved = ""

        row = {
            "item_id": item_id,
            "scenario_id": item["scenario_id"],
            "chatbot": item["chatbot"],
            "dimension": item["dimension"],
            "score_A1": s1,
            "score_A2": s2,
            "disagreement": diff,
            "consensus_mean": f"{mean:.1f}",
            "consensus_rounded": rounded,
            "consensus_after_discussion": cad,
            "unresolved": unresolved,
            "justification_A1": r1.get("justification", "").strip(),
            "justification_A2": r2.get("justification", "").strip(),
            "flagged_A1": r1.get("flagged", "").strip(),
            "flagged_A2": r2.get("flagged", "").strip(),
        }
        rows.append(row)

        if diff >= DISCUSSION_THRESHOLD:
            needs_discussion.append(row)

    if missing:
        raise SystemExit(f"item_id ausente em A1 ou A2: {missing}")

    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # Resumo
    total = len(rows)
    dist: dict[int, int] = {}
    for r in rows:
        dist[r["disagreement"]] = dist.get(r["disagreement"], 0) + 1  # type: ignore[index]

    print(f"Consolidado: {OUT_CSV} ({total} itens)")
    print()
    print("Distribuição de disagreement:")
    for diff in sorted(dist):
        print(f"  Δ={diff}: {dist[diff]} itens")
    print()
    n_disc = len(needs_discussion)
    print(f"Itens com disagreement >= {DISCUSSION_THRESHOLD} (precisam discussão): {n_disc}")
    for r in sorted(needs_discussion, key=lambda x: -int(x["disagreement"])):  # type: ignore[arg-type]
        cad = r["consensus_after_discussion"]
        cad_str = f"  → consenso após discussão: {cad}" if cad != "" else "  → AINDA NÃO DISCUTIDO"
        print(
            f"  Δ={r['disagreement']}  {r['item_id']:<40} "
            f"A1={r['score_A1']} A2={r['score_A2']}{cad_str}"
        )

    # Sanidade: alguma resolução do JSON ficou sem casar com a amostra?
    stray = set(resolutions) - unresolved_used
    if stray:
        raise SystemExit(f"discussion_resolutions.json tem item_id desconhecido: {stray}")


if __name__ == "__main__":
    main()
