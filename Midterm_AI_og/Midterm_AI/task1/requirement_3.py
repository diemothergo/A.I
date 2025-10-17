# task1/requirement_3.py
from dataclasses import dataclass
from typing import Any, Optional, Callable, Tuple, List
from task1.puzzle_rule import PuzzleProblem
from task1.requirement_2 import h0_zero, h1_misplaced_swap_adjust


@dataclass
class _Node:
    state: Any
    g: float
    action: Any
    parent: Optional["_Node"]

# visualize 3x3 grid
def _format_state_grid(state: Tuple[int, ...]) -> str:
    lines = []
    lines.append("┌─────┐")
    for i in range(0, 9, 3):
        row = " ".join(str(x) if x != 0 else "_" for x in state[i:i+3])
        lines.append(f"│{row}│")
    lines.append("└─────┘")
    return "\n".join(lines)


def _format_state_inline(state: Tuple[int, ...]) -> str:
    return str(state).replace("0", "_")


def visualize_search_tree(problem: PuzzleProblem,
                          heuristic: Callable[[Tuple[int, ...]], float],
                          max_nodes: int = 20,
                          display_mode: str = "grid"):
    open_nodes: List[_Node] = []
    visited = set()
    node_list = []

    start = problem.initial_state()
    start_node = _Node(start, 0.0, None, None)
    open_nodes.append(start_node)

    count = 0
    while open_nodes and count < max_nodes:
        node = open_nodes.pop(0)
        s = node.state
        if s in visited:
            continue
        visited.add(s)
        count += 1
        
        node_list.append(node)

        for action, next_state, _ in problem.successors(s):
            if next_state not in visited:
                open_nodes.append(_Node(next_state, node.g + 1, action, node))

    # Display the tree
    print(f"\n{'='*60}")
    print(f"SEARCH TREE VISUALIZATION ({count} nodes)")
    print(f"{'='*60}\n")
    
    for idx, node in enumerate(node_list):
        depth = 0
        temp = node
        while temp.parent is not None:
            depth += 1
            temp = temp.parent
        
        indent = "  " * depth
        prefix = "└─ " if depth > 0 else ""
        
        print(f"{indent}{prefix}Node {idx+1} (depth={depth}):")
        
        if display_mode == "grid":
            state_str = _format_state_grid(node.state)
            for line in state_str.split("\n"):
                print(f"{indent}   {line}")
        else:
            state_str = _format_state_inline(node.state)
            print(f"{indent}   {state_str}")
        
        if node.action:
            print(f"{indent}   Action: {node.action}")
        print()
    
    print(f"{'='*60}\n")


def demo_visualize(state: Tuple[int, ...], heuristic_name: str = "H0", n_nodes: int = 9, display_mode: str = "grid"):
    if heuristic_name == "H0":
        hfun = h0_zero
    elif heuristic_name == "H1":
        hfun = h1_misplaced_swap_adjust
    else:
        raise ValueError("Unknown heuristic name")

    problem = PuzzleProblem(state)
    visualize_search_tree(problem, heuristic=hfun, max_nodes=n_nodes, display_mode=display_mode)