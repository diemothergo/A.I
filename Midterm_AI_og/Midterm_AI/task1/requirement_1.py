# requirement_1.py
# Task 1: State space formulation for 8-puzzle

class PuzzleState:
    def __init__(self, board, parent=None, move=None, depth=0):
        self.board = board
        self.parent = parent
        self.move = move
        self.depth = depth
        self.zero_index = board.index(0)

    def get_neighbors(self):
        neighbors = []
        row, col = divmod(self.zero_index, 3)
        moves = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}

        for move, (dr, dc) in moves.items():
            new_r, new_c = row + dr, col + dc
            if 0 <= new_r < 3 and 0 <= new_c < 3:
                new_index = new_r * 3 + new_c
                new_board = self.board[:]
                new_board[self.zero_index], new_board[new_index] = new_board[new_index], new_board[self.zero_index]
                neighbors.append(PuzzleState(new_board, self, move, self.depth + 1))
        return neighbors


if __name__ == "__main__":
    start = PuzzleState([1, 2, 3, 4, 0, 5, 6, 7, 8])
    print("Initial state:", start.board)
    print("Possible next states:")
    for n in start.get_neighbors():
        print(n.board)
