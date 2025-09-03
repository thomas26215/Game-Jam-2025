import pygame

class InfoHUD:
    """
    Classe représentant l'interface HUD (Head-Up Display) pour afficher
    les informations du joueur, comme les vies (cœurs) et les médicaments collectés.
    """

    def __init__(self, max_lives=5, current_lives=None):
        """
        Initialise l'HUD.

        Args:
            max_lives (int): Nombre maximal de vies du joueur.
            current_lives (int, optional): Vies actuelles. Si None, prend max_lives.
        """
        self.max_lives = max_lives
        self.lives_left = current_lives if current_lives is not None else max_lives
        self.meds_collected = 0

        # Couleurs des cœurs
        self.heart_full_color = (220, 20, 60)    # cœur plein (rouge)
        self.heart_empty_color = (50, 205, 50)   # cœur vide (vert)

        # Police pour afficher les médicaments
        self.font = pygame.font.SysFont(None, 32)

    def set_lives(self, lives):
        """Définit directement le nombre de vies actuelles."""
        self.lives_left = max(0, min(lives, self.max_lives))

    def lose_life(self):
        """Diminue le nombre de vies de 1 si possible."""
        if self.lives_left > 0:
            self.lives_left -= 1

    def gain_life(self):
        """Augmente le nombre de vies de 1 sans dépasser le maximum."""
        if self.lives_left < self.max_lives:
            self.lives_left += 1

    def add_med(self):
        """Incrémente le compteur de médicaments collectés."""
        self.meds_collected += 1

    def draw(self, screen):
        """Dessine l'HUD avec les cœurs."""
        for i in range(self.max_lives):
            color = self.heart_full_color if i < self.lives_left else self.heart_empty_color
            self.draw_heart(screen, 30 + i * 40, 30, 30, color)

        # Affichage du nombre de médicaments
        txt = self.font.render(f"Médicaments : {self.meds_collected}", True, (10, 10, 10))
        screen.blit(txt, (30, 70))

    def draw_heart(self, surface, x, y, size, color):
        """Dessine un cœur stylisé."""
        r = size // 2
        # Cercles supérieurs
        pygame.draw.circle(surface, color, (x - r // 2, y), r // 2)
        pygame.draw.circle(surface, color, (x + r // 2, y), r // 2)
        # Triangle inférieur
        points = [(x - r, y), (x + r, y), (x, y + r + 6)]
        pygame.draw.polygon(surface, color, points)

