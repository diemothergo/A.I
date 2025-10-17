from typing import Iterable, Tuple

GOAL = (1, 2, 3, 4, 5, 6, 7, 8, 0)

NEIGHBORS = {
    0: [1, 3], 1: [0, 2, 4], 2: [1, 5],
    3: [0, 4, 6], 4: [1, 3, 5, 7], 5: [2, 4, 8],
    6: [3, 7], 7: [4, 6, 8], 8: [5, 7]
}

CORNER_PAIRS = [(0, 8), (2, 6)]

class PuzzleProblem:
    """rule:
       - MOVE: move empty square in 4 directions (cost=1)
       - SWAP9: two adjacent squares with A+B=9 can swap(cost=1)
       - SWAP_DIAG: two diagonal corner squares TL↔BR, TR↔BL (no 0) (cost=1)
    """
    def __init__(self, start: Tuple[int, ...]):
        self.start = tuple(start)

    def initial_state(self) -> Tuple[int, ...]:
        return self.start

    def is_goal(self, s: Tuple[int, ...]) -> bool:
        return tuple(s) == GOAL

    def successors(self, s: Tuple[int, ...]) -> Iterable[Tuple[str, Tuple[int, ...], float]]:
        t = list(s)
        zero = t.index(0)

        #a)Move blank
        for j in NEIGHBORS[zero]:
            u = t[:]
            u[zero], u[j] = u[j], u[zero]
            yield ("MOVE", tuple(u), 1.0)

        #b)Swap A+B=9 (dedupe using 'seen')
        seen = set()
        for i in range(9):
            for j in NEIGHBORS[i]:
                if (j, i) in seen:
                    continue
                seen.add((i, j))
                a, b = t[i], t[j]
                if a != 0 and b != 0 and a + b == 9:
                    u = t[:]
                    u[i], u[j] = u[j], u[i]
                    yield ("SWAP9", tuple(u), 1.0)

        #c)Diagonal corner swaps
        for i, j in CORNER_PAIRS:
            a, b = t[i], t[j]
            if a != 0 and b != 0:
                u = t[:]
                u[i], u[j] = u[j], u[i]
                yield ("SWAP_DIAG", tuple(u), 1.0)

if __name__ == "__main__":
    #quick test for this file
    start = (1, 2, 3, 4, 5, 6, 7, 0, 8)
    prob = PuzzleProblem(start)
    print("Initial:", prob.initial_state())
    print("Is goal?", prob.is_goal(start))
    for act, nxt, c in list(prob.successors(start))[:10]:
        print(f"{act:10s} -> {nxt}, cost={c}")
