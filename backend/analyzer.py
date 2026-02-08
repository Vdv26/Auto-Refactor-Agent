import lizard

def get_metrics(code_string):
    """
    Analyzes Java code and returns complexity metrics.
    """
    # Lizard analyzes the code string acting as a file
    analysis = lizard.analyze_file.analyze_source_code("temp.java", code_string)
    
    # If no functions found, return 0
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
    # Weights from your document 
    w1 = 1.0  # Weight for Complexity
    w2 = 0.05 # Weight for Lines of Code (less important)
    
    # H(n) formula
    score = (w1 * metrics["complexity"]) + (w2 * metrics["loc"])
    return score