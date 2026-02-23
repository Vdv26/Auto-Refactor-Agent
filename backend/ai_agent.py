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

    # Inside your ai_refactor_code function in backend/ai_agent.py:
    
    system_prompt = f"""
    You are an Elite Python Developer and Algorithm Expert.
    
    COMPANY CODING STANDARDS:
    {context_rules}
    
    CRITICAL RULES:
    1. STRICTLY PYTHON: Output ONLY valid Python code.
    2. NO HALLUCINATIONS: Do not claim O(1) complexity unless there are no loops. Never use list.count() inside a loop or comprehension.
    3. ALGORITHMIC RE-ENGINEERING: You MUST radically improve Time and Space complexity. Use Sets or Dictionaries to reduce O(n^2) to O(n).
    4. COMPLETENESS: You MUST return the ENTIRE refactored Python code. 
    5. FORMAT: Return ONLY a valid JSON object matching the exact structure below.
    
    EXAMPLE OF PERFECT BEHAVIOR:
    {{
        "algorithmic_flaws": "The original code uses a nested loop and list.count(), resulting in an inefficient O(n^2) time complexity.",
        "proposed_optimal_algorithm": "I will use a Python 'set' to track seen elements, dropping time complexity to O(n) and space complexity to O(n).",
        "time_complexity_before": "O(n^2)",
        "time_complexity_after": "O(n)",
        "optimized_code": "def find_duplicates(lst: list[int]) -> list[int]:\\n    seen = set()\\n    duplicates = set()\\n    for num in lst:\\n        if num in seen:\\n            duplicates.add(num)\\n        else:\\n            seen.add(num)\\n    return list(duplicates)"
    }}
    """

    try:
        print("🤖 [Agent] Sending original code to DeepSeek-Coder (Target: Python)...") 
        response = ollama.chat(
            model='deepseek-coder:latest', 
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': f"Radically optimize this Python code. Do not hallucinate complexities. Rethink the underlying algorithm:\n\n{bad_code}"}
            ],
            format='json',
            # ✨ CRITICAL FIX: Set temperature to 0.0
            # A temperature of 0.0 completely disables the AI's "creativity" and forces 
            # it to strictly follow the mathematical logic of the prompt.
            options={'temperature': 0.0} 
        )

        raw_output = response["message"]["content"]

        parsed = parse_structured_output(raw_output)

        if not parsed:
            return {"error": "Structured parsing failed", "raw": raw_output}

        return parsed

    except Exception as e:
        return {"error": str(e)}
