import time
import random
from typing import List, Tuple, Dict, Any
from dataclasses import dataclass
import tracemalloc
from collections import deque

# Import from existing modules
from task1.puzzle_rule import PuzzleProblem, GOAL, NEIGHBORS
from task1.requirement_2 import h0_zero, h1_misplaced_swap_adjust
from task1.requirement_4 import astar, _Metrics

def write_to_report(text: str, file_path: str = "task1/complexity_report.txt", mode: str = "a"):

    with open(file_path, mode, encoding="utf-8") as f:
        f.write(text + "\n")

@dataclass
class ComplexityMetrics:

    algorithm_name: str
    solution_found: bool
    path_cost: float
    nodes_expanded: int
    max_frontier_size: int
    time_ms: float
    memory_kb: float
    
    def __str__(self):
        return (f"{self.algorithm_name:20s} | "
                f"Found: {str(self.solution_found):5s} | "
                f"Cost: {self.path_cost:6.1f} | "
                f"Expanded: {self.nodes_expanded:7d} | "
                f"Time: {self.time_ms:9.2f}ms | "
                f"Memory: {self.memory_kb:9.2f}KB | "
                f"MaxFrontier: {self.max_frontier_size:7d}")


def bfs(problem: PuzzleProblem, time_limit_sec: float = 10.0) -> Tuple[List, float, _Metrics]:
    start_time = time.perf_counter()
    start_state = problem.initial_state()
    M = _Metrics()
    
    if problem.is_goal(start_state):
        M.time_ms = (time.perf_counter() - start_time) * 1000
        return [], 0.0, M
    
    frontier = deque([(start_state, [], 0.0)])  # (state, actions, cost)
    explored = {start_state}
    
    while frontier:
        # Check time limit
        if (time.perf_counter() - start_time) > time_limit_sec:
            M.time_ms = (time.perf_counter() - start_time) * 1000
            return None, None, M
        
        current_state, actions, cost = frontier.popleft()
        
        # Explore successors using problem.successors()
        for action, next_state, step_cost in problem.successors(current_state):
            if next_state not in explored:
                explored.add(next_state)
                M.expanded += 1
                new_cost = cost + step_cost
                
                if problem.is_goal(next_state):
                    M.time_ms = (time.perf_counter() - start_time) * 1000
                    return actions + [action], new_cost, M
                
                frontier.append((next_state, actions + [action], new_cost))
                M.max_fringe = max(M.max_fringe, len(frontier))
    
    # No solution found
    M.time_ms = (time.perf_counter() - start_time) * 1000
    return None, None, M


def measure_algorithm_performance(
    problem: PuzzleProblem,
    algorithm_name: str,
    algorithm_func,
    time_limit: float = 10.0
) -> ComplexityMetrics:
    
    # Start memory tracking
    tracemalloc.start()
    
    try:
        # Run algorithm
        actions, cost, metrics = algorithm_func(problem, time_limit)
        
        # Get memory usage
        current, peak = tracemalloc.get_traced_memory()
        memory_kb = peak / 1024
        
        tracemalloc.stop()
        
        solution_found = actions is not None and cost is not None
        
        return ComplexityMetrics(
            algorithm_name=algorithm_name,
            solution_found=solution_found,
            path_cost=cost if solution_found else -1.0,
            nodes_expanded=metrics.expanded,
            max_frontier_size=metrics.max_fringe,
            time_ms=metrics.time_ms,
            memory_kb=memory_kb
        )
    except Exception as e:
        tracemalloc.stop()
        print(f"Error in {algorithm_name}: {e}")
        return ComplexityMetrics(
            algorithm_name=algorithm_name,
            solution_found=False,
            path_cost=-1.0,
            nodes_expanded=0,
            max_frontier_size=0,
            time_ms=0.0,
            memory_kb=0.0
        )


def generate_random_state(num_moves: int = 20, seed: int = None) -> Tuple[int, ...]:

    # Generate a random solvable state by applying random moves from goal state.
    if seed is not None:
        random.seed(seed)
    
    state = GOAL
    for _ in range(num_moves):
        # Get neighbors of blank position
        t = list(state)
        zero_pos = t.index(0)
        neighbors = NEIGHBORS[zero_pos]
        
        # Random move
        swap_pos = random.choice(neighbors)
        t[zero_pos], t[swap_pos] = t[swap_pos], t[zero_pos]
        state = tuple(t)
    
    return state


def run_single_comparison(initial_state: Tuple[int, ...], time_limit: float = 10.0) -> List[ComplexityMetrics]:

    problem = PuzzleProblem(initial_state)
    results = []
    
    # A* with H0 (zero heuristic = uniform cost search)
    results.append(measure_algorithm_performance(
        problem,
        "A* (H0 - Zero)",
        lambda p, t: astar(p, heuristic_override=h0_zero, time_limit_sec=t),
        time_limit
    ))
    
    # A* with H1 (misplaced with swap adjustment)
    results.append(measure_algorithm_performance(
        problem,
        "A* (H1 - Heuristic)",
        lambda p, t: astar(p, heuristic_override=h1_misplaced_swap_adjust, time_limit_sec=t),
        time_limit
    ))
    
    # Breadth-First Search
    results.append(measure_algorithm_performance(
        problem,
        "BFS",
        bfs,
        time_limit
    ))
    
    return results


def run_complexity_experiment(
    num_test_cases: int = 20,
    difficulty_levels: List[int] = [5, 10, 15, 20],
    time_limit: float = 10.0,
    seed_offset: int = 1000
) -> Dict[str, Any]:

    print("=" * 100)
    print("Time and Space Complexity Contrast Showing:")
    print("=" * 100)
    print(f"\nExperimental setup:")
    print(f"  - Test cases per difficulty: {num_test_cases}")
    print(f"  - Difficulty levels (moves): {difficulty_levels}")
    print(f"  - Time limit per run: {time_limit}s")
    print(f"  - Algorithms: A* (H0), A* (H1), BFS")
    print("\n" + "=" * 100)
    
    all_results = {level: [] for level in difficulty_levels}
    
    for difficulty in difficulty_levels:
        print(f"\n{'=' * 100}")
        print(f"Testing Difficulty Level: {difficulty} moves from goal")
        print('=' * 100)
        
        for test_num in range(num_test_cases):
            print(f"\nTest Case {test_num + 1}/{num_test_cases}:")
            
            # Generate random state with seed for reproducibility
            seed = seed_offset + difficulty * 100 + test_num
            initial_state = generate_random_state(difficulty, seed=seed)
            print(f"  Initial State: {initial_state}")
            
            # Run comparison
            metrics = run_single_comparison(initial_state, time_limit)
            all_results[difficulty].extend(metrics)
            
            # Display results
            for metric in metrics:
                print(f"  {metric}")
    
    return all_results


def analyze_results(results: Dict[int, List[ComplexityMetrics]]):
    print("\n" + "=" * 100)
    print("Statistial Analysis")
    print("=" * 100)
    
    algorithms = ["A* (H0 - Zero)", "A* (H1 - Heuristic)", "BFS"]
    
    for difficulty in sorted(results.keys()):
        print(f"\n{'=' * 100}")
        print(f"Difficulty Level: {difficulty} moves")
        print('=' * 100)
        
        for algo_name in algorithms:
            # Filter results for this algorithm
            algo_results = [m for m in results[difficulty] if m.algorithm_name == algo_name]
            
            if not algo_results:
                continue
            
            # Calculate statistics
            successful = [m for m in algo_results if m.solution_found]
            success_rate = len(successful) / len(algo_results) * 100
            
            if successful:
                avg_cost = sum(m.path_cost for m in successful) / len(successful)
                avg_expanded = sum(m.nodes_expanded for m in successful) / len(successful)
                avg_time = sum(m.time_ms for m in successful) / len(successful)
                avg_memory = sum(m.memory_kb for m in successful) / len(successful)
                avg_frontier = sum(m.max_frontier_size for m in successful) / len(successful)
                
                print(f"\n{algo_name}:")
                print(f"  Success Rate: {success_rate:.1f}% ({len(successful)}/{len(algo_results)})")
                print(f"  Avg Path Cost: {avg_cost:.2f}")
                print(f"  Avg Nodes Expanded: {avg_expanded:.2f}")
                print(f"  Avg Time: {avg_time:.2f} ms")
                print(f"  Avg Memory: {avg_memory:.2f} KB")
                print(f"  Avg Max Frontier Size: {avg_frontier:.2f}")
            else:
                print(f"\n{algo_name}:")
                print(f"  Success Rate: {success_rate:.1f}% (0/{len(algo_results)})")
    
    # Comparative analysis
    print("\n" + "=" * 100)
    print("Comparative Analysis (Among Successful Cases)")
    print("=" * 100)
    
    for difficulty in sorted(results.keys()):
        print(f"\nDifficulty {difficulty} moves:")
        
        algo_stats = {}
        for algo_name in algorithms:
            algo_results = [m for m in results[difficulty] if m.algorithm_name == algo_name]
            successful = [m for m in algo_results if m.solution_found]
            
            if successful:
                algo_stats[algo_name] = {
                    'expanded': sum(m.nodes_expanded for m in successful) / len(successful),
                    'time': sum(m.time_ms for m in successful) / len(successful),
                    'memory': sum(m.memory_kb for m in successful) / len(successful),
                    'frontier': sum(m.max_frontier_size for m in successful) / len(successful)
                }
        
        if len(algo_stats) >= 2:
            print("\n  Time Efficiency (lower is better):")
            sorted_by_time = sorted(algo_stats.items(), key=lambda x: x[1]['time'])
            for i, (name, stats) in enumerate(sorted_by_time, 1):
                print(f"    {i}. {name}: {stats['time']:.2f} ms")
            
            print("\n  Space Efficiency - Memory (lower is better):")
            sorted_by_memory = sorted(algo_stats.items(), key=lambda x: x[1]['memory'])
            for i, (name, stats) in enumerate(sorted_by_memory, 1):
                print(f"    {i}. {name}: {stats['memory']:.2f} KB")
            
            print("\n  Space Efficiency - Max Frontier Size (lower is better):")
            sorted_by_frontier = sorted(algo_stats.items(), key=lambda x: x[1]['frontier'])
            for i, (name, stats) in enumerate(sorted_by_frontier, 1):
                print(f"    {i}. {name}: {stats['frontier']:.2f} nodes")
            
            print("\n  Node Expansion Efficiency (lower is better):")
            sorted_by_expanded = sorted(algo_stats.items(), key=lambda x: x[1]['expanded'])
            for i, (name, stats) in enumerate(sorted_by_expanded, 1):
                print(f"    {i}. {name}: {stats['expanded']:.2f} nodes")


def export_results_to_csv(results: Dict[int, List[ComplexityMetrics]], filename: str = "complexity_results.csv"):
    try:
        import csv
        
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Difficulty', 'Algorithm', 'Success', 'PathCost', 
                'NodesExpanded', 'MaxFrontierSize', 'Time_ms', 'Memory_KB'
            ])
            
            for difficulty, metrics_list in results.items():
                for metric in metrics_list:
                    writer.writerow([
                        difficulty,
                        metric.algorithm_name,
                        metric.solution_found,
                        metric.path_cost,
                        metric.nodes_expanded,
                        metric.max_frontier_size,
                        metric.time_ms,
                        metric.memory_kb
                    ])
        
        print(f"\nResults exported to {filename}")
    except Exception as e:
        print(f"\nFailed to export results: {e}")


def print_summary_table(results: Dict[int, List[ComplexityMetrics]]):
    print("\n" + "=" * 100)
    print("Summary Table")
    print("=" * 100)
    
    algorithms = ["A* (H0 - Zero)", "A* (H1 - Heuristic)", "BFS"]
    
    # Header
    print(f"\n{'Difficulty':<12} | {'Algorithm':<20} | {'Success%':<10} | {'Avg Time(ms)':<15} | {'Avg Expanded':<15}")
    print("-" * 100)
    
    for difficulty in sorted(results.keys()):
        for algo_name in algorithms:
            algo_results = [m for m in results[difficulty] if m.algorithm_name == algo_name]
            successful = [m for m in algo_results if m.solution_found]
            
            if algo_results:
                success_rate = len(successful) / len(algo_results) * 100
                avg_time = sum(m.time_ms for m in successful) / len(successful) if successful else 0
                avg_expanded = sum(m.nodes_expanded for m in successful) / len(successful) if successful else 0
                
                print(f"{difficulty:<12} | {algo_name:<20} | {success_rate:>9.1f}% | {avg_time:>14.2f} | {avg_expanded:>14.2f}")


def demo_requirement_8():
    report_path = "task1/complexity_report.txt"
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("=" * 100 + "\n")
        f.write("Time and space complexity report\n")
        f.write("=" * 100 + "\n\n")

    def log(text: str = ""):
        write_to_report(text, report_path)

    import builtins
    original_print = builtins.print
    builtins.print = log

    try:
        results = run_complexity_experiment(
            num_test_cases=10,
            difficulty_levels=[5, 10, 15, 20],
            time_limit=10.0,
            seed_offset=1000
        )
        analyze_results(results)
        print_summary_table(results)
    finally:
        builtins.print = original_print

    export_results_to_csv(results, "task1/complexity_results.csv")

    log("\n" + "=" * 100)
    log("Expermient Complete.")
    log("=" * 100)
    log("\nKey Findings:")
    log("  1. A* with H1 expands fewer nodes than H0.")
    log("  2. H0 behaves like Uniform Cost Search.")
    log("  3. BFS explores more nodes but guarantees optimal solution.")
    log("  4. Time complexity ∝ nodes expanded.")
    log("  5. Space complexity shown by max frontier size and memory usage.")

    print(f"Task finished.")
    print(f"Report saved to: {report_path}")


if __name__ == "__main__":
    demo_requirement_8()