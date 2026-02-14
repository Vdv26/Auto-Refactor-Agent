from backend.ai_agent import ai_refactor_code
from backend.validator import check_syntax
import ollama

def reflection_loop(bad_code, language, max_retries=3):
    """
    Forces the LLM to fix its own syntax errors if the validator fails.
    """
    current_code = bad_code
    attempt = 1
    log = []

    # Initial Generation
    log.append(f"Attempt 1: Sending original code to DeepSeek-Coder...")
    agent_response = ai_refactor_code(current_code, language)
    
    # NEW: Properly log the error if the agent fails
    if "error" in agent_response:
         log.append(f"❌ Fatal Error: {agent_response['error']}")
         return None, agent_response["error"], log

    optimized_code = agent_response.get("optimized_code", "")
    analysis = agent_response.get("analysis", "No analysis provided.")
    actions = agent_response.get("actions", [])
    
    log.append(f"Analysis: {analysis}")
    # ... rest of the code remains the same
    # Validation & Correction Loop
    while attempt <= max_retries:
        is_valid, validation_msg = check_syntax(optimized_code, language)
        
        if is_valid:
            log.append(f"Attempt {attempt}: Validation Passed! ✅")
            return optimized_code, "Success", log
            
        log.append(f"Attempt {attempt}: Validation Failed. ❌ Error: {validation_msg.strip().split('\n')[-1]}")
        log.append("Feeding error back to AI for correction...")
        
        # Self-Correction Prompt
        correction_prompt = f"""
        You previously generated this {language} code:
        {optimized_code}
        
        It failed with this syntax error:
        {validation_msg}
        
        Fix the error and return the corrected code.
        RETURN ONLY A JSON OBJECT with the key "optimized_code".
        """
        
        try:
            response = ollama.chat(
                model='deepseek-coder:latest', # Adjust tag based on your exact installed model
                messages=[{'role': 'user', 'content': correction_prompt}],
                options={'temperature': 0.1}
            )
            # Basic parsing for the correction attempt
            import json, re
            raw_output = response['message']['content']
            match = re.search(r'```(?:json)?(.*?)```', raw_output, re.DOTALL)
            if match:
                parsed = json.loads(match.group(1).strip())
                optimized_code = parsed.get("optimized_code", optimized_code)
            else:
                parsed = json.loads(raw_output)
                optimized_code = parsed.get("optimized_code", optimized_code)
                
        except Exception as e:
            log.append(f"Correction iteration failed: {str(e)}")
            break
            
        attempt += 1

    log.append("Max retries reached. Returning best attempt.")
    return optimized_code, "Failed to resolve all syntax errors.", log