import lizard

def get_metrics(code_string):
    """
    Analyzes Python code and returns complexity metrics.
    """
    # Lizard analyzes the code string acting as a Python file
    analysis = lizard.analyze_file.analyze_source_code("temp.py", code_string)
    
    # If no functions found, return fallback
    if not analysis.function_list:
        return {"complexity": 0, "loc": len(code_string.split('\n'))}

    # Calculate average Cyclomatic Complexity
    total_complexity = sum(func.cyclomatic_complexity for func in analysis.function_list)
    avg_complexity = total_complexity / len(analysis.function_list)
    
    return {
        "complexity": avg_complexity,
        "loc": analysis.nloc,
        "function_count": len(analysis.function_list)
    }

def calculate_heuristic(metrics):
    # Weights for Complexity
    w1 = 1.0  
    w2 = 0.05 
    
    # H(n) formula
    score = (w1 * metrics["complexity"]) + (w2 * metrics["loc"])
    return score