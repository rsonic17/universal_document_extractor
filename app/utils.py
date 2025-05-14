# app/utils.py

import os
import json
import time
import hashlib
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Constants
UPLOAD_DIR = "uploads"
CACHE_DIR = ".cache"

USE_TEXTRACT = os.getenv("USE_TEXTRACT", "false").lower() == "true"
POPPLER_PATH = os.getenv(
    "POPPLER_PATH", r"C:\Program Files\poppler-0.68.0\bin"
)

# Ensure cache directory exists
os.makedirs(CACHE_DIR, exist_ok=True)


def is_image_file(filename):
    return filename.lower().endswith((".png", ".jpg", ".jpeg"))


def is_pdf_file(filename):
    return filename.lower().endswith(".pdf")


def file_hash(filepath):
    with open(filepath, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def cache_path(hash_key):
    return os.path.join(CACHE_DIR, f"{hash_key}.txt")


def load_from_cache(hash_key):
    path = cache_path(hash_key)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return None


def save_to_cache(hash_key, content):
    path = cache_path(hash_key)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def is_text_pdf(filepath):
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(filepath)
        for page in doc:
            if page.get_text().strip():
                return True
        return False
    except Exception:
        return False


def clean_uploads(older_than_secs: int = 1800):
    """
    Remove .png and .pdf files older than `older_than_secs` (default: 30 minutes)
    from the uploads/ directory.
    """
    uploads_path = os.path.join(os.path.dirname(__file__), "..", UPLOAD_DIR)
    now = time.time()

    for filename in os.listdir(uploads_path):
        if not (filename.endswith(".png") or filename.endswith(".pdf")):
            continue

        file_path = os.path.join(uploads_path, filename)
        try:
            if os.path.isfile(file_path) and (now - os.path.getmtime(file_path)) > older_than_secs:
                os.remove(file_path)
        except Exception as e:
            print(f"Warning: failed to delete {file_path}: {e}")
