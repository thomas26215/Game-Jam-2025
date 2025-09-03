import pygame

class InfoHUD:
    def __init__(self, max_lives=3):
        self.max_lives = max_lives
        self.lives_left = max_lives
        self.meds_collected = 0
        self.heart_red = (220, 20, 60)
        self.heart_green = (50, 205, 50)
        self.font = pygame.font.SysFont(None, 32)

    def lose_life(self):
        if self.lives_left > 0:
            self.lives_left -= 1

    def add_med(self):
        self.meds_collected += 1

    def draw(self, screen):
        # Dessin des cœurs
        for i in range(self.max_lives):
            color = self.heart_red if i < self.lives_left else self.heart_green
            self.draw_heart(screen, 30 + i * 40, 30, 30, color)
        # Affichage des médicaments récupérés
        txt = self.font.render(f"Médicaments : {self.meds_collected}", True, (10,10,10))
        screen.blit(txt, (30, 70))

    def draw_heart(self, surface, x, y, size, color):
        r = size // 2
        # Deux cercles
        pygame.draw.circle(surface, color, (x - r//2, y), r//2)
        pygame.draw.circle(surface, color, (x + r//2, y), r//2)
        # Triangle bas
        points = [(x - r, y), (x + r, y), (x, y + r + 6)]
        pygame.draw.polygon(surface, color, points)

# --- Exemple d'utilisation dans la boucle principale ---

# pygame.init()
# screen = pygame.display.set_mode((400, 150))
# hud = InfoHUD()
# hud.draw(screen)
# pygame.display.flip()

