# AI Prescription Maker

A guideline-based prescription generation system built as part of a team project for **Smart India Hackathon (SIH) 2025**. It automatically generates a recommended prescription for a given diagnosis, adjusts for patient drug allergies, supports patients being treated across multiple clinics, and allows one-tap cloning of a previous prescription for returning chronic-disease patients.

> **Disclaimer:** This project uses simplified, hard-coded sample clinical data for demonstration purposes only. It is **not** a real medical device and must never be used for actual patient care or clinical decision-making.

## Why this project

Doctors managing chronic-disease patients often re-write near-identical prescriptions across visits, and clinics frequently lack a shared view of a patient's prescription history when that patient is seen at more than one location. This project explores a small, working slice of that problem:

- **Guideline mapping** — map a diagnosis to first-line medications, with an automatic fallback to a second-line drug if the patient is allergic to the first choice.
- **Multi-clinic support** — a patient's full prescription history can be pulled up regardless of which clinic issued each prescription.
- **One-tap cloning** — instantly duplicate a prior prescription into a new visit record instead of re-entering it.

## Tech Stack

- **Backend:** Python, Flask (REST API)
- **Database:** SQLite via Flask-SQLAlchemy
- **Testing:** pytest

## Project Structure

```
ai-prescription-maker/
├── app.py                 # Flask app & API routes
├── models.py               # SQLAlchemy models: Clinic, Patient, Prescription
├── guideline_engine.py      # Diagnosis → medication recommendation logic
├── seed_data.py             # Populates sample clinics & patients
├── requirements.txt
├── tests/
│   └── test_engine.py       # Unit tests for the recommendation engine
└── README.md
```

## Setup & Run

```bash
# 1. Clone the repo
git clone https://github.com/Aishwaryaranisahu/ai-prescription-maker.git
cd ai-prescription-maker

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Seed the database with sample clinics & patients
python seed_data.py

# 5. Run the API
python app.py
```

The API will be live at `http://127.0.0.1:5000`.

## Running Tests

```bash
python -m pytest tests/ -v
```

## API Overview

| Method | Endpoint                              | Description                                       |
|--------|----------------------------------------|---------------------------------------------------|
| POST   | `/clinics`                            | Create a clinic                                   |
| GET    | `/clinics`                            | List all clinics                                  |
| POST   | `/patients`                           | Create a patient (with optional allergy list)     |
| GET    | `/patients/<id>`                      | Get patient details                                |
| GET    | `/diagnoses`                          | List diagnoses supported by the guideline engine  |
| POST   | `/prescriptions`                      | Generate a new guideline-based prescription       |
| GET    | `/prescriptions/patient/<id>`         | Full prescription history across all clinics      |
| POST   | `/prescriptions/<id>/clone`           | One-tap clone a prescription into a new visit     |

### Example: generate a prescription

```bash
curl -X POST http://127.0.0.1:5000/prescriptions \
  -H "Content-Type: application/json" \
  -d '{"patient_id": 1, "clinic_id": 1, "diagnosis": "Bacterial Throat Infection"}'
```

If the patient is allergic to the first-line drug (e.g. Amoxicillin), the engine automatically substitutes the guideline's second-line alternative (e.g. Azithromycin) and records the substitution reason in the response.

### Example: clone a previous prescription

```bash
curl -X POST http://127.0.0.1:5000/prescriptions/1/clone \
  -H "Content-Type: application/json" \
  -d '{"clinic_id": 2}'
```

## What I'd Improve Next

- Replace the hard-coded guideline table with a real, versioned clinical guideline dataset (mapped to ICD-10 codes)
- Add authentication/authorization per clinic
- Add a simple frontend for doctors to search diagnoses and review suggested prescriptions before confirming
- Expand contraindication checking beyond simple allergy-name matching (e.g. drug-drug interactions)

## Team

Built as a team project at Smart India Hackathon (SIH) 2025.
