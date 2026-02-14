from backend.ai_agent import ai_refactor_code, extract_json_from_response
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

    optimized_code = result.get("optimized_code", "")

    if isinstance(optimized_code, list):
        optimized_code = "\n".join(map(str, optimized_code))

    elif isinstance(optimized_code, dict):
        optimized_code = "\n".join(map(str, optimized_code.values()))

    optimized_code = str(optimized_code).strip()


    logs.append(f"Algorithmic Flaws: {result.get('algorithmic_flaws', '')}")
    logs.append(f"Proposed Algorithm: {result.get('proposed_optimal_algorithm', '')}")
    logs.append(f"Time Before: {result.get('time_complexity_before', '')}")
    logs.append(f"Time After: {result.get('time_complexity_after', '')}")

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

        correction_prompt = f"""
    Your previous output was invalid.

    You MUST return ONLY valid JSON in EXACT format:

    {{
        "optimized_code": "FULL COMPLETE PYTHON CODE"
    }}

    DO NOT include explanations.
    DO NOT include markdown.
    DO NOT include extra fields.

    Here is the broken code:

    {optimized_code}
    """


        try:
            print(f"🤖 [Reflection] Sending correction attempt {attempt + 1}...")

            response = ollama.chat(
                model="deepseek-coder:latest",
                messages=[{"role": "user", "content": correction_prompt}],
                format="json",
                options={"temperature": 0.1},
            )

            raw_output = response["message"]["content"]

            # ✅ FIX: Proper JSON parsing
            parsed = extract_json_from_response(raw_output)

            if not parsed or "optimized_code" not in parsed:
                logs.append(f"Attempt {attempt + 1}: LLM returned invalid JSON.")
                optimized_code = ""
            else:
                optimized_code = str(parsed["optimized_code"]).strip()

        except Exception as e:
            logs.append(f"Reflection iteration crashed: {str(e)}")
            break

        attempt += 1

    logs.append("Max retries reached.")
    return optimized_code, "Max retries reached", logs
