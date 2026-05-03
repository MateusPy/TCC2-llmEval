"""Testes para o módulo CLI (Click)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest
import yaml
from click.testing import CliRunner

from llm_eval import cli
from llm_eval.cli import _truncate, main
from llm_eval.runner import RunResult, ScenarioResult


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


VALID_CONFIG: dict[str, Any] = {
    "provider": {
        "type": "gemini",
        "api_key": "k",
        "model": "gemini-2.0-flash-001",
    },
    "judge": {
        "enabled": True,
        "provider": {
            "type": "gemini",
            "api_key": "k",
            "model": "gemini-2.0-flash-001",
        },
    },
    "dimensions": ["factual"],
    "repetitions": 1,
    "output_dir": "./results",
}


def _write_yaml(path: Path, payload: dict[str, Any]) -> Path:
    path.write_text(yaml.safe_dump(payload), encoding="utf-8")
    return path


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def valid_config_file(tmp_path: Path) -> Path:
    config = dict(VALID_CONFIG)
    config["output_dir"] = str(tmp_path / "results")
    return _write_yaml(tmp_path / "config.yaml", config)


# ---------------------------------------------------------------------------
# Stubs and indirection
# ---------------------------------------------------------------------------


class _StubRunner:
    """Records construction and produces a deterministic RunResult."""

    def __init__(
        self,
        cfg: Any,
        *,
        scenarios: list[ScenarioResult] | None = None,
        raise_on_run: BaseException | None = None,
    ) -> None:
        self.cfg = cfg
        self._scenarios = scenarios or [
            ScenarioResult(
                scenario_id="factual-001",
                dimension="factual",
                category="knowledge",
                prompt="p",
            )
        ]
        self._raise_on_run = raise_on_run
        self.run_called = False

    def run(self) -> RunResult:
        self.run_called = True
        if self._raise_on_run is not None:
            raise self._raise_on_run
        return RunResult(
            config={},
            started_at=datetime.now(timezone.utc),
            finished_at=datetime.now(timezone.utc),
            scenario_results=self._scenarios,
        )


def _patch_runner_factory(
    monkeypatch: pytest.MonkeyPatch,
    *,
    scenarios: list[ScenarioResult] | None = None,
    raise_on_run: BaseException | None = None,
    raise_on_init: BaseException | None = None,
) -> dict[str, Any]:
    """Replace cli._build_runner with a factory that returns _StubRunner."""
    state: dict[str, Any] = {"runners": []}

    def factory(cfg: Any) -> _StubRunner:
        if raise_on_init is not None:
            raise raise_on_init
        stub = _StubRunner(cfg, scenarios=scenarios, raise_on_run=raise_on_run)
        state["runners"].append(stub)
        return stub

    monkeypatch.setattr(cli, "_build_runner", factory)
    return state


# ---------------------------------------------------------------------------
# Top-level CLI
# ---------------------------------------------------------------------------


def test_main_help_lists_all_commands(runner: CliRunner):
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    for command in ("run", "validate", "scenarios"):
        assert command in result.output


def test_main_version_flag(runner: CliRunner):
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    # Click's --version emits "main, version <X>"; version_option uses package version.
    assert "version" in result.output.lower()


def test_main_verbose_configures_logging(runner: CliRunner, monkeypatch: pytest.MonkeyPatch):
    captured: dict[str, Any] = {}

    def fake_basic_config(**kwargs: Any) -> None:
        captured.update(kwargs)

    monkeypatch.setattr(cli.logging, "basicConfig", fake_basic_config)
    result = runner.invoke(main, ["--verbose", "scenarios", "--list"])
    assert result.exit_code == 0
    assert captured.get("level") == cli.logging.INFO


# ---------------------------------------------------------------------------
# validate command
# ---------------------------------------------------------------------------


def test_validate_accepts_valid_config(runner: CliRunner, valid_config_file: Path):
    result = runner.invoke(main, ["validate", "-c", str(valid_config_file)])
    assert result.exit_code == 0
    assert "Configuração válida" in result.output


def test_validate_rejects_unpinned_model(runner: CliRunner, tmp_path: Path):
    config = dict(VALID_CONFIG)
    config["provider"] = {**VALID_CONFIG["provider"], "model": "gemini-2.0-flash"}
    path = _write_yaml(tmp_path / "bad.yaml", config)
    result = runner.invoke(main, ["validate", "-c", str(path)])
    assert result.exit_code == 1
    assert "Configuração inválida" in result.output
    assert "not pinned" in result.output


def test_validate_missing_file(runner: CliRunner, tmp_path: Path):
    """Click's path validator rejects missing files before our handler runs."""
    result = runner.invoke(main, ["validate", "-c", str(tmp_path / "missing.yaml")])
    assert result.exit_code != 0
    assert "does not exist" in result.output.lower() or "not found" in result.output.lower()


def test_validate_yaml_syntax_error(runner: CliRunner, tmp_path: Path):
    path = tmp_path / "broken.yaml"
    path.write_text("{this is: not: valid: yaml", encoding="utf-8")
    result = runner.invoke(main, ["validate", "-c", str(path)])
    assert result.exit_code == 1
    assert "Erro inesperado" in result.output or "inválida" in result.output


def test_validate_empty_yaml(runner: CliRunner, tmp_path: Path):
    path = tmp_path / "empty.yaml"
    path.write_text("", encoding="utf-8")
    result = runner.invoke(main, ["validate", "-c", str(path)])
    assert result.exit_code == 1
    assert (
        "inválida" in result.output.lower()
        or "vazia" in result.output.lower()
        or "empty" in result.output.lower()
    )


# ---------------------------------------------------------------------------
# run command
# ---------------------------------------------------------------------------


def test_run_executes_runner_and_reports_result(
    runner: CliRunner,
    valid_config_file: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    state = _patch_runner_factory(monkeypatch)
    result = runner.invoke(main, ["run", "-c", str(valid_config_file)])

    assert result.exit_code == 0
    assert "Configuração carregada" in result.output
    assert "Avaliação concluída" in result.output
    assert "1 cenários executados" in result.output
    assert state["runners"][0].run_called is True


def test_run_reports_failed_scenarios_count(
    runner: CliRunner,
    valid_config_file: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    failing = [
        ScenarioResult(scenario_id="ok-1", dimension="factual", category="knowledge", prompt="p"),
        ScenarioResult(
            scenario_id="bad-1",
            dimension="factual",
            category="knowledge",
            prompt="p",
            error="RuntimeError: boom",
        ),
    ]
    _patch_runner_factory(monkeypatch, scenarios=failing)
    result = runner.invoke(main, ["run", "-c", str(valid_config_file)])
    assert result.exit_code == 0
    assert "2 cenários executados (1 com erro)" in result.output


def test_run_handles_runner_init_value_error(
    runner: CliRunner,
    valid_config_file: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """Runner.__init__ may raise ValueError (e.g. Gemini dual-key check)."""
    _patch_runner_factory(monkeypatch, raise_on_init=ValueError("bad config"))
    result = runner.invoke(main, ["run", "-c", str(valid_config_file)])
    assert result.exit_code == 1
    assert "Erro ao instanciar o runner" in result.output


def test_run_handles_runner_run_exception(
    runner: CliRunner,
    valid_config_file: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    _patch_runner_factory(monkeypatch, raise_on_run=RuntimeError("network down"))
    result = runner.invoke(main, ["run", "-c", str(valid_config_file)])
    assert result.exit_code == 1
    assert "Falha durante a execução" in result.output
    assert "network down" in result.output


def test_run_writes_run_result_path_in_message(
    runner: CliRunner,
    valid_config_file: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    _patch_runner_factory(monkeypatch)
    result = runner.invoke(main, ["run", "-c", str(valid_config_file)])
    assert result.exit_code == 0
    assert "run_result.json" in result.output


# ---------------------------------------------------------------------------
# scenarios command
# ---------------------------------------------------------------------------


def test_scenarios_requires_list_or_dimension(runner: CliRunner):
    result = runner.invoke(main, ["scenarios"])
    assert result.exit_code != 0
    assert "Informe --list" in result.output


def test_scenarios_list_prints_all_dimensions(runner: CliRunner):
    result = runner.invoke(main, ["scenarios", "--list"])
    assert result.exit_code == 0
    assert "factual" in result.output
    assert "consistency" in result.output
    assert "robustness" in result.output


def test_scenarios_dimension_rejects_unknown(runner: CliRunner):
    result = runner.invoke(main, ["scenarios", "--dimension", "bogus"])
    # Click validates the choice before our handler runs.
    assert result.exit_code != 0
    assert "Invalid value" in result.output or "bogus" in result.output


def test_scenarios_dimension_lists_from_custom_path(runner: CliRunner, tmp_path: Path):
    bank = {
        "dimension": "factual",
        "version": "1.0.0",
        "scenarios": [
            {
                "id": "factual-001",
                "dimension": "factual",
                "category": "knowledge",
                "prompt": "Qual é a capital do Brasil?",
                "ground_truth": "Brasília",
                "variants": [],
            }
        ],
    }
    (tmp_path / "factual.json").write_text(json.dumps(bank), encoding="utf-8")
    result = runner.invoke(
        main,
        ["scenarios", "--dimension", "factual", "--path", str(tmp_path)],
    )
    assert result.exit_code == 0
    assert "Total de cenários: 1" in result.output
    assert "factual-001" in result.output
    assert "Qual é a capital do Brasil?" in result.output


def test_scenarios_dimension_handles_empty_bank(runner: CliRunner, tmp_path: Path):
    bank = {"dimension": "factual", "version": "1.0.0", "scenarios": []}
    (tmp_path / "factual.json").write_text(json.dumps(bank), encoding="utf-8")
    result = runner.invoke(
        main,
        ["scenarios", "--dimension", "factual", "--path", str(tmp_path)],
    )
    assert result.exit_code == 0
    assert "Total de cenários: 0" in result.output
    assert "banco vazio" in result.output


def test_scenarios_dimension_surfaces_load_error(runner: CliRunner, tmp_path: Path):
    """Schema mismatch produces a friendly error and exit code 1."""
    bank = {
        "dimension": "factual",
        "version": "1.0.0",
        "scenarios": [{"id": "x"}],  # missing required fields
    }
    (tmp_path / "factual.json").write_text(json.dumps(bank), encoding="utf-8")
    result = runner.invoke(
        main,
        ["scenarios", "--dimension", "factual", "--path", str(tmp_path)],
    )
    assert result.exit_code == 1
    assert "Erro ao carregar cenários" in result.output


def test_scenarios_uses_builtin_bank_when_no_path(
    runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """Without --path, the loader falls back to the package's built-in bank."""
    # The shipped bank is empty by default; just confirm we don't crash.
    result = runner.invoke(main, ["scenarios", "--dimension", "factual"])
    assert result.exit_code == 0
    assert "Dimensão: factual" in result.output


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def test_truncate_short_string_unchanged():
    assert _truncate("hi", 10) == "hi"


def test_truncate_long_string_appends_ellipsis():
    out = _truncate("a" * 80, 10)
    assert len(out) == 10
    assert out.endswith("…")


def test_truncate_strips_newlines():
    assert _truncate("line1\nline2", 100) == "line1 line2"
