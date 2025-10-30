import google.generativeai as genai
import json
import re

def analyze_resume(resume_text, jd_text, api_key, detail_level="Standard"):
    genai.configure(api_key=api_key)

    # Detail level customization
    if detail_level == "Concise":
        note_len = "max 10 words"
        summary_sentences = "3 concise"
    elif detail_level == "Detailed":
        note_len = "15-25 words"
        summary_sentences = "6-7 sentences"
    else:
        note_len = "8-15 words"
        summary_sentences = "4-5 balanced"

    prompt = f"""
You are an AI Resume Analyzer. Compare the RESUME with the JOB DESCRIPTION.
Return ONLY valid JSON with keys: matched_skills:[{{skill,note}}], missing_skills:[{{skill,note}}],
match_percentage:int, justification:str, summary:str.
Notes must be {note_len}. Summary must have {summary_sentences}.
RESUME:\n{resume_text}\n\nJOB DESCRIPTION:\n{jd_text}
"""

    model = genai.GenerativeModel("models/gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text.strip()


def parse_response(raw_text):
    """Try parsing model output to valid JSON format"""
    try:
        cleaned = raw_text.strip().strip('`')
        cleaned = re.sub(r'^json\n', '', cleaned, flags=re.IGNORECASE)
        data = json.loads(cleaned)
    except Exception:
        data = {"matched_skills": [], "missing_skills": [], "match_percentage": 0,
                "justification": "", "summary": "Parsing failed."}
    return data
