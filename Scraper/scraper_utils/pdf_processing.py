# This file is responsible for extracting text using normal or OCR-based PDf parsing
import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_bytes

def extract_text_normal(pdf_bytes):
    text = ""
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_text_ocr(pdf_bytes):
    images = convert_from_bytes(pdf_bytes)
    text = ""
    for img in images:
        text += pytesseract.image_to_string(img)
    return text
