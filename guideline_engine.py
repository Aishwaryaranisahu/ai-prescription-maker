"""
guideline_engine.py

Core recommendation logic for the AI Prescription Maker.

This is a rule-based "guideline mapping" engine: each diagnosis is mapped
to a small set of clinically common first-line and second-line medications
(dummy/simplified data for demonstration purposes only — NOT medical advice
and NOT for real clinical use). The engine:

  1. Looks up the diagnosis in the guideline table.
  2. Filters out any drug the patient is allergic to.
  3. Falls back to an alternative drug if the first-line option is unsafe.
  4. Returns a structured prescription the API layer can persist.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class DrugRecommendation:
    name: str
    dosage: str
    duration: str
    notes: str = ""


@dataclass
class GuidelineEntry:
    diagnosis: str
    first_line: List[DrugRecommendation]
    second_line: List[DrugRecommendation] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Simplified clinical guideline table.
# In a production system this would come from a vetted medical database
# (e.g. mapped to ICD-10 codes) — here it's hard-coded sample data so the
# recommendation logic can be demonstrated end-to-end.
# ---------------------------------------------------------------------------
GUIDELINES = {
    "hypertension": GuidelineEntry(
        diagnosis="Hypertension",
        first_line=[
            DrugRecommendation("Amlodipine", "5 mg once daily", "30 days"),
        ],
        second_line=[
            DrugRecommendation("Losartan", "50 mg once daily", "30 days"),
        ],
    ),
    "type 2 diabetes": GuidelineEntry(
        diagnosis="Type 2 Diabetes",
        first_line=[
            DrugRecommendation("Metformin", "500 mg twice daily", "30 days"),
        ],
        second_line=[
            DrugRecommendation("Glimepiride", "2 mg once daily", "30 days"),
        ],
    ),
    "common cold": GuidelineEntry(
        diagnosis="Common Cold",
        first_line=[
            DrugRecommendation("Paracetamol", "500 mg every 6 hours", "5 days"),
            DrugRecommendation("Cetirizine", "10 mg once daily", "5 days"),
        ],
        second_line=[
            DrugRecommendation("Ibuprofen", "400 mg every 8 hours", "5 days"),
        ],
    ),
    "migraine": GuidelineEntry(
        diagnosis="Migraine",
        first_line=[
            DrugRecommendation("Sumatriptan", "50 mg at onset, may repeat once after 2 hrs", "as needed"),
        ],
        second_line=[
            DrugRecommendation("Naproxen", "500 mg at onset", "as needed"),
        ],
    ),
    "acid reflux": GuidelineEntry(
        diagnosis="Acid Reflux (GERD)",
        first_line=[
            DrugRecommendation("Omeprazole", "20 mg once daily before breakfast", "14 days"),
        ],
        second_line=[
            DrugRecommendation("Ranitidine", "150 mg twice daily", "14 days"),
        ],
    ),
    "bacterial throat infection": GuidelineEntry(
        diagnosis="Bacterial Throat Infection",
        first_line=[
            DrugRecommendation("Amoxicillin", "500 mg three times daily", "7 days"),
        ],
        second_line=[
            DrugRecommendation("Azithromycin", "500 mg once daily", "3 days",
                                notes="Alternative for penicillin allergy"),
        ],
    ),
}


def normalize(text: str) -> str:
    return text.strip().lower()


def is_contraindicated(drug: DrugRecommendation, allergies: List[str]) -> bool:
    normalized_allergies = {normalize(a) for a in allergies}
    return normalize(drug.name) in normalized_allergies


def generate_prescription(diagnosis: str, allergies: Optional[List[str]] = None):
    """
    Given a diagnosis string and a list of patient allergies, return a
    guideline-based prescription: a list of DrugRecommendation objects,
    preferring first-line drugs and swapping in second-line alternatives
    when a first-line drug is contraindicated by allergy.

    Raises KeyError if the diagnosis is not in the guideline table.
    """
    allergies = allergies or []
    key = normalize(diagnosis)
    if key not in GUIDELINES:
        raise KeyError(f"No guideline entry found for diagnosis: '{diagnosis}'")

    entry = GUIDELINES[key]
    prescribed: List[DrugRecommendation] = []
    substitutions: List[str] = []

    for drug in entry.first_line:
        if is_contraindicated(drug, allergies):
            # Try to find a safe second-line alternative
            alternative = next(
                (d for d in entry.second_line if not is_contraindicated(d, allergies)),
                None,
            )
            if alternative:
                prescribed.append(alternative)
                substitutions.append(f"{drug.name} -> {alternative.name} (allergy)")
            else:
                substitutions.append(f"{drug.name} skipped (allergy, no safe alternative found)")
        else:
            prescribed.append(drug)

    return {
        "diagnosis": entry.diagnosis,
        "medications": [d.__dict__ for d in prescribed],
        "substitutions": substitutions,
    }


def list_supported_diagnoses() -> List[str]:
    return [entry.diagnosis for entry in GUIDELINES.values()]
