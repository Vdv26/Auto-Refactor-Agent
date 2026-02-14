from backend.ai_agent import ai_refactor_code
from backend.validator import check_syntax
import ollama


def reflection_loop(bad_code, language="python", max_retries=3):
    logs = []
    attempt = 1

    result = ai_refactor_code(bad_code, language)

    if "error" in result:
        return None, result["error"], logs

    optimized_code = result["optimized_code"]

    logs.append("Algorithmic Flaws: " + result["algorithmic_flaws"])
    logs.append("Proposed Algorithm: " + result["proposed_optimal_algorithm"])
    logs.append("Time Before: " + result["time_complexity_before"])
    logs.append("Time After: " + result["time_complexity_after"])

    while attempt <= max_retries:
        is_valid, message = check_syntax(optimized_code)

        if is_valid:
            logs.append("Validation Passed")
            return optimized_code, "Success", logs

        logs.append(f"Attempt {attempt} Failed: {message}")

        correction_prompt = f"""
Fix this Python syntax error:

Error:
{message}

Broken Code:
{optimized_code}

Return ONLY corrected JSON with optimized_code field.
"""

        response = ollama.chat(
            model="deepseek-coder:latest",
            messages=[{"role": "user", "content": correction_prompt}],
            format="json",
            options={"temperature": 0.1},
        )

        optimized_code = response["message"]["content"]
        attempt += 1

    return optimized_code, "Max retries reached", logs
