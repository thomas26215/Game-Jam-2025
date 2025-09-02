import pygame
import math

class Medicament(pygame.sprite.Sprite):
    def __init__(self, x, y, player, screen_width, screen_height):
        super().__init__()
        self.surf = pygame.Surface((30, 30))
        self.color_close = (255, 105, 180)  # Rose si proche
        self.color_far = (128, 0, 128)      # Violet si loin
        self.rect = self.surf.get_rect(center=(x, y))
        self.player = player
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.activation_distance = 200
        self.collected = False  # Ajouté : état du médicament

    def update(self):
        if self.collected:
            return  # Ne rien faire si déjà ramassé

        # Calcul distance au joueur
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        distance = math.hypot(dx, dy)

        # Couleur selon distance
        if distance < self.activation_distance:
            self.surf.fill(self.color_close)
        else:
            self.surf.fill(self.color_far)

    def draw(self, surface):
        if not self.collected:  # Ne pas dessiner si ramassé
            surface.blit(self.surf, self.rect)

    def collect(self):
        if not self.collected:
            self.collected = True
            print("Médicament collecté !")

