import pygame
import math
import random

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, player, screen_width, screen_height):
        super().__init__()
        self.surf = pygame.Surface((40, 40), pygame.SRCALPHA)  # Surface avec canal alpha
        self.rect = self.surf.get_rect(center=(x, y))
        self.player = player
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Couleur rouge toujours
        self.color_red = (255, 0, 0)
        
        # Vitesse selon distance
        self.speed_close = 1.5
        self.speed_far = 0.75
        self.activation_distance = 200
        
        # Déplacement aléatoire
        self.random_dx = 0
        self.random_dy = 0
        self.direction_timer = 0  # Timer pour changer la direction aléatoire

    def update(self, walls):
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        distance = math.hypot(dx, dy)

        # Calcul alpha (opacité) entre 0 (invisible loin) et 255 (visible proche)
        alpha = max(0, min(255, int(255 * (self.activation_distance - distance) / self.activation_distance)))

        # Remplir la surface en rouge avec alpha variable
        self.surf.fill(self.color_red + (alpha,))  # (R, G, B, Alpha)

        if distance < self.activation_distance:
            # Mode poursuite
            speed = self.speed_close
            if distance != 0:
                dx_norm = dx / distance
                dy_norm = dy / distance
            else:
                dx_norm, dy_norm = 0, 0
        else:
            # Mode déplacement aléatoire
            speed = self.speed_far
            self.direction_timer -= 1
            if self.direction_timer <= 0:
                angle = random.uniform(0, math.pi * 2)
                self.random_dx = math.cos(angle)
                self.random_dy = math.sin(angle)
                self.direction_timer = random.randint(30, 90)
            dx_norm, dy_norm = self.random_dx, self.random_dy

        self.rect.x += dx_norm * speed
        for wall in walls:
            if self.rect.colliderect(wall):
                if dx_norm > 0:
                    self.rect.right = wall.left
                elif dx_norm < 0:
                    self.rect.left = wall.right

        self.rect.y += dy_norm * speed
        for wall in walls:
            if self.rect.colliderect(wall):
                if dy_norm > 0:
                    self.rect.bottom = wall.top
                elif dy_norm < 0:
                    self.rect.top = wall.bottom
        
        self.rect.clamp_ip(pygame.Rect(0, 0, self.screen_width, self.screen_height))

    def draw(self, surface):
        # Dessiner seulement si visible (alpha > 0)
        if self.surf.get_alpha() is None or self.surf.get_alpha() > 0:
            surface.blit(self.surf, self.rect)

