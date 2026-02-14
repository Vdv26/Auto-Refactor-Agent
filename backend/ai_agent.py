import json
import ollama
import re
from backend.knowledge_base import get_refactoring_context

def extract_json_from_response(response_text):
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        match = re.search(r'```(?:json)?(.*?)```', response_text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except:
                pass
        start = response_text.find('{')
        end = response_text.rfind('}')
        if start != -1 and end != -1:
            try:
                return json.loads(response_text[start:end+1])
            except:
                pass
    return None

def ai_refactor_code(bad_code, language="java"):
    
    context_rules = get_refactoring_context(bad_code)
    
    strict_lang = language
    if language.lower() == "c":
        strict_lang = "Pure ANSI C (C++ is strictly forbidden)"
    
    # ✨ NEW: ONE-SHOT PROMPTING. We show it an example instead of giving complex rules.
    system_prompt = f"""
    You are an Expert Software Engineer specializing in {strict_lang}.
    
    COMPANY CODING STANDARDS:
    {context_rules}
    
    CRITICAL RULES:
    1. Keep original function signatures (e.g., keep s_rt).
    2. If sorting in C, you MUST use qsort(). Bubble sort is BANNED.
    
    Respond ONLY with a JSON object matching this EXACT example structure:
    {{
        "analysis": "The code uses O(n^2) bubble sort and leaks memory.",
        "actions": ["Replaced bubble sort with qsort", "Removed malloc to sort in-place"],
        "optimized_code": "#include <stdio.h>\\n#include <stdlib.h>\\n\\nint compare(const void *a, const void *b) {{\\n    return (*(int*)a - *(int*)b);\\n}}\\n\\nint* s_rt(int* a, int sz) {{\\n    qsort(a, sz, sizeof(int), compare);\\n    return a;\\n}}"
    }}
    """

    try:
        print(f"🤖 [Agent] Sending original code to DeepSeek-Coder (Target: {strict_lang})...") 
        response = ollama.chat(
            model='deepseek-coder:latest', 
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': f"Optimize this {language} code:\n\n{bad_code}"}
            ],
            format='json',
            options={'temperature': 0.1}
        )
        
        raw_output = response['message']['content']
        parsed_data = extract_json_from_response(raw_output)
        
        # ✨ NEW: Safety net to catch if the AI renames the key or makes it a list
        if parsed_data:
            code_key = "optimized_code" if "optimized_code" in parsed_data else "optimizedCode"
            if code_key in parsed_data:
                code_val = parsed_data[code_key]
                if isinstance(code_val, list):
                    code_val = "\n".join(code_val) # Fixes the array bug!
                parsed_data["optimized_code"] = code_val
                return parsed_data
        
        print(f"❌ [Agent] PARSE FAILED. Raw Output:\n{raw_output}")
        return {"error": "Failed to parse LLM output into JSON. Check terminal.", "raw": raw_output}

    except Exception as e:
        return {"error": f"Local LLM Error: {str(e)}"}