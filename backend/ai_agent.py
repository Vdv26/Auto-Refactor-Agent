import json
import ollama
import re
from backend.knowledge_base import get_refactoring_context


def extract_json_from_response(response_text: str):
    """
    Extracts JSON safely from LLM response.
    Handles code fences and malformed wrapping text.
    """
    # Remove markdown code fences if present
    response_text = re.sub(r"```json|```", "", response_text).strip()

    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                return None
        print("⚠ RAW LLM OUTPUT:\n", response_text)
    return None



def ai_refactor_code(bad_code: str, language: str = "python"):
    """
    Sends code to DeepSeek-Coder and enforces strict JSON structure.
    Also normalizes optimized_code to always be a clean string.
    """

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

REQUIRED JSON FORMAT:
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
            {
                "role": "system",
                "content": "You must return ONLY valid JSON with this format: {\"optimized_code\": \"FULL COMPLETE PYTHON CODE\"}"
            },
             {
                 "role": "system",
                 "content": system_prompt
             },
             {
            "role": "user",
            "content": bad_code
        }
    ],
    format="json",
    options={"temperature": 0.0},
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

        if not all(key in parsed for key in required_keys):
            return {"error": "Missing required JSON fields", "raw": raw}

        # ---- TYPE NORMALIZATION FOR optimized_code ----
        code_val = parsed.get("optimized_code")

        if isinstance(code_val, list):
            code_val = "\n".join(str(line) for line in code_val)

        elif isinstance(code_val, dict):
            code_val = "\n".join(str(v) for v in code_val.values())

        elif not isinstance(code_val, str):
            code_val = str(code_val)

        parsed["optimized_code"] = code_val.strip()

        return parsed

    except Exception as e:
        return {"error": f"Local LLM Error: {str(e)}"}
