# app/config.py

import os

# Load from environment variables or fallback to defaults
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
CLAUDE_MODEL_ID = os.getenv("CLAUDE_MODEL_ID", "anthropic.claude-3-5-haiku-20241022-v1:0")
CLAUDE_INFERENCE_PROFILE_ARN = os.getenv("CLAUDE_INFERENCE_PROFILE_ARN")

# Path to cache OCR results (Pickled)
CACHE_DIR = os.path.join(os.getcwd(), "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

# Maximum number of cached files allowed before purging old ones
MAX_CACHE_FILES = 10

# Uploads folder for UI and API
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Supported file types
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "eml"}

# Claude prompt default (used unless user overrides)
DEFAULT_PROMPT = """Extract structured data from the document in clean JSON format. Focus on fields such as:
- sender and recipient names and addresses
- email, phone number, tax ID
- invoice number, date, due date, amount
- payment details like card info or transaction ID
Return only a JSON object as the output. Do not include any explanation or preamble.
Ignore footers, headers, boilerplate, disclaimers, and instructions."""
