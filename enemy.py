import pygame
import math
import random

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, player, screen_width, screen_height,
                 walk_spritesheet_path, attack_spritesheet_path,
                 hit_spritesheet_path=None, death_spritesheet_path=None,
                 frame_width=64, frame_height=64,
                 activation_distance=100, speed_close=1.5, speed_far=0.75,
                 attack_range=1, attack_damage=1, obstacles=None):
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
        self.attack_damage = attack_damage

        # --- Vies et états ---
        self.health = 2
        self.alive = True
        self.taking_damage = False
        self.dying = False

        # --- Animation ---
        self.walk_frames = self.load_frames(walk_spritesheet_path)
        self.attack_frames = self.load_frames(attack_spritesheet_path)
        self.hit_frames = self.load_frames(hit_spritesheet_path) if hit_spritesheet_path else []
        self.death_frames = self.load_frames(death_spritesheet_path) if death_spritesheet_path else []

        self.current_frame = 0
        self.animation_speed = 0.2
        self.attack_animation_speed = 0.10
        self.hit_animation_speed = 0.15
        self.death_animation_speed = 0.1

        self.image = self.walk_frames[0].copy()
        self.rect = self.image.get_rect(center=(x, y))
        self.hitbox = self.rect.copy()
        self.hitbox.inflate_ip(-40, -40)  

        # --- Mouvement ---
        self.random_dx = 0
        self.random_dy = 0
        self.direction_timer = 0
        self.attacking = False
        self.attack_in_progress = False
        self.direction = "right"
        self.damage_applied = False
        self.obstacles = obstacles if obstacles is not None else []


    def load_frames(self, path):
        sheet = pygame.image.load(path).convert_alpha()
        frames = []
        sheet_width = sheet.get_width()
        sheet_height = sheet.get_height()
        for y in range(0, sheet_height, self.frame_height):
            for x in range(0, sheet_width, self.frame_width):
                frames.append(sheet.subsurface(pygame.Rect(x, y, self.frame_width, self.frame_height)))
        return frames

    def take_damage(self, damage=1):
        """Réduit la vie de l'ennemi et lance l'animation de dégâts ou de mort."""
        if not self.alive or self.dying:
            return
        self.health -= damage
        if self.health <= 0:
            self.dying = True
            self.current_frame = 0
        else:
            self.taking_damage = True
            self.current_frame = 0

    def update(self):
        if not self.alive and not self.dying:
            return

        # --- Déplacement ---
        if not self.dying and not self.taking_damage:
            dx = self.player.rect.centerx - self.rect.centerx
            dy = self.player.rect.centery - self.rect.centery
            distance = math.hypot(dx, dy)

            if distance <= self.attack_range and not self.attack_in_progress:
                self.attacking = True
                self.attack_in_progress = True
                self.current_frame = 0
                self.damage_applied = False

            if not self.attack_in_progress:
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

                # --- Collision X ---
                self.hitbox.x += dx_norm * speed
                for obs in self.obstacles:
                    if self.hitbox.colliderect(obs):
                        if dx_norm > 0:
                            self.hitbox.right = obs.left
                        elif dx_norm < 0:
                            self.hitbox.left = obs.right

                # --- Collision Y ---
                self.hitbox.y += dy_norm * speed
                for obs in self.obstacles:
                    if self.hitbox.colliderect(obs):
                        if dy_norm > 0:
                            self.hitbox.bottom = obs.top
                        elif dy_norm < 0:
                            self.hitbox.top = obs.bottom

                # Synchronise la position du sprite avec la hitbox
                self.rect.center = self.hitbox.center

                self.direction = "right" if dx >= 0 else "left"

        # --- Choix de l'animation ---
        if self.dying and self.death_frames:
            frames = self.death_frames
            speed = self.death_animation_speed
        elif self.taking_damage and self.hit_frames:
            frames = self.hit_frames
            speed = self.hit_animation_speed
        elif self.attack_in_progress:
            frames = self.attack_frames
            speed = self.attack_animation_speed
        else:
            frames = self.walk_frames
            speed = self.animation_speed

        # --- Animation ---
        if frames:
            self.current_frame += speed
            if self.attack_in_progress and not self.damage_applied and int(self.current_frame) == 3:
                # Hitbox d'attaque
                attack_hitbox = self.rect.copy()
                attack_hitbox.width = self.rect.width // 3
                attack_hitbox.height = self.rect.height // 2
                if self.direction == "right":
                    attack_hitbox.x += self.rect.width // 2
                else:
                    attack_hitbox.x -= self.rect.width // 2
                attack_hitbox.y += self.rect.height // 4
                if attack_hitbox.colliderect(self.player.rect):
                    self.player.take_damage(self.attack_damage)
                    self.damage_applied = True

            if self.current_frame >= len(frames):
                if self.dying:
                    self.alive = False
                    self.kill()  # Supprime le sprite du groupe
                self.attack_in_progress = False
                self.attacking = False
                self.taking_damage = False
                self.current_frame = 0

            frame = frames[int(self.current_frame)].copy()
            if self.direction == "left":
                frame = pygame.transform.flip(frame, True, False)
            self.image = frame

        # --- Limite l'écran ---
        self.rect.clamp_ip(pygame.Rect(0, 0, self.screen_width, self.screen_height))

    def draw(self, surface):
        if self.alive or self.dying:
            surface.blit(self.image, self.rect)

