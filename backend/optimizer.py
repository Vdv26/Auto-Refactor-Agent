from backend.ai_agent import ai_refactor_code
from backend.validator import check_syntax
import ollama


def reflection_loop(bad_code: str, language: str = "python", max_retries: int = 3):
    logs = []
    attempt = 1

    # ---- INITIAL GENERATION ----
    result = ai_refactor_code(bad_code, language)

    if "error" in result:
        logs.append(f"Initial generation failed: {result['error']}")
        return None, result["error"], logs

    optimized_code = result.get("optimized_code", "").strip()

    logs.append("Algorithmic Flaws: " + result.get("analysis", ""))
    logs.append("Proposed Algorithm: " + result.get("algorithm", ""))
    logs.append("Time Before: " + result.get("time_before", ""))
    logs.append("Time After: " + result.get("time_after", ""))

    # ---- VALIDATION LOOP ----
    while attempt <= max_retries:

        if not optimized_code:
            logs.append(f"Attempt {attempt} Failed: Generated code is empty.")
        else:
            is_valid, message = check_syntax(optimized_code)

            if is_valid:
                logs.append(f"Attempt {attempt}: Validation Passed ✅")
                return optimized_code, "Success", logs

            logs.append(f"Attempt {attempt} Failed: {message}")

        # ---- REFLECTION PROMPT ----
        correction_prompt = f"""
You previously generated invalid Python code.

STRICT FORMAT (DO NOT BREAK FORMAT):

===ANALYSIS===
Explain what went wrong.

===ALGORITHM===
Name optimal algorithm.

===TIME_BEFORE===
O(...)

===TIME_AFTER===
O(...)

===CODE===
FULL COMPLETE CORRECT PYTHON CODE

Fix the following broken code:

{optimized_code}
"""

        try:
            print(f"🤖 [Reflection] Sending correction attempt {attempt + 1}...")

            response = ollama.chat(
                model="deepseek-coder:latest",
                messages=[{"role": "user", "content": correction_prompt}],
                options={"temperature": 0.0},
            )

            raw_output = response["message"]["content"]

            # Parse again using ai_agent's structured parser
            new_result = ai_refactor_code(optimized_code, language)

            if "error" in new_result:
                logs.append(f"Attempt {attempt + 1}: Structured parsing failed.")
                optimized_code = ""
            else:
                optimized_code = new_result.get("optimized_code", "").strip()

        except Exception as e:
            logs.append(f"Reflection iteration crashed: {str(e)}")
            break

        attempt += 1

    logs.append("Max retries reached.")
    return optimized_code, "Max retries reached", logs
