#!/usr/bin/env python3
"""Quality gate parser para o CI.

Lê ``report.json`` produzido pelo ``llm-eval run`` e falha (exit 1) se a
média de qualquer dimensão estiver abaixo do threshold informado pela
variável de ambiente ``EVAL_THRESHOLD``.

Imprime uma tabela com todas as dimensões antes de decidir, para que o
log do CI mostre tanto sucessos quanto falhas.

Uso (esperado dentro do job do GitHub Actions):

    EVAL_THRESHOLD=3.5 python examples/demo-chatbot/scripts/check_gate.py \\
        examples/demo-chatbot/results/report.json
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("uso: check_gate.py <caminho/do/report.json>", file=sys.stderr)
        return 2

    report_path = Path(argv[1])
    if not report_path.is_file():
        print(f"erro: report nao encontrado em {report_path}", file=sys.stderr)
        return 2

    threshold_raw = os.environ.get("EVAL_THRESHOLD")
    if threshold_raw is None:
        print("erro: variavel EVAL_THRESHOLD nao definida", file=sys.stderr)
        return 2
    try:
        threshold = float(threshold_raw)
    except ValueError:
        print(f"erro: EVAL_THRESHOLD invalido: {threshold_raw!r}", file=sys.stderr)
        return 2

    report = json.loads(report_path.read_text(encoding="utf-8"))
    by_dim = report.get("summary", {}).get("by_dimension", {})
    if not by_dim:
        print("erro: report nao tem summary.by_dimension", file=sys.stderr)
        return 2

    print(f"Quality gate — threshold = {threshold}")
    print()
    print(f"{'dimensao':<15} {'media':>8} {'status':>10}")
    print("-" * 35)

    failed: list[str] = []
    for dim, stats in by_dim.items():
        mean = stats.get("mean")
        if mean is None:
            print(f"{dim:<15} {'?':>8} {'SKIP':>10}  (sem media)")
            continue
        status = "OK" if mean >= threshold else "FAIL"
        print(f"{dim:<15} {mean:>8.2f} {status:>10}")
        if mean < threshold:
            failed.append(f"{dim} ({mean:.2f} < {threshold})")

    print()
    if failed:
        print(f"GATE FAILED: {len(failed)} dimensao(oes) abaixo do threshold:")
        for f in failed:
            print(f"  - {f}")
        return 1

    print("GATE PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
