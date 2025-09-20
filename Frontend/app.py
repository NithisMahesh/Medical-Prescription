# frontend/app.py
import streamlit as st
import requests
import pandas as pd
import io
import json
import os

st.set_page_config(page_title="RxGuard+ — Prescription Safety", layout="centered")
st.title("RxGuard+ — Prescription Safety Verifier 🩺")
st.caption("Upload a prescription (PDF / image), enter patient details and get safety checks, urgency detection, and a smart medication schedule.")

# ---------- Backend configuration ----------
DEFAULT_API = os.getenv("RXGUARD_API_URL", "http://localhost:8000")
st.sidebar.header("Configuration")
api_url = st.sidebar.text_input("Backend API URL", value=DEFAULT_API)
if api_url.endswith("/"):
    api_url = api_url[:-1]

# Force HTTPS for non-localhost URLs
if api_url.startswith("http://") and "localhost" not in api_url:
    api_url = api_url.replace("http://", "https://")

# ---------- Helper function ----------
def call_verify_api(file_bytes: bytes, filename: str, patient: dict, api_url: str, timeout: int = 60):
    files = {"file": (filename, file_bytes, "application/octet-stream")}
    data = {
        "patient_name": patient.get("name", ""),
        "patient_age": str(patient.get("age", "")),
        "patient_conditions": ",".join(patient.get("conditions", [])),
        "patient_allergies": ",".join(patient.get("allergies", [])),
        "patient_current_meds": ",".join(patient.get("current_meds", []))
    }
    resp = requests.post(f"{api_url}/verify-prescription/", files=files, data=data, timeout=timeout)
    resp.raise_for_status()
    return resp.json()

# ---------- Main UI ----------
with st.form("verify_form"):
    uploaded = st.file_uploader("Upload prescription (PDF / image)", type=["jpg","jpeg","png","pdf"])
    name = st.text_input("Patient name", "")
    age = st.number_input("Age", min_value=0, max_value=130, value=30)
    gender = st.selectbox("Gender (optional)", ["", "Male", "Female", "Other"])
    conditions = st.text_input("Known conditions (comma separated)")
    allergies = st.text_input("Allergies (comma separated)")
    current_meds = st.text_input("Current medications (comma separated)")
    submitted = st.form_submit_button("Analyze prescription")

if submitted:
    if not uploaded:
        st.error("Please upload a prescription file.")
    else:
        patient = {
            "name": name,
            "age": int(age) if age else None,
            "gender": gender,
            "conditions": [s.strip() for s in conditions.split(",") if s.strip()],
            "allergies": [s.strip() for s in allergies.split(",") if s.strip()],
            "current_meds": [s.strip() for s in current_meds.split(",") if s.strip()]
        }
        try:
            with st.spinner("Analyzing prescription..."):
                result = call_verify_api(uploaded.getvalue(), uploaded.name, patient, api_url)
        except Exception as e:
            st.error(f"Error contacting backend API at {api_url}:\n{e}")
            st.stop()
        st.subheader("Backend response")
        st.json(result)

st.markdown("⚠ This tool is a demo. It does not replace professional medical advice. Always consult a licensed clinician.")