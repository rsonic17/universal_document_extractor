# app/llm.py

import os
import json
import boto3
import logging

logger = logging.getLogger("universal_doc_extractor")

bedrock = boto3.client(
    "bedrock-runtime",
    region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
)

MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")

def clean_json_output(raw_output: str):
    """Try to clean and pretty-print JSON, or return raw if not valid JSON."""
    cleaned = raw_output.strip()

    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, str):
            parsed = json.loads(parsed)
        return json.dumps(parsed, indent=2)
    except Exception:
        return cleaned


def build_claude_messages(user_prompt: str, ocr_text: str):
    """Wrap user or default prompt in consistent Claude-friendly scaffold."""
    system_instructions = (
        "You are a document parsing assistant.\n\n"
        "Your task is to extract structured data from the OCR text provided below.\n\n"
        "⚠️ Rules:\n"
        "- Use only the information explicitly visible in the text.\n"
        "- Do not hallucinate, guess, or fabricate values.\n"
        "- If any field is not clearly present, omit it from the output.\n"
        "- The response must be a valid JSON object.\n"
        "- Do not include explanations, formatting guides, or extra text.\n"
    )

    full_prompt = f"{system_instructions}\n{user_prompt.strip()}\n\nOCR Text:\n{ocr_text.strip()}"
    logger.debug("🧠 Full prompt sent to Claude:\n---\n%s\n---", full_prompt)
    return [{"role": "user", "content": full_prompt}]


def extract_with_llm(text: str, prompt: str = None):
    if not prompt:
        logger.warning("No prompt provided to extract_with_llm.")
        return {"error": "No prompt provided."}

    logger.info(f"Invoking Claude via Bedrock model: {MODEL_ID}")

    messages = build_claude_messages(prompt, text)

    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "messages": messages,
        "max_tokens": 1024,
        "temperature": 0.3,
        "top_p": 0.9
    }

    try:
        response = bedrock.invoke_model(
            modelId=MODEL_ID,
            body=json.dumps(payload),
            contentType="application/json",
            accept="application/json"
        )

        raw_body = response["body"].read().decode("utf-8")
        logger.debug("Raw Claude response: %s", raw_body)

        result = json.loads(raw_body)
        content_blocks = result.get("content", [])

        if not content_blocks:
            logger.warning("⚠️ Claude returned no content.")
            return {"error": "Claude returned an empty response."}

        # Claude returns list of blocks; get combined text
        text_block = next((block.get("text", "") for block in content_blocks if block.get("type") == "text"), "").strip()

        logger.debug("📏 Prompt tokens: %s | Output tokens: %s",
                     result.get("usage", {}).get("input_tokens"),
                     result.get("usage", {}).get("output_tokens"))

        if not text_block:
            return {"error": "Claude returned no usable text."}

        return clean_json_output(text_block)

    except Exception as e:
        logger.error(f"Claude call failed: {e}")
        return {"error": str(e)}
