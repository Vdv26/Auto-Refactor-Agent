import ast

def check_syntax(code, language="python"):
    """
    Validates Python syntax using the Abstract Syntax Tree (AST) without executing the code.
    Returns (True, "Valid") or (False, "Error Message").
    """
    if not isinstance(code, str):
        return False, f"JSON Format Error ❌: The 'optimized_code' value MUST be a single string, but you provided a {type(code).__name__}. Fix your JSON format."

    try:
        ast.parse(code)
        return True, "Syntax Valid ✅"
    except SyntaxError as e:
        return False, f"Python Syntax Error ❌: {e.msg} at line {e.lineno}"
    except Exception as e:
        return False, f"Python Parse Error ❌: {str(e)}"