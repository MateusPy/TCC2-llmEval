"""Verifica integridade de um run_result.json do full run da #50.

Garante que cada cenário do banco de origem foi processado, que erros são
explícitos por cenário (não silenciosos), e que a contagem de prompts
respondidos bate com `repetitions × (1 + variantes)`.

Uso:
    python experiments/full/scripts/integrity_check.py <run_result.json>

Exit code:
    0 — íntegro
    1 — divergência (cenário faltando, prompt faltando, erro silencioso)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def _load_bank(scenarios_path: Path) -> dict[str, list[dict]]:
    """Carrega os cenários do banco apontado pelo config."""
    bank: dict[str, list[dict]] = {}
    for dim in ("factual", "consistency", "robustness"):
        file = scenarios_path / f"{dim}.json"
        if not file.exists():
            continue
        data = json.loads(file.read_text(encoding="utf-8"))
        bank[dim] = data["scenarios"]
    return bank


def _expected_responses(scenario: dict, repetitions: int) -> int:
    """Quantas respostas o chatbot deveria ter produzido para um cenário."""
    dim = scenario["dimension"]
    n_variants = len(scenario.get("variants", []))
    if dim == "factual":
        return repetitions
    return 1 + n_variants


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_result", type=Path, help="run_result.json a verificar")
    args = parser.parse_args()

    run = json.loads(args.run_result.read_text(encoding="utf-8"))
    config = run["config"]
    repetitions = config["repetitions"]
    scenarios_path = (REPO_ROOT / config["scenarios_path"]).resolve()
    bank = _load_bank(scenarios_path)

    # ID -> scenario no banco
    bank_index: dict[str, dict] = {s["id"]: s for scenarios in bank.values() for s in scenarios}
    expected_ids = set(bank_index.keys())

    actual_results = {r["scenario_id"]: r for r in run["scenario_results"]}
    actual_ids = set(actual_results.keys())

    problems: list[str] = []

    missing = expected_ids - actual_ids
    extra = actual_ids - expected_ids
    if missing:
        problems.append(
            f"{len(missing)} cenários faltando no run_result: {sorted(missing)[:5]}{'...' if len(missing) > 5 else ''}"
        )
    if extra:
        problems.append(f"{len(extra)} cenários inesperados no run_result: {sorted(extra)[:5]}")

    # contagem por dimensão e contagem de prompts/respostas
    total_expected_prompts = 0
    total_actual_prompts = 0
    errors_by_id: dict[str, str] = {}

    for sid, result in actual_results.items():
        scenario = bank_index.get(sid)
        if scenario is None:
            continue
        expected = _expected_responses(scenario, repetitions)
        total_expected_prompts += expected

        responses = result.get("responses") or []
        variant_responses = result.get("variant_responses") or []
        actual = len(responses) + len(variant_responses)
        total_actual_prompts += actual

        if result.get("error"):
            errors_by_id[sid] = result["error"]
            continue

        if actual != expected:
            problems.append(
                f"{sid}: esperava {expected} respostas (rep={repetitions}, "
                f"variantes={len(scenario.get('variants', []))}), obteve {actual}"
            )

    # cenários sem error mas com 0 respostas → erro silencioso
    silent = [
        sid
        for sid, r in actual_results.items()
        if not r.get("error") and not (r.get("responses") or r.get("variant_responses"))
    ]
    if silent:
        problems.append(
            f"{len(silent)} cenários com 0 respostas e sem erro (silencioso): {silent[:5]}"
        )

    print("=" * 60)
    print(f"Run result: {args.run_result}")
    print(f"Bank dir:   {scenarios_path}")
    print(f"Repetitions: {repetitions}")
    print("-" * 60)
    for dim, scenarios in bank.items():
        n_in_run = sum(1 for s in scenarios if s["id"] in actual_ids)
        print(f"  {dim:12s}: {n_in_run}/{len(scenarios)} cenários processados")
    print("-" * 60)
    print(f"  Total cenários esperados: {len(expected_ids)}")
    print(f"  Total cenários no run:    {len(actual_ids)}")
    print(f"  Total prompts esperados:  {total_expected_prompts}")
    print(f"  Total prompts obtidos:    {total_actual_prompts}")
    print(f"  Erros explícitos:         {len(errors_by_id)}")
    if errors_by_id:
        for sid, err in list(errors_by_id.items())[:5]:
            print(f"    - {sid}: {err[:120]}")
    print("=" * 60)

    if problems:
        print("FALHA — divergências encontradas:")
        for p in problems:
            print(f"  ! {p}")
        return 1

    print("OK — integridade verificada.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
