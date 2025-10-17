# requirement_6.py
import pygame
from requirement_5 import Maze, State, a_star

class Game:
    def __init__(self, layout_file):
        self.maze = Maze(layout_file)
        self.state = State(self.maze.start, self.maze.food)
        self.actions, _ = a_star(self.state, self.maze)
        self.index = 0
        pygame.init()
        self.screen = pygame.display.set_mode((400, 400))
        self.clock = pygame.time.Clock()

    def draw(self):
        self.screen.fill((0, 0, 0))
        for i, row in enumerate(self.maze.grid):
            for j, ch in enumerate(row):
                color = (255, 255, 255) if ch == '%' else (50, 50, 50)
                pygame.draw.rect(self.screen, color, (j*20, i*20, 20, 20))
        x, y = self.state.position
        pygame.draw.circle(self.screen, (255, 255, 0), (y*20+10, x*20+10), 8)
        pygame.display.flip()

    def update(self):
        if self.index < len(self.actions):
            move = self.actions[self.index]
            dx, dy = {'North': (-1, 0), 'South': (1, 0), 'West': (0, -1), 'East': (0, 1)}[move]
            new_pos = (self.state.position[0] + dx, self.state.position[1] + dy)
            if new_pos in self.state.food:
                self.state.food.remove(new_pos)
            self.state.position = new_pos
            self.index += 1

    def run(self):
        running = True
        while running:
            self.clock.tick(5)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            self.update()
            self.draw()
        pygame.quit()

if __name__ == "__main__":
    Game("task02_pacman_example_map.txt").run()
