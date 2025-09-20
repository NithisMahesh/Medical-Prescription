# backend/verify_utils.py
import json, re
from rapidfuzz import process, fuzz
from typing import List, Dict, Any
import os

# Load simple demo DBs (edit file paths if necessary)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DRUGS_DB_PATH = os.path.join(BASE_DIR, "drugs.json")
DOCTORS_DB_PATH = os.path.join(BASE_DIR, "doctors.json")

with open(DRUGS_DB_PATH, "r", encoding="utf-8") as f:
    drugs_arr = json.load(f)
DRUGS_DB = {d["name"]: d for d in drugs_arr}

with open(DOCTORS_DB_PATH, "r", encoding="utf-8") as f:
    DOCTORS_DB = json.load(f)

dose_re = re.compile(r'(\d{1,4}\s*(?:mg|g|mcg|µg|ml|units|iu))', re.IGNORECASE)
drug_line_re = re.compile(r'([A-Za-z][A-Za-z0-9\-\s]{2,60})\s*(?:,|-)?\s*(\d{1,4}\s*(?:mg|g|mcg|µg|ml|units|iu))', re.IGNORECASE)

def find_med_dose_pairs(text: str) -> List[Dict[str,str]]:
    results=[]
    for m in drug_line_re.finditer(text):
        name=m.group(1).strip(); dose=m.group(2).strip()
        results.append({"raw_name":name,"dose_text":dose})
    for m in dose_re.finditer(text):
        dose=m.group(1).strip()
        start=max(0,m.start()-60); context=text[start:m.start()]
        tokens=re.findall(r'([A-Za-z][A-Za-z0-9\-\s]{2,40})', context)
        name=tokens[-1].strip() if tokens else ""
        if name:
            results.append({"raw_name":name,"dose_text":dose})
    # dedupe
    seen=set(); out=[]
    for r in results:
        key=(r["raw_name"].lower(), r["dose_text"].lower())
        if key not in seen:
            seen.add(key); out.append(r)
    return out

def fuzzy_match_drug(name: str):
    if not name: return (None,0)
    candidates=list(DRUGS_DB.keys())
    best = process.extractOne(name, candidates, scorer=fuzz.WRatio)
    if best: return (best[0], best[1])
    return (None,0)

def parse_mg(dose_text: str):
    if not dose_text: return None
    m = re.search(r'(\d{1,4})', dose_text)
    return int(m.group(1)) if m else None

# simple interactions demo; replace with KB in prod
INTERACTIONS = {("Warfarin","Amoxicillin"): "May increase bleeding risk — monitor INR",
                ("Warfarin","Aspirin"): "Additive bleeding risk"}

def verify(parsed_meds: List[Dict[str,str]], patient: Dict[str,Any]) -> Dict[str,Any]:
    issues=[]; verified=[]
    for item in parsed_meds:
        raw=item.get("raw_name"); dose=item.get("dose_text")
        match,score = fuzzy_match_drug(raw)
        mg = parse_mg(dose)
        entry={"raw_name":raw,"dose_text":dose,"matched_name":match,"match_score":score,"dose_mg":mg}
        if not match or score<60:
            issues.append(f"Unknown/uncertain med: '{raw}' (score={score})")
        else:
            db = DRUGS_DB.get(match,{})
            if mg:
                if mg < db.get("min_mg",0):
                    issues.append(f"Low dose for {match}: {mg}mg (min {db.get('min_mg')})")
                if mg > db.get("max_mg",999999):
                    issues.append(f"High dose for {match}: {mg}mg (max {db.get('max_mg')})")
            for allergy in (patient.get("allergies") or []):
                if allergy.lower() in [a.lower() for a in db.get("allergens",[])] or allergy.lower() in match.lower():
                    issues.append(f"Allergy alert: patient allergic to {allergy} — prescribed {match}")
        verified.append(entry)
    # interactions with existing meds
    existing=[m.strip() for m in (patient.get("current_meds") or []) if m.strip()]
    for v in verified:
        a=v.get("matched_name")
        if not a: continue
        for ex in existing:
            ex_match,_ = fuzzy_match_drug(ex)
            if ex_match:
                for pair,note in INTERACTIONS.items():
                    if set([a,ex_match]) == set(pair):
                        issues.append(f"Interaction: {a} + {ex_match} -> {note}")
    status = "Valid" if not issues else "Suspicious"
    return {"status":status,"issues":issues,"verified":verified}
