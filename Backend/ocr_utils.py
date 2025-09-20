# backend/ocr_utils.py
import io
import os
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes

# === Project root ===
PROJECT_ROOT = r"C:\Users\cu191\Desktop\Medical Prescription"

# Paths for Tesseract and Poppler
TESSERACT_EXE = os.path.join(PROJECT_ROOT, "tesseract", "tesseract.exe")
POPPLER_BIN = os.path.join(PROJECT_ROOT, "poppler", "bin")

# --- Debug print to confirm paths ---
print("[OCR] Project root:", PROJECT_ROOT)
print("[OCR] Tesseract exe:", TESSERACT_EXE)
print("[OCR] Poppler bin:", POPPLER_BIN)

# Configure pytesseract if Tesseract exists
if os.path.exists(TESSERACT_EXE):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_EXE
    print("[OCR] Tesseract configured successfully.")
else:
    print("[OCR] WARNING: Tesseract not found at", TESSERACT_EXE)

# Ensure Poppler bin exists
if not os.path.isdir(POPPLER_BIN):
    print("[OCR] WARNING: Poppler bin not found at", POPPLER_BIN)

def extract_text_from_bytes(file_bytes: bytes, filename: str) -> str:
    """
    Accepts image or PDF bytes; returns extracted text using pytesseract.
    If PDF, uses pdf2image with poppler_path for Windows.
    """
    text = ""
    fname = (filename or "").lower()

    try:
        if fname.endswith(".pdf"):
            print("[OCR] Processing PDF with Poppler...")
            images = convert_from_bytes(file_bytes, poppler_path=POPPLER_BIN)
            for img in images:
                text += pytesseract.image_to_string(img) + "\n"
            return text

        # Otherwise process as image
        print("[OCR] Processing image file...")
        img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
        text = pytesseract.image_to_string(img)

    except Exception as e:
        print("[OCR] ERROR during OCR:", str(e))
        # fallback: try pdf2image anyway
        try:
            images = convert_from_bytes(file_bytes, poppler_path=POPPLER_BIN)
            for img in images:
                text += pytesseract.image_to_string(img) + "\n"
        except Exception as e2:
            print("[OCR] FATAL: Could not extract text:", str(e2))
            raise e2

    return text
