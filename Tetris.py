import pygame
import random
import sys

pygame.init()

# Dimensions de la fenêtre de jeu
screen_width = 300
screen_height = 600
block_size = 30
columns = screen_width // block_size
rows = screen_height // block_size

# Création de la fenêtre de jeu
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Tetris")

touches = pygame.key.get_pressed()
# Couleurs
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLORS = [
    (0, 255, 255), # I
    (0, 0, 255),   # J
    (255, 165, 0), # L
    (255, 255, 0), # O
    (0, 255, 0),   # S
    (128, 0, 128), # T
    (255, 0, 0)    # Z
]

# Définition des formes (pièces Tetris)
SHAPES = [
    [[1, 1, 1, 1]],                      # I
    [[1, 0, 0], [1, 1, 1]],              # J
    [[0, 0, 1], [1, 1, 1]],              # L
    [[1, 1], [1, 1]],                    # O
    [[0, 1, 1], [1, 1, 0]],              # S
    [[0, 1, 0], [1, 1, 1]],              # T
    [[1, 1, 0], [0, 1, 1]]               # Z
]

# Classe pour les pièces de Tetris
class Piece:
    def __init__(self):
        self.shape = random.choice(SHAPES)
        self.color = random.choice(COLORS)
        self.x = columns // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

# Vérification des collisions
def check_collision(piece, grid, offset_x=0, offset_y=0):
    for y, row in enumerate(piece.shape):
        for x, cell in enumerate(row):
            if cell:
                new_x = x + piece.x + offset_x
                new_y = y + piece.y + offset_y
                if (
                    new_x < 0 or
                    new_x >= columns or
                    new_y >= rows or
                    (new_y >= 0 and grid[new_y][new_x] != BLACK)
                ):
                    return True
    return False

# Ajout de la pièce à la grille
def merge_piece(piece, grid):
    for y, row in enumerate(piece.shape):
        for x, cell in enumerate(row):
            if cell:
                grid[y + piece.y][x + piece.x] = piece.color

# Suppression des lignes complètes
def clear_lines(grid):
    new_grid = [row for row in grid if any(cell == BLACK for cell in row)]
    cleared_lines = rows - len(new_grid)
    new_grid = [[BLACK] * columns for _ in range(cleared_lines)] + new_grid
    return new_grid, cleared_lines

# Création de la grille vide
def create_grid():
    return [[BLACK for _ in range(columns)] for _ in range(rows)]

# Affichage de la grille
def draw_grid(grid):
    for y in range(rows):
        for x in range(columns):
            pygame.draw.rect(screen, grid[y][x], (x * block_size, y * block_size, block_size, block_size))

# Affichage de la fin de jeu
def draw_game_over(score, record):
    font = pygame.font.SysFont('arial', 36)
    game_over_text = font.render("Game Over", True, WHITE)
    score_text = font.render(f"Score: {score}", True, WHITE)
    record_text = font.render(f"Record: {record}", True, WHITE)
    
    # Affichage du texte à l'écran
    screen.fill(BLACK)
    screen.blit(game_over_text, (screen_width // 4, screen_height // 3))
    screen.blit(score_text, (screen_width // 4, screen_height // 2))
    screen.blit(record_text, (screen_width // 4, screen_height // 1.5))
    pygame.display.flip()

    # Attendre une action avant de fermer le jeu (par exemple, appuyer sur une touche)
    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()  # Quitter le jeu si l'utilisateur appuie sur ESCAPE
                elif event.key == pygame.K_SPACE:
                    main()
                else:
                    waiting_for_input = False  # Quitter l'écran de fin si une autre touche est pressée

# Boucle principale du jeu
def main():
    clock = pygame.time.Clock()
    grid = create_grid()
    piece = Piece()
    score = 0
    fall_speed = 500  # Intervalle en millisecondes pour faire tomber les pièces
    last_fall_time = pygame.time.get_ticks()

    running = True
    while running:
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and not check_collision(piece, grid, offset_x=-1):
                    piece.x -= 1
                elif event.key == pygame.K_RIGHT and not check_collision(piece, grid, offset_x=1):
                    piece.x += 1
                elif event.key == pygame.K_DOWN:
                    piece.y += 1 if not check_collision(piece, grid, offset_y=1) else 0
                elif event.key == pygame.K_UP:
                    piece.rotate()
                    if check_collision(piece, grid):
                        piece.rotate()
                        piece.rotate()
                        piece.rotate()  # Annuler la rotation si collision

        # Mise à jour de la chute de la pièce
        if pygame.time.get_ticks() - last_fall_time > fall_speed:
            last_fall_time = pygame.time.get_ticks()
            if not check_collision(piece, grid, offset_y=1):
                piece.y += 1
            else:
                merge_piece(piece, grid)
                grid, cleared_lines = clear_lines(grid)
                score += cleared_lines * 10  # Score selon le nombre de lignes supprimées
                piece = Piece()
                if check_collision(piece, grid):
                    running = False  # Fin du jeu en cas de collision avec le haut de la grille

        #Marquer les records
        
        with open("data/score.txt", "r") as record:
            record = int(record.read())
        if score > record:
            with open("data/score.txt", "w") as record:
                record.write(str(score))
    

        # Affichage de la grille et de la pièce actuelle
        screen.fill(BLACK)
        draw_grid(grid)
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, piece.color, ((piece.x + x) * block_size, (piece.y + y) * block_size, block_size, block_size))

        # Affichage du score
        font = pygame.font.SysFont('arial', 24)
        score_text = font.render(f'Score: {score}', True, WHITE)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(30)

    draw_game_over(score, record)

# Lancer le jeu
main()