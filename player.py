import pygame
from pygame.locals import *

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, screen_width=1024, screen_height=700,
                 walk_spritesheet_path=None, idle_spritesheet_path=None,
                 attack_spritesheet_path=None, hurt_spritesheet_path=None,
                 death_spritesheets=None, frame_width=50, frame_height=50):
        super().__init__()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.speed = 3.5

        # Direction et état
        self.direction = "right"
        self.state = "idle"  # idle, walk, attack, hurt, dead
        self.moving = False
        self.health = 3

        # Spritesheets
        self.walk_frames = self.load_frames(walk_spritesheet_path, frame_width, frame_height) if walk_spritesheet_path else []
        self.idle_frames = self.load_frames(idle_spritesheet_path, frame_width, frame_height) if idle_spritesheet_path else []
        self.attack_frames = self.load_frames(attack_spritesheet_path, frame_width, frame_height) if attack_spritesheet_path else []
        self.hurt_frames = self.load_frames(hurt_spritesheet_path, frame_width, frame_height) if hurt_spritesheet_path else []
        self.death_frames = []
        if death_spritesheets:
            for path in death_spritesheets:
                self.death_frames.append(self.load_frames(path, frame_width, frame_height))

        # Animation
        self.current_frame = 0
        self.animation_speed = 0.15

        # Image initiale
        if self.idle_frames:
            self.image = self.idle_frames[0].copy()
        else:
            self.image = pygame.Surface((50, 50))
            self.image.fill((0, 128, 255))

        self.rect = self.image.get_rect(center=(x, y))

        # Cooldowns et timers
        self.attack_cooldown = 500  # ms
        self.last_attack_time = 0
        self.hurt_timer = 0

        # Joystick
        pygame.joystick.init()
        self.joystick = pygame.joystick.Joystick(0) if pygame.joystick.get_count() > 0 else None
        if self.joystick:
            self.joystick.init()

    def load_frames(self, path, frame_width, frame_height, scale=2):
        sheet = pygame.image.load(path).convert_alpha()
        frames = []
        sheet_width = sheet.get_width()
        sheet_height = sheet.get_height()
        for y in range(0, sheet_height, frame_height):
            for x in range(0, sheet_width, frame_width):
                frame = sheet.subsurface(pygame.Rect(x, y, frame_width, frame_height))
                frame = pygame.transform.scale(frame, (frame_width*scale, frame_height*scale))
                frames.append(frame)
        return frames

    def take_damage(self, amount):
        if self.state != "dead" and self.state != "hurt":
            self.health -= amount
            if self.health <= 0:
                self.state = "dead"
                self.current_frame = 0
            else:
                self.state = "hurt"
                self.current_frame = 0
                self.hurt_timer = pygame.time.get_ticks()

    def attack(self):
        now = pygame.time.get_ticks()
        if now - self.last_attack_time >= self.attack_cooldown and self.state not in ["attack", "hurt", "dead"]:
            self.state = "attack"
            self.current_frame = 0
            self.last_attack_time = now

    def update(self, keys, walls):
        dx = dy = 0
        self.moving = False

        # --- Gestion attaque ---
        if keys[K_SPACE]:
            self.attack()

        # Si attaque ou mort, le joueur ne bouge pas
        if self.state in ["attack", "hurt", "dead"]:
            self.animate()
            return

        # --- Clavier ---

        if keys[K_UP] or keys[K_z]:
            dy = -self.speed
            self.moving = True
        if keys[K_DOWN] or keys[K_s]:
            dy = self.speed
            self.moving = True
        if keys[K_LEFT] or keys[K_q]:
            dx = -self.speed
            self.direction = "left"
            self.moving = True
        if keys[K_RIGHT] or keys[K_d]:
            dx = self.speed
            self.direction = "right"
            self.moving = True


        # --- Joystick ---
        if self.joystick:
            axis_x = self.joystick.get_axis(0)
            axis_y = self.joystick.get_axis(1)
            deadzone = 0.2
            if abs(axis_x) > deadzone:
                dx = axis_x * self.speed
                self.direction = "right" if dx > 0 else "left"
                self.moving = True
            if abs(axis_y) > deadzone:
                dy = axis_y * self.speed
                self.moving = True

        # Déplacement et collisions
        self.rect.x += dx
        for wall in walls:
            if self.rect.colliderect(wall):
                if dx > 0: self.rect.right = wall.left
                elif dx < 0: self.rect.left = wall.right
        self.rect.y += dy
        for wall in walls:
            if self.rect.colliderect(wall):
                if dy > 0: self.rect.bottom = wall.top
                elif dy < 0: self.rect.top = wall.bottom

        # Limites écran
        self.rect.clamp_ip(pygame.Rect(0, 0, self.screen_width, self.screen_height))

        # Animation selon mouvement
        self.state = "walk" if self.moving else "idle"
        self.animate()

    def animate(self):
        if self.state == "idle":
            frames = self.idle_frames
        elif self.state == "walk":
            frames = self.walk_frames
        elif self.state == "attack":
            frames = self.attack_frames
        elif self.state == "hurt":
            frames = self.hurt_frames
            # Revenir à idle après 300ms
            if pygame.time.get_ticks() - self.hurt_timer > 300:
                self.state = "idle"
                self.current_frame = 0
        elif self.state == "dead":
            # Choisir une des deux animations de mort
            frames = self.death_frames[0] if self.direction == "right" else self.death_frames[1]
        else:
            frames = self.idle_frames

        if frames:
            self.current_frame += self.animation_speed
            if self.current_frame >= len(frames):
                if self.state == "attack":
                    self.state = "idle"
                if self.state == "dead":
                    self.current_frame = len(frames) - 1  # figer sur dernière frame
                else:
                    self.current_frame = 0
            frame = frames[int(self.current_frame)].copy()
            if self.direction == "left":
                frame = pygame.transform.flip(frame, True, False)
            self.image = frame

    def draw(self, surface):
        surface.blit(self.image, self.rect)

