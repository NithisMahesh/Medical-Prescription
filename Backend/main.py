# Backend/main.py
from fastapi import FastAPI
from Backend import ocr_utils, nlp_utils, validation_utils

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Backend is running!"}

@app.post("/upload-prescription/")
async def upload_prescription(file: UploadFile = File("C:\Users\cu191\Desktop\Medical Prescription\sample")):
    content = await file.read()
    # Call OCR + NLP here
    return {"extracted_text": "Dummy response for now"}