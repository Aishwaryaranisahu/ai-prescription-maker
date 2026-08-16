"""
models.py

SQLAlchemy models supporting multi-clinic prescription management:

- Clinic: a healthcare provider location a patient can visit.
- Patient: a person who can be treated at more than one Clinic.
- Prescription: a record generated either fresh (via the guideline engine)
  or cloned from a previous prescription (one-tap cloning), always linked
  to both a Patient and the Clinic that issued it.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Clinic(db.Model):
    __tablename__ = "clinics"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(200))

    prescriptions = db.relationship("Prescription", backref="clinic", lazy=True)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "location": self.location}


class Patient(db.Model):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer)
    allergies = db.Column(db.String(300), default="")  # comma-separated drug names

    prescriptions = db.relationship("Prescription", backref="patient", lazy=True)

    def allergy_list(self):
        return [a.strip() for a in self.allergies.split(",") if a.strip()]

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "allergies": self.allergy_list(),
        }


class Prescription(db.Model):
    __tablename__ = "prescriptions"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    clinic_id = db.Column(db.Integer, db.ForeignKey("clinics.id"), nullable=False)
    diagnosis = db.Column(db.String(200), nullable=False)
    medications_json = db.Column(db.Text, nullable=False)  # JSON-encoded list of drugs
    substitutions_json = db.Column(db.Text, default="[]")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    cloned_from_id = db.Column(db.Integer, db.ForeignKey("prescriptions.id"), nullable=True)

    def to_dict(self):
        import json

        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "clinic_id": self.clinic_id,
            "diagnosis": self.diagnosis,
            "medications": json.loads(self.medications_json),
            "substitutions": json.loads(self.substitutions_json),
            "created_at": self.created_at.isoformat(),
            "cloned_from_id": self.cloned_from_id,
        }
