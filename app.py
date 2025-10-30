from flask import Flask, render_template, request, redirect, url_for
import os
from dotenv import load_dotenv
from utils.pdf_utils import extract_text_from_pdf
from utils.analyzer import analyze_resume, parse_response

app = Flask(__name__)

# Load env variables
load_dotenv()
# Support either GEMINI_API_KEY or GOOGLE_API_KEY env name
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        jd_text = request.form.get("job_description")
        detail_level = request.form.get("detail_level")
        resume_file = request.files.get("resume")

        if not jd_text or not resume_file:
            return render_template("error.html", message="Please upload resume and job description.")

        try:
            if not GEMINI_API_KEY:
                raise RuntimeError("API key not configured. Set GEMINI_API_KEY (or GOOGLE_API_KEY) in a .env file.")

            # Extract text
            if resume_file.filename.lower().endswith(".pdf"):
                # Ensure stream is at start for pdfplumber
                try:
                    resume_file.stream.seek(0)
                except Exception:
                    pass
                resume_text = extract_text_from_pdf(resume_file.stream)
            else:
                resume_file.stream.seek(0)
                resume_text = resume_file.read().decode("utf-8", errors="ignore")

            if not resume_text or not resume_text.strip():
                raise ValueError("Could not extract any text from the uploaded resume.")

            # Analyze with Gemini
            raw_output = analyze_resume(resume_text, jd_text, GEMINI_API_KEY, detail_level)
            parsed = parse_response(raw_output)

            return render_template("result.html", parsed=parsed)
        except Exception as e:
            return render_template("error.html", message=str(e))

    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
