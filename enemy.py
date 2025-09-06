import pygame
import math
import random
import os

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, player, screen_width, screen_height,
                 sprites_folder,
                 resurrected_sprites_folder=None,
                 frame_width=64, frame_height=64,
                 activation_distance=100, speed_close=1.5, speed_far=0.75,
                 attack_range=1, attack_damage=1, obstacles=None,
                 alive=True, resurrected=False):
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

        # --- États de vie ---
        self.alive = alive
        self.dying = False
        self.resurrected = resurrected
        self.taking_damage = False

        # --- PV ---
        if self.resurrected:
            self.health = 3
            self.alive = True
        elif self.alive:
            self.health = 2
        else:
            self.health = 0
            self.dying = True

        # --- Animations ---
        self.walk_frames = self.load_frames_from_folder(sprites_folder, "Walk")
        self.attack_frames = self.load_frames_from_folder(sprites_folder, "Attack")
        self.hit_frames = self.load_frames_from_folder(sprites_folder, "Hurt")
        self.death_frames = self.load_frames_from_folder(sprites_folder, "Dead")
        self.resurrected_frames = self.load_frames_from_folder(resurrected_sprites_folder, "Walk") if resurrected_sprites_folder else self.walk_frames

        self.current_frame = 0
        self.animation_speed = 0.2
        self.attack_animation_speed = 0.10
        self.hit_animation_speed = 0.15
        self.death_animation_speed = 0.1

        if self.resurrected:
            self.image = self.resurrected_frames[0].copy() if self.resurrected_frames else pygame.Surface((frame_width, frame_height))
        elif self.alive:
            self.image = self.walk_frames[0].copy()
        else:
            self.image = self.death_frames[0].copy() if self.death_frames else pygame.Surface((frame_width, frame_height))

        self.rect = self.image.get_rect(center=(x, y))

        # --- Hitbox réduite ---
        hitbox_width = int(self.rect.width * 0.3)
        hitbox_height = int(self.rect.height * 0.4)
        self.hitbox = pygame.Rect(
            self.rect.centerx - hitbox_width // 2,
            self.rect.centery - hitbox_height // 2,
            hitbox_width,
            hitbox_height
        )

        # --- Mouvement ---
        self.random_dx = 0
        self.random_dy = 0
        self.direction_timer = 0
        self.attacking = False
        self.attack_in_progress = False
        self.direction = "right"
        self.damage_applied = False
        self.obstacles = obstacles if obstacles else []

    def load_frames_from_folder(self, folder, action_name):
        """Charge les frames d'une action depuis un spritesheet."""
        if not folder:
            return []
        path = os.path.join(folder, f"{action_name}.png")
        if not os.path.exists(path):
            return []
        sheet = pygame.image.load(path).convert_alpha()
        frames = []
        sheet_width = sheet.get_width()
        sheet_height = sheet.get_height()
        for y in range(0, sheet_height, self.frame_height):
            for x in range(0, sheet_width, self.frame_width):
                frames.append(sheet.subsurface(pygame.Rect(x, y, self.frame_width, self.frame_height)))
        return frames

    def take_damage(self, damage=1):
        """Réduit la vie et gère mort ou résurrection."""
        if self.resurrected or not self.alive or self.dying:
            return

        self.health -= damage

        if self.health <= 0:
            if self.health < 0:
                # Résurrection
                self.resurrected = True
                self.alive = True
                self.dying = False
                self.health = 3  # nouvelle vie en mode ressuscité
                self.current_frame = 0
            else:
                # Mort normale
                self.dying = True
                self.current_frame = 0
        else:
            # Animation de coup
            self.taking_damage = True
            self.current_frame = 0

    def update(self, current_room):
        if not self.alive and not self.dying and not self.resurrected:
            return

        # --- Ennemi normal ---
        if not self.dying and not self.taking_damage and not self.resurrected:
            dx = self.player.hitbox.centerx - self.hitbox.centerx
            dy = self.player.hitbox.centery - self.hitbox.centery
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

                # Collisions
                self.hitbox.x += dx_norm * speed
                for obs in current_room.obstacles:
                    if self.hitbox.colliderect(obs):
                        if dx_norm > 0: self.hitbox.right = obs.left
                        elif dx_norm < 0: self.hitbox.left = obs.right

                self.hitbox.y += dy_norm * speed
                for obs in current_room.obstacles:
                    if self.hitbox.colliderect(obs):
                        if dy_norm > 0: self.hitbox.bottom = obs.top
                        elif dy_norm < 0: self.hitbox.top = obs.bottom

                self.rect.center = self.hitbox.center
                self.direction = "right" if dx >= 0 else "left"

        # --- Mode ressuscité ---
        if self.resurrected and not self.dying:
            speed = self.speed_far
            self.direction_timer -= 1
            if self.direction_timer <= 0:
                angle = random.uniform(0, math.pi * 2)
                self.random_dx = math.cos(angle)
                self.random_dy = math.sin(angle)
                self.direction_timer = random.randint(30, 90)
            dx_norm, dy_norm = self.random_dx, self.random_dy

            self.hitbox.x += dx_norm * speed
            for obs in current_room.obstacles:
                if self.hitbox.colliderect(obs):
                    if dx_norm > 0: self.hitbox.right = obs.left
                    elif dx_norm < 0: self.hitbox.left = obs.right

            self.hitbox.y += dy_norm * speed
            for obs in current_room.obstacles:
                if self.hitbox.colliderect(obs):
                    if dy_norm > 0: self.hitbox.bottom = obs.top
                    elif dy_norm < 0: self.hitbox.top = obs.bottom

            self.rect.center = self.hitbox.center
            self.direction = "right" if dx_norm >= 0 else "left"

        # --- Choix des frames ---
        if self.resurrected:
            frames = self.resurrected_frames
            speed = self.animation_speed
        elif self.dying and self.death_frames:
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
                attack_hitbox = self.hitbox.copy()
                attack_hitbox.width = self.hitbox.width
                attack_hitbox.height = self.hitbox.height // 2
                if self.direction == "right":
                    attack_hitbox.x += self.hitbox.width // 2
                else:
                    attack_hitbox.x -= self.hitbox.width // 2
                attack_hitbox.y += self.hitbox.height // 4
                if attack_hitbox.colliderect(self.player.hitbox):
                    self.player.take_damage(self.attack_damage)
                    self.damage_applied = True

            if self.current_frame >= len(frames):
                if self.dying:
                    self.alive = False
                    self.kill()
                self.attack_in_progress = False
                self.attacking = False
                self.taking_damage = False
                self.current_frame = 0

            frame = frames[int(self.current_frame)].copy()
            if self.direction == "left":
                frame = pygame.transform.flip(frame, True, False)
            self.image = frame

        # --- Limiter à l’écran ---
        self.rect.clamp_ip(pygame.Rect(0, 0, self.screen_width, self.screen_height))
        self.hitbox.center = self.rect.center

    def draw(self, surface):
        if self.alive or self.dying or self.resurrected:
            surface.blit(self.image, self.rect)
            

