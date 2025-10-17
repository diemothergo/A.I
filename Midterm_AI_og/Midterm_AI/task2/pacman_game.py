# pacman_game_final.py
# FINAL VERSION — AI with Step-by-Step Reaction & Correct Teleport Logic

import sys, os, pygame, time, random
from collections import deque, namedtuple
import heapq

# ===================================================================
# FIX UNICODE OUTPUT ON WINDOWS
# ===================================================================
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# ===================================================================
# CONSTANTS & COLORS
# ===================================================================
CELL_SIZE = 24
FPS = 18
BLACK, WHITE, BLUE, YELLOW, RED, GREEN, GREY, ORANGE, GHOST_BLUE, EXIT_COLOR = (
    (0,0,0), (255,255,255), (33,150,243), (255,255,0), (255,0,0),
    (0,255,0), (120,120,120), (255,165,0), (0,0,205), (0,255,255)
)

# ===================================================================
# A* SOLVER
# ===================================================================
class AStarSolver:
    def __init__(self, problem): self.problem = problem
    def heuristic(self, a, b): return self.problem.get_dist(a, b)

    def neighbors(self, node, can_pass_wall):
        x,y = node
        for dx,dy in [(0,1),(1,0),(0,-1),(-1,0)]:
            nx, ny = x+dx, y+dy
            if not (0 <= nx < self.problem.width and 0 <= ny < self.problem.height): continue
            if (nx,ny) in self.problem.walls and not can_pass_wall: continue
            yield (nx,ny)
        if node in self.problem.teleport_cells:
            for t in self.problem.teleport_cells:
                if t != node: yield t

    def search(self, start, goal, can_pass_wall=False, obstacles=set()):
        t0 = time.time()
        open_set = []
        heapq.heappush(open_set, (0 + self.heuristic(start, goal), 0, start))
        came_from = {start: None}; gscore = {start: 0}; closed = set()
        nodes_expanded = 0
        while open_set:
            _, gcur, current = heapq.heappop(open_set)
            if current in closed: continue
            nodes_expanded += 1
            if current == goal:
                path = []; cur = current
                while cur is not None: path.append(cur); cur = came_from[cur]
                return list(reversed(path)), nodes_expanded, time.time()-t0
            closed.add(current)
            for nb in self.neighbors(current, can_pass_wall):
                if nb in obstacles: continue
                tentative_g = gcur + 1
                if nb in gscore and tentative_g >= gscore[nb]: continue
                came_from[nb] = current
                gscore[nb] = tentative_g
                f = tentative_g + self.heuristic(nb, goal)
                heapq.heappush(open_set, (f, tentative_g, nb))
        return None, nodes_expanded, time.time()-t0

# ===================================================================
# PACMAN PROBLEM - MAP, STATE, RULES
# ===================================================================
class PacmanProblem:
    State = namedtuple('State',['pacman_pos','food_left','ghost_positions','ghost_directions','magic_timer'])

    def __init__(self, layout_text):
        self._parse_layout(layout_text)
        self.teleport_cells = self._find_teleport_cells()
        self.dist_cache = {}; self._precompute_distances()
        self.astar = AStarSolver(self)

    def _parse_layout(self, layout_text):
        lines = [l.rstrip('\n') for l in layout_text.strip().split('\n') if l.strip()]
        self.height = len(lines); self.width = max(len(l) for l in lines)
        self.walls, self.food, self.magic, self.ghost_starts = set(), set(), set(), []
        self.exit_pos = self.pacman_start = None
        for y, line in enumerate(lines):
            for x, ch in enumerate(line):
                p = (x,y)
                if ch == '%': self.walls.add(p)
                elif ch == '.': self.food.add(p)
                elif ch in 'oO': self.magic.add(p)
                elif ch == 'G': self.ghost_starts.append({'pos':p,'dir':1})
                elif ch == 'P': self.pacman_start = p
                elif ch == 'E': self.exit_pos = p
        self.all_food_start = self.food.union(self.magic)
        if not self.pacman_start or not self.exit_pos:
            raise ValueError("Map missing 'P' or 'E'.")

    def _find_teleport_cells(self):
        corners = [(0,0),(self.width-1,0),(0,self.height-1),(self.width-1,self.height-1)]
        found=[]
        for cx,cy in corners:
            if (cx,cy) not in self.walls:
                found.append((cx,cy))
            else:
                best=None; bd=9999
                for y in range(self.height):
                    for x in range(self.width):
                        if (x,y) in self.walls: continue
                        d = abs(x-cx)+abs(y-cy)
                        if d < bd: bd=d; best=(x,y)
                if best: found.append(best)
        uniq=[]; [uniq.append(c) for c in found if c not in uniq]
        return tuple(uniq)

    def _precompute_distances(self):
        print("Pre-computing distances...")
        free=[(x,y) for y in range(self.height) for x in range(self.width) if (x,y) not in self.walls]
        for p in free:
            d=self._bfs_all_from(p)
            for q,v in d.items(): self.dist_cache[(p,q)] = v
        print("Done pre-computing.")

    def _bfs_all_from(self,start):
        d={start:0}; q=deque([start])
        while q:
            cur=q.popleft(); cx,cy=cur
            for dx,dy in [(0,1),(1,0),(0,-1),(-1,0)]:
                nxt=(cx+dx,cy+dy)
                if not(0<=nxt[0]<self.width and 0<=nxt[1]<self.height): continue
                if nxt in self.walls or nxt in d: continue
                d[nxt]=d[cur]+1; q.append(nxt)
        return d

    def get_dist(self,a,b): return self.dist_cache.get((a,b), abs(a[0]-b[0]) + abs(a[1]-b[1]))

    def get_initial_state(self):
        return self.State(self.pacman_start,frozenset(self.all_food_start),
            tuple(gs['pos'] for gs in self.ghost_starts),
            tuple(gs['dir'] for gs in self.ghost_starts),0)

    def apply_move(self, state, new_pos, is_wait=False):
        food_left = set(state.food_left)
        magic = state.magic_timer if is_wait else max(0, state.magic_timer - 1)
        ghosts = list(state.ghost_positions); dirs = list(state.ghost_directions)
        
        pacman_prev_pos = state.pacman_pos

        # --- SỬA LỖI LOGIC: Xóa logic teleport ngẫu nhiên ở đây ---
        # AI sẽ tự quyết định bước nhảy trong kế hoạch của nó.
        
        if new_pos in food_left:
            food_left.remove(new_pos)
            if new_pos in self.magic:
                magic = 5

        new_gpos, new_gdir = [], []
        for (gx, gy), d in zip(ghosts, dirs):
            nx = gx + d
            if not (0 <= nx < self.width) or (nx, gy) in self.walls:
                d *= -1; gx=gx
            else:
                gx = nx
            new_gpos.append((gx,gy)); new_gdir.append(d)

        if new_pos in new_gpos: return None
        for i, g_new in enumerate(new_gpos):
            g_prev = ghosts[i]
            if new_pos == g_prev and pacman_prev_pos == g_new:
                return None

        return self.State(new_pos, frozenset(food_left), tuple(new_gpos), tuple(new_gdir), magic)

# ===================================================================
# GAME (PYGAME)
# ===================================================================
class Game:
    def __init__(self,map_file):
        pygame.init()
        with open(map_file,'r',encoding='utf-8') as f: txt=f.read()
        self.problem=PacmanProblem(txt)
        self.screen=pygame.display.set_mode((self.problem.width*CELL_SIZE,(self.problem.height+2)*CELL_SIZE))
        pygame.display.set_caption("Pacman AI Final (press A=Auto or M=Manual)")
        self.clock=pygame.time.Clock()
        self.font=pygame.font.SysFont('Consolas',18,bold=True)
        self.frame=0; self.direction='East'; self.bg=self._create_background(); self.mode=None

    def _create_background(self):
        bg=pygame.Surface(self.screen.get_size()); bg.fill(BLACK)
        for (x,y) in self.problem.walls:
            pygame.draw.rect(bg,BLUE,(x*CELL_SIZE,y*CELL_SIZE,CELL_SIZE,CELL_SIZE))
        return bg

    def _draw_pacman(self,pos,magic):
        cx,cy=pos[0]*CELL_SIZE+CELL_SIZE//2,pos[1]*CELL_SIZE+CELL_SIZE//2
        r=CELL_SIZE//2-2; color=GREEN if magic>0 else YELLOW
        pygame.draw.circle(self.screen,color,(cx,cy),r)
        if (self.frame//4)%2==0:
            if self.direction=='East': pts=[(cx,cy),(cx+r,cy-r//2),(cx+r,cy+r//2)]
            elif self.direction=='West': pts=[(cx,cy),(cx-r,cy-r//2),(cx-r,cy+r//2)]
            elif self.direction=='North': pts=[(cx,cy),(cx-r//2,cy-r),(cx+r//2,cy-r)]
            else: pts=[(cx,cy),(cx-r//2,cy+r),(cx+r//2,cy+r)]
            pygame.draw.polygon(self.screen,BLACK,pts)

    def _draw_ghost(self,pos, vulnerable=False):
        x,y=pos; cx=x*CELL_SIZE; cy=y*CELL_SIZE;
        color=GHOST_BLUE if vulnerable else RED
        body=pygame.Rect(cx+2,cy+CELL_SIZE//3,CELL_SIZE-4,int(CELL_SIZE/1.5))
        pygame.draw.rect(self.screen,color,body)
        pygame.draw.circle(self.screen,color,(cx+CELL_SIZE//2,cy+CELL_SIZE//3),CELL_SIZE//2-2)
        ex1=(cx+CELL_SIZE//3,cy+CELL_SIZE//3); ex2=(cx+2*CELL_SIZE//3,cy+CELL_SIZE//3)
        pygame.draw.circle(self.screen,WHITE,ex1,CELL_SIZE//6); pygame.draw.circle(self.screen,WHITE,ex2,CELL_SIZE//6)
        pygame.draw.circle(self.screen,BLACK,ex1,CELL_SIZE//12); pygame.draw.circle(self.screen,BLACK,ex2,CELL_SIZE//12)
        for i in range(3): pygame.draw.circle(self.screen,color,(cx+i*(CELL_SIZE//3)+CELL_SIZE//6,cy+CELL_SIZE-3),CELL_SIZE//6)

    def _draw_state(self,state,info=""):
        self.screen.blit(self.bg,(0,0))
        for (x,y) in state.food_left:
            color=ORANGE if (x,y) in self.problem.magic else WHITE
            rad=CELL_SIZE//3 if (x,y) in self.problem.magic else CELL_SIZE//8
            pygame.draw.circle(self.screen,color,(x*CELL_SIZE+CELL_SIZE//2,y*CELL_SIZE+CELL_SIZE//2),rad)
        for t in self.problem.teleport_cells:
            pygame.draw.rect(self.screen,(255,255,0),(t[0]*CELL_SIZE+3,t[1]*CELL_SIZE+3,CELL_SIZE-6,CELL_SIZE-6),2)
        for gpos in state.ghost_positions: self._draw_ghost(gpos, state.magic_timer > 0)
        ex=self.problem.exit_pos
        pygame.draw.rect(self.screen,EXIT_COLOR,(ex[0]*CELL_SIZE+6,ex[1]*CELL_SIZE+6,CELL_SIZE-12,CELL_SIZE-12))
        self._draw_pacman(state.pacman_pos,state.magic_timer)
        panel_y=self.problem.height*CELL_SIZE
        pygame.draw.rect(self.screen,GREY,(0,panel_y,self.problem.width*CELL_SIZE,2*CELL_SIZE))
        self.screen.blit(self.font.render(info,True,BLACK),(10,panel_y+8))
        pygame.display.flip()

    def _update_direction(self,new_pos,prev_pos):
        if new_pos[0]>prev_pos[0]: self.direction='East'
        elif new_pos[0]<prev_pos[0]: self.direction='West'
        elif new_pos[1]<prev_pos[1]: self.direction='North' # Pygame Y is inverted
        elif new_pos[1]>prev_pos[1]: self.direction='South'

    def _death_anim(self):
        for alpha in range(0,255,15):
            fade=pygame.Surface(self.screen.get_size()); fade.fill(BLACK); fade.set_alpha(alpha)
            self.screen.blit(fade,(0,0)); pygame.display.update(); pygame.time.delay(30)

    def _win_anim(self):
        for alpha in range(0,255,15):
            fade=pygame.Surface(self.screen.get_size()); fade.fill(WHITE); fade.set_alpha(alpha)
            self.screen.blit(fade,(0,0)); pygame.display.update(); pygame.time.delay(20)
            
    # -------- Auto Mode --------
    def run_auto(self):
        state = self.problem.get_initial_state()
        total_nodes, total_time = 0, 0.0
        self._draw_state(state, "Auto Mode: Step-by-Step Reactive A*")

        while True:
            if any(e.type==pygame.QUIT for e in pygame.event.get()): return
            
            food_left = set(state.food_left)
            if not food_left and state.pacman_pos == self.problem.exit_pos:
                self._draw_state(state, "🎉 Pacman escaped successfully!")
                self._win_anim(); return

            pac = state.pacman_pos
            can_pass = state.magic_timer > 0
            obstacles = set(state.ghost_positions)
            
            targets = sorted(food_left, key=lambda f: (f not in self.problem.magic, self.problem.get_dist(pac, f)))
            if not food_left: targets = [self.problem.exit_pos]

            path, nodes, t = None, 0, 0
            for target in targets:
                path, nodes, t = self.problem.astar.search(pac, target, can_pass_wall=can_pass, obstacles=obstacles)
                total_nodes += nodes; total_time += t
                if path and len(path) > 1:
                    print(f"A* to {target}: nodes={nodes}, t={t:.4f}s. Path found. Taking one step.")
                    break
            
            if path and len(path) > 1:
                next_pos = path[1] 
                prev_pos = state.pacman_pos
                new_state = self.problem.apply_move(state, next_pos)
                if new_state is None:
                    self._draw_state(state, "💀 Pacman touched a ghost! Game Over.")
                    self._death_anim(); return
                
                self._update_direction(new_state.pacman_pos, prev_pos)
                state = new_state
            else:
                print("⚠️ No safe path found. Pacman waits.")
                state = self.problem.apply_move(state, state.pacman_pos, is_wait=True)

            self.frame += 1
            info = f"A*: food left={len(state.food_left)} | magic={state.magic_timer}"
            self._draw_state(state, info)
            self.clock.tick(FPS)

    # -------- Manual Mode --------
    def run_manual(self):
        state=self.problem.get_initial_state()
        self._draw_state(state,"Manual Mode — Arrow keys to move")
        while True:
            for e in pygame.event.get():
                if e.type==pygame.QUIT or (e.type==pygame.KEYDOWN and e.key==pygame.K_ESCAPE):
                    pygame.quit(); return
                if e.type==pygame.KEYDOWN:
                    move, direction = None, self.direction
                    if e.key==pygame.K_LEFT: move=(-1,0); direction='West'
                    elif e.key==pygame.K_RIGHT: move=(1,0); direction='East'
                    elif e.key==pygame.K_UP: move=(0,-1); direction='North'
                    elif e.key==pygame.K_DOWN: move=(0,1); direction='South'
                    if move:
                        self.direction = direction
                        np=(state.pacman_pos[0]+move[0],state.pacman_pos[1]+move[1])
                        if not(0<=np[0]<self.problem.width and 0<=np[1]<self.problem.height): continue
                        if np in self.problem.walls and state.magic_timer==0: continue
                        
                        new_state=self.problem.apply_move(state,np)
                        if new_state is None:
                            self._draw_state(state,"💀 Pacman touched a ghost! Game Over."); self._death_anim(); return
                        state=new_state; self.frame+=1
                        
            info=f"Manual: food left={len(state.food_left)} | magic={state.magic_timer}"
            self._draw_state(state,info)
            if not state.food_left and state.pacman_pos==self.problem.exit_pos:
                self._draw_state(state,"🎉 Pacman escaped successfully!"); self._win_anim(); return
            self.clock.tick(FPS)

    def _menu(self):
        w,h=600,140; sc=pygame.display.set_mode((w,h))
        pygame.display.set_caption("Select Mode: A = Auto | M = Manual | ESC = Exit")
        font=pygame.font.SysFont('Consolas',18,bold=True)
        sc.fill(BLACK)
        sc.blit(font.render("Press A for Auto (A*) or M for Manual (arrow keys). ESC to quit.",True,WHITE),(10,20))
        sc.blit(font.render("Auto uses reactive A* with wall-pass logic.",True,WHITE),(10,60))
        sc.blit(font.render("Pacman CANNOT eat ghosts. Reach Exit (E) after all food eaten.",True,WHITE),(10,90))
        pygame.display.flip()
        while True:
            for e in pygame.event.get():
                if e.type==pygame.QUIT or (e.type==pygame.KEYDOWN and e.key==pygame.K_ESCAPE):
                    pygame.quit(); sys.exit()
                if e.type==pygame.KEYDOWN:
                    if e.key==pygame.K_a:
                        self.mode='auto'; self.screen=pygame.display.set_mode((self.problem.width*CELL_SIZE,(self.problem.height+2)*CELL_SIZE)); return
                    if e.key==pygame.K_m:
                        self.mode='manual'; self.screen=pygame.display.set_mode((self.problem.width*CELL_SIZE,(self.problem.height+2)*CELL_SIZE)); return
            time.sleep(0.02)

    def run(self):
        self._menu()
        if self.mode=='auto': self.run_auto()
        else: self.run_manual()
        while True:
            if any(e.type==pygame.QUIT for e in pygame.event.get()):
                pygame.quit(); return
            time.sleep(0.05)


# ===================== MAIN =====================
if __name__=="__main__":
    script_dir=os.path.dirname(os.path.abspath(__file__))
    map_file=os.path.join(script_dir,"task02_pacman_example_map.txt")
    if not os.path.exists(map_file):
        print("❌ Missing map file: task02_pacman_example_map.txt"); sys.exit(1)
    Game(map_file).run()