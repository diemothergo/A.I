from typing import Tuple

GOALS = [
    (1,2,3,4,5,6,7,8,0),
    (8,7,6,5,4,3,2,1,0),
    (1,2,0,3,4,5,6,7,8),
    (8,7,0,6,5,4,3,2,1),
]

NEI = {
    0:[1,3], 1:[0,2,4], 2:[1,5],
    3:[0,4,6],4:[1,3,5,7],5:[2,4,8],
    6:[3,7], 7:[4,6,8], 8:[5,7]
}

CORNER_PAIRS = [(0,8),(2,6)]

def h0_zero(state: Tuple[int, ...]) -> float:
    """Baseline heuristic = 0 (A* ≡ UCS). Admissible & Consistent."""
    return 0.0

def _best_goal_for_state(state: Tuple[int, ...]) -> Tuple[int, ...]:
    best_g, best_mis = None, 10
    for g in GOALS:
        mis = sum(1 for i, v in enumerate(state) if v != 0 and v != g[i])
        if mis < best_mis:
            best_mis, best_g = mis, g
    return best_g

def h1_misplaced_swap_adjust(state: Tuple[int, ...]) -> float:
    """Misplaced tiles with adjustment for special swaps (A + B = 9, corner swaps).
    Only subtract 1 when a swap currently places BOTH tiles correctly → keeps admissible/consistent."""
    g = _best_goal_for_state(state)
    mis = sum(1 for i, v in enumerate(state) if v != 0 and v != g[i])

    used = set()
    pairs = 0

    for i in range(9):
        for j in NEI[i]:
            if j < i:
                continue
            a, b = state[i], state[j]
            if a == 0 or b == 0:
                continue
            if a + b == 9 and (i not in used) and (j not in used):
                if (b == g[i]) and (a == g[j]):
                    pairs += 1
                    used.add(i); used.add(j)

    for i, j in CORNER_PAIRS:
        a, b = state[i], state[j]
        if a == 0 or b == 0:
            continue
        if (i not in used) and (j not in used):
            if (b == g[i]) and (a == g[j]):
                pairs += 1
                used.add(i); used.add(j)

    return max(0, mis - pairs)

if __name__ == "__main__":
    #quick test(only this one)
    s = (1,2,3,4,5,6,7,0,8)
    print("H0 =", h0_zero(s))
    print("H1 =", h1_misplaced_swap_adjust(s))
