import pygame
import math

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, player, screen_width, screen_height):
        super().__init__()
        self.surf = pygame.Surface((40, 40))
        self.surf.fill((255, 0, 0))
        self.rect = self.surf.get_rect(center=(x, y))
        self.speed = 3
        self.player = player
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.visible = False  # visible seulement si proche du joueur
        self.activation_distance = 200  # distance minimale pour apparaître

    def update(self, walls):
        # Calcul distance au joueur
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        distance = math.hypot(dx, dy)

        # Contrôle visibilité selon distance
        if distance < self.activation_distance:
            self.visible = True
            # Normalisation pour direction
            if distance != 0:
                dx_norm = dx / distance
                dy_norm = dy / distance
            else:
                dx_norm, dy_norm = 0, 0
            
            # Déplacement vers le joueur
            self.rect.x += dx_norm * self.speed
            for wall in walls:
                if self.rect.colliderect(wall):
                    if dx_norm > 0:
                        self.rect.right = wall.left
                    elif dx_norm < 0:
                        self.rect.left = wall.right
            
            self.rect.y += dy_norm * self.speed
            for wall in walls:
                if self.rect.colliderect(wall):
                    if dy_norm > 0:
                        self.rect.bottom = wall.top
                    elif dy_norm < 0:
                        self.rect.top = wall.bottom
            
            # Limites écran
            self.rect.clamp_ip(pygame.Rect(0, 0, self.screen_width, self.screen_height))
        else:
            self.visible = False

    def draw(self, surface):
        if self.visible:
            surface.blit(self.surf, self.rect)
