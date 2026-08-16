"""
seed_data.py

Populates the database with a couple of clinics and patients so the API
can be demoed immediately after setup, without manual data entry.

Usage:
    python seed_data.py
"""

from app import create_app
from models import db, Clinic, Patient


def seed():
    app = create_app()
    with app.app_context():
        if Clinic.query.first():
            print("Database already has data — skipping seed.")
            return

        clinic_a = Clinic(name="Sunrise Family Clinic", location="Bhubaneswar")
        clinic_b = Clinic(name="Riverside Health Center", location="Cuttack")
        db.session.add_all([clinic_a, clinic_b])

        patient_1 = Patient(name="Ramesh Nayak", age=54, allergies="Amoxicillin")
        patient_2 = Patient(name="Sita Behera", age=29, allergies="")
        db.session.add_all([patient_1, patient_2])

        db.session.commit()
        print("Seeded clinics:", [c.name for c in [clinic_a, clinic_b]])
        print("Seeded patients:", [p.name for p in [patient_1, patient_2]])
        print(f"Patient IDs -> {patient_1.name}: {patient_1.id}, {patient_2.name}: {patient_2.id}")
        print(f"Clinic IDs  -> {clinic_a.name}: {clinic_a.id}, {clinic_b.name}: {clinic_b.id}")


if __name__ == "__main__":
    seed()
