import pygame

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.surf = pygame.Surface((width, height))
        self.surf.fill((100, 100, 100))  # couleur grise
        self.rect = self.surf.get_rect(topleft=(x, y))

    def draw(self, surface):
        surface.blit(self.surf, self.rect)

