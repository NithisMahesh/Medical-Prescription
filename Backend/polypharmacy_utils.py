# backend/polypharmacy_utils.py
import re

def group_medicines(meds: list, dosages: list):
    """
    Groups medicines into Morning / Afternoon / Night slots based on dosage hints.
    """
    schedule = {
        "Morning": [],
        "Afternoon": [],
        "Night": []
    }

    # Combine meds and dosages if available
    combined = []
    for i, med in enumerate(meds):
        dose = dosages[i] if i < len(dosages) else ""
        combined.append(f"{med} {dose}".strip())

    for item in combined:
        text = item.lower()
        if re.search(r"morning|am|once daily", text):
            schedule["Morning"].append(item)
        elif re.search(r"afternoon|midday|noon", text):
            schedule["Afternoon"].append(item)
        elif re.search(r"night|bedtime|pm|evening", text):
            schedule["Night"].append(item)
        else:
            # Default → Morning
            schedule["Morning"].append(item)

    return schedule