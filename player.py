import pygame
from config import COLLECT_MEDECINE, HEAL_INFECTED
from pygame.locals import *
from infos_hud import InfoHUD

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, settings, screen_width=1024, screen_height=700,
                 walk_spritesheet_path=None, idle_spritesheet_path=None,
                 attack_spritesheet_path=None, hurt_spritesheet_path=None,
                 death_spritesheets=None, frame_width=50, frame_height=50,
                 throw_spritesheet_path=None, hud=None):
        super().__init__()
        self.settings = settings
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.speed = 3.5
        self.direction = "right"
        self.state = "idle"
        self.moving = False
        self.health = 3
        self.attack_rect = None
        self.has_hit_enemy = False  
        self.hud = hud  

        # Chargement des animations
        self.walk_frames = self.load_frames(walk_spritesheet_path, frame_width, frame_height) if walk_spritesheet_path else []
        self.idle_frames = self.load_frames(idle_spritesheet_path, frame_width, frame_height) if idle_spritesheet_path else []
        self.attack_frames = self.load_frames(attack_spritesheet_path, frame_width, frame_height) if attack_spritesheet_path else []
        self.hurt_frames = self.load_frames(hurt_spritesheet_path, frame_width, frame_height) if hurt_spritesheet_path else []
        self.throw_frames = self.load_frames(throw_spritesheet_path, frame_width, frame_height) if throw_spritesheet_path else []
        self.death_frames = []
        if death_spritesheets:
            for path in death_spritesheets:
                self.death_frames.append(self.load_frames(path, frame_width, frame_height))

        self.current_frame = 0
        self.animation_speed = 0.15

        # Image par défaut
        if self.idle_frames:
            self.image = self.idle_frames[0].copy()
        else:
            self.image = pygame.Surface((50, 50))
            self.image.fill((0, 128, 255))

        self.rect = self.image.get_rect(center=(x, y))
        self.hitbox = self.rect.copy()
        self.hitbox.inflate_ip(-90, -75)

        # Cooldowns
        self.attack_cooldown = 500  
        self.last_attack_time = 0
        self.throw_cooldown = 800  
        self.last_throw_time = 0

        self.hurt_timer = 0

        # Joystick
        pygame.joystick.init()
        self.joystick = pygame.joystick.Joystick(0) if pygame.joystick.get_count() > 0 else None
        if self.joystick:
            self.joystick.init()

    def load_frames(self, path, frame_width, frame_height, scale=2):
        """Charge une spritesheet et découpe les frames."""
        try:
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
        except pygame.error as e:
            return []
        except FileNotFoundError:
            return []

    def take_damage(self, amount):
        """Inflige des dégâts au joueur."""
        if self.state not in ["dead", "hurt"]:
            self.health -= amount
            if self.health <= 0:
                self.state = "dead"
                self.current_frame = 0
            else:
                self.state = "hurt"
                self.current_frame = 0
                self.hurt_timer = pygame.time.get_ticks()

    def attack(self, attack_type):
        """
        Déclenche une attaque.
        attack_type == 1 → attaque classique
        attack_type != 1 → lancer de potion
        """
        now = pygame.time.get_ticks()

        if attack_type == COLLECT_MEDECINE:
            if now - self.last_attack_time >= self.attack_cooldown and self.state not in ["attack", "hurt", "dead", "throw"]:
                self.state = "attack"
                self.current_frame = 0
                self.last_attack_time = now
                self.has_hit_enemy = False  # Réinitialise l'attaque

                attack_rect = self.rect.copy()
                attack_rect.width += 30
                attack_rect.height += 20
                if self.direction == "right":
                    attack_rect.x += 20
                else:
                    attack_rect.x -= 20
                self.attack_rect = attack_rect

        # Lancer potion
        else:
            if now - self.last_throw_time >= self.throw_cooldown and self.state not in ["attack", "hurt", "dead", "throw"] and self.hud.use_med():
                self.state = "throw"
                self.current_frame = 0
                self.last_throw_time = now
                self.has_hit_enemy = False  # Réinitialise l'attaque pour le throw

                # ⚡ Crée un attack_rect sur le joueur comme pour l'attaque normale
                attack_rect = self.rect.copy()
                attack_rect.width += 40  # potion peut avoir une zone un peu plus grande
                attack_rect.height += 30
                if self.direction == "right":
                    attack_rect.x += 20
                else:
                    attack_rect.x -= 20
                self.attack_rect = attack_rect

    def update(self, keys, current_room):
        """Met à jour le joueur."""
        dx = dy = 0
        self.moving = False

        # Si animation spéciale
        if self.state in ["attack", "hurt", "dead", "throw"]:
            self.animate()
            return

        # Déplacements clavier
        if any(keys[key] for key in self.settings.get_control("move_up", "keyboard")):
            dy = -self.speed
            self.moving = True
        if any(keys[key] for key in self.settings.get_control("move_down", "keyboard")):
            dy = self.speed
            self.moving = True
        if any(keys[key] for key in self.settings.get_control("move_left", "keyboard")):
            dx = -self.speed
            self.direction = "left"
            self.moving = True
        if any(keys[key] for key in self.settings.get_control("move_right", "keyboard")):
            dx = self.speed
            self.direction = "right"
            self.moving = True

        # Déplacements manette
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

        # Collision + mouvement
        self.hitbox.x += dx
        for obs in current_room.obstacles:
            if self.hitbox.colliderect(obs):
                if dx > 0:
                    self.hitbox.right = obs.left
                elif dx < 0:
                    self.hitbox.left = obs.right
        self.hitbox.y += dy
        for obs in current_room.obstacles:
            if self.hitbox.colliderect(obs):
                if dy > 0:
                    self.hitbox.bottom = obs.top
                elif dy < 0:
                    self.hitbox.top = obs.bottom

        self.rect.center = self.hitbox.center
        self.state = "walk" if self.moving else "idle"
        self.animate()

    def animate(self):
        """Gère les animations du joueur."""
        if self.state == "idle":
            frames = self.idle_frames
        elif self.state == "walk":
            frames = self.walk_frames
        elif self.state == "attack":
            frames = self.attack_frames
        elif self.state == "hurt":
            frames = self.hurt_frames
            if pygame.time.get_ticks() - self.hurt_timer > 300:
                self.state = "idle"
                self.current_frame = 0
        elif self.state == "dead":
            frames = self.death_frames[0] if self.direction == "right" else self.death_frames[1]
        elif self.state == "throw":
            frames = self.throw_frames
        else:
            frames = self.idle_frames

        if not frames:
            return

        # Gestion spéciale attaque et lancer
        if self.state in ["attack", "throw"]:
            if int(self.current_frame) >= len(frames) - 1:
                self.image = frames[-1].copy()
                if self.direction == "left":
                    self.image = pygame.transform.flip(self.image, True, False)
                self.state = "idle"
                self.current_frame = 0
                return

        # Animation générale
        self.current_frame += self.animation_speed
        if self.current_frame >= len(frames):
            self.current_frame = 0

        self.image = frames[int(self.current_frame)].copy()
        if self.direction == "left":
            self.image = pygame.transform.flip(self.image, True, False)

    def draw(self, surface):
        """Affiche le joueur à l'écran."""
        surface.blit(self.image, self.rect)
        pygame.draw.rect(surface, (255, 0, 0), self.rect, 2)  # Hitbox rouge

