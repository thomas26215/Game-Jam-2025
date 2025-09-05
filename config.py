import pygame

# Écran
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 700
HEAD_BAR_HEIGHT = 100

# Mur et portes
WALL_THICKNESS = 10
DOOR_SIZE = 20

# Minimap
MINIMAP_SCALE = 20  # Taille des carrés
MINIMAP_MARGIN = 10  # Marge autour

# États du jeu
STATE_MENU = "MENU"
STATE_PLAY = "GAME"
STATE_PAUSE = "PAUSE"
STATE_GAME_OVER = "GAME_OVER"
STATE_OPTIONS = "OPTIONS"
STATE_VICTORY = "VICTORY"
STATE_BACK = "BACK"

# Etats de la quête
COLLECT_MEDECINE = "COLLECT_MEDICINE"
HEAL_INFECTED = "HEAL_INFECTED"



# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Police
pygame.init()
pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

FONT = pygame.font.SysFont("Arial", 36)

# Configuration des touches par défaut
DEFAULT_CONTROLS = {
    "move_up": {"keyboard": [pygame.K_UP, pygame.K_z], "gamepad": []},  # Bouton 1 = Triangle/Y
    "move_down": {"keyboard": [pygame.K_DOWN, pygame.K_s], "gamepad": []},  # Bouton 0 = X/A
    "move_left": {"keyboard": [pygame.K_LEFT, pygame.K_q], "gamepad": []},  # Pas de bouton par défaut, utilise les sticks
    "move_right": {"keyboard": [pygame.K_RIGHT, pygame.K_d], "gamepad": []},
    "attack": {"keyboard": [pygame.K_SPACE], "gamepad": [1]},
    "interact": {"keyboard": [pygame.K_e], "gamepad": [2]},
}
