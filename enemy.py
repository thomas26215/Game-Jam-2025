import pygame
import math
import random

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, player, screen_width, screen_height):
        super().__init__()
        self.surf = pygame.Surface((40, 40))
        self.color_close = (255, 0, 0)  # Rouge si proche
        self.color_far = (0, 255, 0)    # Vert si loin
        self.rect = self.surf.get_rect(center=(x, y))
        self.player = player
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Vitesse
        self.speed_close = 3
        self.speed_far = 1
        self.activation_distance = 200

        # Déplacement aléatoire
        self.random_dx = 0
        self.random_dy = 0
        self.direction_timer = 0  # timer pour changer direction

    def update(self, walls):
        # Calcul distance au joueur
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        distance = math.hypot(dx, dy)

        if distance < self.activation_distance:
            # Mode poursuite
            self.surf.fill(self.color_close)
            speed = self.speed_close

            # Normalisation
            if distance != 0:
                dx_norm = dx / distance
                dy_norm = dy / distance
            else:
                dx_norm, dy_norm = 0, 0
        else:
            # Mode déplacement aléatoire
            self.surf.fill(self.color_far)
            speed = self.speed_far

            # Timer pour changer direction
            self.direction_timer -= 1
            if self.direction_timer <= 0:
                angle = random.uniform(0, math.pi * 2)
                self.random_dx = math.cos(angle)
                self.random_dy = math.sin(angle)
                self.direction_timer = random.randint(30, 90)  # change tous les 0.5-1.5s

            dx_norm, dy_norm = self.random_dx, self.random_dy

        # Déplacement avec collisions
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

        # Limites écran
        self.rect.clamp_ip(pygame.Rect(0, 0, self.screen_width, self.screen_height))

    def draw(self, surface):
        surface.blit(self.surf, self.rect)

