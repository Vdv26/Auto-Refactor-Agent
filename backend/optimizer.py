from backend.ai_agent import ai_refactor_code, extract_json_from_response
from backend.validator import check_syntax
import ollama

def reflection_loop(bad_code, language, max_retries=3):
    current_code = bad_code
    attempt = 1
    log = []

    log.append(f"Attempt 1: Sending original code to DeepSeek-Coder...")
    agent_response = ai_refactor_code(current_code, language)
    
    if "error" in agent_response:
         log.append(f"❌ Fatal Error: {agent_response['error']}")
         return None, agent_response["error"], log

    optimized_code = agent_response.get("optimized_code", "")
    analysis = agent_response.get("analysis", "No analysis provided.")
    
    log.append(f"Analysis: {analysis}")

    while attempt <= max_retries:
        is_valid, validation_msg = check_syntax(optimized_code, language)
        
        if is_valid:
            log.append(f"Attempt {attempt}: Validation Passed! ✅")
            return optimized_code, "Success", log
            
        log.append(f"Attempt {attempt}: Validation Failed. ❌ Error:\n{validation_msg.strip()}")
        log.append("Feeding error back to AI for correction...")
        
        # ✨ NEW: Smart Correction Prompt (No placeholders it can copy)
        correction_prompt = f"""
        Your previous Python code failed with this Syntax Error:
        {validation_msg}
        
        Here is the broken code you wrote:
        {optimized_code}
        
        Fix the python syntax error. Return ONLY a valid JSON object. 
        The "optimized_code" key MUST contain the actual fixed Python code. Do not write placeholder text.
        
        {{
            "optimized_code": "def your_function():\\n    # real fixed code goes here"
        }}
        """
        
        try:
            print(f"🤖 [Reflection] Sending error back to LLM for Attempt {attempt + 1}...")
            response = ollama.chat(
                model='deepseek-coder:latest', 
                messages=[{'role': 'user', 'content': correction_prompt}],
                format='json', 
                options={'temperature': 0.1}
            )
            raw_output = response['message']['content']
            parsed = extract_json_from_response(raw_output)
            
            if parsed and isinstance(parsed, dict) and "optimized_code" in parsed:
                code_val = parsed["optimized_code"]
                # Aggressive Type Catcher for Reflection too
                if isinstance(code_val, dict):
                    code_val = "\n".join(str(v) for v in code_val.values())
                elif isinstance(code_val, list):
                    code_val = "\n".join(str(v) for v in code_val)
                optimized_code = str(code_val)
            else:
                log.append(f"Attempt {attempt + 1}: LLM failed to return valid JSON structure.")
                
        except Exception as e:
            log.append(f"Correction iteration failed: {str(e)}")
            break
            
        attempt += 1

    log.append("Max retries reached. Returning best attempt.")
    return optimized_code, "Failed to resolve all syntax errors.", log