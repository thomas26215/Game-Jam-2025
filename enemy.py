import pygame
import math
import random

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, player, screen_width, screen_height,
                 walk_spritesheet_path, attack_spritesheet_path,
                 frame_width, frame_height,
                 activation_distance=100, speed_close=1.5, speed_far=0.75,
                 attack_range=50):
        super().__init__()
        self.player = player
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.activation_distance = activation_distance
        self.speed_close = speed_close
        self.speed_far = speed_far
        self.attack_range = attack_range

        # Charger les spritesheets
        self.walk_frames = self.load_frames(walk_spritesheet_path)
        self.attack_frames = self.load_frames(attack_spritesheet_path)

        # Animation
        self.current_frame = 0
        self.animation_speed = 0.2
        self.attack_animation_speed = 0.1  # très lent

        # Image initiale
        self.image = self.walk_frames[0].copy()
        self.rect = self.image.get_rect(center=(x, y))

        # Déplacement aléatoire
        self.random_dx = 0
        self.random_dy = 0
        self.direction_timer = 0

        self.attacking = False
        self.attack_in_progress = False  # nouvel indicateur
        self.direction = "right"

    def load_frames(self, path):
        sheet = pygame.image.load(path).convert_alpha()
        frames = []
        sheet_width = sheet.get_width()
        sheet_height = sheet.get_height()
        for y in range(0, sheet_height, self.frame_height):
            for x in range(0, sheet_width, self.frame_width):
                frames.append(sheet.subsurface(pygame.Rect(x, y, self.frame_width, self.frame_height)))
        return frames

    def update(self, walls):
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        distance = math.hypot(dx, dy)

        # Détecter le début d'attaque
        if distance <= self.attack_range and not self.attack_in_progress:
            self.attacking = True
            self.attack_in_progress = True
            self.current_frame = 0  # recommence l’animation d’attaque

        if not self.attack_in_progress:
            # Déplacement normal
            if distance < self.activation_distance:
                speed = self.speed_close
                dx_norm, dy_norm = (dx / distance, dy / distance) if distance != 0 else (0, 0)
            else:
                speed = self.speed_far
                self.direction_timer -= 1
                if self.direction_timer <= 0:
                    angle = random.uniform(0, math.pi * 2)
                    self.random_dx = math.cos(angle)
                    self.random_dy = math.sin(angle)
                    self.direction_timer = random.randint(30, 90)
                dx_norm, dy_norm = self.random_dx, self.random_dy

            # Déplacement
            self.rect.x += dx_norm * speed
            self.rect.y += dy_norm * speed

            # Direction pour flip
            self.direction = "right" if dx >= 0 else "left"

        # Choix des frames et vitesse
        frames = self.attack_frames if self.attack_in_progress else self.walk_frames
        speed = self.attack_animation_speed if self.attack_in_progress else self.animation_speed

        if frames:
            self.current_frame += speed
            if self.current_frame >= len(frames):
                if self.attack_in_progress:
                    # Fin de l’attaque
                    self.attack_in_progress = False
                    self.attacking = False
                self.current_frame = 0
            frame = frames[int(self.current_frame)].copy()
            if self.direction == "left":
                frame = pygame.transform.flip(frame, True, False)
            self.image = frame

        # Limites écran
        self.rect.clamp_ip(pygame.Rect(0, 0, self.screen_width, self.screen_height))

    def draw(self, surface):
        surface.blit(self.image, self.rect)

