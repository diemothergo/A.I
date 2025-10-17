# requirement_8.py
import time
import tracemalloc
from requirement_5 import Maze, State, a_star

def run_experiment(layout_file):
    maze = Maze(layout_file)
    start_state = State(maze.start, maze.food)

    tracemalloc.start()
    start_time = time.perf_counter()
    actions, cost = a_star(start_state, maze)
    end_time = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print("time:", round((end_time - start_time) * 1000), "ms")
    print("Number of steps:", len(actions))
    print("Total cost:", cost)
    print("Memory:", round(peak / 1024 / 1024, 2), "MB")

if __name__ == "__main__":
    run_experiment("task02_pacman_example_map.txt")
