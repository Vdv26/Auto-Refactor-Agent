import json
import ollama
import re
from backend.knowledge_base import get_refactoring_context

def extract_json_from_response(response_text):
    """Aggressively tries to extract JSON from the LLM output."""
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        # Try finding markdown JSON blocks
        match = re.search(r'```(?:json)?(.*?)```', response_text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except:
                pass
        # Emergency fallback: Find the first { and last }
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
    
    # ✨ NEW: Intercept and force strict language definitions
    strict_lang = language
    if language.lower() == "c":
        strict_lang = "Pure ANSI C. You must use <stdlib.h> for utilities. C++ features are strictly incompatible."
    
    system_prompt = f"""
    You are an Expert Senior Software Engineer specializing in {strict_lang}.
    
    You MUST strictly obey these COMPANY CODING STANDARDS:
    {context_rules}
    
    CRITICAL INSTRUCTIONS:
    1. Output a RAW JSON object. NO markdown formatting. NO backticks. NO conversational text.
    2. "optimized_code" MUST contain the ENTIRE, COMPLETE, and RUNNABLE script. 
    3. KEEP ORIGINAL SIGNATURES: You MUST keep the original function names (e.g., do not change a utility function into a main() function).
    4. ALGORITHMS: If the language is C, you must implement a manual efficient sorting algorithm (like Quick Sort or Merge Sort) or use the standard C qsort().
    
    Return EXACTLY this JSON template and absolutely nothing else:
    {{
        "analysis": "Explain the complexity and memory issues.",
        "actions": ["List of changes made"],
        "optimized_code": "The FULL rewritten {language} code here"
    }}
    """

    try:
        print(f"🤖 [Agent] Sending original code to DeepSeek-Coder (Target: {strict_lang})...") 
        response = ollama.chat(
            model='deepseek-coder', 
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': f"Optimize this {language} code:\n\n{bad_code}"}
            ],
            format='json',
            options={'temperature': 0.1}
        )
        
        raw_output = response['message']['content']
        parsed_data = extract_json_from_response(raw_output)
        
        if parsed_data and "optimized_code" in parsed_data:
            return parsed_data
        else:
            print(f"❌ [Agent] PARSE FAILED. Raw Output:\n{raw_output}")
            return {"error": "Failed to parse LLM output into JSON. Check terminal.", "raw": raw_output}

    except Exception as e:
        return {"error": f"Local LLM Error: {str(e)}"}