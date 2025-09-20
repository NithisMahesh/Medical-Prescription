# backend/validation_utils.py

def validate_prescription(meds: list, dosages: list, patient_profile: dict):
    """
    Validate extracted medicines/dosages against a patient profile.
    
    patient_profile = {
        "age": 7,
        "allergies": ["penicillin"],
        "conditions": ["asthma"],
        "current_meds": ["warfarin"]
    }
    """
    alerts = []

    # Allergy check
    for allergy in patient_profile.get("allergies", []):
        for med in meds:
            if allergy.lower() in med.lower():
                alerts.append(f"⚠️ Allergy conflict: {med} is unsafe for patient (allergy: {allergy}).")

    # Interaction check (demo rules – can expand later with real dataset)
    risky_combos = [
        ("amoxicillin", "warfarin"),  # known antibiotic interaction
        ("ibuprofen", "aspirin"),     # NSAID combo risk
    ]
    for m1, m2 in risky_combos:
        if m1 in [m.lower() for m in meds] and m2 in [m.lower() for m in patient_profile.get("current_meds", [])]:
            alerts.append(f"⚠️ Interaction alert: {m1} may interact with {m2} (current med).")

    # Age-based check (simple demo)
    if patient_profile.get("age", 0) < 12:
        for med in meds:
            if "aspirin" in med.lower():
                alerts.append("⚠️ Pediatric alert: Aspirin is unsafe for children under 12.")

    # Dosage sanity check (very simple regex-based – expandable)
    for dose in dosages:
        if "500mg" in dose.lower() and patient_profile.get("age", 0) < 12:
            alerts.append("⚠️ Dosage too high: 500mg not recommended for children under 12.")

    return alerts
