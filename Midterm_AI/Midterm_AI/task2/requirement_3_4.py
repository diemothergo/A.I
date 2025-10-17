import pygame
import sys

CELL_SIZE = 18
FPS = 60
GHOST_MOVE_COOLDOWN = 700 #ghost speed
MOVE_COOLDOWN = 150 #pacman speed

BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)


class Maze:
    def __init__(self, layout_path):
        with open(layout_path, 'r') as f:
            self.original_layout = [line.rstrip('\n') for line in f if line.strip()]
        
        self.layout = [list(row) for row in self.original_layout]
        self.height = len(self.layout)
        self.width = len(self.layout[0])
        self.display_size = max(self.width, self.height)
        
        self.start_pos = self._find_symbol('P')
        self.food_positions = set(self._find_all_symbols('.'))
        self.pie_positions = set(self._find_all_symbols('O'))
        self.total_food = len(self.food_positions)
        self.exit_pos = self._find_symbol('E')

        self.teleporter_corners = self._find_teleporter_corners()
        
        for y, row in enumerate(self.layout):
            for x, cell in enumerate(row):
                if cell in ['G', 'P']:
                    self.layout[y][x] = ' '

    def _find_symbol(self, symbol):
        for y, row in enumerate(self.original_layout):
            for x, cell in enumerate(row):
                if cell == symbol:
                    return (x, y)
        return None
    
    def _find_all_symbols(self, symbol):
        positions = []
        for y, row in enumerate(self.original_layout):
            for x, cell in enumerate(row):
                if cell == symbol:
                    positions.append((x, y))
        return positions
    
    def _find_teleporter_corners(self):
        corners = []
        
        #Upperleft corner
        for y in range(self.height):
            for x in range(self.width):
                if self.layout[y][x] != '%':
                    corners.append((x, y))
                    break
            if len(corners) > 0:
                break
        
        #Upperright corner
        for y in range(self.height):
            for x in range(self.width - 1, -1, -1):
                if self.layout[y][x] != '%':
                    corners.append((x, y))
                    break
            if len(corners) > 1:
                break
        
        #Lowerleft corner
        for y in range(self.height - 1, -1, -1):
            for x in range(self.width):
                if self.layout[y][x] != '%':
                    corners.append((x, y))
                    break
            if len(corners) > 2:
                break
        
        #Lowerright corner
        for y in range(self.height - 1, -1, -1):
            for x in range(self.width - 1, -1, -1):
                if self.layout[y][x] != '%':
                    corners.append((x, y))
                    break
            if len(corners) > 3:
                break
        
        return corners

    def is_wall(self, x, y, can_eat_walls=False):
        if can_eat_walls:
            return False
        if 0 <= y < self.height and 0 <= x < self.width:
            return self.layout[y][x] == '%'
        return True
    
    def collect_item(self, x, y):
        pos = (x, y)
        if pos in self.food_positions:
            self.food_positions.remove(pos)
            self.layout[y][x] = ' '
            return 'food'
        elif pos in self.pie_positions:
            self.pie_positions.remove(pos)
            self.layout[y][x] = ' '
            return 'pie'
        return None
    
    def rotate_90_clockwise(self):
        new_layout = []
        new_height = self.width
        new_width = self.height
        
        for x in range(self.width):
            new_row = []
            for y in range(self.height - 1, -1, -1):
                new_row.append(self.layout[y][x])
            new_layout.append(new_row)
        
        self.layout = new_layout
        self.height = new_height
        self.width = new_width
        
        self.food_positions = set(self._rotate_positions(self.food_positions, new_height, new_width))
        self.pie_positions = set(self._rotate_positions(self.pie_positions, new_height, new_width))
        self.exit_pos = self._rotate_position(self.exit_pos, new_height, new_width)
        self.teleporter_corners = [self._rotate_position(c, new_height, new_width) for c in self.teleporter_corners]
    
    def _rotate_position(self, pos, new_height, new_width):
        if pos is None:
            return None
        x, y = pos
        old_height = new_width
        return (old_height - 1 - y, x)
    
    def _rotate_positions(self, positions, new_height, new_width):
        return [self._rotate_position(pos, new_height, new_width) for pos in positions]

    def draw(self, screen):
        for y, row in enumerate(self.layout):
            for x, cell in enumerate(row):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if cell == '%':
                    pygame.draw.rect(screen, BLUE, rect)
                elif cell == '.':
                    pygame.draw.circle(screen, WHITE, rect.center, CELL_SIZE // 8)
                elif cell == 'O':
                    pygame.draw.circle(screen, ORANGE, rect.center, CELL_SIZE // 4)
                elif cell == 'E':
                    pygame.draw.rect(screen, GREEN, rect)
                else:
                    pygame.draw.rect(screen, BLACK, rect)
        
        #Draw teleporters in corners
        for corner in self.teleporter_corners:
            x, y = corner
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, CYAN, rect, 3)
            pygame.draw.circle(screen, CYAN, rect.center, CELL_SIZE // 6)


class Ghost:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = 1
    
    def move(self, maze):
        new_x = self.x + self.direction
        if maze.is_wall(new_x, self.y):
            self.direction *= -1
            new_x = self.x + self.direction
        
        if not maze.is_wall(new_x, self.y):
            self.x = new_x
    
    def rotate_position(self, old_width, old_height):
        new_x = old_height - 1 - self.y
        new_y = self.x
        self.x = new_x
        self.y = new_y
        self.direction = 1 if (self.x + self.y) % 2 == 0 else -1
    
    def draw(self, screen):
        rect = pygame.Rect(self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.circle(screen, RED, rect.center, CELL_SIZE // 3)


class Pacman:
    def __init__(self, start_pos):
        self.x, self.y = start_pos
        self.target_x, self.target_y = start_pos
        self.visual_x, self.visual_y = float(start_pos[0]), float(start_pos[1])
        self.pie_steps_remaining = 0
        self.animation_speed = 0.15

    def move(self, dx, dy, maze):
        can_eat_walls = self.pie_steps_remaining > 0
        new_x, new_y = self.x + dx, self.y + dy
        
        if not maze.is_wall(new_x, new_y, can_eat_walls):
            self.x, self.y = new_x, new_y
            self.target_x, self.target_y = new_x, new_y
            if self.pie_steps_remaining > 0:
                self.pie_steps_remaining -= 1
            return True
        return False
    
    #move animation for pacman
    def update_animation(self):
        dx = self.target_x - self.visual_x
        dy = self.target_y - self.visual_y
        
        if abs(dx) > 0.01:
            self.visual_x += dx * self.animation_speed
        else:
            self.visual_x = self.target_x
            
        if abs(dy) > 0.01:
            self.visual_y += dy * self.animation_speed
        else:
            self.visual_y = self.target_y
    
    def collect(self, maze):
        item = maze.collect_item(self.x, self.y)
        if item == 'pie':
            self.pie_steps_remaining = 5
        return item
    
    def is_at_teleporter(self, maze):
        return (self.x, self.y) in maze.teleporter_corners
    
    def teleport(self, corner_pos): #very hard to do
        self.x, self.y = corner_pos
        self.visual_x, self.visual_y = float(corner_pos[0]), float(corner_pos[1])
        self.target_x, self.target_y = corner_pos
    
    def rotate_position(self, old_width, old_height):
        new_x = old_height - 1 - self.y
        new_y = self.x
        self.x = new_x
        self.y = new_y
        self.target_x = new_x
        self.target_y = new_y
        self.visual_x = float(new_x)
        self.visual_y = float(new_y)

    def draw(self, screen):
        rect = pygame.Rect(self.visual_x * CELL_SIZE, self.visual_y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        color = PURPLE if self.pie_steps_remaining > 0 else YELLOW #purple if pie otherwise yellow
        pygame.draw.circle(screen, color, rect.center, CELL_SIZE // 2 - 2)


class Game:
    def __init__(self, layout_path):
        pygame.init()
        self.maze = Maze(layout_path)
        self.pacman = Pacman(self.maze.start_pos)
        
        self.ghosts = []
        ghost_positions = self.maze._find_all_symbols('G')
        for gx, gy in ghost_positions:
            self.ghosts.append(Ghost(gx, gy))

        window_size = self.maze.display_size * CELL_SIZE
        self.screen = pygame.display.set_mode((window_size, window_size))
        pygame.display.set_caption("Pacman")
        self.clock = pygame.time.Clock()
        self.running = True
        self.steps = 0
        self.food_collected = 0
        self.game_state = "playing"
        
        self.teleport_mode = False
        
        self.last_ghost_move = pygame.time.get_ticks()
        self.last_player_move = 0

    def handle_input(self):
        if self.game_state != "playing":
            return
        
        current_time = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()

        if self.teleport_mode:
            if keys[pygame.K_1] and len(self.maze.teleporter_corners) > 0:
                self.pacman.teleport(self.maze.teleporter_corners[0])
                self.teleport_mode = False
            elif keys[pygame.K_2] and len(self.maze.teleporter_corners) > 1:
                self.pacman.teleport(self.maze.teleporter_corners[1])
                self.teleport_mode = False
            elif keys[pygame.K_3] and len(self.maze.teleporter_corners) > 2:
                self.pacman.teleport(self.maze.teleporter_corners[2])
                self.teleport_mode = False
            elif keys[pygame.K_4] and len(self.maze.teleporter_corners) > 3:
                self.pacman.teleport(self.maze.teleporter_corners[3])
                self.teleport_mode = False
            return
        
        if current_time - self.last_player_move < MOVE_COOLDOWN:
            return
        
        dx, dy = 0, 0
        if keys[pygame.K_UP]:
            dy = -1
        elif keys[pygame.K_DOWN]:
            dy = 1
        elif keys[pygame.K_LEFT]:
            dx = -1
        elif keys[pygame.K_RIGHT]:
            dx = 1

        if dx != 0 or dy != 0:
            moved = self.pacman.move(dx, dy, self.maze)
            if moved:
                self.last_player_move = current_time
                self.steps += 1

                item = self.pacman.collect(self.maze)
                if item == 'food':
                    self.food_collected += 1

                if self.pacman.is_at_teleporter(self.maze):
                    self.teleport_mode = True

                if self.check_ghost_collision():
                    self.steps += 10

                if self.check_win_condition():
                    self.game_state = "won"

                if self.steps % 30 == 0 and self.steps > 0:
                    self.rotate_maze()
    
    def update_ghosts(self):
        if self.game_state != "playing":
            return
            
        current_time = pygame.time.get_ticks()
        if current_time - self.last_ghost_move >= GHOST_MOVE_COOLDOWN:
            for ghost in self.ghosts:
                ghost.move(self.maze)
            self.last_ghost_move = current_time
            
            if self.check_ghost_collision(): 
                self.steps += 10 #plus 10 steps if touch ghost as punishment

    def check_ghost_collision(self):
        for ghost in self.ghosts:
            if self.pacman.x == ghost.x and self.pacman.y == ghost.y:
                return True
        return False
    
    def check_win_condition(self):
        if self.food_collected >= self.maze.total_food:
            if (self.pacman.x, self.pacman.y) == self.maze.exit_pos:
                return True
        return False
    
    def rotate_maze(self):
        old_width = self.maze.width
        old_height = self.maze.height
        
        self.maze.rotate_90_clockwise()
        self.pacman.rotate_position(old_width, old_height)
        
        for ghost in self.ghosts:
            ghost.rotate_position(old_width, old_height)

    def draw_hud(self):
        font = pygame.font.SysFont("arial", 12)
        
        #steps and food counter
        text1 = font.render(f"Steps: {self.steps}", True, WHITE)
        text2 = font.render(f"Food: {self.food_collected}/{self.maze.total_food}", True, WHITE)
        self.screen.blit(text1, (5, 5))
        self.screen.blit(text2, (5, 20))
        
        if self.pacman.pie_steps_remaining > 0:
            text3 = font.render(f"Wall-eating: {self.pacman.pie_steps_remaining}", True, PURPLE)
            self.screen.blit(text3, (5, 35))
        
        if self.teleport_mode:
            text4 = font.render("Teleport to corner (1-4):", True, CYAN)
            self.screen.blit(text4, (5, 50))
            labels = ["1: Upper-Left", "2: Upper-Right", "3: Lower-Left", "4: Lower-Right"]
            for i in range(min(4, len(self.maze.teleporter_corners))):
                text5 = font.render(labels[i], True, CYAN)
                self.screen.blit(text5, (5, 65 + i * 15))
        
        if self.game_state == "won":
            big_font = pygame.font.SysFont("arial", 32)
            text = big_font.render("your winner", True, GREEN)
            rect = text.get_rect(center=(self.maze.display_size * CELL_SIZE // 2, 
                                         self.maze.display_size * CELL_SIZE // 2))
            bg_rect = rect.inflate(20, 20)
            pygame.draw.rect(self.screen, BLACK, bg_rect)
            pygame.draw.rect(self.screen, GREEN, bg_rect, 3)
            self.screen.blit(text, rect)
        elif self.game_state == "lost":
            big_font = pygame.font.SysFont("arial", 32)
            text = big_font.render("you lose", True, RED)
            rect = text.get_rect(center=(self.maze.display_size * CELL_SIZE // 2, 
                                         self.maze.display_size * CELL_SIZE // 2))
            bg_rect = rect.inflate(20, 20)
            pygame.draw.rect(self.screen, BLACK, bg_rect)
            pygame.draw.rect(self.screen, RED, bg_rect, 3)
            self.screen.blit(text, rect)

    def draw(self):
        self.screen.fill(BLACK)
        self.maze.draw(self.screen)
        
        for ghost in self.ghosts:
            ghost.draw(self.screen)
        
        self.pacman.update_animation()
        self.pacman.draw(self.screen)
        self.draw_hud()
        pygame.display.flip()

    #main game loop
    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    sys.exit()

            self.handle_input()
            self.update_ghosts()
            self.draw()
            self.clock.tick(FPS) 

#main menu for requirement 3 UI UX 
def main_menu():
    pygame.init()
    screen = pygame.display.set_mode((600, 400))
    pygame.display.set_caption("Pacman")
    font_title = pygame.font.SysFont("arial", 64, bold=True)
    font_button = pygame.font.SysFont("arial", 32)
    clock = pygame.time.Clock()
    running = True

    buttons = [
        {"text": "Play", "rect": pygame.Rect(220, 160, 160, 50)},
        {"text": "Quit", "rect": pygame.Rect(250, 240, 100, 50)}
    ]

    while running:
        screen.fill(BLACK)
        title_surface = font_title.render("PACMAN", True, YELLOW)
        screen.blit(title_surface, (180, 60))

        mouse_pos = pygame.mouse.get_pos() #hover check
        for button in buttons:
            rect = button["rect"]
            color = WHITE
            if rect.collidepoint(mouse_pos):
                color = YELLOW #hover color
            pygame.draw.rect(screen, color, rect, border_radius=10)
            text_surface = font_button.render(button["text"], True, BLACK)
            text_rect = text_surface.get_rect(center=rect.center)
            screen.blit(text_surface, text_rect)

        #click button check
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in buttons:
                    if button["rect"].collidepoint(event.pos):
                        if button["text"] == "Play":
                            game = Game("task02_pacman_example_map.txt")
                            game.run()
                        elif button["text"] == "Quit":
                            running = False
                            pygame.quit()
                            sys.exit()

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main_menu()