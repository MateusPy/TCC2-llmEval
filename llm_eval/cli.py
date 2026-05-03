"""Interface de linha de comando do llm-eval.

Comandos disponíveis:

- ``llm-eval run --config CFG``: executa o pipeline completo de avaliação
- ``llm-eval validate --config CFG``: apenas valida o YAML
- ``llm-eval scenarios --list``: lista as dimensões disponíveis no banco
- ``llm-eval scenarios --dimension D``: lista cenários da dimensão ``D``
- ``llm-eval report --input R --format F --output O``: gera relatório a partir
  de um ``run_result.json`` previamente salvo
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import click
from pydantic import ValidationError

from llm_eval.config import Config
from llm_eval.report import ReportGenerator
from llm_eval.runner import RunResult, Runner
from llm_eval.scenarios.loader import (
    ALLOWED_DIMENSIONS,
    ScenarioLoader,
    ScenarioLoadError,
)

REPORT_FORMATS = ("json", "markdown")


def _build_runner(cfg: Config) -> Runner:
    """Indirection used by tests to inject a stub Runner without touching real SDKs."""
    return Runner(cfg)


def _build_loader(scenarios_path: str | Path | None) -> ScenarioLoader:
    """Indirection used by tests to inject a stub loader without touching the package data."""
    return ScenarioLoader(scenarios_path)


@click.group()
@click.version_option()
@click.option("--verbose", "-v", is_flag=True, help="Habilita logs em nível INFO.")
def main(verbose: bool) -> None:
    """llm-eval: Framework para avaliação de confiabilidade de chatbots baseados em LLMs."""
    if verbose:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )


@main.command()
@click.option(
    "--config",
    "-c",
    "config_path",
    required=True,
    type=click.Path(exists=True, dir_okay=False, readable=True, path_type=Path),
    help="Caminho para o arquivo de configuração YAML.",
)
def run(config_path: Path) -> None:
    """Executa o pipeline completo de avaliação."""
    cfg = _load_config_or_exit(config_path)
    click.echo(f"Configuração carregada de {config_path}")
    click.echo(
        f"Dimensões: {', '.join(cfg.dimensions)} | "
        f"repetitions: {cfg.repetitions} | "
        f"output_dir: {cfg.output_dir}"
    )

    try:
        runner = _build_runner(cfg)
    except ValueError as exc:
        click.echo(f"Erro ao instanciar o runner: {exc}", err=True)
        raise SystemExit(1) from exc

    try:
        result = runner.run()
    except Exception as exc:
        click.echo(f"Falha durante a execução do runner: {exc}", err=True)
        raise SystemExit(1) from exc

    final_path = Path(cfg.output_dir) / "run_result.json"
    total = len(result.scenario_results)
    failed = sum(1 for s in result.scenario_results if s.error is not None)
    click.echo(
        f"Avaliação concluída. {total} cenários executados "
        f"({failed} com erro). Resultado salvo em: {final_path}"
    )

    written_reports = _write_reports_from_result(result, cfg.output_dir, cfg.output_format)
    for fmt, path in written_reports:
        click.echo(f"Relatório {fmt} salvo em: {path}")


def _write_reports_from_result(
    result: RunResult,
    output_dir: str,
    formats: list[str],
) -> list[tuple[str, Path]]:
    """Render the configured ``output_format`` reports next to ``run_result.json``."""
    if not formats:
        return []
    generator = ReportGenerator(result)
    written: list[tuple[str, Path]] = []
    base = Path(output_dir)
    for fmt in formats:
        normalized = fmt.lower()
        if normalized == "json":
            written.append(("JSON", generator.to_json(base / "report.json")))
        elif normalized == "markdown":
            written.append(("Markdown", generator.to_markdown(base / "report.md")))
        # Unknown formats are silently ignored — config validation already
        # restricts the values, so this is just defensive.
    return written


@main.command()
@click.option(
    "--config",
    "-c",
    "config_path",
    required=True,
    type=click.Path(exists=True, dir_okay=False, readable=True, path_type=Path),
    help="Caminho para o arquivo de configuração YAML.",
)
def validate(config_path: Path) -> None:
    """Valida o YAML sem executar o pipeline."""
    _load_config_or_exit(config_path)
    click.echo(f"Configuração válida: {config_path}")


@main.command()
@click.option(
    "--list",
    "list_all",
    is_flag=True,
    help="Listar dimensões disponíveis no banco embutido.",
)
@click.option(
    "--dimension",
    "-d",
    type=click.Choice(list(ALLOWED_DIMENSIONS), case_sensitive=False),
    help="Listar cenários de uma dimensão específica.",
)
@click.option(
    "--path",
    "-p",
    "scenarios_path",
    type=click.Path(exists=True, file_okay=False, readable=True, path_type=Path),
    help="Caminho para um banco de cenários customizado (opcional).",
)
def scenarios(list_all: bool, dimension: str | None, scenarios_path: Path | None) -> None:
    """Inspeciona o banco de cenários disponível."""
    if list_all and dimension is not None:
        raise click.UsageError("Use --list OU --dimension <nome>, não ambos.")

    if list_all:
        click.echo("Dimensões disponíveis:")
        for dim in ALLOWED_DIMENSIONS:
            click.echo(f"  - {dim}")
        return

    if dimension is None:
        raise click.UsageError(
            "Informe --list para ver as dimensões ou --dimension <nome> para listar cenários."
        )

    # ``dimension`` is narrowed to str here — no need for an assert (asserts are
    # stripped under ``python -O``, so they can't be relied on for control flow).
    try:
        loader = _build_loader(scenarios_path)
        bank = loader.load(dimension)
    except ScenarioLoadError as exc:
        click.echo(f"Erro ao carregar cenários da dimensão '{dimension}': {exc}", err=True)
        raise SystemExit(1) from exc

    click.echo(f"Dimensão: {bank.dimension} (versão {bank.version})")
    click.echo(f"Total de cenários: {len(bank.scenarios)}")
    if not bank.scenarios:
        click.echo("  (banco vazio — popular via issue #27)")
        return
    for scenario in bank.scenarios:
        prompt_preview = _truncate(scenario.prompt, 60)
        click.echo(f"  [{scenario.id}] {scenario.category}: {prompt_preview}")


@main.command()
@click.option(
    "--input",
    "-i",
    "input_path",
    required=True,
    type=click.Path(exists=True, dir_okay=False, readable=True, path_type=Path),
    help="Arquivo run_result.json produzido por 'llm-eval run'.",
)
@click.option(
    "--format",
    "-f",
    "fmt",
    required=True,
    type=click.Choice(list(REPORT_FORMATS), case_sensitive=False),
    help="Formato de saída.",
)
@click.option(
    "--output",
    "-o",
    "output_path",
    required=True,
    type=click.Path(dir_okay=False, writable=True, path_type=Path),
    help="Caminho do arquivo de saída.",
)
def report(input_path: Path, fmt: str, output_path: Path) -> None:
    """Gera um relatório a partir de um run_result.json salvo previamente."""
    try:
        payload = json.loads(input_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        click.echo(f"Arquivo de entrada não é JSON válido: {exc}", err=True)
        raise SystemExit(1) from exc
    try:
        result = RunResult.model_validate(payload)
    except ValidationError as exc:
        click.echo(f"Conteúdo de {input_path} não é um RunResult válido:\n{exc}", err=True)
        raise SystemExit(1) from exc

    generator = ReportGenerator(result)
    fmt_normalized = fmt.lower()
    if fmt_normalized == "json":
        written = generator.to_json(output_path)
    else:
        written = generator.to_markdown(output_path)
    click.echo(f"Relatório {fmt_normalized} gerado em: {written}")


def _load_config_or_exit(path: Path) -> Config:
    """Try to load config; on any error print to stderr and exit with code 1."""
    try:
        return Config.from_yaml(path)
    except FileNotFoundError as exc:
        click.echo(f"Arquivo de configuração não encontrado: {path}", err=True)
        raise SystemExit(1) from exc
    except ValidationError as exc:
        click.echo(f"Configuração inválida em {path}:\n{exc}", err=True)
        raise SystemExit(1) from exc
    except ValueError as exc:
        click.echo(f"Configuração inválida em {path}: {exc}", err=True)
        raise SystemExit(1) from exc
    except Exception as exc:  # noqa: BLE001 - top-level CLI safety net
        click.echo(f"Erro inesperado ao carregar {path}: {exc}", err=True)
        raise SystemExit(1) from exc


def _truncate(text: str, limit: int) -> str:
    """Return ``text`` shortened to ``limit`` characters with an ellipsis when needed."""
    text = text.replace("\n", " ").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


if __name__ == "__main__":  # pragma: no cover
    main()
