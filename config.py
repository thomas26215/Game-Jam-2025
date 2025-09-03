import pygame

# Écran
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 700

# Mur et portes
WALL_THICKNESS = 20
DOOR_SIZE = 60

# Minimap
MINIMAP_SCALE = 20  # Taille des carrés
MINIMAP_MARGIN = 10  # Marge autour

# États du jeu
STATE_MENU = "MENU"
STATE_PLAY = "GAME"

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Police
pygame.init()
FONT = pygame.font.SysFont("Arial", 36)

