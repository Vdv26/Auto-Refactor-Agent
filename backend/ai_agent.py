import json
import ollama
import re
from backend.knowledge_base import get_refactoring_context


def extract_json_from_response(response_text: str):
    try:
        return json.loads(response_text)
    except:
        match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                return None
    return None


def ai_refactor_code(bad_code: str, language: str = "python"):
    context_rules = get_refactoring_context(bad_code)

    system_prompt = f"""
You are an elite senior Python engineer.

STRICT RULES:
1. Improve algorithm complexity.
2. Rename variables professionally.
3. Add type hints.
4. Add docstring.
5. Return ONLY valid JSON.

COMPANY STANDARDS:
{context_rules}

REQUIRED JSON:
{{
    "algorithmic_flaws": "...",
    "proposed_optimal_algorithm": "...",
    "time_complexity_before": "...",
    "time_complexity_after": "...",
    "optimized_code": "FULL COMPLETE PYTHON CODE"
}}
"""

    try:
        response = ollama.chat(
            model="deepseek-coder:latest",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": bad_code},
            ],
            format="json",
            options={"temperature": 0.2},
        )

        raw = response["message"]["content"]
        parsed = extract_json_from_response(raw)

        if not parsed:
            return {"error": "JSON parsing failed", "raw": raw}

        required_keys = [
            "algorithmic_flaws",
            "proposed_optimal_algorithm",
            "time_complexity_before",
            "time_complexity_after",
            "optimized_code",
        ]

        if not all(k in parsed for k in required_keys):
            return {"error": "Missing required JSON fields", "raw": raw}

        return parsed

    except Exception as e:
        return {"error": str(e)}
