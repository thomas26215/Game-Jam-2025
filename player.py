import pygame
from pygame.locals import *
import math

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, screen_width=1024, screen_height=700):
        super().__init__()
        self.surf = pygame.Surface((50, 50))
        self.surf.fill((0, 128, 255))
        self.rect = self.surf.get_rect(center=(x, y))
        self.speed = 5
        self.screen_width = screen_width
        self.screen_height = screen_height

    def update(self, keys, walls):
        dx = dy = 0
        if keys[K_UP]:
            dy = -self.speed
        if keys[K_DOWN]:
            dy = self.speed
        if keys[K_LEFT]:
            dx = -self.speed
        if keys[K_RIGHT]:
            dx = self.speed

        # Déplacement horizontal
        self.rect.x += dx
        for wall in walls:
            if self.rect.colliderect(wall):
                if dx > 0:
                    self.rect.right = wall.left
                elif dx < 0:
                    self.rect.left = wall.right

        # Déplacement vertical
        self.rect.y += dy
        for wall in walls:
            if self.rect.colliderect(wall):
                if dy > 0:
                    self.rect.bottom = wall.top
                elif dy < 0:
                    self.rect.top = wall.bottom

        # Limites écran
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > self.screen_width:
            self.rect.right = self.screen_width
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > self.screen_height:
            self.rect.bottom = self.screen_height


class Medicament(pygame.sprite.Sprite):
    def __init__(self, x, y, player, screen_width=1024, screen_height=700):
        super().__init__()
        self.surf = pygame.Surface((30, 30))
        self.color_close = (255, 105, 180)  # Rose si proche
        self.color_far = (128, 0, 128)      # Violet si loin
        self.rect = self.surf.get_rect(center=(x, y))
        self.player = player
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.activation_distance = 200
        self.collected = False

    def update(self):
        if self.collected:
            return  # Ne rien faire si déjà collecté

        # Calcul distance au joueur
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        distance = math.hypot(dx, dy)

        # Changer couleur selon distance
        if distance < self.activation_distance:
            self.surf.fill(self.color_close)
        else:
            self.surf.fill(self.color_far)

        # Vérifier collision avec le joueur
        if self.rect.colliderect(self.player.rect):
            self.collect()

    def draw(self, surface):
        if not self.collected:
            surface.blit(self.surf, self.rect)

    def collect(self):
        if not self.collected:
            self.collected = True
            print("Médicament collecté !")
            # Ici tu peux ajouter un effet, un son, ou augmenter le score

