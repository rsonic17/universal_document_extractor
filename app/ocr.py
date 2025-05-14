# app/ocr.py

import os
import tempfile
import easyocr
import boto3
import fitz  # PyMuPDF
import hashlib
from pdf2image import convert_from_path

from app.utils import is_image_file, USE_TEXTRACT, POPPLER_PATH, cache_path, load_from_cache, save_to_cache

reader = easyocr.Reader(['en'], gpu=False)
textract = boto3.client("textract")


def hash_file(filepath):
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def ocr_with_easyocr(image_path):
    result = reader.readtext(image_path, detail=0, paragraph=True)
    return '\n'.join(result)


def ocr_with_textract(image_path):
    with open(image_path, 'rb') as f:
        bytes_data = f.read()
    response = textract.detect_document_text(Document={'Bytes': bytes_data})
    lines = [item["Text"] for item in response["Blocks"] if item["BlockType"] == "LINE"]
    return '\n'.join(lines)


def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text_content = ""
    for page in doc:
        text = page.get_text()
        if text.strip():
            text_content += text + "\n"
    return text_content.strip() if text_content.strip() else None


def ocr_file(filepath):
    file_hash = hash_file(filepath)
    cached = load_from_cache(file_hash)
    if cached:
        return cached

    if is_image_file(filepath):
        text = ocr_with_textract(filepath) if USE_TEXTRACT else ocr_with_easyocr(filepath)

    elif filepath.lower().endswith('.pdf'):
        text = extract_text_from_pdf(filepath)
        if not text:  # image-based PDF fallback
            images = convert_from_path(filepath, poppler_path=POPPLER_PATH)
            all_text = []
            for i, img in enumerate(images):
                with tempfile.NamedTemporaryFile(suffix=f"_page_{i}.png", delete=False) as tmp:
                    img_path = tmp.name
                img.save(img_path)  # save and flush
                try:
                    ocr_text = ocr_with_textract(img_path) if USE_TEXTRACT else ocr_with_easyocr(img_path)
                    all_text.append(ocr_text)
                finally:
                    os.unlink(img_path)
            text = "\n".join(all_text)

    else:
        raise ValueError("Unsupported file type")

    save_to_cache(file_hash, text)
    return text
