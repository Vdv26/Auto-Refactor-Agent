from backend.analyzer import get_metrics, calculate_heuristic
from backend.refactorer import rename_variable, remove_comments

def hill_climbing_search(original_code):
    """
    Performs a Greedy Hill Climbing search to optimize code.
    """
    current_code = original_code
    current_metrics = get_metrics(current_code)
    current_score = calculate_heuristic(current_metrics)
    
    change_log = [] # To track what the AI did 
    
    # Search Loop (Try to improve 5 times)
    for _ in range(5):
        best_neighbor_code = None
        best_neighbor_score = float('inf')
        action_taken = ""

        # GENERATE NEIGHBORS (Try different actions)
        
        # Neighbor 1: Remove Comments
        candidate_1 = remove_comments(current_code)
        score_1 = calculate_heuristic(get_metrics(candidate_1))
        
        if score_1 < current_score:
            best_neighbor_code = candidate_1
            best_neighbor_score = score_1
            action_taken = "Removed Comments"

        # Neighbor 2: Rename 'x' to 'index' (Example of specific heuristic)
        if "int x" in current_code:
            candidate_2 = rename_variable(current_code, "x", "index")
            score_2 = calculate_heuristic(get_metrics(candidate_2))
            
            if score_2 < best_neighbor_score: # Is this better than Neighbor 1?
                best_neighbor_code = candidate_2
                best_neighbor_score = score_2
                action_taken = "Renamed variable 'x' to 'index' for clarity"

        # DECISION STEP
        # If we found a better state, move there. If not, stop (Local Optima).
        if best_neighbor_code and best_neighbor_score < current_score:
            current_code = best_neighbor_code
            current_score = best_neighbor_score
            change_log.append(f"Action: {action_taken} | New Score: {current_score:.2f}")
        else:
            break # No improvement found
            
    return current_code, change_log, current_metrics