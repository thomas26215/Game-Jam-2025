import pygame
from pygame.locals import *

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, screen_width=1024, screen_height=700,
                 walk_spritesheet_path=None, idle_spritesheet_path=None,
                 frame_width=50, frame_height=50):
        super().__init__()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.speed = 3.5

        # Direction et état
        self.direction = "right"  # "left" ou "right"
        self.moving = False

        # Spritesheets
        self.walk_frames = []
        self.idle_frames = []

        if walk_spritesheet_path:
            self.walk_frames = self.load_frames(walk_spritesheet_path, frame_width, frame_height)
        if idle_spritesheet_path:
            self.idle_frames = self.load_frames(idle_spritesheet_path, frame_width, frame_height)

        # Animation
        self.current_frame = 0
        self.animation_speed = 0.1

        # Image initiale
        if self.idle_frames:
            self.image = self.idle_frames[0].copy()
        elif self.walk_frames:
            self.image = self.walk_frames[0].copy()
        else:
            self.image = pygame.Surface((50, 50))
            self.image.fill((0, 128, 255))

        self.rect = self.image.get_rect(center=(x, y))

        # Initialiser joystick
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
                # Redimensionner le frame
                frame = pygame.transform.scale(frame, (frame_width*scale, frame_height*scale))
                frames.append(frame)
        return frames


    def update(self, keys, walls):
        dx = dy = 0
        self.moving = False

        # ----- Clavier -----
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

        # ----- Manette (joystick) -----
        if self.joystick:
            axis_x = self.joystick.get_axis(0)  # gauche/droite
            axis_y = self.joystick.get_axis(1)  # haut/bas
            deadzone = 0.2  # éviter les mouvements involontaires
            if abs(axis_x) > deadzone:
                dx = axis_x * self.speed
                self.direction = "right" if dx > 0 else "left"
                self.moving = True
            if abs(axis_y) > deadzone:
                dy = axis_y * self.speed
                self.moving = True

        # Déplacement horizontal
        self.rect.x += dx
        for wall in walls:
            if self.rect.colliderect(wall):
                if dx > 0:
                    self.rect.right = wall.left
                elif dx < 0:
                    self.rect.left = wall.right

        # Déplacement vertical
        self.rect.y += dy
        for wall in walls:
            if self.rect.colliderect(wall):
                if dy > 0:
                    self.rect.bottom = wall.top
                elif dy < 0:
                    self.rect.top = wall.bottom

        # Limites écran
        self.rect.clamp_ip(pygame.Rect(0, 0, self.screen_width, self.screen_height))

        # Choisir les frames selon état
        frames_to_use = self.walk_frames if self.moving else self.idle_frames
        if frames_to_use:
            self.current_frame += self.animation_speed
            if self.current_frame >= len(frames_to_use):
                self.current_frame = 0
            frame = frames_to_use[int(self.current_frame)].copy()

            # Flip horizontal si gauche
            if self.direction == "left":
                frame = pygame.transform.flip(frame, True, False)

            self.image = frame

    def draw(self, surface):
        surface.blit(self.image, self.rect)

