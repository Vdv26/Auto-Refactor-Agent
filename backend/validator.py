import subprocess
import os

def check_java_syntax(java_code):
    """
    Tries to compile the code to check for syntax errors.
    Returns (True, "") if valid, or (False, error_message) if invalid.
    """
    # Create a temporary file
    filename = "TempCheck.java"
    
    # We need to ensure the class name matches the filename for Java
    # This is a hacky fix for the demo; in production, you'd parse the class name.
    if "public class" in java_code:
        # standardizing class name for the test
        java_code = java_code.replace("public class MessyProcessor", "public class TempCheck")
        java_code = java_code.replace("public class Test", "public class TempCheck")
    
    with open(filename, "w") as f:
        f.write(java_code)
        
    # Run javac (Java Compiler)
    try:
        result = subprocess.run(["javac", filename], capture_output=True, text=True)
        if result.returncode == 0:
            return True, "Syntax Valid ✅"
        else:
            return False, f"Syntax Error ❌:\n{result.stderr}"
    except FileNotFoundError:
        return False, "Java Compiler (javac) not found. Is Java installed?"