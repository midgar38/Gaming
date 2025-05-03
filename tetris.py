import pygame
import random
import asyncio
import platform

# Initialize pygame
pygame.init()

# Constants
GRID_WIDTH = 10
GRID_HEIGHT = 20
BLOCK_SIZE = 30
SCREEN_WIDTH = GRID_WIDTH * BLOCK_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * BLOCK_SIZE
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
MAGENTA = (255, 0, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)

# Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]]   # Z
]

COLORS = [CYAN, YELLOW, MAGENTA, ORANGE, BLUE, GREEN, RED]

# Game variables
screen = None
grid = None
current_piece = None
piece_x = 0
piece_y = 0
score = 0
game_over = False
clock = pygame.time.Clock()

class Piece:
    def __init__(self, shape, color):
        self.shape = shape
        self.color = color
        self.width = len(shape[0])
        self.height = len(shape)

def create_grid():
    return [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

def new_piece():
    global current_piece, piece_x, piece_y
    shape_idx = random.randint(0, len(SHAPES) - 1)
    current_piece = Piece(SHAPES[shape_idx], COLORS[shape_idx])
    piece_x = GRID_WIDTH // 2 - current_piece.width // 2
    piece_y = 0
    if not is_valid_position(current_piece, piece_x, piece_y):
        return False
    return True

def is_valid_position(piece, x, y):
    for i in range(piece.height):
        for j in range(piece.width):
            if piece.shape[i][j]:
                if (x + j < 0 or x + j >= GRID_WIDTH or
                    y + i >= GRID_HEIGHT or
                    (y + i >= 0 and grid[y + i][x + j] != BLACK)):
                    return False
    return True

def merge_piece():
    global score
    for i in range(current_piece.height):
        for j in range(current_piece.width):
            if current_piece.shape[i][j]:
                if piece_y + i >= 0:
                    grid[piece_y + i][piece_x + j] = current_piece.color
    clear_lines()
    if not new_piece():
        global game_over
        game_over = True

def clear_lines():
    global grid, score
    lines_cleared = 0
    new_grid = [row for row in grid if any(cell == BLACK for cell in row)]
    lines_cleared = GRID_HEIGHT - len(new_grid)
    score += lines_cleared * 100
    while len(new_grid) < GRID_HEIGHT:
        new_grid.insert(0, [BLACK for _ in range(GRID_WIDTH)])
    grid = new_grid

def rotate_piece():
    global current_piece
    new_shape = [[current_piece.shape[j][i] for j in range(current_piece.height - 1, -1, -1)]
                 for i in range(current_piece.width)]
    new_piece = Piece(new_shape, current_piece.color)
    if is_valid_position(new_piece, piece_x, piece_y):
        current_piece = new_piece

def draw():
    screen.fill(BLACK)
    # Draw grid
    for i in range(GRID_HEIGHT):
        for j in range(GRID_WIDTH):
            if grid[i][j] != BLACK:
                pygame.draw.rect(screen, grid[i][j],
                               (j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE - 1, BLOCK_SIZE - 1))
    # Draw current piece
    for i in range(current_piece.height):
        for j in range(current_piece.width):
            if current_piece.shape[i][j] and piece_y + i >= 0:
                pygame.draw.rect(screen, current_piece.color,
                               ((piece_x + j) * BLOCK_SIZE, (piece_y + i) * BLOCK_SIZE,
                                BLOCK_SIZE - 1, BLOCK_SIZE - 1))
    # Draw score
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    if game_over:
        game_over_text = font.render("Game Over!", True, WHITE)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2))
    pygame.display.flip()

def setup():
    global screen, grid, clock
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris")
    grid = create_grid()
    clock = pygame.time.Clock()
    new_piece()

def update_loop():
    global piece_y, game_over
    if game_over:
        return
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                if is_valid_position(current_piece, piece_x - 1, piece_y):
                    globals()['piece_x'] -= 1
            elif event.key == pygame.K_RIGHT:
                if is_valid_position(current_piece, piece_x + 1, piece_y):
                    globals()['piece_x'] += 1
            elif event.key == pygame.K_DOWN:
                if is_valid_position(current_piece, piece_x, piece_y + 1):
                    piece_y += 1
                else:
                    merge_piece()
            elif event.key == pygame.K_UP:
                rotate_piece()
            elif event.key == pygame.K_SPACE:
                while is_valid_position(current_piece, piece_x, piece_y + 1):
                    piece_y += 1
                merge_piece()
    
    # Auto-fall
    if pygame.time.get_ticks() % 1000 < 17:  # Fall every second
        if is_valid_position(current_piece, piece_x, piece_y + 1):
            piece_y += 1
        else:
            merge_piece()
    
    draw()

async def main():
    setup()
    while not game_over:
        update_loop()
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())