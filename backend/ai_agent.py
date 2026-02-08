import os
from groq import Groq

def ai_refactor_code(bad_code):
    """
    Sends code to Groq API (Cloud) to fix syntax and optimize logic.
    """
    # Get the API Key from Streamlit Secrets (Best Practice)
    api_key = os.environ.get("GROQ_API_KEY")
    
    if not api_key:
        return "Error: GROQ_API_KEY not found. Please add it to Streamlit Secrets."

    client = Groq(api_key=api_key)
    
    prompt = f"""
    You are an expert Senior Software Engineer.
    1. Fix any Syntax Errors in this Java code.
    2. Optimize the Logic (Time/Space complexity).
    3. Remove comments and unused variables.
    4. RETURN ONLY THE JAVA CODE. No markdown, no explanations.
    
    Code:
    {bad_code}
    """
    
    try:
        completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile", # Uses a powerful model freely
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"API Error: {str(e)}"