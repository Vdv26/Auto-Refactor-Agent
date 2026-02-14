import subprocess
import ast
import os

def check_syntax(code, language):
    """
    Validates syntax without executing the code.
    Returns (True, "Valid") or (False, "Error Message").
    """
    language = language.lower()

    if language == "python":
        try:
            ast.parse(code)
            return True, "Syntax Valid ✅"
        except SyntaxError as e:
            return False, f"Python Syntax Error ❌: {e.msg} at line {e.lineno}"

    elif language in ["c", "cpp", "c++"]:
        ext = "c" if language == "c" else "cpp"
        compiler = "gcc" if language == "c" else "g++"
        filename = f"temp_check.{ext}"
        
        with open(filename, "w") as f:
            f.write(code)
            
        try:
            # -fsyntax-only checks the code without compiling/linking
            result = subprocess.run([compiler, "-fsyntax-only", filename], capture_output=True, text=True)
            if result.returncode == 0:
                return True, "Syntax Valid ✅"
            else:
                return False, f"Syntax Error ❌:\n{result.stderr}"
        except FileNotFoundError:
            return False, f"Compiler '{compiler}' not found on system."
        finally:
            if os.path.exists(filename):
                os.remove(filename)

    elif language == "java":
        filename = "TempCheck.java"
        # Standardizing class name for the test
        safe_code = code
        if "public class" in safe_code:
            # Extract actual class name and replace it for testing
            import re
            safe_code = re.sub(r'public\s+class\s+\w+', 'public class TempCheck', safe_code)
            
        with open(filename, "w") as f:
            f.write(safe_code)
            
        try:
            result = subprocess.run(["javac", filename], capture_output=True, text=True)
            if result.returncode == 0:
                return True, "Syntax Valid ✅"
            else:
                return False, f"Java Syntax Error ❌:\n{result.stderr}"
        except FileNotFoundError:
            return False, "Java Compiler (javac) not found."
        finally:
            if os.path.exists(filename):
                os.remove(filename)
            if os.path.exists("TempCheck.class"):
                os.remove("TempCheck.class")
                
    return False, "Unsupported language."