# requirement_5.py
import heapq

class State:
    def __init__(self, position, food, cost=0):
        self.position = position  # (x, y)
        self.food = food          # set of (x, y)
        self.cost = cost

    def is_goal(self):
        return len(self.food) == 0

    def successors(self, maze):
        moves = {'North': (-1, 0), 'South': (1, 0), 'West': (0, -1), 'East': (0, 1)}
        result = []
        for action, (dx, dy) in moves.items():
            new_pos = (self.position[0] + dx, self.position[1] + dy)
            if maze.is_valid(new_pos):
                new_food = set(self.food)
                if new_pos in new_food:
                    new_food.remove(new_pos)
                result.append((State(new_pos, new_food, self.cost + 1), action, 1))
        return result

    def __hash__(self):
        return hash((self.position, frozenset(self.food)))

    def __eq__(self, other):
        return self.position == other.position and self.food == other.food
    
    def __lt__(self, other):
        return (self.position, self.food) < (other.position, other.food)
    
class Maze:
    def __init__(self, layout_file):
        self.grid = []
        self.food = set()
        self.start = None
        with open(layout_file) as f:
            for i, line in enumerate(f):
                row = []
                for j, ch in enumerate(line.strip()):
                    row.append(ch)
                    if ch == 'P':
                        self.start = (i, j)
                    elif ch == '.':
                        self.food.add((i, j))
                self.grid.append(row)

    def is_valid(self, pos):
        x, y = pos
        return 0 <= x < len(self.grid) and 0 <= y < len(self.grid[0]) and self.grid[x][y] != '%'

def heuristic(state):
    if not state.food:
        return 0
    return max(abs(state.position[0] - fx) + abs(state.position[1] - fy) for fx, fy in state.food)

def a_star(start_state, maze):
    open_set = []
    heapq.heappush(open_set, (heuristic(start_state), start_state))
    came_from = {}
    g_score = {start_state: 0}

    while open_set:
        _, current = heapq.heappop(open_set)
        if current.is_goal():
            path = []
            while current in came_from:
                current, action = came_from[current]
                path.append(action)
            return list(reversed(path)), g_score[current]

        for neighbor, action, cost in current.successors(maze):
            tentative_g = g_score[current] + cost
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = (current, action)
                g_score[neighbor] = tentative_g
                f_score = tentative_g + heuristic(neighbor)
                heapq.heappush(open_set, (f_score, neighbor))
    return [], 0

if __name__ == "__main__":
    maze = Maze("task02_pacman_example_map.txt")
    start_state = State(maze.start, maze.food)
    actions, cost = a_star(start_state, maze)
    print("Actions:", actions)
    print("Total cost:", cost)
