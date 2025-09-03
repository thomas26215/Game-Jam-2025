import pygame
import random
import pytmx
from config import SCREEN_WIDTH, SCREEN_HEIGHT, DOOR_SIZE, FONT
from enemy import Enemy
from medicament import Medicament

class MapLoader:
    """Charge un fichier TMX et extrait les obstacles."""
    def __init__(self, tmx_file):
        print(f"Loading TMX file: {tmx_file}")
        self.tmx_data = pytmx.load_pygame(tmx_file)
        print(f"Map size: {self.tmx_data.width}x{self.tmx_data.height} tiles")
        self.width = self.tmx_data.width * self.tmx_data.tilewidth
        self.height = self.tmx_data.height * self.tmx_data.tileheight
        self.obstacles = self._load_obstacles()
        print(f"Loaded {len(self.obstacles)} obstacles from TMX.")

    def _load_obstacles(self):
        obstacles = []
        for layer in self.tmx_data.layers:
            if isinstance(layer, pytmx.TiledObjectGroup):
                for obj in layer:
                    rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                    obstacles.append(rect)
        return obstacles

class Room:
    def __init__(self, position, tmx_file=None, color=(50, 50, 50), description="Salle",
                 nb_medicaments=10, nb_ennemis=None):
        self.position = position
        print("Room position:", position)
        print("tmx_file:", tmx_file)
        self.color = color
        self.description = description

        # Portes et ennemis
        self.doors = []
        self.enemies = []

        # Médicaments
        self.nb_medicaments = nb_medicaments
        self.medicaments = []
        self.medicaments_positions = []
        self.medicaments_state = {}

        # Obstacles et TMX
        self.obstacles = []
        self.map_loader = None
        if tmx_file is not None:
            self.map_loader = MapLoader(tmx_file)
            self.obstacles = self.map_loader.obstacles

        # Nombre d’ennemis
        self.nb_enemies_in_room = nb_ennemis

    def generate_walls_and_doors(self, grid):
        """Génère les portes selon la grille."""
        self.doors.clear()
        r, c = self.position
        W, SW, SH, door_size = DOOR_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, DOOR_SIZE
        center_x, center_y = (SW - door_size) // 2, (SH - DOOR_SIZE) // 2

        def has_neighbor(direction):
            if direction == 'up': return (r - 1, c) in grid
            if direction == 'down': return (r + 1, c) in grid
            if direction == 'left': return (r, c - 1) in grid
            if direction == 'right': return (r, c + 1) in grid
            return False

        if has_neighbor('up'):
            self.doors.append(('up', pygame.Rect(center_x, 0, door_size, W)))
        if has_neighbor('down'):
            self.doors.append(('down', pygame.Rect(center_x, SH - W, door_size, W)))
        if has_neighbor('left'):
            self.doors.append(('left', pygame.Rect(0, center_y, W, door_size)))
        if has_neighbor('right'):
            self.doors.append(('right', pygame.Rect(SW - W, center_y, W, door_size)))

    def generate_contents(self, player, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT):
        """Génère ennemis et médicaments en évitant obstacles et portes."""
        self.enemies.clear()
        self.medicaments.clear()

        if self.nb_enemies_in_room is None:
            self.nb_enemies_in_room = random.randint(1, 4)

        door_areas = [door for _, door in self.doors]

        # Génération des ennemis
        for _ in range(self.nb_enemies_in_room):
            while True:
                x = random.randint(50, screen_width - 50)
                y = random.randint(50, screen_height - 50)
                new_rect = pygame.Rect(x - 15, y - 15, 30, 30)
                collision = any(new_rect.colliderect(obs) for obs in self.obstacles + door_areas)
                if not collision:
                    break
            self.enemies.append(
                Enemy(x, y, player, screen_width, screen_height,
                      walk_spritesheet_path="zombies/Zombie_1/Walk.png",
                      attack_spritesheet_path="zombies/Zombie_1/Attack.png",
                      frame_width=128, frame_height=128,
                      activation_distance=200,
                      speed_close=1.5, speed_far=0.75,
                      attack_range=50)
            )

        # Génération des médicaments
        if not self.medicaments_positions:
            for _ in range(self.nb_medicaments):
                while True:
                    x = random.randint(20, screen_width - 20)
                    y = random.randint(20, screen_height - 20)
                    new_rect = pygame.Rect(x - 15, y - 15, 30, 30)
                    collision = any(new_rect.colliderect(obs) for obs in self.obstacles + door_areas)
                    if not collision:
                        break
                self.medicaments_positions.append((x, y))
                self.medicaments_state[(x, y)] = False

        for pos in self.medicaments_positions:
            x, y = pos
            med = Medicament(x, y, player, screen_width, screen_height,
                             spritesheet_path="potion/PotionBlue.png", frame_width=22, frame_height=37)
            med.collected = self.medicaments_state[pos]
            self.medicaments.append(med)

    def update_medicaments_state(self):
        for med, pos in zip(self.medicaments, self.medicaments_positions):
            self.medicaments_state[pos] = med.collected

    def draw(self, surface):
        """Dessine la salle et la map TMX, en gérant gid déjà Surface."""
        if self.map_loader is not None:
            tmx_data = self.map_loader.tmx_data
            for layer in tmx_data.visible_layers:
                if hasattr(layer, 'tiles'):
                    for x, y, gid in layer.tiles():
                        # --- Correction: gid peut déjà être une Surface ---
                        if isinstance(gid, pygame.Surface):
                            tile = gid
                        else:
                            tile = tmx_data.get_tile_image_by_gid(gid)
                        if tile:
                            surface.blit(tile, (x * tmx_data.tilewidth, y * tmx_data.tileheight))
                            # Debug tile
                            # print(f"Tile at ({x},{y}) drawn.")

        # Dessin de la salle (nom)
        surface.blit(FONT.render(self.description, True, (255, 255, 255)), (20, 20))

        # Dessin des portes
        for _, door in self.doors:
            pygame.draw.rect(surface, (255, 0, 0), door)

        # Dessin des obstacles (rect collision)
        for obs in self.obstacles:
            pygame.draw.rect(surface, (100, 100, 100), obs)

        # Dessin ennemis et médicaments
        for enemy in self.enemies:
            enemy.draw(surface)
        for med in self.medicaments:
            med.draw(surface)

    def draw_contents(self, surface):
        for enemy in self.enemies:
            enemy.draw(surface)
        for med in self.medicaments:
            med.draw(surface)

