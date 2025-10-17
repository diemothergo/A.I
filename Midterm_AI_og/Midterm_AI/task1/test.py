from task1.requirement_4 import astar
from task1.puzzle_rule import PuzzleProblem
from task1.requirement_2 import h0_zero, h1_misplaced_swap_adjust

def run_case(name, start):
    prob = PuzzleProblem(start)
    acts0, cost0, m0 = astar(prob, heuristic_override=h0_zero, time_limit_sec=2.0)
    acts1, cost1, m1 = astar(prob, heuristic_override=h1_misplaced_swap_adjust, time_limit_sec=2.0)

    print(f"\n=== {name} ===")
    print("Start:", start)
    print(f"H0 -> cost={cost0}, expanded={m0.expanded}, time_ms={m0.time_ms:.2f}")
    print(f"H1 -> cost={cost1}, expanded={m1.expanded}, time_ms={m1.time_ms:.2f}")

    assert cost0 == cost1, "A* must give the same optimal for both H0 and H1"

if __name__ == "__main__":
    
    #3 quick test: 
    run_case("Near-goal", (1,2,3,4,5,6,0,7,8))
    run_case("Adj swap 9 candidate", (1,2,3,4,5,6,7,0,8))
    run_case("Diagonal swap candidate", (8,2,3,4,5,6,7,0,1))
    print("\nAll quick tests passed")

# Test requirement 3
try:
    from task1.requirement_3 import demo_visualize
    print("\nGenerating tree visualization...")
    demo_visualize((1,2,3,4,5,6,7,0,8), 'H1', n_nodes=9, display_mode='grid')
except Exception as e:
    print("Visualization failed:", e)


# Test requirement 7
# Run python -m task1.requirement_7 in terminal to update for new files
print("Class diagram generating...")


try:
    from task1.requirement_7 import generate_class_diagram
    generate_class_diagram("task1", output_format="all")
    print("\nClass diagram generated successfully!")
    print("Files created:")
    print(" - class_diagram.txt (plaintext)")
    print(" - class_diagram.mmd (paste file at https://mermaid.live)")
    print(" - class_diagram.puml (paste file at https://plantuml.com)")
except Exception as e:
    print(f"Class diagram generation failed: {e}")