import pygame

class InfoHUD:
    """
    Classe représentant l'interface HUD (Head-Up Display) pour afficher les informations
    du joueur telles que le nombre de vies restantes et les médicaments collectés.
    """

    def __init__(self, max_lives=3, current_lives=None):
        """
        Initialise l'HUD.

        Args:
            max_lives (int): Nombre maximal de vies du joueur.
            current_lives (int, optional): Nombre actuel de vies. Si None, on prend max_lives.
        """
        self.max_lives = max_lives
        self.lives_left = current_lives if current_lives is not None else max_lives
        self.meds_collected = 0

        # Couleurs des cœurs
        self.heart_red = (220, 20, 60)    # cœur plein
        self.heart_green = (50, 205, 50)  # cœur vide

        # Police pour afficher le nombre de médicaments
        self.font = pygame.font.SysFont(None, 32)

    def set_lives(self, lives):
        """
        Définit directement le nombre de vies actuelles.

        Args:
            lives (int): Nombre de vies du joueur (entre 0 et max_lives).
        """
        self.lives_left = max(0, min(lives, self.max_lives))

    def lose_life(self):
        """
        Diminue le nombre de vies de 1, si possible.
        """
        if self.lives_left > 0:
            self.lives_left -= 1

    def gain_life(self):
        """
        Augmente le nombre de vies de 1, sans dépasser le maximum.
        """
        if self.lives_left < self.max_lives:
            self.lives_left += 1

    def add_med(self):
        """
        Incrémente le compteur de médicaments collectés.
        """
        self.meds_collected += 1

    def draw(self, screen):
        """
        Dessine le HUD à l'écran.

        Args:
            screen (pygame.Surface): Surface sur laquelle dessiner le HUD.
        """
        # Dessin des cœurs représentant les vies
        for i in range(self.max_lives):
            # Si i < lives_left → cœur plein, sinon cœur vide
            color = self.heart_red if i < self.lives_left else self.heart_green
            self.draw_heart(screen, 30 + i * 40, 30, 30, color)

        # Affichage du nombre de médicaments collectés
        txt = self.font.render(f"Médicaments : {self.meds_collected}", True, (10, 10, 10))
        screen.blit(txt, (30, 70))

    def draw_heart(self, surface, x, y, size, color):
        """
        Dessine un cœur stylisé à une position donnée.

        Args:
            surface (pygame.Surface): Surface sur laquelle dessiner.
            x (int): Coordonnée x du centre du cœur.
            y (int): Coordonnée y du centre du cœur.
            size (int): Taille globale du cœur.
            color (tuple): Couleur du cœur (R, G, B).
        """
        r = size // 2

        # Dessiner les deux cercles supérieurs du cœur
        pygame.draw.circle(surface, color, (x - r // 2, y), r // 2)
        pygame.draw.circle(surface, color, (x + r // 2, y), r // 2)

        # Dessiner le triangle inférieur du cœur
        points = [(x - r, y), (x + r, y), (x, y + r + 6)]
        pygame.draw.polygon(surface, color, points)

