import pygame
import time
import heapq

WALL_COLOR = (40, 40, 40)
PATH_COLOR = (0, 255, 0)
PACMAN_COLOR = (255, 255, 0)
GOAL_COLOR = (255, 0, 0)
VISITED_COLOR = (0, 0, 255)
EMPTY_COLOR = (255, 255, 255)

CELL_SIZE = 30
FPS = 15  

maze = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,1,0,0,0,0,1,0,0,0,0,1],
    [1,0,1,0,1,0,1,1,0,1,0,1,1,0,1],
    [1,0,1,0,0,0,0,1,0,0,0,1,0,0,1],
    [1,0,1,1,1,1,0,1,1,1,0,1,0,1,1],
    [1,0,0,0,0,1,0,0,0,1,0,1,0,0,1],
    [1,1,1,1,0,1,1,1,0,1,0,1,1,0,1],
    [1,0,0,1,0,0,0,1,0,0,0,0,0,0,1],
    [1,0,1,1,1,1,0,1,1,1,1,1,1,0,1],
    [1,0,0,0,0,1,0,0,0,0,0,0,1,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]

def heuristic(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def astar(maze, start, goal):
    rows, cols = len(maze), len(maze[0])
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    visited = set()

    while open_set:
        _, current = heapq.heappop(open_set)
        visited.add(current)

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path, visited

        neighbors = [(0,1),(1,0),(0,-1),(-1,0)]
        for dr, dc in neighbors:
            nr, nc = current[0]+dr, current[1]+dc
            if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] == 0:
                tentative_g = g_score[current] + 1
                if (nr, nc) not in g_score or tentative_g < g_score[(nr, nc)]:
                    came_from[(nr, nc)] = current
                    g_score[(nr, nc)] = tentative_g
                    f_score = tentative_g + heuristic((nr, nc), goal)
                    heapq.heappush(open_set, (f_score, (nr, nc)))
    return [], visited

def draw_grid(win, grid, path, visited, start, goal, pac_pos=None):
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            color = EMPTY_COLOR
            if grid[r][c] == 1:
                color = WALL_COLOR
            elif (r, c) in visited:
                color = VISITED_COLOR
            elif (r, c) in path:
                color = PATH_COLOR
            pygame.draw.rect(win, color, (c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(win, (200,200,200), (c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

    pygame.draw.rect(win, GOAL_COLOR, (goal[1]*CELL_SIZE, goal[0]*CELL_SIZE, CELL_SIZE, CELL_SIZE))
    if pac_pos:
        pygame.draw.circle(win, PACMAN_COLOR,
                           (pac_pos[1]*CELL_SIZE + CELL_SIZE//2, pac_pos[0]*CELL_SIZE + CELL_SIZE//2),
                           CELL_SIZE//3)
    else:
        pygame.draw.circle(win, PACMAN_COLOR,
                           (start[1]*CELL_SIZE + CELL_SIZE//2, start[0]*CELL_SIZE + CELL_SIZE//2),
                           CELL_SIZE//3)
    pygame.display.update()

def main():
    pygame.init()
    win = pygame.display.set_mode((len(maze[0])*CELL_SIZE, len(maze)*CELL_SIZE))
    pygame.display.set_caption("Requirement 7 - Pacman A* Animation")

    start = (1, 1)
    goal = (9, 13)

    start_time = time.time()
    path, visited = astar(maze, start, goal)
    elapsed = time.time() - start_time
    print(f"Path length: {len(path)} | Visited: {len(visited)} | Time: {elapsed:.4f}s")

    running = True
    clock = pygame.time.Clock()


    for pos in path:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        draw_grid(win, maze, path, visited, start, goal, pac_pos=pos)
        clock.tick(FPS)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    pygame.quit()

if __name__ == "__main__":
    main()
