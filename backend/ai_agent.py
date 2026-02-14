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
    
    # ✨ NEW: Chain-of-Thought Prompting 
    # The JSON structure forces the AI to publicly admit the mathematical flaws
    # and declare the specific optimal algorithm BEFORE it generates the code.
    system_prompt = f"""
    You are an Elite, Industry-Level Python Developer and Algorithm Expert.
    
    COMPANY CODING STANDARDS:
    {context_rules}
    
    CRITICAL RULES:
    1. STRICTLY PYTHON: Output ONLY valid Python code.
    2. ALGORITHMIC RE-ENGINEERING: You MUST radically improve Time and Space complexity. Do NOT just fix syntax. If the input uses a brute-force approach (e.g., O(n^2)), you MUST replace it with an optimal mathematical or data-structure-based approach (e.g., O(n), O(n log n), or O(1)).
    3. CLEAN CODE: Correct all syntax/logic errors. Rename variables to be highly descriptive. Add standard Python Type Hints and docstrings.
    4. COMPLETENESS: You MUST return the ENTIRE refactored Python code. Do NOT truncate, abbreviate, or write "# rest of the code".
    5. FORMAT: Return ONLY a valid JSON object matching the exact Chain-of-Thought structure below. No conversational text.
    
    CHAIN OF THOUGHT JSON FORMAT:
    {{
        "algorithmic_flaws": "Identify why the original algorithm is mathematically or structurally inefficient.",
        "proposed_optimal_algorithm": "Name the specific optimal algorithm or data structure you will use instead (e.g., 'Sieve of Eratosthenes', 'Hash Map').",
        "time_complexity_before": "e.g., O(n^2)",
        "time_complexity_after": "e.g., O(n log log n)",
        "optimized_code": "def highly_optimized_function():\\n    # Complete, production-ready code here"
    }}
    """

    try:
        print("🤖 [Agent] Sending original code to DeepSeek-Coder (Target: Python)...") 
        response = ollama.chat(
            model='deepseek-coder:latest', 
            messages=[
                {'role': 'system', 'content': system_prompt},
                # ✨ NEW: Explicit instruction in the user prompt to rethink the math
                {'role': 'user', 'content': f"Radically optimize this Python code. Rethink the underlying algorithm:\n\n{bad_code}"}
            ],
            format='json',
            # ✨ NEW: Increased temperature from 0.1 to 0.3. 
            # This allows the AI enough "creative freedom" to leap to a new algorithm 
            # instead of copying the structure of the bad code.
            options={'temperature': 0.3} 
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