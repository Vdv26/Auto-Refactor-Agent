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

def ai_refactor_code(bad_code, language="python"):
    
    context_rules = get_refactoring_context(bad_code)
    
    # 🎯 Stripped down, Python-focused prompt
    system_prompt = f"""
    You are an Expert Python Developer.
    
    COMPANY CODING STANDARDS:
    {context_rules}
    
    CRITICAL RULES:
    1. Analyze the Python code and improve its Time and Space complexity.
    2. Keep the original function name.
    3. Return ONLY a valid JSON object. No conversational text.
    
    Respond EXACTLY using this JSON structure:
    {{
        "analysis": "The code uses an inefficient O(n^2) loop.",
        "actions": ["Replaced nested loops with an optimized algorithm like Sieve of Eratosthenes", "Used list comprehensions"],
        "optimized_code": "def example_function(n):\\n    # highly optimized Python code here\\n    return result"
    }}
    """

    try:
        print("🤖 [Agent] Sending original code to DeepSeek-Coder (Target: Python)...") 
        response = ollama.chat(
            model='deepseek-coder:latest', 
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': f"Optimize this Python code:\n\n{bad_code}"}
            ],
            format='json',
            options={'temperature': 0.1}
        )
        
        raw_output = response['message']['content']
        parsed_data = extract_json_from_response(raw_output)
        
        # Safety net for JSON keys
        if parsed_data:
            code_key = "optimized_code" if "optimized_code" in parsed_data else "optimizedCode"
            if code_key in parsed_data:
                code_val = parsed_data[code_key]
                if isinstance(code_val, list):
                    code_val = "\n".join(code_val)
                parsed_data["optimized_code"] = code_val
                return parsed_data
        
        print(f"❌ [Agent] PARSE FAILED. Raw Output:\n{raw_output}")
        return {"error": "Failed to parse LLM output into JSON. Check terminal.", "raw": raw_output}

    except Exception as e:
        return {"error": f"Local LLM Error: {str(e)}"}