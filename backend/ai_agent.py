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
    return None

def ai_refactor_code(bad_code, language="java"):
    
    # 1. RETRIEVAL: Get the most relevant rules from ChromaDB
    context_rules = get_refactoring_context(bad_code)
    
    # 2. AUGMENTATION: Inject the rules into the system prompt
    system_prompt = f"""
    You are an Expert Senior Software Engineer specializing in {language}.
    
    Follow these STRICT COMPANY CODING STANDARDS:
    {context_rules}
    
    Analyze the provided code and return a JSON object with EXACTLY these three keys:
    1. "analysis": A brief explanation of the current Time/Space complexity and any code smells.
    2. "actions": A list of strings detailing the specific improvements you will make, referencing the rules above.
    3. "optimized_code": The complete, fully rewritten {language} code. It must be highly optimized, adhere to the rules, and contain NO syntax errors.
    
    DO NOT output any text outside of the JSON object.
    """

    try:
        response = ollama.chat(
            model='deepseek-coder', # Matching your installed model
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': f"Optimize this {language} code:\n\n{bad_code}"}
            ],
            options={'temperature': 0.1}
        )
        
        raw_output = response['message']['content']
        parsed_data = extract_json_from_response(raw_output)
        
        if parsed_data and "optimized_code" in parsed_data:
            return parsed_data
        else:
            return {"error": "Failed to parse LLM output into JSON.", "raw": raw_output}

    except Exception as e:
        return {"error": f"Local LLM Error: {str(e)}. Is Ollama running?"}