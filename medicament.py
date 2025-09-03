import pygame
import math

class Medicament(pygame.sprite.Sprite):
    def __init__(self, x, y, player, screen_width, screen_height):
        super().__init__()
        pygame.mixer.init()  # Initialiser le mixer pour le son
        # Surface avec canal alpha pour gérer la transparence
        self.surf = pygame.Surface((30, 30), pygame.SRCALPHA)
        
        self.color_close = (255, 105, 180)  # Rose si proche
        self.color_far = (128, 0, 128)      # Violet si loin
        self.rect = self.surf.get_rect(center=(x, y))
        self.player = player
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.activation_distance = 200
        self.collected = False  # état du médicament
        
        # Charger le son de collecte
        self.collect_sound = pygame.mixer.Sound('bruitages/sharp-pop-328170.mp3')
        
    def update(self):
        if self.collected:
            return  # Ne rien faire si déjà ramassé
        
        # Calcul distance au joueur
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        distance = math.hypot(dx, dy)

        # Calcul alpha (opacité) entre 0 (invisible loin) et 255 (visible proche)
        alpha = max(0, min(255, int(255 * (self.activation_distance - distance) / self.activation_distance)))

        # Déterminer couleur selon distance (close ou far)
        color = self.color_close if distance < self.activation_distance else self.color_far
        
        # Remplir la surface avec la couleur et l’alpha
        self.surf.fill(color + (alpha,))  # (R, G, B, Alpha)
        
    def draw(self, surface):
        if not self.collected and self.surf.get_alpha() != 0:  # Ne pas dessiner si ramassé ou invisible
            surface.blit(self.surf, self.rect)
            
    def collect(self):
        if not self.collected:
            self.collected = True
            self.collect_sound.play()  # Jouer le son de collecte

