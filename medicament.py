import pygame
import math

class Medicament(pygame.sprite.Sprite):
    def __init__(self, x, y, player, screen_width, screen_height, spritesheet_path="potion/PotionBlue.png", frame_width=22, frame_height=37):
        super().__init__()
        pygame.mixer.init()  # Initialiser le mixer pour le son
        # Surface avec canal alpha pour gérer la transparence
        self.surf = pygame.Surface((30, 30), pygame.SRCALPHA)

        self.player = player
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.activation_distance = 200
        self.collected = False  # état du médicament
        
        # Charger le son de collecte
        self.collect_sound = pygame.mixer.Sound('bruitages/sharp-pop-328170.mp3')
        pygame.mixer.music.set_volume(0.2)
        self.animation = self.load_frames(spritesheet_path)

        # Animation
        self.current_frame = 0
        self.animation_speed = 0.2

        # Image initiale
        self.image = self.animation[0].copy()
        self.rect = self.image.get_rect(center=(x, y))

    def load_frames(self, path):
        sheet = pygame.image.load(path).convert_alpha()
        frames = []
        sheet_width = sheet.get_width()
        sheet_height = sheet.get_height()
        for y in range(0, sheet_height, self.frame_height):
            for x in range(0, sheet_width, self.frame_width):
                frames.append(sheet.subsurface(pygame.Rect(x, y, self.frame_width, self.frame_height)))
        return frames

        
    def update(self):
        if self.collected:
            return  # Ne rien faire si déjà ramassé
        
        # Calcul distance au joueur
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        distance = math.hypot(dx, dy)

        # Calcul alpha (opacité) entre 0 (invisible loin) et 255 (visible proche)
        alpha = max(0, min(255, int(255 * (self.activation_distance - distance) / self.activation_distance)))

        frames = self.animation

        if frames: 
            self.current_frame += self.animation_speed
            if self.current_frame >= len(frames):
                self.current_frame = 0
            frame = frames[int(self.current_frame)].copy()
            self.image = frame
            self.image.set_alpha(alpha)


    def draw(self, surface):
        if not self.collected and self.surf.get_alpha() != 0:  # Ne pas dessiner si ramassé ou invisible
            surface.blit(self.image, self.rect)
            
    def collect(self):
        if not self.collected:
            self.collected = True
            self.collect_sound.play()  # Jouer le son de collecte

