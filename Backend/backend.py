# backend/backend.py
import os
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from .ocr_utils import extract_text_from_bytes
from .verify_utils import find_med_dose_pairs, verify
from .nlp_utils import extract_entities

app = FastAPI(title="RxGuard+ API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.post("/verify-prescription/")
async def verify_prescription(
    file: UploadFile = File(...),
    patient_name: Optional[str] = Form(None),
    patient_age: Optional[int] = Form(None),
    patient_conditions: Optional[str] = Form(""),
    patient_allergies: Optional[str] = Form(""),
    patient_current_meds: Optional[str] = Form("")
):
    contents = await file.read()
    raw_text = extract_text_from_bytes(contents, file.filename)
    meds = find_med_dose_pairs(raw_text)
    patient = {
        "name": patient_name,
        "age": patient_age,
        "conditions": [s.strip() for s in patient_conditions.split(",") if s.strip()],
        "allergies": [s.strip() for s in patient_allergies.split(",") if s.strip()],
        "current_meds": [s.strip() for s in patient_current_meds.split(",") if s.strip()]
    }
    verification = verify(meds, patient)
    entities = extract_entities(raw_text)
    # group simple schedule (Morning/Afternoon/Night)
    schedule = {"Morning":[], "Afternoon":[], "Night":[]}
    for v in verification["verified"]:
        name = v.get("matched_name") or v.get("raw_name")
        dose = v.get("dose_text")
        # very simple placement default to Morning
        schedule["Morning"].append({"name":name,"dose":dose})
    return {
        "status": verification["status"],
        "issues": verification["issues"],
        "verified": verification["verified"],
        "schedule": schedule,
        "notes_analysis": {"doctors": entities.get("doctors", [])},
        "raw_text": raw_text[:8000]
    }

@app.get("/health")
def health():
    return {"status":"ok"}
