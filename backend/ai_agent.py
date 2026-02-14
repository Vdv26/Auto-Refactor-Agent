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
    
    # We added a strict template here
    system_prompt = f"""
    You are an Expert Senior Software Engineer specializing in {language}.
    
    You MUST strictly obey these COMPANY CODING STANDARDS. Do not ignore them:
    {context_rules}
    
    CRITICAL INSTRUCTIONS:
    1. "optimized_code" MUST contain the ENTIRE, COMPLETE, and RUNNABLE script.
    2. Do NOT output partial snippets. Do NOT remove function definitions or includes.
    3. You MUST completely rewrite inefficient algorithms (like Bubble Sort) into efficient ones if the rules demand it.
    4. You MUST rename bad variables.
    
    Return EXACTLY this JSON template and nothing else. Output it inside a markdown block:
    ```json
    {{
        "analysis": "Explain why the original code is bad and its complexity.",
        "actions": ["List of specific changes made"],
        "optimized_code": "The FULL, complete, runnable rewritten {language} code"
    }}
    ```
    """

    try:
        print("🤖 [Agent] Sending original code to DeepSeek-Coder...") 
        response = ollama.chat(
            model='deepseek-coder:latest', 
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': f"Optimize this {language} code:\n\n{bad_code}"}
            ],
            # ✨ REMOVED format='json' FROM HERE
            options={'temperature': 0.1}
        )
        
        raw_output = response['message']['content']
        print(f"📥 [Agent] Received response of length: {len(raw_output)} characters.")
        
        parsed_data = extract_json_from_response(raw_output)
        
        if parsed_data and "optimized_code" in parsed_data:
            return parsed_data
        else:
            # If it STILL fails, we print exactly what it outputted to your terminal so we can debug it
            print(f"❌ [Agent] PARSE FAILED. Raw Output:\n{raw_output}")
            return {"error": "Failed to parse LLM output into JSON. Check your terminal to see the raw output.", "raw": raw_output}

    except Exception as e:
        return {"error": f"Local LLM Error: {str(e)}"}