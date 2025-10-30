# utils/analyzer.py
import os
import re
import json
import google.generativeai as genai


MODEL_CANDIDATES = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.5-pro",
]


def analyze_resume(resume_text, jd_text, api_key, detail_level="Standard"):
    """
    Uses Gemini API to analyze resume vs job description and returns a JSON string.

    Contract:
    - Inputs: resume_text (str), jd_text (str), api_key (str), detail_level (str: Concise|Standard|Detailed)
    - Output: JSON string matching the response schema below
    - Errors: Raises ValueError for missing API key or empty model response
    """
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY. Set it in a .env file or environment variables.")

    genai.configure(api_key=api_key)

    # Detail configuration per user request
    level = (detail_level or "Standard").strip()
    if level == "Concise":
        note_len = "max 10 words"
        summary_sentences = "3 concise"
    elif level == "Detailed":
        note_len = "15-25 words with specific evidence (projects, metrics if present)"
        summary_sentences = "6-7 rich"
    else:  # Standard
        note_len = "8-15 words"
        summary_sentences = "4-5 balanced"

    def make_generation_config(with_schema: bool):
        if not with_schema:
            return {"temperature": 0.2}
        return {
            "temperature": 0.2,
            "response_mime_type": "application/json",
            "response_schema": {
                "type": "object",
                "properties": {
                    "match_percentage": {"type": "integer"},
                    "matched_skills": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "skill": {"type": "string"},
                                "note": {"type": "string"},
                            },
                            "required": ["skill", "note"],
                        },
                    },
                    "missing_skills": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "skill": {"type": "string"},
                                "note": {"type": "string"},
                            },
                            "required": ["skill", "note"],
                        },
                    },
                    "justification": {"type": "string"},
                    "summary": {"type": "string"},
                },
                "required": [
                    "match_percentage",
                    "matched_skills",
                    "missing_skills",
                    "justification",
                    "summary",
                ],
            },
        }

    prompt = (
        "You are an AI Resume Analyzer. Compare the RESUME with the JOB DESCRIPTION.\n"
        "Return ONLY valid minified JSON (no markdown fences, no commentary) using these keys: "
        "matched_skills:[{skill,note}], missing_skills:[{skill,note}], match_percentage:int (0-100), justification:str, summary:str.\n"
        f"For each matched_skills / missing_skills 'note' use {note_len}. Avoid repeating the skill name inside the note.\n"
        "Notes must explain relevance or gap (impact, context, or why important). No bullet symbols.\n"
        "match_percentage: integer (no % sign) reflecting how many required skills appear plus overall strength.\n"
        "justification: one sentence referencing strongest and most critical missing areas.\n"
        f"summary: {summary_sentences} sentences, professional tone, cover strengths, gaps, and actionable improvement suggestions.\n"
        "Do not include technologies in both matched and missing. Merge obvious synonyms.\n\n"
        f"RESUME:\n{resume_text}\n\nJOB DESCRIPTION:\n{jd_text}"
    )

    last_error = None
    # First attempt: try candidates with schema enforcement
    for name in MODEL_CANDIDATES:
        try:
            model = genai.GenerativeModel(
                model_name=name,
                generation_config=make_generation_config(with_schema=True),
            )
            response = model.generate_content(prompt)
            text = getattr(response, "text", None)
            if not text:
                raise ValueError("Empty response from model.")
            return text
        except Exception as e:
            last_error = e
            # Try next model name
            continue

    # Second attempt: try candidates without schema (prompt-enforced JSON)
    for name in MODEL_CANDIDATES:
        try:
            model = genai.GenerativeModel(
                model_name=name,
                generation_config=make_generation_config(with_schema=False),
            )
            # Strengthen prompt since no schema
            fallback_prompt = (
                prompt
                + "\nReturn ONLY valid JSON. Do not include markdown, code fences, or explanations."
            )
            response = model.generate_content(fallback_prompt)
            text = getattr(response, "text", None)
            if not text:
                raise ValueError("Empty response from model.")
            return text
        except Exception as e:
            last_error = e
            continue

    # If all fail, surface the last error for the error page
    raise RuntimeError(f"All model attempts failed: {last_error}")


def _coerce_int_0_100(value):
    try:
        iv = int(value)
        return max(0, min(100, iv))
    except Exception:
        return "N/A"


def parse_response(raw_output):
    """Robustly parse model output into a dict expected by the templates.

    - Tries direct JSON load first
    - If that fails, extracts the first JSON object with regex and tries again
    - Falls back to N/A/empty values but preserves raw output for debugging
    """
    obj = None
    if isinstance(raw_output, dict):
        obj = raw_output
    else:
        # First attempt: direct JSON
        try:
            obj = json.loads(raw_output)
        except Exception:
            # Second attempt: extract JSON object substring
            try:
                m = re.search(r"\{[\s\S]*\}", str(raw_output))
                if m:
                    obj = json.loads(m.group(0))
            except Exception:
                obj = None

    if isinstance(obj, dict):
        match = _coerce_int_0_100(obj.get("match_percentage"))

        def normalize_skills(val):
            if not val:
                return []
            out = []
            for item in val:
                if isinstance(item, dict):
                    skill = item.get("skill") or item.get("name") or item.get("technology") or ""
                    note = item.get("note") or item.get("reason") or ""
                    out.append({"skill": str(skill), "note": str(note)})
                else:
                    out.append({"skill": str(item), "note": ""})
            return out

        matched = normalize_skills(obj.get("matched_skills"))
        missing = normalize_skills(obj.get("missing_skills"))

        return {
            "match": match,
            "matched_skills": matched,
            "missing_skills": missing,
            "summary": obj.get("summary", obj.get("Summary", "Not available")) or "Not available",
            "justification": obj.get("justification", obj.get("Justification", "Not available")) or "Not available",
            # Keep recommendations for backward compatibility if old outputs exist
            "recommendations": obj.get("recommendations", "") or "",
            "raw": raw_output,
        }

    # Fallback if parsing failed
    return {
        "match": "N/A",
        "matched_skills": [],
        "missing_skills": [],
        "summary": "Not available",
        "recommendations": "Not available",
        "raw": raw_output,
    }
