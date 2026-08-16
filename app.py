"""
app.py

Flask REST API for the AI Prescription Maker.

Endpoints
---------
POST   /clinics                          Create a clinic
GET    /clinics                          List clinics

POST   /patients                         Create a patient
GET    /patients/<id>                    Get a patient (with allergy list)

POST   /prescriptions                    Generate a NEW guideline-based prescription
GET    /prescriptions/patient/<id>       Full prescription history for a patient,
                                          across all clinics (multi-clinic support)
POST   /prescriptions/<id>/clone         One-tap clone of an existing prescription
                                          into a new clinic visit

GET    /diagnoses                        List diagnoses supported by the guideline engine
"""

import json
from flask import Flask, request, jsonify
from models import db, Clinic, Patient, Prescription
import guideline_engine as engine


def create_app(db_path="sqlite:///prescriptions.db"):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()

    # ---------------- Clinics ----------------
    @app.post("/clinics")
    def create_clinic():
        data = request.get_json(force=True)
        if not data.get("name"):
            return jsonify({"error": "name is required"}), 400
        clinic = Clinic(name=data["name"], location=data.get("location", ""))
        db.session.add(clinic)
        db.session.commit()
        return jsonify(clinic.to_dict()), 201

    @app.get("/clinics")
    def list_clinics():
        return jsonify([c.to_dict() for c in Clinic.query.all()])

    # ---------------- Patients ----------------
    @app.post("/patients")
    def create_patient():
        data = request.get_json(force=True)
        if not data.get("name"):
            return jsonify({"error": "name is required"}), 400
        allergies = data.get("allergies", [])
        patient = Patient(
            name=data["name"],
            age=data.get("age"),
            allergies=",".join(allergies) if isinstance(allergies, list) else allergies,
        )
        db.session.add(patient)
        db.session.commit()
        return jsonify(patient.to_dict()), 201

    @app.get("/patients/<int:patient_id>")
    def get_patient(patient_id):
        patient = Patient.query.get_or_404(patient_id)
        return jsonify(patient.to_dict())

    # ---------------- Diagnoses ----------------
    @app.get("/diagnoses")
    def list_diagnoses():
        return jsonify(engine.list_supported_diagnoses())

    # ---------------- Prescriptions ----------------
    @app.post("/prescriptions")
    def create_prescription():
        """
        Body: { "patient_id": int, "clinic_id": int, "diagnosis": str }
        Generates a fresh guideline-based prescription, automatically
        excluding any drug the patient is allergic to.
        """
        data = request.get_json(force=True)
        patient = Patient.query.get_or_404(data["patient_id"])
        clinic = Clinic.query.get_or_404(data["clinic_id"])
        diagnosis = data.get("diagnosis", "")

        try:
            result = engine.generate_prescription(diagnosis, patient.allergy_list())
        except KeyError as e:
            return jsonify({"error": str(e), "supported": engine.list_supported_diagnoses()}), 400

        prescription = Prescription(
            patient_id=patient.id,
            clinic_id=clinic.id,
            diagnosis=result["diagnosis"],
            medications_json=json.dumps(result["medications"]),
            substitutions_json=json.dumps(result["substitutions"]),
        )
        db.session.add(prescription)
        db.session.commit()
        return jsonify(prescription.to_dict()), 201

    @app.get("/prescriptions/patient/<int:patient_id>")
    def patient_history(patient_id):
        """
        Multi-clinic support: returns every prescription for this patient
        regardless of which clinic issued it, most recent first.
        """
        Patient.query.get_or_404(patient_id)
        prescriptions = (
            Prescription.query.filter_by(patient_id=patient_id)
            .order_by(Prescription.created_at.desc())
            .all()
        )
        return jsonify([p.to_dict() for p in prescriptions])

    @app.post("/prescriptions/<int:prescription_id>/clone")
    def clone_prescription(prescription_id):
        """
        One-tap cloning: duplicates a previous prescription's medications
        into a brand-new prescription record (e.g. for a returning
        chronic-disease patient), optionally at a different clinic.
        """
        original = Prescription.query.get_or_404(prescription_id)
        data = request.get_json(silent=True) or {}
        target_clinic_id = data.get("clinic_id", original.clinic_id)
        Clinic.query.get_or_404(target_clinic_id)

        clone = Prescription(
            patient_id=original.patient_id,
            clinic_id=target_clinic_id,
            diagnosis=original.diagnosis,
            medications_json=original.medications_json,
            substitutions_json=original.substitutions_json,
            cloned_from_id=original.id,
        )
        db.session.add(clone)
        db.session.commit()
        return jsonify(clone.to_dict()), 201

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
