"""Command-line interface for llm-eval."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

import click
from pydantic import ValidationError

from llm_eval.config import Config, ProviderSettings
from llm_eval.evaluation.judge import Judge
from llm_eval.evaluation.validation import (
    JudgeValidationError,
    JudgeValidator,
    ValidationReport,
)
from llm_eval.report import ReportGenerator
from llm_eval.runner import RunResult, Runner, default_provider_factory
from llm_eval.scenarios.loader import (
    ALLOWED_DIMENSIONS,
    ScenarioLoader,
    ScenarioLoadError,
)

REPORT_FORMATS = ("json", "markdown")
VALIDATION_PROVIDER_DEFAULTS = {
    "gemini": {
        "model": "gemini-2.0-flash-001",
        "api_env": "GEMINI_API_KEY",
    },
    "mistral": {
        "model": "mistral-small-2503",
        "api_env": "MISTRAL_API_KEY",
    },
}


def _build_runner(cfg: Config) -> Runner:
    """Indirection used by tests to inject a stub Runner without touching real SDKs."""
    return Runner(cfg)


def _build_loader(scenarios_path: str | Path | None) -> ScenarioLoader:
    """Indirection used by tests to inject a stub loader without touching package data."""
    return ScenarioLoader(scenarios_path)


def _build_validation_judge(
    provider_name: str,
    *,
    model: str | None,
    api_key: str | None,
    temperature: float,
    max_tokens: int,
    seed: int | None,
) -> Judge:
    """Build the judge used by ``validate-judge`` from CLI parameters."""
    normalized_provider = provider_name.lower()
    if normalized_provider not in VALIDATION_PROVIDER_DEFAULTS:
        raise ValueError(f"Unsupported validation provider: {provider_name}")

    resolved_model = model or VALIDATION_PROVIDER_DEFAULTS[normalized_provider]["model"]
    resolved_api_key = _resolve_validation_api_key(normalized_provider, api_key)

    settings = ProviderSettings(
        type=normalized_provider,
        api_key=resolved_api_key,
        model=resolved_model,
        temperature=temperature,
        max_tokens=max_tokens,
        seed=seed,
    )
    return Judge(default_provider_factory(settings))


def _resolve_validation_api_key(provider_name: str, explicit_api_key: str | None) -> str:
    """Resolve the API key for ``validate-judge`` from CLI or environment."""
    if explicit_api_key:
        return explicit_api_key

    env_var = VALIDATION_PROVIDER_DEFAULTS[provider_name]["api_env"]
    env_value = os.environ.get(env_var)
    if env_value:
        return env_value
    raise ValueError(
        f"API key not provided. Use --api-key or define the environment variable {env_var}."
    )


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
    failed = sum(1 for scenario in result.scenario_results if scenario.error is not None)
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

    try:
        loader = _build_loader(scenarios_path)
        bank = loader.load(dimension)
    except ScenarioLoadError as exc:
        click.echo(f"Erro ao carregar cenários da dimensão '{dimension}': {exc}", err=True)
        raise SystemExit(1) from exc

    click.echo(f"Dimensão: {bank.dimension} (versão {bank.version})")
    click.echo(f"Total de cenários: {len(bank.scenarios)}")
    if not bank.scenarios:
        click.echo("  (banco vazio — adicione cenários ao arquivo JSON correspondente)")
        return
    for scenario in bank.scenarios:
        prompt_preview = _truncate(scenario.prompt, 60)
        click.echo(f"  [{scenario.id}] {scenario.category}: {prompt_preview}")


@main.command("validate-judge")
@click.option(
    "--provider",
    "provider_name",
    required=True,
    type=click.Choice(list(VALIDATION_PROVIDER_DEFAULTS), case_sensitive=False),
    help="Provider do LLM usado como juiz (gemini ou mistral).",
)
@click.option(
    "--model",
    default=None,
    help="Modelo do juiz. Se omitido, usa um default pinado por provider.",
)
@click.option(
    "--api-key",
    "api_key",
    default=None,
    help="API key do provider. Se omitida, usa a variável de ambiente padrão do provider.",
)
@click.option(
    "--golden-set",
    "golden_set_path",
    default=None,
    type=click.Path(exists=True, dir_okay=False, readable=True, path_type=Path),
    help="Arquivo JSON do golden set. Se omitido, usa o dataset embutido no pacote.",
)
@click.option(
    "--output",
    "-o",
    "output_path",
    default=Path("results/validation_report.json"),
    show_default=True,
    type=click.Path(dir_okay=False, path_type=Path),
    help="Caminho do relatório JSON gerado.",
)
@click.option(
    "--temperature",
    default=0.0,
    show_default=True,
    type=float,
    help="Temperature usada no juiz.",
)
@click.option(
    "--max-tokens",
    default=2048,
    show_default=True,
    type=int,
    help="Máximo de tokens para a resposta do juiz.",
)
@click.option(
    "--seed",
    default=42,
    show_default=True,
    type=int,
    help="Seed encaminhada ao provider quando suportada.",
)
def validate_judge(
    provider_name: str,
    model: str | None,
    api_key: str | None,
    golden_set_path: Path | None,
    output_path: Path,
    temperature: float,
    max_tokens: int,
    seed: int,
) -> None:
    """Valida a concordância do LLM-as-a-Judge contra um golden set."""
    judge: Judge | None = None
    try:
        judge = _build_validation_judge(
            provider_name,
            model=model,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
            seed=seed,
        )
        report = JudgeValidator(judge, golden_set_path).run()
        _write_validation_report(output_path, report)
    except (JudgeValidationError, ValueError) as exc:
        click.echo(f"Falha na validação do juiz: {exc}", err=True)
        raise SystemExit(1) from exc
    except Exception as exc:
        click.echo(f"Erro inesperado durante validate-judge: {exc}", err=True)
        raise SystemExit(1) from exc
    finally:
        if judge is not None:
            try:
                judge.provider.close()
            except Exception:
                logging.getLogger(__name__).warning("Falha ao fechar o provider do juiz.")

    click.echo(f"Cohen's Kappa: {report.cohen_kappa:.2f} ({report.agreement_label})")
    click.echo(f"Pearson correlation: {report.pearson_correlation:.2f}")
    click.echo(f"MAE: {report.mae:.2f}")
    click.echo(f"Cenários avaliados: {report.evaluated_scenarios}/{report.total_scenarios}")
    for dimension, summary in report.by_dimension.items():
        click.echo(
            f"  - {dimension}: kappa={summary.kappa:.2f}, "
            f"pearson={summary.pearson_correlation:.2f}, mae={summary.mae:.2f}"
        )
    if report.high_disagreements:
        click.echo(f"Divergências >=2 pontos: {len(report.high_disagreements)}")
        for row in report.high_disagreements:
            click.echo(
                f"  - {row.scenario_id} ({row.dimension}): "
                f"humano={row.human_consensus_score}, juiz={row.judge_score}"
            )
    click.echo(f"Relatório salvo em: {output_path}")


def _write_validation_report(output_path: Path, report: ValidationReport) -> None:
    """Persist ``ValidationReport`` as JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report.model_dump(mode="json"), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


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
