"""Carregamento e validação de cenários de teste.

Este módulo implementa o carregador de cenários do framework. Um cenário descreve
um caso de teste a ser enviado ao chatbot avaliado, organizado por dimensão de
confiabilidade (``factual``, ``consistency`` ou ``robustness``).

O formato esperado dos arquivos JSON segue a estrutura documentada no README e
no documento de metodologia (``docs/metodologia-cenarios.md``):

.. code-block:: json

    {
      "dimension": "factual",
      "version": "1.0.0",
      "scenarios": [
        {
          "id": "factual-001",
          "dimension": "factual",
          "category": "knowledge",
          "prompt": "...",
          "ground_truth": "...",
          "variants": []
        }
      ]
    }

Campos extras (``source``, ``derivation_method``, etc.) são preservados como
metadados de rastreabilidade conforme a metodologia adotada no estudo.
"""

from __future__ import annotations

import json
from importlib import resources
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

ALLOWED_DIMENSIONS = ("factual", "consistency", "robustness")
DEFAULT_BANK_PACKAGE = "llm_eval.scenarios.bank"
DEFAULT_BANK_FILES = {
    "factual": "factual.json",
    "consistency": "consistency.json",
    "robustness": "robustness.json",
}


class ScenarioLoadError(Exception):
    """Raised when a scenarios file cannot be loaded or fails validation."""


class ScenarioVariant(BaseModel):
    """Variant of a scenario prompt.

    Used by the ``consistency`` and ``robustness`` dimensions to express
    paraphrases or perturbations of the base prompt. Extra metadata fields
    (e.g. ``level``, ``type``) are preserved to support traceability.

    Attributes:
        text: Variant text sent to the chatbot.
    """

    model_config = ConfigDict(extra="allow")

    text: str


class Scenario(BaseModel):
    """Single test scenario.

    Attributes:
        id: Unique identifier within the bank.
        dimension: Reliability dimension this scenario belongs to.
        category: Topical category of the scenario (free-form, see README).
        prompt: Base prompt sent to the chatbot.
        ground_truth: Expected reference answer used for evaluation.
        variants: Variants derived from the base prompt (paraphrases or
            perturbations). Empty list for purely factual scenarios.
    """

    model_config = ConfigDict(extra="allow")

    id: str
    dimension: str
    category: str
    prompt: str
    ground_truth: str
    variants: list[ScenarioVariant] = Field(default_factory=list)

    @field_validator("dimension")
    @classmethod
    def _validate_dimension(cls, v: str) -> str:
        if v not in ALLOWED_DIMENSIONS:
            raise ValueError(f"Invalid dimension '{v}'. Allowed values: {list(ALLOWED_DIMENSIONS)}")
        return v


class ScenarioBank(BaseModel):
    """Collection of scenarios for a single dimension.

    Mirrors the on-disk JSON structure with a ``dimension``/``version`` header
    and a ``scenarios`` list.

    Attributes:
        dimension: Reliability dimension covered by this bank.
        version: Bank schema version.
        scenarios: Scenarios contained in this bank.
    """

    model_config = ConfigDict(extra="allow")

    dimension: str
    version: str
    scenarios: list[Scenario] = Field(default_factory=list)

    @field_validator("dimension")
    @classmethod
    def _validate_dimension(cls, v: str) -> str:
        if v not in ALLOWED_DIMENSIONS:
            raise ValueError(f"Invalid dimension '{v}'. Allowed values: {list(ALLOWED_DIMENSIONS)}")
        return v

    def model_post_init(self, __context: Any) -> None:
        """Ensure every scenario matches the bank's declared dimension."""
        mismatched = [s.id for s in self.scenarios if s.dimension != self.dimension]
        if mismatched:
            raise ValueError(
                f"Scenarios {mismatched} do not match bank dimension '{self.dimension}'"
            )

        seen: set[str] = set()
        duplicates: list[str] = []
        for scenario in self.scenarios:
            if scenario.id in seen:
                duplicates.append(scenario.id)
            seen.add(scenario.id)
        if duplicates:
            raise ValueError(f"Duplicate scenario ids in bank: {sorted(set(duplicates))}")


class ScenarioLoader:
    """Loads scenario banks from disk or from the built-in package data.

    When ``base_path`` is provided, the loader reads ``factual.json``,
    ``consistency.json`` and ``robustness.json`` from that directory. When
    ``base_path`` is ``None``, it falls back to the bank shipped with the
    package (``llm_eval.scenarios.bank``).

    Attributes:
        base_path: Optional directory containing custom scenario files.
    """

    def __init__(self, base_path: str | Path | None = None) -> None:
        """Initialize the loader.

        Args:
            base_path: Directory containing the JSON files. ``None`` selects
                the built-in scenario bank.

        Raises:
            ScenarioLoadError: If ``base_path`` is provided but does not point
                to an existing directory.
        """
        if base_path is None:
            self.base_path: Path | None = None
        else:
            path = Path(base_path)
            if not path.exists():
                raise ScenarioLoadError(f"Scenarios path does not exist: {path}")
            if not path.is_dir():
                raise ScenarioLoadError(f"Scenarios path is not a directory: {path}")
            self.base_path = path

    def load(self, dimension: str) -> ScenarioBank:
        """Load the scenario bank for a single dimension.

        Args:
            dimension: One of ``"factual"``, ``"consistency"`` or
                ``"robustness"``.

        Returns:
            ScenarioBank: Validated scenario bank for the requested dimension.

        Raises:
            ScenarioLoadError: If the dimension is unknown, the file is
                missing, the JSON is malformed, or the schema fails validation.
        """
        if dimension not in ALLOWED_DIMENSIONS:
            raise ScenarioLoadError(
                f"Unknown dimension '{dimension}'. Allowed values: {list(ALLOWED_DIMENSIONS)}"
            )

        raw = self._read_raw(dimension)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ScenarioLoadError(
                f"Invalid JSON in scenario file for dimension '{dimension}': {exc}"
            ) from exc

        if not isinstance(data, dict):
            raise ScenarioLoadError(
                f"Scenario file for dimension '{dimension}' must contain a JSON object, "
                f"got {type(data).__name__}"
            )

        try:
            bank = ScenarioBank(**data)
        except ValidationError as exc:
            raise ScenarioLoadError(
                f"Schema validation failed for dimension '{dimension}': {exc}"
            ) from exc

        if bank.dimension != dimension:
            raise ScenarioLoadError(
                f"Bank dimension '{bank.dimension}' does not match requested "
                f"dimension '{dimension}'"
            )
        return bank

    def load_all(self, dimensions: list[str] | None = None) -> dict[str, ScenarioBank]:
        """Load multiple scenario banks at once.

        Args:
            dimensions: Dimensions to load. ``None`` loads all supported
                dimensions.

        Returns:
            dict[str, ScenarioBank]: Mapping from dimension name to its bank.
        """
        target = list(dimensions) if dimensions is not None else list(ALLOWED_DIMENSIONS)
        return {dim: self.load(dim) for dim in target}

    def _read_raw(self, dimension: str) -> str:
        """Read the raw JSON content for ``dimension`` from disk or package data."""
        filename = DEFAULT_BANK_FILES[dimension]

        if self.base_path is not None:
            file_path = self.base_path / filename
            if not file_path.exists():
                raise ScenarioLoadError(f"Scenario file not found: {file_path}")
            return file_path.read_text(encoding="utf-8")

        try:
            return (
                resources.files(DEFAULT_BANK_PACKAGE).joinpath(filename).read_text(encoding="utf-8")
            )
        except (FileNotFoundError, ModuleNotFoundError) as exc:
            raise ScenarioLoadError(
                f"Built-in scenario file '{filename}' is missing from the package"
            ) from exc
