import pygame

class Background(pygame.sprite.Sprite):
    def __init__(self, image_path, x=0, y=0):
        super().__init__()
        # Charger l'image
        self.image = pygame.image.load(image_path).convert()
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self, surface):
        surface.blit(self.image, self.rect)

