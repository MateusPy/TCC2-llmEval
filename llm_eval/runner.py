"""Runner: orquestra o fluxo completo de avaliação do framework.

Liga as peças produzidas pelos demais módulos (config, scenarios, providers,
evaluation) num único pipeline:

1. Constrói os providers (alvo + juiz) a partir da :class:`Config`.
2. Carrega o banco de cenários para as dimensões selecionadas via
   :class:`ScenarioLoader`.
3. Para cada cenário, executa o fluxo apropriado para a dimensão:

   - **factual**: envia o prompt ``repetitions`` vezes, avalia cada resposta
     pelo :meth:`Judge.evaluate_factual` e computa BERTScore contra
     ``ground_truth``.
   - **consistency**: envia o prompt-base + todas as variantes, avalia o
     conjunto pelo :meth:`Judge.evaluate_consistency` e computa
     :func:`calculate_consistency`.
   - **robustness**: envia o prompt-base e cada variante, avalia cada par
     pelo :meth:`Judge.evaluate_robustness` e computa BERTScore entre as
     duas respostas.

4. Salva o :class:`RunResult` incrementalmente em disco a cada cenário
   concluído (``output_dir/run_partial.json``) e, ao final, em
   ``output_dir/run_result.json``.

Erros de cenário individuais são capturados e registrados em
``ScenarioResult.error`` em vez de abortar o run inteiro.
"""

from __future__ import annotations

import json
import logging
import os
import tempfile
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from llm_eval.config import Config, ProviderSettings
from llm_eval.evaluation.judge import Judge, JudgeResult
from llm_eval.evaluation.metrics import (
    MetricResult,
    calculate_bertscore,
    calculate_consistency,
)
from llm_eval.providers.base import BaseProvider, ProviderConfig, ProviderResponse
from llm_eval.providers.custom import build_from_settings as build_custom_provider
from llm_eval.providers.gemini import GeminiProvider
from llm_eval.providers.mistral import MistralProvider
from llm_eval.scenarios.loader import Scenario, ScenarioLoader

logger = logging.getLogger(__name__)

PARTIAL_FILENAME = "run_partial.json"
FINAL_FILENAME = "run_result.json"

ProviderFactory = Callable[[ProviderSettings], BaseProvider]
BertScoreFn = Callable[..., MetricResult]
ConsistencyFn = Callable[..., MetricResult]


class ScenarioResult(BaseModel):
    """Outcome of evaluating a single scenario.

    Attributes:
        scenario_id: Identifier from the scenario bank.
        dimension: Reliability dimension (``factual``/``consistency``/``robustness``).
        category: Topical category copied from the scenario.
        prompt: Base prompt that was sent to the chatbot.
        responses: Responses to the base prompt (one per repetition for
            factual, single entry for consistency/robustness).
        variant_responses: Map ``variant_id -> ProviderResponse`` for
            ``consistency`` and ``robustness`` scenarios. Empty for factual.
        judge_results: Qualitative evaluations produced by the judge.
        metric_results: Quantitative metrics (BERTScore, consistency) produced
            by ``llm_eval.evaluation.metrics``.
        error: Populated when the scenario crashed; siblings keep running.
    """

    model_config = ConfigDict(extra="forbid")

    scenario_id: str
    dimension: str
    category: str
    prompt: str
    responses: list[ProviderResponse] = Field(default_factory=list)
    variant_responses: dict[str, ProviderResponse] = Field(default_factory=dict)
    judge_results: list[JudgeResult] = Field(default_factory=list)
    metric_results: list[MetricResult] = Field(default_factory=list)
    error: str | None = None


class RunResult(BaseModel):
    """Aggregate result of a full evaluation run.

    Attributes:
        config: Sanitized configuration used (without API keys).
        started_at: When :meth:`Runner.run` was invoked.
        finished_at: When the run finished (``None`` while still in progress).
        scenario_results: One entry per scenario evaluated, in execution order.
    """

    model_config = ConfigDict(extra="forbid")

    config: dict[str, Any]
    started_at: datetime
    finished_at: datetime | None = None
    scenario_results: list[ScenarioResult] = Field(default_factory=list)


def _settings_to_provider_config(settings: ProviderSettings) -> ProviderConfig:
    return ProviderConfig(
        api_key=settings.api_key or "",
        model=settings.model,
        temperature=settings.temperature,
        max_tokens=settings.max_tokens,
    )


def _validate_gemini_dual_provider(config: Config) -> None:
    """Reject configurations that would corrupt the Gemini SDK global state.

    The ``google-generativeai`` SDK authenticates via the process-global
    :func:`genai.configure`. When both the chatbot under test and the judge
    are Gemini-backed but use different API keys, the second provider
    constructed silently overwrites the first's credentials — meaning calls
    on either provider may end up using the wrong key. Detect that exact
    case at construction time and raise rather than letting the run produce
    silently corrupted results.
    """
    if not config.judge.enabled:
        return
    if config.provider.type != "gemini" or config.judge.provider.type != "gemini":
        return
    target_key = config.provider.api_key
    judge_key = config.judge.provider.api_key
    if target_key and judge_key and target_key != judge_key:
        raise ValueError(
            "Cannot use two Gemini providers with different API keys in the same "
            "process: google-generativeai authenticates globally and the second "
            "configure() call would corrupt the first provider's credentials. "
            "Use the same API key for both, switch one of them to a different "
            "provider type, or run them in separate processes."
        )


def default_provider_factory(settings: ProviderSettings) -> BaseProvider:
    """Build a concrete :class:`BaseProvider` from user-facing settings."""
    if settings.type == "gemini":
        return GeminiProvider(_settings_to_provider_config(settings))
    if settings.type == "mistral":
        return MistralProvider(_settings_to_provider_config(settings))
    if settings.type == "custom":
        return build_custom_provider(
            type=settings.type,
            api_key=settings.api_key,
            model=settings.model,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            url=settings.url,
            method=settings.method,
            headers=settings.headers,
            request_template=settings.request_template,
            response_path=settings.response_path,
        )
    raise ValueError(f"Unknown provider type: {settings.type!r}")


def sanitize_config(config: Config) -> dict[str, Any]:
    """Return a serializable config dump with API keys redacted."""
    data = config.model_dump(mode="json")
    _redact_api_keys(data)
    return data


def _redact_api_keys(obj: Any) -> None:
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == "api_key" and isinstance(value, str) and value:
                obj[key] = "***REDACTED***"
            else:
                _redact_api_keys(value)
    elif isinstance(obj, list):
        for item in obj:
            _redact_api_keys(item)


class Runner:
    """Orchestrates the end-to-end evaluation flow.

    The runner is intentionally synchronous and dependency-injectable: each
    collaborator (provider factory, judge, scenario loader, metrics) can be
    overridden so tests can exercise the orchestration logic without hitting
    real LLMs or filesystems.
    """

    def __init__(
        self,
        config: Config,
        *,
        scenarios_loader: ScenarioLoader | None = None,
        provider_factory: ProviderFactory | None = None,
        judge: Judge | None = None,
        bertscore_fn: BertScoreFn | None = None,
        consistency_fn: ConsistencyFn | None = None,
        partial_save_every: int = 1,
    ) -> None:
        """Initialize the runner.

        Args:
            config: Validated framework configuration.
            scenarios_loader: Pre-built loader; ``None`` builds one from
                ``config.scenarios_path``.
            provider_factory: Factory used to build the chatbot under test
                and the judge provider. ``None`` uses
                :func:`default_provider_factory`.
            judge: Pre-built judge instance. ``None`` builds one from
                ``config.judge``. Ignored when ``config.judge.enabled`` is
                ``False``.
            bertscore_fn: Override for :func:`calculate_bertscore`. Tests
                use this to skip BERT model loading.
            consistency_fn: Override for :func:`calculate_consistency`.
            partial_save_every: Save the partial JSON result every N
                scenarios. ``1`` (default) saves after every scenario.

        Raises:
            ValueError: If both ``config.provider`` and ``config.judge.provider``
                are Gemini with different ``api_key``s. The
                ``google-generativeai`` SDK uses process-global authentication,
                so two Gemini providers with different keys in the same process
                would silently corrupt each other (see :mod:`llm_eval.providers.gemini`).
        """
        _validate_gemini_dual_provider(config)

        self.config = config
        self._scenarios_loader = scenarios_loader or ScenarioLoader(config.scenarios_path)
        self._provider_factory = provider_factory or default_provider_factory
        self._provider = self._provider_factory(config.provider)
        self._owns_judge = judge is None
        self._judge: Judge | None
        if not config.judge.enabled:
            self._judge = None
            self._owns_judge = False
        elif judge is not None:
            self._judge = judge
        else:
            self._judge = Judge(self._provider_factory(config.judge.provider))
        self._bertscore = bertscore_fn or calculate_bertscore
        self._consistency = consistency_fn or calculate_consistency
        self._partial_save_every = max(1, int(partial_save_every))

    def run(self) -> RunResult:
        """Execute the full evaluation flow and persist the result.

        Provider resources (including any ``httpx.Client`` owned by a
        :class:`CustomProvider`) are released in a ``finally`` block, even
        if the run is interrupted by an unhandled exception.
        """
        result = RunResult(
            config=sanitize_config(self.config),
            started_at=datetime.now(timezone.utc),
        )

        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        partial_path = output_dir / PARTIAL_FILENAME
        final_path = output_dir / FINAL_FILENAME

        try:
            scenarios = self._collect_scenarios()
            total = len(scenarios)
            logger.info(
                "Runner starting: %d scenarios across %d dimensions (judge: %s)",
                total,
                len(self.config.dimensions),
                "enabled" if self._judge is not None else "disabled",
            )

            for index, scenario in enumerate(scenarios, start=1):
                logger.info(
                    "Evaluating scenario %d/%d [%s] %s",
                    index,
                    total,
                    scenario.dimension,
                    scenario.id,
                )
                scenario_result = self._evaluate_scenario(scenario)
                result.scenario_results.append(scenario_result)

                if index % self._partial_save_every == 0 or index == total:
                    self._save_json(partial_path, result)

            result.finished_at = datetime.now(timezone.utc)
            self._save_json(final_path, result)
            if partial_path.exists():
                partial_path.unlink()
            logger.info("Runner finished: results saved to %s", final_path)
            return result
        finally:
            self._close_providers()

    def _close_providers(self) -> None:
        """Release every provider this runner owns, swallowing close errors.

        Called from ``run()``'s ``finally`` block to avoid socket/FD leaks on
        long-lived processes or repeated runs in the same session.
        """
        providers_to_close: list[BaseProvider] = [self._provider]
        if self._owns_judge and self._judge is not None:
            providers_to_close.append(self._judge.provider)

        for provider in providers_to_close:
            try:
                provider.close()
            except Exception as exc:
                logger.warning(
                    "Failed to close provider %s: %s",
                    type(provider).__name__,
                    exc,
                )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _collect_scenarios(self) -> list[Scenario]:
        scenarios: list[Scenario] = []
        for dimension in self.config.dimensions:
            bank = self._scenarios_loader.load(dimension)
            scenarios.extend(bank.scenarios)
        return scenarios

    def _evaluate_scenario(self, scenario: Scenario) -> ScenarioResult:
        try:
            if scenario.dimension == "factual":
                return self._evaluate_factual(scenario)
            if scenario.dimension == "consistency":
                return self._evaluate_consistency(scenario)
            if scenario.dimension == "robustness":
                return self._evaluate_robustness(scenario)
            raise ValueError(f"Unsupported dimension: {scenario.dimension}")
        except Exception as exc:
            logger.exception("Scenario %s failed: %s", scenario.id, exc)
            return ScenarioResult(
                scenario_id=scenario.id,
                dimension=scenario.dimension,
                category=scenario.category,
                prompt=scenario.prompt,
                error=f"{type(exc).__name__}: {exc}",
            )

    def _evaluate_factual(self, scenario: Scenario) -> ScenarioResult:
        result = ScenarioResult(
            scenario_id=scenario.id,
            dimension=scenario.dimension,
            category=scenario.category,
            prompt=scenario.prompt,
        )
        ground_truth = scenario.ground_truth or ""

        for _ in range(self.config.repetitions):
            response = self._provider.send(scenario.prompt)
            result.responses.append(response)
            if self._judge is not None:
                result.judge_results.append(
                    self._judge.evaluate_factual(
                        prompt=scenario.prompt,
                        ground_truth=ground_truth,
                        response=response.response_text,
                    )
                )
            result.metric_results.append(self._bertscore(ground_truth, response.response_text))
        return result

    def _evaluate_consistency(self, scenario: Scenario) -> ScenarioResult:
        result = ScenarioResult(
            scenario_id=scenario.id,
            dimension=scenario.dimension,
            category=scenario.category,
            prompt=scenario.prompt,
        )

        base_response = self._provider.send(scenario.prompt)
        result.responses.append(base_response)

        responses_for_consistency: list[str] = [base_response.response_text]
        for variant in scenario.variants:
            variant_response = self._provider.send(variant.prompt)
            result.variant_responses[variant.id] = variant_response
            responses_for_consistency.append(variant_response.response_text)

        if self._judge is not None:
            result.judge_results.append(
                self._judge.evaluate_consistency(
                    prompt=scenario.prompt,
                    responses=responses_for_consistency,
                )
            )
        result.metric_results.append(self._consistency(responses_for_consistency))
        return result

    def _evaluate_robustness(self, scenario: Scenario) -> ScenarioResult:
        result = ScenarioResult(
            scenario_id=scenario.id,
            dimension=scenario.dimension,
            category=scenario.category,
            prompt=scenario.prompt,
        )

        base_response = self._provider.send(scenario.prompt)
        result.responses.append(base_response)

        for variant in scenario.variants:
            variant_response = self._provider.send(variant.prompt)
            result.variant_responses[variant.id] = variant_response
            if self._judge is not None:
                result.judge_results.append(
                    self._judge.evaluate_robustness(
                        prompt=scenario.prompt,
                        original_response=base_response.response_text,
                        variant_type=variant.variant_type,
                        variant_prompt=variant.prompt,
                        variant_response=variant_response.response_text,
                    )
                )
            result.metric_results.append(
                self._bertscore(base_response.response_text, variant_response.response_text)
            )
        return result

    def _save_json(self, path: Path, result: RunResult) -> None:
        """Serialize ``result`` to ``path`` atomically.

        Writes to a temporary file in the same directory and then uses
        :func:`os.replace` (atomic on POSIX and Windows) to move it onto
        the target. This prevents ``run_partial.json`` /
        ``run_result.json`` from being observed in a half-written,
        unparseable state if the process crashes or the disk fills mid-write.
        """
        payload = result.model_dump(mode="json")
        serialized = json.dumps(payload, indent=2, ensure_ascii=False)

        directory = path.parent
        directory.mkdir(parents=True, exist_ok=True)

        fd, tmp_name = tempfile.mkstemp(
            prefix=f".{path.name}.",
            suffix=".tmp",
            dir=directory,
        )
        tmp_path = Path(tmp_name)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                fh.write(serialized)
                fh.flush()
                try:
                    os.fsync(fh.fileno())
                except OSError:  # pragma: no cover - filesystem-dependent
                    # fsync is best-effort; some filesystems (e.g. Windows
                    # network mounts) don't support it. The atomic rename
                    # below still guarantees no partially-written file.
                    pass
            os.replace(tmp_path, path)
        except Exception:
            tmp_path.unlink(missing_ok=True)
            raise
