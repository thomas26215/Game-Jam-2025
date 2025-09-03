import pygame
from pygame.locals import *

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, screen_width=1024, screen_height=700,
                 walk_spritesheet_path=None, idle_spritesheet_path=None,
                 attack_spritesheet_path=None, hurt_spritesheet_path=None,
                 death1_spritesheet_path=None, death2_spritesheet_path=None,
                 frame_width=50, frame_height=50):
        super().__init__()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.speed = 3.5

        # Direction et état
        self.direction = "right"
        self.state = "idle"  # idle, walk, attack, hurt, death1, death2
        self.moving = False

        # Charger toutes les animations
        self.animations = {
            "walk": self.load_frames(walk_spritesheet_path, frame_width, frame_height) if walk_spritesheet_path else [],
            "idle": self.load_frames(idle_spritesheet_path, frame_width, frame_height) if idle_spritesheet_path else [],
            "attack": self.load_frames(attack_spritesheet_path, frame_width, frame_height) if attack_spritesheet_path else [],
            "hurt": self.load_frames(hurt_spritesheet_path, frame_width, frame_height) if hurt_spritesheet_path else [],
            "death1": self.load_frames(death1_spritesheet_path, frame_width, frame_height) if death1_spritesheet_path else [],
            "death2": self.load_frames(death2_spritesheet_path, frame_width, frame_height) if death2_spritesheet_path else [],
        }

        # Image de base
        self.image = self.animations["idle"][0] if self.animations["idle"] else pygame.Surface((50, 50))
        self.rect = self.image.get_rect(center=(x, y))

        # Hitbox réduite
        hitbox_width = self.rect.width * 0.6
        hitbox_height = self.rect.height * 0.8
        self.hitbox = pygame.Rect(0, 0, hitbox_width, hitbox_height)
        self.hitbox.center = self.rect.center

        # Animation
        self.current_frame = 0
        self.animation_speed = 0.15
        self.attacking = False

        # Joystick
        pygame.joystick.init()
        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()

    def load_frames(self, path, frame_width, frame_height, scale=2):
        sheet = pygame.image.load(path).convert_alpha()
        frames = []
        sheet_width = sheet.get_width()
        sheet_height = sheet.get_height()
        for y in range(0, sheet_height, frame_height):
            for x in range(0, sheet_width, frame_width):
                frame = sheet.subsurface(pygame.Rect(x, y, frame_width, frame_height))
                frame = pygame.transform.scale(frame, (frame_width * scale, frame_height * scale))
                frames.append(frame)
        return frames

    def handle_input(self, keys):
        if self.state in ["attack", "hurt", "death1", "death2"]:
            return 0, 0  # Pas de déplacement pendant ces animations

        dx = dy = 0
        self.moving = False

        if keys[K_UP]:
            dy = -self.speed
            self.moving = True
        if keys[K_DOWN]:
            dy = self.speed
            self.moving = True
        if keys[K_LEFT]:
            dx = -self.speed
            self.direction = "left"
            self.moving = True
        if keys[K_RIGHT]:
            dx = self.speed
            self.direction = "right"
            self.moving = True

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

        return dx, dy

    def update(self, keys, walls):
        # Lancer attaque
        if keys[K_SPACE] and not self.attacking and self.state not in ["hurt", "death1", "death2"]:
            self.state = "attack"
            self.attacking = True
            self.current_frame = 0

        dx, dy = self.handle_input(keys)

        # Déplacement seulement si pas d'attaque/dégât/mort
        if self.state not in ["attack", "hurt", "death1", "death2"]:
            self.hitbox.x += dx
            for wall in walls:
                if self.hitbox.colliderect(wall):
                    if dx > 0:
                        self.hitbox.right = wall.left
                    elif dx < 0:
                        self.hitbox.left = wall.right

            self.hitbox.y += dy
            for wall in walls:
                if self.hitbox.colliderect(wall):
                    if dy > 0:
                        self.hitbox.bottom = wall.top
                    elif dy < 0:
                        self.hitbox.top = wall.bottom

        self.hitbox.clamp_ip(pygame.Rect(0, 0, self.screen_width, self.screen_height))
        self.rect.center = self.hitbox.center

        # Déterminer l'état si pas d'attaque/dégât/mort
        if self.state not in ["attack", "hurt", "death1", "death2"]:
            self.state = "walk" if self.moving else "idle"

        self.animate()

    def animate(self):
        frames = self.animations.get(self.state, [])
        if not frames:
            return

        self.current_frame += self.animation_speed
        if self.current_frame >= len(frames):
            if self.state in ["attack", "hurt"]:
                self.state = "idle"
                self.attacking = False
                self.current_frame = 0
            elif self.state in ["death1", "death2"]:
                self.current_frame = len(frames) - 1  # Rester sur la dernière frame
            else:
                self.current_frame = 0

        frame = frames[int(self.current_frame)].copy()
        if self.direction == "left":
            frame = pygame.transform.flip(frame, True, False)
        self.image = frame

    def take_damage(self):
        if self.state not in ["death1", "death2"]:
            self.state = "hurt"
            self.current_frame = 0

    def die(self, type=1):
        self.state = f"death{type}"
        self.current_frame = 0

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        # pygame.draw.rect(surface, (255, 0, 0), self.hitbox, 2)

