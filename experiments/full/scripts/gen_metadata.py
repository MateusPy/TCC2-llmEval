"""Gera metadata.json para um run do full run da #50.

Coleta a informação que a AC do #50 pede: data/hora, modelo pinado,
hash do banco de cenários, versão do framework, versão do BERTScore,
commit do git.

Uso:
    python experiments/full/scripts/gen_metadata.py \\
        --run-result experiments/full/results/<chatbot>/run_result.json \\
        --config experiments/full/config-<chatbot>.yaml \\
        --output  experiments/full/results/<chatbot>/metadata.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]


def _bank_hash(scenarios_path: Path) -> dict[str, str | dict[str, str]]:
    """Hash determinístico do banco apontado pelo config.

    Concatena o conteúdo bruto de cada arquivo na ordem alfabética e calcula
    SHA-256. Também reporta hashes individuais para debug.
    """
    files = sorted(scenarios_path.glob("*.json"))
    per_file: dict[str, str] = {}
    combined = hashlib.sha256()
    for f in files:
        content = f.read_bytes()
        per_file[f.name] = hashlib.sha256(content).hexdigest()
        combined.update(content)
    return {"combined": combined.hexdigest(), "files": per_file}


def _git_commit() -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True
        ).strip()
        return out
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _pkg_version(name: str) -> str:
    try:
        return version(name)
    except PackageNotFoundError:
        return "not-installed"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-result", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    run = json.loads(args.run_result.read_text(encoding="utf-8"))
    cfg = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    scenarios_path = (REPO_ROOT / cfg["scenarios_path"]).resolve()

    chatbot_model = cfg["provider"].get("model", "n/a")
    chatbot_type = cfg["provider"]["type"]
    judge_cfg = cfg.get("judge", {}).get("provider", {})

    metadata = {
        "issue": "#50",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "run": {
            "started_at": run.get("started_at"),
            "finished_at": run.get("finished_at"),
            "config_file": str(args.config.relative_to(REPO_ROOT))
            if args.config.is_absolute()
            else str(args.config),
            "run_result_file": str(args.run_result.relative_to(REPO_ROOT))
            if args.run_result.is_absolute()
            else str(args.run_result),
        },
        "chatbot": {
            "provider": chatbot_type,
            "model": chatbot_model,
            "temperature": cfg["provider"].get("temperature"),
            "seed": cfg["provider"].get("seed"),
        },
        "judge": {
            "provider": judge_cfg.get("type"),
            "model": judge_cfg.get("model"),
            "temperature": judge_cfg.get("temperature"),
            "seed": judge_cfg.get("seed"),
        },
        "scenarios": {
            "path": str(scenarios_path.relative_to(REPO_ROOT))
            if scenarios_path.is_relative_to(REPO_ROOT)
            else str(scenarios_path),
            "repetitions": cfg.get("repetitions"),
            "hash": _bank_hash(scenarios_path),
        },
        "framework": {
            "git_commit": _git_commit(),
            "llm_eval_version": _pkg_version("llm-eval"),
            "bert_score_version": _pkg_version("bert-score"),
            "google_genai_version": _pkg_version("google-generativeai"),
            "mistralai_version": _pkg_version("mistralai"),
            "pydantic_version": _pkg_version("pydantic"),
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"metadata.json escrito em {args.output}")


if __name__ == "__main__":
    main()
