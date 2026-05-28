"""Gera planilhas da rodada zero (calibração) para A1 e A2.

5 cenários hand-picked, **fora da amostra de 30** do `sample.json`. Os dois
anotadores fazem os mesmos 5 cenários (sem randomização — o ponto é discutir
exatamente os mesmos casos depois) e se reúnem pra alinhar interpretação da
rubrica ANTES da coleta real começar.

A escolha tenta cobrir as 3 dimensões e os 3 chatbots, sem repetir nenhum
scenario_id que esteja na amostra principal.

Uso:
    python3 experiments/human-validation/scripts/build_calibration_sheets.py
"""

from __future__ import annotations

import csv
import json
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
HV = REPO / "experiments/human-validation"

sys.path.insert(0, str(Path(__file__).parent))
from build_annotation_sheets import (  # noqa: E402
    BANK_PATHS,
    RUN_PATHS,
    load_bank,
    load_run,
    render_item_markdown,
)


# 5 cenários de calibração. Cada item é (dim, scenario_id, chatbot, category).
# NENHUM destes está na amostra principal de 30 (sample.json).
CALIBRATION_ITEMS = [
    {
        "scenario_id": "factual-002",
        "chatbot": "Mistral",
        "dimension": "factual",
        "category": "geography",
    },
    {
        "scenario_id": "consistency-003",
        "chatbot": "Gemini",
        "dimension": "consistency",
        "category": "writing",
    },
    {
        "scenario_id": "robustness-002",
        "chatbot": "Gemini",
        "dimension": "robustness",
        "category": "science",
    },
    {
        "scenario_id": "factual-tutor-002",
        "chatbot": "Custom",
        "dimension": "factual",
        "category": "programming",
    },
    {
        "scenario_id": "robustness-tutor-003",
        "chatbot": "Custom",
        "dimension": "robustness",
        "category": "python_basics",
    },
]


def assert_outside_sample() -> None:
    """Falha se algum item de calibração estiver na amostra principal."""
    sample = json.loads((HV / "sample.json").read_text(encoding="utf-8"))
    sample_keys = {(it["scenario_id"], it["chatbot"]) for it in sample["items"]}
    for c in CALIBRATION_ITEMS:
        if (c["scenario_id"], c["chatbot"]) in sample_keys:
            raise SystemExit(
                f"FALHA: item de calibração {c['scenario_id']} ({c['chatbot']}) "
                "também está em sample.json — calibração deve ser disjunta."
            )


def main() -> None:
    assert_outside_sample()

    banks = {chatbot: load_bank(path) for chatbot, path in BANK_PATHS.items()}
    runs = {chatbot: load_run(path) for chatbot, path in RUN_PATHS.items()}

    out_dir = HV / "calibration"
    items_subdir = out_dir / "items"
    if items_subdir.exists():
        shutil.rmtree(items_subdir)
    items_subdir.mkdir(parents=True, exist_ok=True)

    for pos, item in enumerate(CALIBRATION_ITEMS, 1):
        sid = item["scenario_id"]
        chatbot = item["chatbot"]
        bank_entry = banks[chatbot].get(sid)
        if bank_entry is None:
            raise SystemExit(f"FALHA: scenario {sid} não encontrado no banco do {chatbot}")
        run_entry = runs[chatbot].get(sid)
        if run_entry is None:
            raise SystemExit(f"FALHA: scenario {sid} não encontrado no run_result do {chatbot}")
        md = render_item_markdown(item, bank_entry, run_entry, pos, "(calibração)")
        md_name = f"{pos:02d}-{sid}-{chatbot}.md"
        (items_subdir / md_name).write_text(md, encoding="utf-8")

    # Um CSV por anotador (mesma ordem dos 5 cenários)
    for anotador in ("A1", "A2"):
        csv_path = out_dir / f"calibration_{anotador}.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(
                [
                    "position",
                    "item_id",
                    "scenario_id",
                    "chatbot",
                    "dimension",
                    "score",
                    "justification",
                    "flagged",
                    "notes",
                    "ts_start",
                    "ts_end",
                ]
            )
            for pos, item in enumerate(CALIBRATION_ITEMS, 1):
                w.writerow(
                    [
                        f"{pos:02d}",
                        f"{item['scenario_id']}|{item['chatbot']}",
                        item["scenario_id"],
                        item["chatbot"],
                        item["dimension"],
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                    ]
                )
        print(f"[calibration {anotador}] {csv_path}")

    print(f"[calibration] {len(CALIBRATION_ITEMS)} items em {items_subdir}/")


if __name__ == "__main__":
    main()
