# requirement_5.py
import heapq
import sys
import io

# This line forces Python to use UTF-8 encoding for its output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# --- FIX: Heuristic functions are now standalone ---
def misplaced_tiles(board, goal):
    """Counts how many tiles are not in their goal position."""
    misplaced = 0
    for r in range(3):
        for c in range(3):
            if board[r][c] != goal[r][c] and board[r][c] != 0:
                misplaced += 1
    return misplaced

def manhattan_distance(board, goal):
    """Calculates the Manhattan distance for all tiles."""
    distance = 0
    goal_positions = {goal[r][c]: (r, c) for r in range(3) for c in range(3)}
    for r in range(3):
        for c in range(3):
            val = board[r][c]
            if val != 0:
                goal_x, goal_y = goal_positions[val]
                distance += abs(r - goal_x) + abs(c - goal_y)
    return distance

class PuzzleState:
    """Represents a state of the 8-puzzle board."""
    # (This class is the same as the previously corrected version)
    def __init__(self, board, parent=None, move="", depth=0):
        self.board = board
        self.parent = parent
        self.move = move
        self.depth = depth
    def __eq__(self, other): return self.board == other.board
    def __lt__(self, other): return False
    def __hash__(self): return hash(tuple(map(tuple, self.board)))
    def get_neighbors(self):
        # This method remains the same, with all the special move types
        # ... (code for get_neighbors is unchanged) ...
        # (For brevity, the unchanged get_neighbors code is omitted here)
        # Please use the full get_neighbors method from the previous answer.
        pass # Placeholder for the full method

class AStarSolver:
    """Solves the puzzle using the A* algorithm."""
    # --- FIX: The solver now takes the heuristic function during initialization ---
    def __init__(self, heuristic):
        self.heuristic = heuristic

    def reconstruct_path(self, state):
        path = []
        current = state
        while current.parent is not None:
            path.append(current.move)
            current = current.parent
        path.reverse()
        return path

    # --- FIX: The solve method now takes start and goal states as arguments ---
    def solve(self, start_state, goal_state):
        open_list = []
        closed_set = set()
        
        f_start = self.heuristic(start_state.board, goal_state)
        heapq.heappush(open_list, (f_start, start_state))

        while open_list:
            _, current = heapq.heappop(open_list)

            if current in closed_set:
                continue

            if current.board == goal_state:
                return self.reconstruct_path(current), len(closed_set)

            closed_set.add(current)

            for neighbor in current.get_neighbors():
                if neighbor in closed_set:
                    continue
                
                g_score = neighbor.depth
                h_score = self.heuristic(neighbor.board, goal_state)
                f_score = g_score + h_score
                heapq.heappush(open_list, (f_score, neighbor))
        
        return None, len(closed_set)