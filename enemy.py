import pygame
import math
import random
import os

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, player, screen_width, screen_height,
                 sprites_folder,
                 resurrected_sprites_folder=None,
                 base_health=2,
                 frame_width=64, frame_height=64,
                 activation_distance=100, speed_close=1.5,
                 speed_far=0.75, attack_range=1,
                 attack_damage=1, obstacles=None,
                 is_final_scene=False):
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
        self.health = base_health
        self.base_health = base_health
        self.taking_damage = False
        self.current_frame = 0
        self.damage_applied = False
        self.attacking = False
        self.attack_in_progress = False
        self.direction = "right"
        self.obstacles = obstacles if obstacles else []
        self.animation_speed = 0.2
        self.attack_animation_speed = 0.10
        self.hit_animation_speed = 0.15
        self.death_animation_speed = 0.1
        self.walk_frames = self.load_frames_from_folder(sprites_folder, "Walk")
        self.attack_frames = self.load_frames_from_folder(sprites_folder, "Attack")
        self.hit_frames = self.load_frames_from_folder(sprites_folder, "Hurt")
        self.death_frames = self.load_frames_from_folder(sprites_folder, "Dead")
        self.resurrected_frames = self.load_frames_from_folder(resurrected_sprites_folder, "Walk") if resurrected_sprites_folder else self.walk_frames

        # Image initiale
        if self.health < 0:
            self.image = self.resurrected_frames[0].copy() if self.resurrected_frames else pygame.Surface((frame_width, frame_height))
        elif self.health > 0:
            self.image = self.walk_frames[0].copy() if self.walk_frames else pygame.Surface((frame_width, frame_height))
        else:
            self.image = self.death_frames[0].copy() if self.death_frames else pygame.Surface((frame_width, frame_height))

        self.rect = self.image.get_rect(center=(x, y))
        hitbox_width = int(self.rect.width * 0.3)
        hitbox_height = int(self.rect.height * 0.4)
        self.hitbox = pygame.Rect(
            self.rect.centerx - hitbox_width // 2,
            self.rect.centery - hitbox_height // 2,
            hitbox_width,
            hitbox_height
        )
        self.random_dx = 0
        self.random_dy = 0
        self.direction_timer = 0
        self.is_final_scene = is_final_scene

    def load_frames_from_folder(self, folder, action_name):
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
        if self.health == 0:
            return
        self.health -= damage
        self.current_frame = 0
        self.taking_damage = self.health > 0
        self.attacking = False
        self.attack_in_progress = False
        self.damage_applied = False

    def animate(self, frames, anim_speed, flip=False, attack_hitbox_check=False):
        """Animation générique pour l'ennemi."""
        if not frames:
            return

        # Avancer l'animation
        self.current_frame += anim_speed
        if self.current_frame >= len(frames):
            self.current_frame = 0
            if self.attack_in_progress:
                self.attack_in_progress = False
                self.attacking = False
            if self.taking_damage:
                self.taking_damage = False

        frame = frames[int(self.current_frame)].copy()

        # Flip si nécessaire
        if flip and self.direction == "left":
            frame = pygame.transform.flip(frame, True, False)

        self.image = frame

        # Vérification d'attaque
        if attack_hitbox_check and self.attack_in_progress and not self.damage_applied:
            if int(self.current_frame) == 3:  # frame clé de l'attaque
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

    def final_scene(self):
        """Scène finale : uniquement marche."""
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        dx = center_x - self.hitbox.centerx
        dy = center_y - self.hitbox.centery
        distance = math.hypot(dx, dy)

        if distance > 1:
            # Avancer vers le centre
            norm_dx, norm_dy = dx / distance, dy / distance
            self.hitbox.x += norm_dx * self.speed_close
            self.hitbox.y += norm_dy * self.speed_close
            self.direction = "right" if norm_dx >= 0 else "left"
        else:
            # Une fois arrivé au centre -> disparition
            self.image.set_alpha(0)
            return

        self.rect.center = self.hitbox.center
        self.animate(self.walk_frames, self.animation_speed, flip=True)


    def update(self, current_room):
        if self.health == 0:
            return

        # Scène finale
        if self.is_final_scene:
            self.final_scene()
            return

        # Déplacement et comportement
        dx = self.player.hitbox.centerx - self.hitbox.centerx
        dy = self.player.hitbox.centery - self.hitbox.centery
        distance = math.hypot(dx, dy)

        if self.health < 0:  # ressuscité
            self.attacking = False
            self.attack_in_progress = False
            self.direction_timer -= 1
            if self.direction_timer <= 0:
                angle = random.uniform(0, math.pi * 2)
                self.random_dx = math.cos(angle)
                self.random_dy = math.sin(angle)
                self.direction_timer = random.randint(30, 90)
            dx_norm, dy_norm = self.random_dx, self.random_dy
            speed = self.speed_close
        else:
            if not self.attack_in_progress and distance <= self.attack_range:
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
            else:
                dx_norm, dy_norm = 0, 0
                speed = 0

        # Déplacement et collisions
        self.hitbox.x += dx_norm * speed
        self.hitbox.y += dy_norm * speed
        for obs in current_room.obstacles:
            if self.hitbox.colliderect(obs):
                if dx_norm > 0:
                    self.hitbox.right = obs.left
                elif dx_norm < 0:
                    self.hitbox.left = obs.right
                if dy_norm > 0:
                    self.hitbox.bottom = obs.top
                elif dy_norm < 0:
                    self.hitbox.top = obs.bottom

        self.rect.center = self.hitbox.center
        self.direction = "right" if dx >= 0 else "left"

        # Choix des frames
        if self.health < 0:
            frames = self.resurrected_frames
            anim_speed = self.animation_speed
            check_attack = False
        elif self.health == 0:
            frames = self.death_frames
            anim_speed = self.death_animation_speed
            check_attack = False
        elif self.taking_damage:
            frames = self.hit_frames
            anim_speed = self.hit_animation_speed
            check_attack = False
        elif self.attack_in_progress:
            frames = self.attack_frames
            anim_speed = self.attack_animation_speed
            check_attack = True
        else:
            frames = self.walk_frames
            anim_speed = self.animation_speed
            check_attack = False

        self.animate(frames, anim_speed, flip=True, attack_hitbox_check=check_attack)

        # Clamp pour rester dans l'écran
        self.rect.clamp_ip(pygame.Rect(0, 0, self.screen_width, self.screen_height))
        self.hitbox.center = self.rect.center

    def draw(self, surface):
        if self.health != 0:
            surface.blit(self.image, self.rect)

