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
    
    system_prompt = f"""
    You are an Elite, Industry-Level Python Developer.
    
    COMPANY CODING STANDARDS:
    {context_rules}
    
    CRITICAL RULES:
    1. STRICTLY PYTHON: Output ONLY valid Python code.
    2. OPTIMIZATION: Radically improve Time and Space complexity. Convert O(n^2) loops to O(n) or O(n log n) using dictionaries, sets, or efficient built-ins whenever mathematically possible.
    3. CLEAN CODE: Correct all syntax/logic errors. Rename variables to be highly descriptive (no single letters unless loop iterators). Add standard Python Type Hints and docstrings.
    4. COMPLETENESS: You MUST return the ENTIRE refactored Python code. Do NOT truncate, abbreviate, or write "# rest of the code".
    5. FORMAT: Return ONLY a valid JSON object. No conversational text.
    
    EXAMPLE FORMAT:
    {{
        "analysis": "The original code used an inefficient O(n^2) nested loop. I optimized it to O(n) using a hash map and implemented industry-standard variable names with type hints.",
        "optimized_code": "def process_data(data_list: list[int]) -> list[int]:\\n    # Complete, highly optimized Python code here\\n    return result"
    }}
    """

    try:
        print("🤖 [Agent] Sending original code to DeepSeek-Coder (Target: Python)...") 
        response = ollama.chat(
            model='deepseek-coder:latest', 
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': f"Optimize this Python code completely:\n\n{bad_code}"}
            ],
            format='json',
            options={'temperature': 0.1}
        )
        
        raw_output = response['message']['content']
        parsed_data = extract_json_from_response(raw_output)
        
        if parsed_data:
            code_key = "optimized_code" if "optimized_code" in parsed_data else "optimizedCode"
            if code_key in parsed_data:
                code_val = parsed_data[code_key]
                
                # Aggressive Type Catcher
                if isinstance(code_val, dict):
                    code_val = "\n".join(str(v) for v in code_val.values())
                elif isinstance(code_val, list):
                    code_val = "\n".join(str(v) for v in code_val)
                
                parsed_data["optimized_code"] = str(code_val)
                return parsed_data
        
        print(f"❌ [Agent] PARSE FAILED. Raw Output:\n{raw_output}")
        return {"error": "Failed to parse LLM output into JSON. Check terminal.", "raw": raw_output}

    except Exception as e:
        return {"error": f"Local LLM Error: {str(e)}"}