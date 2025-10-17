import pygame
import time
from collections import deque

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

def bfs(maze, start, goal):
    queue = deque([start])
    visited = {start: None}
    while queue:
        current = queue.popleft()
        if current == goal:
            path = []
            while current:
                path.append(current)
                current = visited[current]
            path.reverse()
            return path, visited
        for dr, dc in [(0,1),(1,0),(0,-1),(-1,0)]:
            nr, nc = current[0]+dr, current[1]+dc
            if (0 <= nr < len(maze) and 0 <= nc < len(maze[0]) and 
                maze[nr][nc] == 0 and (nr,nc) not in visited):
                visited[(nr,nc)] = current
                queue.append((nr,nc))
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
    pygame.display.set_caption("Requirement 1 - BFS Pacman Animation")

    start, goal = (1,1), (9,13)
    start_time = time.time()
    path, visited = bfs(maze, start, goal)
    elapsed = time.time() - start_time
    print(f"Path length: {len(path)} | Visited: {len(visited)} | Time: {elapsed:.4f}s")

    clock = pygame.time.Clock()
    running = True
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
