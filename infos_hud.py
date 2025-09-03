import pygame

class InfoHUD:
    """
    Classe représentant l'interface HUD (Head-Up Display) pour afficher
    les informations du joueur, comme la barre de vie et les médicaments collectés.
    """

    def __init__(self, max_health=100, current_health=None):
        """
        Initialise l'HUD.

        Args:
            max_health (int): Santé maximale du joueur.
            current_health (int, optional): Santé actuelle. Si None, prend max_health.
        """
        self.max_health = max_health
        self.current_health = current_health if current_health is not None else max_health
        self.meds_collected = 0

        # Couleurs
        self.health_bg_color = (50, 50, 50)     # arrière-plan de la barre
        self.health_fg_color = (220, 20, 60)    # barre de vie (rouge)
        self.font = pygame.font.SysFont(None, 32)

        # Dimensions de la barre
        self.bar_width = 200
        self.bar_height = 25
        self.bar_x = 30
        self.bar_y = 30

    def set_health(self, health):
        """Définit la santé actuelle (0 → max_health)."""
        self.current_health = max(0, min(health, self.max_health))

    def take_damage(self, amount):
        """Inflige des dégâts au joueur."""
        self.set_health(self.current_health - amount)

    def heal(self, amount):
        """Soigne le joueur."""
        self.set_health(self.current_health + amount)

    def add_med(self):
        """Incrémente le compteur de médicaments collectés."""
        self.meds_collected += 1

    def draw(self, screen):
        """Dessine l'HUD."""
        # Barre de fond
        pygame.draw.rect(screen, self.health_bg_color,
                         (self.bar_x, self.bar_y, self.bar_width, self.bar_height), border_radius=5)

        # Barre de vie proportionnelle
        health_ratio = self.current_health / self.max_health
        pygame.draw.rect(screen, self.health_fg_color,
                         (self.bar_x, self.bar_y, int(self.bar_width * health_ratio), self.bar_height),
                         border_radius=5)

        # Contour de la barre
        pygame.draw.rect(screen, (0, 0, 0),
                         (self.bar_x, self.bar_y, self.bar_width, self.bar_height), 2, border_radius=5)

        # Affichage des médicaments
        txt = self.font.render(f"Médicaments : {self.meds_collected}", True, (10, 10, 10))
        screen.blit(txt, (self.bar_x, self.bar_y + self.bar_height + 10))

