"""
tests/test_engine.py

Unit tests for guideline_engine.py — run with:
    python -m pytest tests/
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import guideline_engine as engine


def test_generates_first_line_drug_when_no_allergy():
    result = engine.generate_prescription("Hypertension", allergies=[])
    names = [m["name"] for m in result["medications"]]
    assert "Amlodipine" in names
    assert result["substitutions"] == []


def test_substitutes_second_line_when_allergic():
    result = engine.generate_prescription("Bacterial Throat Infection", allergies=["Amoxicillin"])
    names = [m["name"] for m in result["medications"]]
    assert "Amoxicillin" not in names
    assert "Azithromycin" in names
    assert len(result["substitutions"]) == 1


def test_case_and_whitespace_insensitive_lookup():
    result = engine.generate_prescription("  hYpErTeNsIoN  ")
    assert result["diagnosis"] == "Hypertension"


def test_unknown_diagnosis_raises_key_error():
    with pytest.raises(KeyError):
        engine.generate_prescription("Nonexistent Condition")


def test_multiple_first_line_drugs_common_cold():
    result = engine.generate_prescription("Common Cold")
    names = {m["name"] for m in result["medications"]}
    assert {"Paracetamol", "Cetirizine"}.issubset(names)


def test_list_supported_diagnoses_not_empty():
    diagnoses = engine.list_supported_diagnoses()
    assert len(diagnoses) >= 5
    assert "Hypertension" in diagnoses
