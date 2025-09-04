import pygame

class Portail:
    def __init__(self, x, y, width=None, height=None):
        """
        Initialise un portail à une position donnée.
        
        :param x: Position horizontale
        :param y: Position verticale
        :param width: Largeur optionnelle pour redimensionner
        :param height: Hauteur optionnelle pour redimensionner
        """
        # Charger l'image APRÈS pygame.init() et pygame.display.set_mode()
        self.image = pygame.image.load("portail.png").convert_alpha()
        
        # Redimensionner si besoin
        if width and height:
            self.image = pygame.transform.scale(self.image, (width, height))
        
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self, surface):
        """
        Affiche le portail sur la surface donnée.
        
        :param surface: La surface pygame où dessiner le portail
        """
        surface.blit(self.image, self.rect)

