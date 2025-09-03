import pygame
import math
import random

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, player, screen_width, screen_height, spritesheet_path, frame_width, frame_height):
        super().__init__()
        self.player = player
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Charger le spritesheet
        self.spritesheet = pygame.image.load(spritesheet_path).convert_alpha()
        self.frame_width = frame_width
        self.frame_height = frame_height

        # Extraire toutes les frames
        self.frames = self.load_frames()
        self.current_frame = 0
        self.animation_speed = 0.2  # Vitesse de défilement des frames

        # Image et position initiales
        self.image = self.frames[self.current_frame].copy()
        self.rect = self.image.get_rect(center=(x, y))

        # Paramètres de déplacement
        self.speed_close = 1.5
        self.speed_far = 0.75
        self.activation_distance = 200
        self.random_dx = 0
        self.random_dy = 0
        self.direction_timer = 0

    def load_frames(self):
        """Découpe les frames du spritesheet et les stocke dans une liste."""
        frames = []
        sheet_width = self.spritesheet.get_width()
        sheet_height = self.spritesheet.get_height()
        for y in range(0, sheet_height, self.frame_height):
            for x in range(0, sheet_width, self.frame_width):
                frame = self.spritesheet.subsurface(pygame.Rect(x, y, self.frame_width, self.frame_height))
                frames.append(frame)
        return frames

    def update(self, walls):
        """Met à jour la position, l'animation et l'apparence de l'ennemi."""
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        distance = math.hypot(dx, dy)

        # Calcul alpha (opacité) en fonction de la distance
        alpha = max(0, min(255, int(255 * (self.activation_distance - distance) / self.activation_distance)))

        # Détermination de la direction
        if distance < self.activation_distance:
            speed = self.speed_close
            if distance != 0:
                dx_norm = dx / distance
                dy_norm = dy / distance
            else:
                dx_norm, dy_norm = 0, 0
        else:
            speed = self.speed_far
            self.direction_timer -= 1
            if self.direction_timer <= 0:
                angle = random.uniform(0, math.pi * 2)
                self.random_dx = math.cos(angle)
                self.random_dy = math.sin(angle)
                self.direction_timer = random.randint(30, 90)
            dx_norm, dy_norm = self.random_dx, self.random_dy

        # Déplacement horizontal
        self.rect.x += dx_norm * speed
        for wall in walls:
            if self.rect.colliderect(wall):
                if dx_norm > 0:
                    self.rect.right = wall.left
                elif dx_norm < 0:
                    self.rect.left = wall.right

        # Déplacement vertical
        self.rect.y += dy_norm * speed
        for wall in walls:
            if self.rect.colliderect(wall):
                if dy_norm > 0:
                    self.rect.bottom = wall.top
                elif dy_norm < 0:
                    self.rect.top = wall.bottom

        # Empêcher de sortir de l'écran
        self.rect.clamp_ip(pygame.Rect(0, 0, self.screen_width, self.screen_height))

        # Animation (uniquement si l'ennemi se déplace)
        if dx_norm != 0 or dy_norm != 0:
            self.current_frame += self.animation_speed
            if self.current_frame >= len(self.frames):
                self.current_frame = 0

        # Appliquer l'alpha à la frame actuelle
        frame = self.frames[int(self.current_frame)].copy()
        frame.set_alpha(alpha)

        # Inverser horizontalement si le zombie va vers la gauche
        if dx_norm < 0:
            frame = pygame.transform.flip(frame, True, False)

        self.image = frame

    def draw(self, surface):
        """Dessine l'ennemi à l'écran."""
        surface.blit(self.image, self.rect)

