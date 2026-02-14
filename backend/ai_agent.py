import ollama
from backend.knowledge_base import get_refactoring_context


def parse_structured_output(text: str):
    sections = {
        "analysis": "",
        "algorithm": "",
        "time_before": "",
        "time_after": "",
        "optimized_code": "",
    }

    try:
        sections["analysis"] = text.split("===ANALYSIS===")[1].split("===ALGORITHM===")[0].strip()
        sections["algorithm"] = text.split("===ALGORITHM===")[1].split("===TIME_BEFORE===")[0].strip()
        sections["time_before"] = text.split("===TIME_BEFORE===")[1].split("===TIME_AFTER===")[0].strip()
        sections["time_after"] = text.split("===TIME_AFTER===")[1].split("===CODE===")[0].strip()
        sections["optimized_code"] = text.split("===CODE===")[1].strip()
    except Exception:
        return None

    return sections


def ai_refactor_code(bad_code: str, language: str = "python"):

    context_rules = get_refactoring_context(bad_code)

    prompt = f"""
You are an elite senior Python engineer.

STRICT RULES:
- Improve algorithm complexity.
- Rename variables professionally.
- Add type hints.
- Add docstring.
- DO NOT include markdown.
- DO NOT include JSON.
- Follow EXACT output format below.

COMPANY STANDARDS:
{context_rules}

OUTPUT FORMAT:

===ANALYSIS===
Explain algorithmic flaws.

===ALGORITHM===
Name optimal algorithm.

===TIME_BEFORE===
O(...)

===TIME_AFTER===
O(...)

===CODE===
FULL COMPLETE PYTHON CODE

Now refactor this code:

{bad_code}
"""

    try:
        response = ollama.chat(
            model="deepseek-coder:latest",
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.2},
        )

        raw_output = response["message"]["content"]

        parsed = parse_structured_output(raw_output)

        if not parsed:
            return {"error": "Structured parsing failed", "raw": raw_output}

        return parsed

    except Exception as e:
        return {"error": str(e)}
