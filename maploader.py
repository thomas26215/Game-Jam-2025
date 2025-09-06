import os
import pygame
import pytmx

from config import SCREEN_HEIGHT, SCREEN_WIDTH


class MapLoader:
    """Charge un fichier TMX et extrait les obstacles."""
    def __init__(self):
        self.tmx_data = None
        self.width = 0
        self.height = 0
        self.obstacles = []

    def load(self, tmx_file):
        """Charge le TMX uniquement si le fichier existe."""
        if not tmx_file or not os.path.exists(tmx_file):
            self.tmx_data = None
            self.obstacles = []
            self.width = SCREEN_WIDTH
            self.height = SCREEN_HEIGHT
            return

        #print(f"Tentative de chargement du TMX : {tmx_file}")
        self.tmx_data = pytmx.load_pygame(tmx_file)
        self.width = self.tmx_data.width * self.tmx_data.tilewidth
        self.height = self.tmx_data.height * self.tmx_data.tileheight
        self.obstacles = self._load_obstacles()

    def _load_obstacles(self):
        obstacles = []
        if not self.tmx_data:
            return obstacles
        for layer in self.tmx_data.layers:
            if isinstance(layer, pytmx.TiledObjectGroup):
                for obj in layer:
                    rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                    obstacles.append(rect)
        return obstacles

