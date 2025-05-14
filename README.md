# Universal Document Extractor

A Flask-based web app that extracts structured data (like invoice fields) from uploaded documents (PDFs or images) using OCR and an LLM (Claude 3 Haiku on Bedrock). Outputs clean JSON alongside the original document and extracted text.

---

## 🧠 Features

- 📄 Supports PDFs (text or image-based), PNGs, JPEGs
- 🔍 OCR via [EasyOCR](https://github.com/JaidedAI/EasyOCR) or AWS Textract
- 🤖 LLM extraction via Claude 3 Haiku (Bedrock API)
- 🧠 Prompts can be customized per document
- 🧠 OCR caching to speed up re-analysis
- 🖥️ Intuitive frontend: document preview, extracted text, JSON side-by-side

---

## 🏗️ Project Structure

```
universal_doc_extractor/
├── app/
│   ├── ocr.py          # OCR logic (EasyOCR or Textract)
│   ├── llm.py          # Bedrock Claude LLM interface
│   ├── utils.py        # File checks, caching, path logic
│   ├── prompt.py       # Default LLM prompt
├── api/
│   └── server.py       # Flask API and frontend routes
├── static/             # JS, CSS
├── templates/          # HTML templates
├── uploads/            # Temporary uploaded files (ignored by git)
├── .cache/             # OCR text cache
├── .env.example        # Environment variable template
└── README.md
```

---

## 🚀 Setup Instructions

### 1. Clone the repo

```bash
git clone https://github.com/your-username/universal-doc-extractor.git
cd universal-doc-extractor
```

### 2. Create your environment

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup .env

Copy the example and edit your AWS/Textract settings:

```bash
cp .env.example .env
```

### 5. Install [Poppler](http://blog.alivate.com.au/poppler-windows/) (Windows only)

Set `POPPLER_PATH` in `.env` to its /bin path.

---

## 🧪 Running Locally

```bash
python -m api.server
```

Then open: [http://localhost:8080](http://localhost:8080)

---

## 🧪 Testing

- Upload a PDF or image.
- Wait for OCR + LLM extraction.
- Optional: enter a custom prompt and re-extract JSON from cached OCR.
- Click “Download JSON” to export output.

---

## 📦 Requirements

- Python 3.8+
- Flask
- easyocr
- boto3
- PyMuPDF (fitz)
- pdf2image
- AWS credentials with Bedrock + optional Textract access

---

## 🛡️ Security

- .env is excluded from git via .gitignore
- Only .env.example is checked in
- Uploaded files and extracted text are not stored permanently

---

## 📌 Notes

- Claude 3 Haiku is used for structured extraction via Bedrock
- OCR fallback supports multi-page PDFs and image-based scans
- Textract usage is optional via USE_TEXTRACT=true

---

## 🤝 Contributing

Pull requests welcome. Please add a test file or example input.

---

## 🧠 Credits

- [EasyOCR](https://github.com/JaidedAI/EasyOCR)
- [Claude (Anthropic)](https://www.anthropic.com/index/claude)
- [AWS Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html)