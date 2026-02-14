from backend.validator import check_syntax
import ollama
import re


def extract_python_code(text: str) -> str:
    """
    Extracts the first Python code block or returns raw text.
    """
    # Try markdown code block
    match = re.search(r"```python(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Fallback: remove triple backticks
    text = re.sub(r"```", "", text)

    return text.strip()


def sanitize_unicode(code: str) -> str:
    """
    Replace smart quotes and problematic unicode characters.
    """
    replacements = {
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
    }

    for bad, good in replacements.items():
        code = code.replace(bad, good)

    return code


def reflection_loop(bad_code: str, language: str = "python", max_retries: int = 1):
    logs = []

    prompt = f"""
You are an elite Python engineer.

STRICT RULES:
- Output ONLY valid Python code.
- Do NOT include explanations.
- Do NOT include markdown.
- Do NOT include comments outside code.
- Return COMPLETE optimized implementation.

Optimize this code:

{bad_code}
"""

    try:
        response = ollama.chat(
            model="deepseek-coder:latest",
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.2},
        )

        raw_output = response["message"]["content"]

        optimized_code = extract_python_code(raw_output)
        optimized_code = sanitize_unicode(optimized_code)

        if not optimized_code.strip():
            logs.append("Model returned empty code.")
            return "", "Failed: Empty Output", logs

        is_valid, message = check_syntax(optimized_code)

        if is_valid:
            logs.append("Validation Passed ✅")
            return optimized_code, "Success", logs

        logs.append(f"Validation Failed: {message}")

        # ---- ONE SAFE RETRY ----
        retry_response = ollama.chat(
            model="deepseek-coder:latest",
            messages=[
                {
                    "role": "user",
                    "content": f"""
The previous code had a syntax error:

{message}

Return ONLY corrected Python code.
No explanations.
No markdown.

Fix this:

{optimized_code}
"""
                }
            ],
            options={"temperature": 0.0},
        )

        retry_output = retry_response["message"]["content"]
        optimized_code = extract_python_code(retry_output)
        optimized_code = sanitize_unicode(optimized_code)

        is_valid, message = check_syntax(optimized_code)

        if is_valid:
            logs.append("Retry Validation Passed ✅")
            return optimized_code, "Success", logs

        logs.append(f"Retry Failed: {message}")
        return optimized_code, "Failed after retry", logs

    except Exception as e:
        return "", f"Error: {str(e)}", logs
