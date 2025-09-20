# backend/nlp_utils.py (extend this)

from transformers import pipeline

# Load emotion/sentiment pipeline
# First time run may download ~100-300MB
emotion_pipeline = pipeline("text-classification", model="bhadresh-savani/bert-base-uncased-emotion")

def analyze_doctor_notes(notes_text: str):
    """
    Input: doctors’ notes text
    Output: list of detected emotions / urgency levels
    """
    if not notes_text.strip():
        return []

    results = emotion_pipeline(notes_text[:512])  # limit to first 512 chars for speed
    analysis = [{"label": r["label"], "score": r["score"]} for r in results]
    return analysis
