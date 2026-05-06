"""Testes para scenarios/loader.py."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from llm_eval.scenarios.loader import (
    ALLOWED_DIMENSIONS,
    Scenario,
    ScenarioBank,
    ScenarioLoader,
    ScenarioLoadError,
    ScenarioVariant,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _variant(
    variant_id: str,
    variant_type: str = "paraphrase",
    prompt: str = "Em qual cidade fica a capital brasileira?",
    **extras: object,
) -> dict:
    payload: dict = {"id": variant_id, "variant_type": variant_type, "prompt": prompt}
    payload.update(extras)
    return payload


def _factual_scenario(scenario_id: str = "factual-001") -> dict:
    return {
        "id": scenario_id,
        "dimension": "factual",
        "category": "knowledge",
        "prompt": "Qual é a capital do Brasil?",
        "ground_truth": "Brasília",
        "variants": [],
    }


def _consistency_scenario(scenario_id: str = "consistency-001") -> dict:
    return {
        "id": scenario_id,
        "dimension": "consistency",
        "category": "knowledge",
        "prompt": "Qual é a capital do Brasil?",
        "ground_truth": "Brasília",
        "variants": [
            _variant(f"{scenario_id}-v1", prompt="Em qual cidade fica a capital brasileira?"),
            _variant(f"{scenario_id}-v2", prompt="Onde fica a sede do governo brasileiro?"),
        ],
    }


def _robustness_scenario(scenario_id: str = "robustness-001") -> dict:
    return {
        "id": scenario_id,
        "dimension": "robustness",
        "category": "knowledge",
        "prompt": "Qual é a capital do Brasil?",
        "ground_truth": "Brasília",
        "variants": [
            _variant(
                f"{scenario_id}-v1",
                variant_type="typo",
                prompt="Qaul é a capital do Brasl?",
                level="character",
                description="Inversão de letras",
            ),
        ],
    }


def _bank(dimension: str, scenarios: list[dict], version: str = "0.1.0") -> dict:
    return {"dimension": dimension, "version": version, "scenarios": scenarios}


def _write_bank(directory: Path, dimension: str, payload: dict) -> Path:
    file_path = directory / f"{dimension}.json"
    file_path.write_text(json.dumps(payload), encoding="utf-8")
    return file_path


# ---------------------------------------------------------------------------
# ScenarioVariant
# ---------------------------------------------------------------------------


def test_variant_minimal_valid():
    v = ScenarioVariant(id="v1", variant_type="paraphrase", prompt="abc")
    assert v.id == "v1"
    assert v.variant_type == "paraphrase"
    assert v.prompt == "abc"
    assert v.description is None
    assert v.level is None


def test_variant_with_level_and_description():
    v = ScenarioVariant(
        id="v1",
        variant_type="typo",
        prompt="captial",
        level="character",
        description="Typo intencional em 'capital'",
    )
    assert v.level == "character"
    assert v.description == "Typo intencional em 'capital'"


def test_variant_missing_required_fields():
    with pytest.raises(ValidationError):
        ScenarioVariant(id="v1", prompt="abc")  # type: ignore[call-arg]


def test_variant_preserves_extra_metadata():
    v = ScenarioVariant(
        id="v1",
        variant_type="paraphrase",
        prompt="abc",
        source="manual",  # type: ignore[call-arg]
    )
    assert getattr(v, "source") == "manual"


# ---------------------------------------------------------------------------
# Scenario — happy paths and dimension-specific constraints
# ---------------------------------------------------------------------------


def test_scenario_factual_minimal_valid():
    scenario = Scenario(**_factual_scenario())
    assert scenario.id == "factual-001"
    assert scenario.dimension == "factual"
    assert scenario.variants == []


def test_scenario_consistency_with_variants_valid():
    scenario = Scenario(**_consistency_scenario())
    assert scenario.dimension == "consistency"
    assert len(scenario.variants) == 2
    assert scenario.variants[0].variant_type == "paraphrase"


def test_scenario_robustness_with_variant_metadata():
    scenario = Scenario(**_robustness_scenario())
    variant = scenario.variants[0]
    assert variant.variant_type == "typo"
    assert variant.level == "character"


def test_scenario_invalid_dimension():
    bad = _factual_scenario()
    bad["dimension"] = "invalid"
    with pytest.raises(ValidationError, match="Invalid dimension"):
        Scenario(**bad)


def test_scenario_missing_required_fields():
    with pytest.raises(ValidationError):
        Scenario(id="x", dimension="factual")  # type: ignore[call-arg]


def test_scenario_factual_requires_ground_truth():
    bad = _factual_scenario()
    bad["ground_truth"] = None
    with pytest.raises(ValidationError, match="no ground_truth"):
        Scenario(**bad)


def test_scenario_factual_rejects_missing_ground_truth_field():
    bad = _factual_scenario()
    del bad["ground_truth"]
    with pytest.raises(ValidationError, match="no ground_truth"):
        Scenario(**bad)


def test_scenario_consistency_requires_at_least_one_variant():
    bad = _consistency_scenario()
    bad["variants"] = []
    with pytest.raises(ValidationError, match="must declare at least one variant"):
        Scenario(**bad)


def test_scenario_robustness_requires_at_least_one_variant():
    bad = _robustness_scenario()
    bad["variants"] = []
    with pytest.raises(ValidationError, match="must declare at least one variant"):
        Scenario(**bad)


def test_scenario_consistency_allows_missing_ground_truth():
    payload = _consistency_scenario()
    payload["ground_truth"] = None
    scenario = Scenario(**payload)
    assert scenario.ground_truth is None


def test_scenario_preserves_extra_metadata():
    payload = _factual_scenario()
    payload["source"] = {"benchmark": "TruthfulQA", "original_id": "tqa_142"}
    payload["derivation_method"] = "tradução supervisionada"
    scenario = Scenario(**payload)
    assert getattr(scenario, "source") == {
        "benchmark": "TruthfulQA",
        "original_id": "tqa_142",
    }
    assert getattr(scenario, "derivation_method") == "tradução supervisionada"


# ---------------------------------------------------------------------------
# ScenarioBank
# ---------------------------------------------------------------------------


def test_scenario_bank_valid():
    bank = ScenarioBank(**_bank("factual", [_factual_scenario()]))
    assert bank.dimension == "factual"
    assert bank.version == "0.1.0"
    assert len(bank.scenarios) == 1


def test_scenario_bank_empty_scenarios_allowed():
    bank = ScenarioBank(**_bank("factual", []))
    assert bank.scenarios == []


def test_scenario_bank_invalid_dimension():
    with pytest.raises(ValidationError, match="Invalid dimension"):
        ScenarioBank(**_bank("invalid", []))


def test_scenario_bank_dimension_mismatch():
    payload = _bank("factual", [_consistency_scenario()])
    with pytest.raises(ValidationError, match="do not match bank dimension"):
        ScenarioBank(**payload)


def test_scenario_bank_duplicate_ids():
    payload = _bank(
        "factual",
        [_factual_scenario("dup-1"), _factual_scenario("dup-1")],
    )
    with pytest.raises(ValidationError, match="Duplicate scenario ids"):
        ScenarioBank(**payload)


# ---------------------------------------------------------------------------
# ScenarioLoader — base_path validation
# ---------------------------------------------------------------------------


def test_loader_init_nonexistent_path(tmp_path: Path):
    missing = tmp_path / "does-not-exist"
    with pytest.raises(ScenarioLoadError, match="does not exist"):
        ScenarioLoader(base_path=missing)


def test_loader_init_path_not_directory(tmp_path: Path):
    file_path = tmp_path / "regular.json"
    file_path.write_text("{}", encoding="utf-8")
    with pytest.raises(ScenarioLoadError, match="not a directory"):
        ScenarioLoader(base_path=file_path)


def test_loader_init_accepts_string_path(tmp_path: Path):
    loader = ScenarioLoader(base_path=str(tmp_path))
    assert loader.base_path == tmp_path


# ---------------------------------------------------------------------------
# ScenarioLoader.load — happy paths
# ---------------------------------------------------------------------------


def test_loader_load_factual(tmp_path: Path):
    _write_bank(tmp_path, "factual", _bank("factual", [_factual_scenario()]))
    loader = ScenarioLoader(base_path=tmp_path)
    bank = loader.load("factual")
    assert bank.dimension == "factual"
    assert len(bank.scenarios) == 1
    assert bank.scenarios[0].id == "factual-001"


def test_loader_load_consistency_with_variants(tmp_path: Path):
    _write_bank(tmp_path, "consistency", _bank("consistency", [_consistency_scenario()]))
    loader = ScenarioLoader(base_path=tmp_path)
    bank = loader.load("consistency")
    assert len(bank.scenarios[0].variants) == 2
    assert bank.scenarios[0].variants[0].prompt.startswith("Em qual cidade")


def test_loader_load_robustness_preserves_variant_metadata(tmp_path: Path):
    _write_bank(tmp_path, "robustness", _bank("robustness", [_robustness_scenario()]))
    loader = ScenarioLoader(base_path=tmp_path)
    bank = loader.load("robustness")
    variant = bank.scenarios[0].variants[0]
    assert variant.level == "character"
    assert variant.variant_type == "typo"


# ---------------------------------------------------------------------------
# ScenarioLoader.load — error paths
# ---------------------------------------------------------------------------


def test_loader_unknown_dimension(tmp_path: Path):
    loader = ScenarioLoader(base_path=tmp_path)
    with pytest.raises(ScenarioLoadError, match="Unknown dimension"):
        loader.load("invalid")


def test_loader_missing_file(tmp_path: Path):
    loader = ScenarioLoader(base_path=tmp_path)
    with pytest.raises(ScenarioLoadError, match="not found"):
        loader.load("factual")


def test_loader_invalid_json(tmp_path: Path):
    (tmp_path / "factual.json").write_text("{not valid json", encoding="utf-8")
    loader = ScenarioLoader(base_path=tmp_path)
    with pytest.raises(ScenarioLoadError, match="Invalid JSON"):
        loader.load("factual")


def test_loader_top_level_not_object(tmp_path: Path):
    (tmp_path / "factual.json").write_text("[]", encoding="utf-8")
    loader = ScenarioLoader(base_path=tmp_path)
    with pytest.raises(ScenarioLoadError, match="must contain a JSON object"):
        loader.load("factual")


def test_loader_schema_validation_error_missing_field(tmp_path: Path):
    bad_scenario = _factual_scenario()
    del bad_scenario["prompt"]
    _write_bank(tmp_path, "factual", _bank("factual", [bad_scenario]))
    loader = ScenarioLoader(base_path=tmp_path)
    with pytest.raises(ScenarioLoadError, match="Schema validation failed"):
        loader.load("factual")


def test_loader_schema_validation_error_factual_without_ground_truth(tmp_path: Path):
    """Cross-field validation surfaces as ScenarioLoadError, not raw ValueError."""
    bad_scenario = _factual_scenario()
    del bad_scenario["ground_truth"]
    _write_bank(tmp_path, "factual", _bank("factual", [bad_scenario]))
    loader = ScenarioLoader(base_path=tmp_path)
    with pytest.raises(ScenarioLoadError, match="Schema validation failed"):
        loader.load("factual")


def test_loader_schema_validation_error_consistency_without_variants(tmp_path: Path):
    bad_scenario = _consistency_scenario()
    bad_scenario["variants"] = []
    _write_bank(tmp_path, "consistency", _bank("consistency", [bad_scenario]))
    loader = ScenarioLoader(base_path=tmp_path)
    with pytest.raises(ScenarioLoadError, match="Schema validation failed"):
        loader.load("consistency")


def test_loader_dimension_header_mismatch(tmp_path: Path):
    payload = _bank("consistency", [_consistency_scenario()])
    (tmp_path / "factual.json").write_text(json.dumps(payload), encoding="utf-8")
    loader = ScenarioLoader(base_path=tmp_path)
    with pytest.raises(ScenarioLoadError, match="does not match requested dimension"):
        loader.load("factual")


def test_loader_bank_cross_field_errors_surface_as_load_error(tmp_path: Path):
    """ScenarioBank cross-field validation must produce ScenarioLoadError."""
    payload = _bank(
        "factual",
        [_factual_scenario("dup"), _factual_scenario("dup")],
    )
    _write_bank(tmp_path, "factual", payload)
    loader = ScenarioLoader(base_path=tmp_path)
    with pytest.raises(ScenarioLoadError, match="Schema validation failed"):
        loader.load("factual")


# ---------------------------------------------------------------------------
# ScenarioLoader.load_all
# ---------------------------------------------------------------------------


def test_load_all_default_dimensions(tmp_path: Path):
    _write_bank(tmp_path, "factual", _bank("factual", [_factual_scenario()]))
    _write_bank(tmp_path, "consistency", _bank("consistency", [_consistency_scenario()]))
    _write_bank(tmp_path, "robustness", _bank("robustness", [_robustness_scenario()]))
    loader = ScenarioLoader(base_path=tmp_path)
    banks = loader.load_all()
    assert set(banks) == set(ALLOWED_DIMENSIONS)


def test_load_all_subset(tmp_path: Path):
    _write_bank(tmp_path, "factual", _bank("factual", [_factual_scenario()]))
    loader = ScenarioLoader(base_path=tmp_path)
    banks = loader.load_all(dimensions=["factual"])
    assert list(banks) == ["factual"]


def test_load_all_propagates_failure(tmp_path: Path):
    _write_bank(tmp_path, "factual", _bank("factual", [_factual_scenario()]))
    loader = ScenarioLoader(base_path=tmp_path)
    with pytest.raises(ScenarioLoadError):
        loader.load_all()


# ---------------------------------------------------------------------------
# Built-in bank (package data fallback)
# ---------------------------------------------------------------------------


def test_loader_builtin_bank_loads_all_dimensions():
    """The built-in banks shipped with the package must validate cleanly."""
    loader = ScenarioLoader()
    banks = loader.load_all()
    minimum_counts = {"factual": 30, "consistency": 20, "robustness": 20}
    for dimension, bank in banks.items():
        assert bank.dimension == dimension
        assert isinstance(bank.scenarios, list)
        assert len(bank.scenarios) >= minimum_counts[dimension]
