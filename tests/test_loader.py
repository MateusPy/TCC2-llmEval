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
            {"text": "Em qual cidade fica a capital brasileira?", "type": "paraphrase"},
            {"text": "Onde fica a sede do governo brasileiro?", "type": "paraphrase"},
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
            {"text": "Qaul é a capital do Brasl?", "level": "character", "type": "typo"},
        ],
    }


def _bank(dimension: str, scenarios: list[dict], version: str = "0.1.0") -> dict:
    return {"dimension": dimension, "version": version, "scenarios": scenarios}


def _write_bank(directory: Path, dimension: str, payload: dict) -> Path:
    file_path = directory / f"{dimension}.json"
    file_path.write_text(json.dumps(payload), encoding="utf-8")
    return file_path


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


def test_scenario_minimal_valid():
    scenario = Scenario(**_factual_scenario())
    assert scenario.id == "factual-001"
    assert scenario.dimension == "factual"
    assert scenario.variants == []


def test_scenario_invalid_dimension():
    bad = _factual_scenario()
    bad["dimension"] = "invalid"
    with pytest.raises(ValidationError, match="Invalid dimension"):
        Scenario(**bad)


def test_scenario_missing_required_fields():
    with pytest.raises(ValidationError):
        Scenario(id="x", dimension="factual")  # type: ignore[call-arg]


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


def test_scenario_variant_preserves_extra_metadata():
    variant = ScenarioVariant(text="abc", level="character", type="typo")  # type: ignore[call-arg]
    assert variant.text == "abc"
    assert getattr(variant, "level") == "character"
    assert getattr(variant, "type") == "typo"


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
    assert bank.scenarios[0].variants[0].text.startswith("Em qual cidade")


def test_loader_load_robustness_preserves_variant_metadata(tmp_path: Path):
    _write_bank(tmp_path, "robustness", _bank("robustness", [_robustness_scenario()]))
    loader = ScenarioLoader(base_path=tmp_path)
    bank = loader.load("robustness")
    variant = bank.scenarios[0].variants[0]
    assert getattr(variant, "level") == "character"
    assert getattr(variant, "type") == "typo"


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


def test_loader_schema_validation_error(tmp_path: Path):
    bad_scenario = _factual_scenario()
    del bad_scenario["ground_truth"]
    _write_bank(tmp_path, "factual", _bank("factual", [bad_scenario]))
    loader = ScenarioLoader(base_path=tmp_path)
    with pytest.raises(ScenarioLoadError, match="Schema validation failed"):
        loader.load("factual")


def test_loader_dimension_header_mismatch(tmp_path: Path):
    payload = _bank("consistency", [_consistency_scenario()])
    (tmp_path / "factual.json").write_text(json.dumps(payload), encoding="utf-8")
    loader = ScenarioLoader(base_path=tmp_path)
    with pytest.raises(ScenarioLoadError, match="does not match requested dimension"):
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
    """The empty banks shipped with the package must validate cleanly."""
    loader = ScenarioLoader()
    banks = loader.load_all()
    for dimension, bank in banks.items():
        assert bank.dimension == dimension
        assert isinstance(bank.scenarios, list)
