# requirement_6.py
import random
import time
# --- FIX: Import the corrected solver and heuristics ---
from requirement_5 import PuzzleState, AStarSolver, misplaced_tiles, manhattan_distance

def generate_random_start(goal_state, shuffles=30):
    """
    Generates a solvable random start state by making random moves from the goal.
    This is much better than shuffling, which can create unsolvable puzzles.
    """
    state = goal_state
    for _ in range(shuffles):
        neighbors = state.get_neighbors()
        if not neighbors: # Should not happen in an 8-puzzle
            continue
        state = random.choice(neighbors)
        state.parent = None # Reset parent to make it a new root
    return state

def run_experiment(num_tests=5):
    # --- FIX: Goal state is now a proper 2D list (3x3 matrix) ---
    goal_board = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
    goal_state = PuzzleState(goal_board) # The goal is also a state object
    
    results = {'misplaced_tiles': [], 'manhattan_distance': []}

    print(f"Running {num_tests} tests for each heuristic...")
    for i in range(num_tests):
        print(f"  Test #{i+1}...")
        # --- FIX: Use the new function to get a solvable start state ---
        start_state = generate_random_start(goal_state, shuffles=30)

        # --- FIX: Loop keys must match the results dictionary keys ---
        for name, heuristic_func in [('misplaced_tiles', misplaced_tiles), ('manhattan_distance', manhattan_distance)]:
            # --- FIX: Initialize solver with the heuristic function ---
            solver = AStarSolver(heuristic=heuristic_func)
            t0 = time.time()
            # --- FIX: Call solve with the correct arguments ---
            path, visited = solver.solve(start_state, goal_board)
            t1 = time.time()

            if path is not None:
                results[name].append({
                    'path_len': len(path),
                    'time': round(t1 - t0, 4),
                    'visited': visited
                })

    print("\n✅ === Experiment Results === ✅")
    for h_name, h_results in results.items():
        if not h_results:
            print(f"Heuristic: {h_name} -> No solutions found in tests.")
            continue
        
        avg_len = sum(r['path_len'] for r in h_results) / len(h_results)
        avg_time = sum(r['time'] for r in h_results) / len(h_results)
        avg_visit = sum(r['visited'] for r in h_results) / len(h_results)
        
        print(f"Heuristic: {h_name}")
        print(f"  Avg path length: {avg_len:.2f}")
        print(f"  Avg time: {avg_time:.4f}s")
        print(f"  Avg visited nodes: {avg_visit:.2f}\n")

if __name__ == "__main__":
    run_experiment(num_tests=5)