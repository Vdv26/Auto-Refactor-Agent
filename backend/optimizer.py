from backend.ai_agent import ai_refactor_code, extract_json_from_response # <- Add extract_json_from_response here
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
        
        It failed validation with this compiler error:
        {validation_msg}
        
        Fix the error and return ONLY a RAW JSON object. NO markdown formatting. NO backticks.
        
        CRITICAL RULES FOR CORRECTION:
        1. The "optimized_code" MUST contain the ENTIRE, FULLY FUNCTIONAL script (includes, function definitions, logic, returns). Do not output just the single fixed line.
        2. Ensure strict {language} syntax. If the target is C, do NOT use C++ features.
        
        Use exactly this template:
        {{
            "optimized_code": "The FULL corrected script here"
        }}
        """
        
        try:
            print(f"🤖 [Reflection] Sending error back to LLM for Attempt {attempt + 1}...")
            response = ollama.chat(
                model='deepseek-coder:latest', 
                messages=[{'role': 'user', 'content': correction_prompt}],
                format='json', # ✨ IT IS BACK!
                options={'temperature': 0.1}
            )
            raw_output = response['message']['content']
            
            # ✨ NEW: Safely extract the JSON using the robust function we built earlier
            parsed = extract_json_from_response(raw_output)
            
            if parsed and isinstance(parsed, dict) and "optimized_code" in parsed:
                optimized_code = parsed["optimized_code"]
            else:
                log.append(f"Attempt {attempt + 1}: LLM failed to return valid JSON structure.")
                
        except Exception as e:
            log.append(f"Correction iteration failed: {str(e)}")
            break
            
        attempt += 1

    log.append("Max retries reached. Returning best attempt.")
    return optimized_code, "Failed to resolve all syntax errors.", log