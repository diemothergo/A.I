# requirement_5.py
import heapq
import sys
import io


sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

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

    def __init__(self, board, parent=None, move="", depth=0):
        self.board = board
        self.parent = parent
        self.move = move
        self.depth = depth
    def __eq__(self, other): return self.board == other.board
    def __lt__(self, other): return False
    def __hash__(self): return hash(tuple(map(tuple, self.board)))
    def get_neighbors(self):

        pass 

class AStarSolver:
    """Solves the puzzle using the A* algorithm."""

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