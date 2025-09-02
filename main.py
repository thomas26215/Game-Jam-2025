import pygame
from pygame.locals import (
    K_UP, K_DOWN, K_LEFT, K_RIGHT, K_ESCAPE,
    KEYDOWN, QUIT
)

# Définir les constantes pour la taille de la fenêtre
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

# Définir une classe Joueur simple
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((50, 50))
        self.surf.fill((0, 128, 255))  # Couleur bleu
        self.rect = self.surf.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))

    def update(self, keys):
        if keys[K_UP]:
            self.rect.move_ip(0, -5)
        if keys[K_DOWN]:
            self.rect.move_ip(0, 5)
        if keys[K_LEFT]:
            self.rect.move_ip(-5, 0)
        if keys[K_RIGHT]:
            self.rect.move_ip(5, 0)

        # Limiter les déplacements à l'écran
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

# Initialisation de pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Mon Jeu Pygame')
clock = pygame.time.Clock()

player = Player()
running = True

# Boucle principale du jeu
while running:
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
        elif event.type == QUIT:
            running = False

    # Gestion des touches du clavier
    pressed_keys = pygame.key.get_pressed()
    player.update(pressed_keys)

    # Dessin
    screen.fill((0, 0, 0))  # Fond noir
    screen.blit(player.surf, player.rect)
    pygame.display.flip()

    clock.tick(60)  # Limite à 60 FPS

pygame.quit()

