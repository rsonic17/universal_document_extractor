# app/main.py

import os
import time
import json

from app.config import CACHE_DIR, DEFAULT_PROMPT, MAX_CACHE_FILES
from app.utils import (
    is_new_upload,
    cache_result,
    load_cached_result,
    enforce_cache_limit,
    save_debug_text,
)
from app.ocr import extract_text_from_file
from app.llm import extract_json_with_llm
from app.prompt import build_prompt
from app.utils import estimate_confidence_for_fields, validate_fields

import logging
logger = logging.getLogger(__name__)


def scan_and_cache(file_path: str, force_reset: bool = False) -> tuple[list[str], float, float]:
    """
    Extracts OCR text from the file (or loads cached version) and returns:
    - list of pages as strings
    - overall confidence score
    - scan time in seconds
    """
    if not force_reset and not is_new_upload(file_path):
        cached = load_cached_result(file_path)
        if cached:
            logger.info("✅ Loaded OCR text from cache.")
            if isinstance(cached, tuple) and len(cached) == 2:
                return cached[0], cached[1], 0.0
            else:
                raise ValueError("❌ Cached result format invalid.")

    logger.info("🔍 Running OCR/text extraction...")
    start = time.time()
    result = extract_text_from_file(file_path)
    scan_time = round(time.time() - start, 2)

    if isinstance(result, tuple) and len(result) == 2 and result[0]:
        pages, confidence = result
        cache_result(file_path, (pages, confidence))
        enforce_cache_limit(max_files=MAX_CACHE_FILES)
        return pages, confidence, scan_time
    else:
        raise ValueError("❌ OCR result was invalid or empty.")


def process_file(file_path: str, prompt_override: str = "", force_reset: bool = False) -> dict:
    """
    Main function to process a document end-to-end:
    - OCR extraction
    - LLM prompt construction
    - Claude invocation
    - Validation and confidence estimation

    Returns a result dictionary with:
    - extracted JSON result
    - metrics (timings, confidence)
    - error (if any)
    """
    try:
        pages, confidence, scan_time = scan_and_cache(file_path, force_reset=force_reset)
        full_text = "\n\n".join(pages)
        save_debug_text("debug_ocr_output.txt", full_text)

        prompt = build_prompt(prompt_override, full_text)
        logger.info("📤 Final prompt sent to Claude.")
        logger.debug("📦 Prompt preview:\n%s", prompt[:3000])

        llm_start = time.time()
        llm_output, raw_output = extract_json_with_llm(prompt)
        llm_time = round(time.time() - llm_start, 2)

        if isinstance(llm_output, dict):
            validated = validate_fields(llm_output)
            field_scores = estimate_confidence_for_fields(full_text, validated)
            validated["_field_confidence"] = field_scores
        else:
            validated = {"raw_output": raw_output, "error": "Invalid LLM output"}

        return {
            "result": validated,
            "metrics": {
                "scan_time_sec": scan_time,
                "llm_time_sec": llm_time,
                "confidence_score": confidence,
            },
            "error": None
        }

    except Exception as e:
        logger.exception("❌ Full processing failed.")
        return {
            "result": {"error": "Document processing failed."},
            "metrics": {
                "scan_time_sec": 0.0,
                "llm_time_sec": 0.0,
                "confidence_score": 0.0,
            },
            "error": str(e)
        }
