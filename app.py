import os, sys, json
from flask import Flask, request, jsonify
from flask_cors import CORS
from pypdf import PdfReader
from resumeparser import ats_extractor

UPLOAD_PATH = "__DATA__"
os.makedirs(UPLOAD_PATH, exist_ok=True)

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return {"message": "Resume Parser API is live!"}

@app.route("/process", methods=["POST"])
def ats():
    doc = request.files.get('pdf_doc')
    if not doc:
        return jsonify({"error": "No file uploaded"}), 400
    if not doc.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported"}), 400

    filepath = os.path.join(UPLOAD_PATH, "file.pdf")
    doc.save(filepath)

    try:
        resume_text = _read_file_from_path(filepath)
    except Exception as e:
        return jsonify({"error": "Failed to read PDF", "details": str(e)}), 400
    extracted_data = ats_extractor(resume_text)

    try:
        return jsonify(json.loads(extracted_data))
    except Exception:
        return jsonify({
            "error": "Invalid JSON from OpenAI",
            "raw_response": extracted_data
        }), 500

def _read_file_from_path(path):
    reader = PdfReader(path)
    return "".join(page.extract_text() for page in reader.pages)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
