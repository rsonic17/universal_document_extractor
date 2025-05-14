import os
import time
import logging
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename

from app.ocr import ocr_file
from app.llm import extract_with_llm
from app.prompt import DEFAULT_PROMPT
from app.utils import is_image_file, is_pdf_file, clean_uploads

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("universal_doc_extractor")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
TEMPLATE_FOLDER = os.path.join(BASE_DIR, 'templates')
STATIC_FOLDER = os.path.join(BASE_DIR, 'static')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__, static_folder=STATIC_FOLDER, template_folder=TEMPLATE_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ocr_cache = {}

@app.route("/")
def index():
    logger.info("Rendering index.html")
    clean_uploads(older_than_secs=0)  # Clean all PNG/PDFs on page load
    return render_template("index.html")


@app.route("/extract", methods=["POST"])
def extract():
    file = request.files.get("file")
    prompt = request.form.get("prompt", DEFAULT_PROMPT)

    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    if not (is_image_file(filename) or is_pdf_file(filename)):
        return jsonify({"error": "Unsupported file type"}), 400

    try:
        ocr_start = time.time()
        ocr_text = ocr_file(filepath)
        ocr_time = round(time.time() - ocr_start, 2)
        ocr_cache['latest'] = {'filename': filename, 'text': ocr_text}
    except Exception as e:
        logger.exception("OCR failed")
        return jsonify({"error": f"OCR failed: {str(e)}"}), 500

    try:
        llm_start = time.time()
        llm_result = extract_with_llm(ocr_text, prompt)
        llm_time = round(time.time() - llm_start, 2)
    except Exception as e:
        logger.exception("LLM extraction failed")
        llm_result = {"error": str(e)}
        llm_time = "--"

    return jsonify({
        "ocr_text": ocr_text,
        "llm_output": llm_result,
        "timing": {
            "ocr_seconds": ocr_time,
            "llm_seconds": llm_time
        }
    })


@app.route("/extract_prompt", methods=["POST"])
def extract_prompt():
    prompt = request.json.get("prompt", DEFAULT_PROMPT)
    if 'latest' not in ocr_cache:
        return jsonify({"error": "No OCR cache found. Please extract a document first."}), 400

    try:
        llm_start = time.time()
        llm_result = extract_with_llm(ocr_cache['latest']['text'], prompt)
        llm_time = round(time.time() - llm_start, 2)
        return jsonify({
            "llm_output": llm_result,
            "llm_seconds": llm_time
        })
    except Exception as e:
        logger.exception("Prompt-based LLM extraction failed")
        return jsonify({"error": str(e)}), 500


@app.route("/reset", methods=["POST"])
def reset_cache():
    ocr_cache.clear()
    clean_uploads(older_than_secs=0)  # Clean everything on reset
    return jsonify({"message": "OCR cache and uploads cleared."})


if __name__ == "__main__":
    app.run(debug=True, port=8080)
