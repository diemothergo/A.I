# task1/Requirement_4.py
import csv, random, statistics as st, time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Hashable, Iterable, List, Optional, Tuple
import heapq

from task1.puzzle_rule import PuzzleProblem, GOAL as GOAL_RULE, NEIGHBORS as NEI_RULE
from task1.requirement_2 import h0_zero, h1_misplaced_swap_adjust

@dataclass(order=True)
class _PQItem:
    priority: float
    count: int
    item: Any = field(compare=False)

class _PriorityQueue:
    def __init__(self):
        self._h = []
        self._c = 0
    def push(self, item, priority: float):
        heapq.heappush(self._h, _PQItem(priority, self._c, item)); self._c += 1
    def pop(self):
        return heapq.heappop(self._h).item
    def empty(self) -> bool:
        return not self._h
    def __len__(self): return len(self._h)

@dataclass
class _Node:
    state: Any
    g: float
    action: Any
    parent: "Optional[_Node]"

@dataclass
class _Metrics:
    expanded: int = 0
    max_fringe: int = 0
    time_ms: float = 0.0

def _reconstruct(node: _Node) -> List:
    acts = []
    while node.parent is not None:
        acts.append(node.action)
        node = node.parent
    return list(reversed(acts))

def astar(problem: Any, heuristic_override: Optional[Callable[[Hashable], float]] = None,
          time_limit_sec: float = 10.0) -> Tuple[Optional[List], Optional[float], _Metrics]:
    """General-purpose A* algorithm, calls functions from PuzzleProblem:
       - initial_state(), is_goal(s), successors(s) -> (action, next_state, cost)"""
    h = heuristic_override or (lambda s: 0.0)
    start = problem.initial_state()
    start_t = time.perf_counter()
    M = _Metrics()

    openq = _PriorityQueue()
    openq.push(_Node(start, g=0.0, action=None, parent=None), priority=h(start))
    best_g: Dict[Hashable, float] = {}

    while not openq.empty():
        if (time.perf_counter() - start_t) > time_limit_sec:
            M.time_ms = (time.perf_counter() - start_t) * 1000
            return None, None, M

        node = openq.pop()
        s = node.state
        if problem.is_goal(s):
            M.time_ms = (time.perf_counter() - start_t) * 1000
            return _reconstruct(node), node.g, M

        prev = best_g.get(s, float("inf"))
        if node.g >= prev:
            continue
        best_g[s] = node.g

        for action, s2, cost in problem.successors(s):
            g2 = node.g + cost
            prev2 = best_g.get(s2, float("inf"))
            if g2 < prev2:
                openq.push(_Node(s2, g=g2, action=action, parent=node), priority=g2 + h(s2))
                M.expanded += 1
        M.max_fringe = max(M.max_fringe, len(openq))

    M.time_ms = (time.perf_counter() - start_t) * 1000
    return None, None, M

GOAL = GOAL_RULE
NEI = NEI_RULE

def neighbors_for_blank(state: Tuple[int, ...]) -> List[Tuple[int, ...]]:
    t = list(state); z = t.index(0)
    out = []
    for j in NEI[z]:
        u = t[:]
        u[z], u[j] = u[j], u[z]
        out.append(tuple(u))
    return out

def scramble_from_goal(k: int, seed: int = 0) -> Tuple[int, ...]:
    random.seed(seed)
    s = GOAL
    for _ in range(k):
        s = random.choice(neighbors_for_blank(s))
    return s

def run_case(state: Tuple[int, ...], heuristic_name: str, time_limit=5.0):
    if heuristic_name == "H0":
        hfun = h0_zero
    elif heuristic_name == "H1":
        hfun = h1_misplaced_swap_adjust
    else:
        raise ValueError("Unknown heuristic name")

    prob = PuzzleProblem(state)
    actions, cost, metrics = astar(prob, heuristic_override=hfun, time_limit_sec=time_limit)
    solved = actions is not None

    return dict(
        solved=solved,
        cost=(cost if solved else None),
        expanded=metrics.expanded,
        max_fringe=metrics.max_fringe,
        time_ms=metrics.time_ms
    )

def run_experiments(out_csv: str = None, num_cases=100, ks=(5, 10, 15, 20), time_limit=5.0):
    rows = []
    case_id = 0
    for k in ks:
        for _ in range(num_cases // len(ks)):
            seed = case_id
            start_state = scramble_from_goal(k=k, seed=seed)

            for hname in ["H0", "H1"]:
                res = run_case(start_state, hname, time_limit=time_limit)
                rows.append([
                    case_id, k, hname,
                    res["solved"], res["cost"],
                    res["expanded"], res["max_fringe"], round(res["time_ms"], 2)
                ])
            case_id += 1

    if out_csv:
        with open(out_csv, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["case_id","scramble_k","heuristic","solved","cost","expanded","max_fringe","time_ms"])
            w.writerows(rows)

    def summary_for(h):
        sub = [r for r in rows if r[2] == h and r[3] is True]
        if not sub:
            return f"{h}: solved=0"
        exps = [r[5] for r in sub]
        tms  = [r[7] for r in sub]
        costs= [r[4] for r in sub]
        return (f"{h}: solved={len(sub)}/{len(rows)//2}, "
                f"cost_mean={st.mean(costs):.1f}, "
                f"expanded_mean={st.mean(exps):.1f}, "
                f"time_ms_mean={st.mean(tms):.1f}")

    print(summary_for("H0"))
    print(summary_for("H1"))
    return rows

if __name__ == "__main__":
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    rows = run_experiments(out_csv="results_task1.csv", num_cases=n, ks=(5,10,15,20), time_limit=5.0)
    print("Saved CSV to: results_task1.csv")
