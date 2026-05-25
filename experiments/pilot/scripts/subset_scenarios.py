"""Generate the pilot scenario subset from the embedded bank.

Reads the project's embedded scenario bank (``llm_eval/scenarios/bank/*.json``),
keeps the first ``N`` scenarios of each dimension (in their original order),
and writes the subset to ``experiments/pilot/scenarios/*.json``.

The subset preserves the exact bank schema (``dimension``, ``version``,
``scenarios``) and every per-scenario metadata field (``source``, ``trap``,
``expected_topic``, ``expected_behavior``, ``context_shift``, variants, etc.),
so the resulting files load with ``ScenarioLoader`` without modification.

Usage:
    python experiments/pilot/scripts/subset_scenarios.py
    python experiments/pilot/scripts/subset_scenarios.py --count 5

Determinism:
    The subset is the first ``N`` scenarios by file order. The order in
    ``bank/*.json`` is stable, so re-running the script always produces the
    same subset (required by the methodology for reproducibility).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from llm_eval.scenarios.loader import (
    ALLOWED_DIMENSIONS,
    DEFAULT_BANK_FILES,
    ScenarioLoader,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
BANK_DIR = REPO_ROOT / "llm_eval" / "scenarios" / "bank"
OUTPUT_DIR = REPO_ROOT / "experiments" / "pilot" / "scenarios"


def build_subset(dimension: str, count: int) -> dict:
    source = BANK_DIR / DEFAULT_BANK_FILES[dimension]
    bank = json.loads(source.read_text(encoding="utf-8"))
    subset = {
        "dimension": bank["dimension"],
        "version": bank["version"],
        "scenarios": bank["scenarios"][:count],
    }
    return subset


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Number of scenarios to keep per dimension (default: 10).",
    )
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for dimension in ALLOWED_DIMENSIONS:
        subset = build_subset(dimension, args.count)
        target = OUTPUT_DIR / DEFAULT_BANK_FILES[dimension]
        target.write_text(
            json.dumps(subset, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"[{dimension}] {len(subset['scenarios'])} scenarios -> {target}")

    loader = ScenarioLoader(OUTPUT_DIR)
    for dimension in ALLOWED_DIMENSIONS:
        bank = loader.load(dimension)
        print(f"[{dimension}] subset loads OK ({len(bank.scenarios)} scenarios)")


if __name__ == "__main__":
    main()
