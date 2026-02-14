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
    
    You MUST strictly obey these COMPANY CODING STANDARDS:
    {context_rules}
    
    CRITICAL INSTRUCTIONS:
    1. You must output a RAW JSON object. NO markdown formatting. NO backticks. NO conversational text.
    2. "optimized_code" MUST contain the ENTIRE, COMPLETE, and RUNNABLE script. You MUST include all necessary #includes, function signatures (e.g., int* myFunction(...) {{ }}), and return statements. DO NOT output partial snippets.
    3. NO LANGUAGE BLEED: If the target language is C, you are STRICTLY FORBIDDEN from using C++ headers (like <algorithm>) or C++ namespaces (like std::sort). You MUST write pure C using <stdlib.h> and qsort, or implement a manual C sorting algorithm.
    4. Fix memory leaks (e.g., unnecessary mallocs) and rewrite inefficient algorithms.
    
    Return EXACTLY this JSON template and absolutely nothing else:
    {{
        "analysis": "Explain the complexity and memory issues.",
        "actions": ["List of changes made"],
        "optimized_code": "The FULL rewritten {language} code here"
    }}
    """

    try:
        print("🤖 [Agent] Sending original code to DeepSeek-Coder...") 
        response = ollama.chat(
            model='deepseek-coder:latest', 
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': f"Optimize this {language} code:\n\n{bad_code}"}
            ],
            format='json', # ✨ IT IS BACK!
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