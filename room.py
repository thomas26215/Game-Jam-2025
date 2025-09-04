import os
import pygame
import random
import pytmx
from config import SCREEN_WIDTH, SCREEN_HEIGHT, DOOR_SIZE, FONT
from enemy import Enemy
from medicament import Medicament


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
            print(f"No TMX file found or provided: {tmx_file}. Continuing without map.")
            self.tmx_data = None
            self.obstacles = []
            self.width = SCREEN_WIDTH
            self.height = SCREEN_HEIGHT
            return

        print(f"Loading TMX file: {tmx_file}")
        self.tmx_data = pytmx.load_pygame(tmx_file)
        self.width = self.tmx_data.width * self.tmx_data.tilewidth
        self.height = self.tmx_data.height * self.tmx_data.tileheight
        self.obstacles = self._load_obstacles()
        print(f"Map size: {self.tmx_data.width}x{self.tmx_data.height} tiles")
        print(f"Loaded {len(self.obstacles)} obstacles from TMX.")

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


class Room:
    def __init__(self, position, color=(50, 50, 50), description="Salle",
                 nb_medicaments=10, nb_ennemis=None):
        self.position = position
        self.color = color
        self.description = description

        self.doors = []
        self.enemies = []
        self.enemies_data = []

        self.nb_medicaments = nb_medicaments
        self.medicaments = []
        self.medicaments_positions = []
        self.medicaments_state = {}

        self.obstacles = []

        self.map_loader = MapLoader()
        self.tmx_file = None  # TMX à charger plus tard si nécessaire
        self.nb_enemies_in_room = nb_ennemis

    def load_map(self):
        """Charge le TMX et les obstacles si un fichier est défini et existe."""
        if self.tmx_file and os.path.exists(self.tmx_file):
            self.map_loader.load(self.tmx_file)
            self.obstacles = self.map_loader.obstacles

            # Ajouter les murs du TMX si la couche existe
            if self.map_loader.tmx_data:
                try:
                    walls_layer = self.map_loader.tmx_data.get_layer_by_name("Walls")
                    if walls_layer:
                        for obj in walls_layer:
                            rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                            self.obstacles.append(rect)
                except ValueError:
                    # Pas de couche Walls
                    pass
        else:
            # Aucun fichier TMX : juste la taille par défaut
            self.obstacles = []

    def generate_walls_and_doors(self, grid):
        """Génère les portes selon la grille et détermine le fichier TMX."""
        self.doors.clear()
        r, c = self.position
        SW, SH = SCREEN_WIDTH, SCREEN_HEIGHT

        directions = []
        if (r - 1, c) in grid:
            self.doors.append(('up', pygame.Rect(0, 0, SW, DOOR_SIZE)))
            directions.append('up')
        if (r + 1, c) in grid:
            self.doors.append(('down', pygame.Rect(0, SH - DOOR_SIZE, SW, DOOR_SIZE)))
            directions.append('down')
        if (r, c - 1) in grid:
            self.doors.append(('left', pygame.Rect(0, 0, DOOR_SIZE, SH)))
            directions.append('left')
        if (r, c + 1) in grid:
            self.doors.append(('right', pygame.Rect(SW - DOOR_SIZE, 0, DOOR_SIZE, SH)))
            directions.append('right')

        # Génération du nom de TMX selon les directions
        if directions:
            directions_sorted = sorted(directions)
            self.tmx_file = f"maps/{'_'.join(directions_sorted)}.tmx"
        else:
            self.tmx_file = None

        self.load_map()

    def generate_contents(self, player, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT):
        """Génère ennemis et médicaments en évitant obstacles et portes."""
        self.enemies.clear()
        self.medicaments.clear()
        door_areas = [door for _, door in self.doors]

        # --- Génération des ennemis ---
        if not self.enemies_data:
            if self.nb_enemies_in_room is None:
                self.nb_enemies_in_room = random.randint(1, 4)

            for _ in range(self.nb_enemies_in_room):
                while True:
                    x = random.randint(50, screen_width - 50)
                    y = random.randint(50, screen_height - 50)
                    new_rect = pygame.Rect(x - 15, y - 15, 30, 30)
                    collision = any(new_rect.colliderect(obs) for obs in self.obstacles + door_areas)
                    if not collision:
                        break
                zombie_number = random.randint(1, 4)
                self.enemies_data.append({
                    "x": x,
                    "y": y,
                    "folder": f"zombies/Zombie_{zombie_number}"
                })

        for data in self.enemies_data:
            folder = data["folder"]
            enemy = Enemy(
                data["x"], data["y"], player, screen_width, screen_height,
                walk_spritesheet_path=f"{folder}/Walk.png",
                attack_spritesheet_path=f"{folder}/Attack.png",
                hit_spritesheet_path=f"{folder}/Hurt.png",
                death_spritesheet_path=f"{folder}/Dead.png",
                frame_width=128,
                frame_height=128,
                activation_distance=200,
                speed_close=1.5,
                speed_far=0.75,
                attack_range=50,
                attack_damage=1
            )
            self.enemies.append(enemy)

        # --- Génération des médicaments ---
        if not self.medicaments_positions:
            for _ in range(self.nb_medicaments):
                while True:
                    x = random.randint(20, screen_width - 20)
                    y = random.randint(20, screen_height - 20)
                    new_rect = pygame.Rect(x - 15, y - 15, 30, 30)
                    collision = any(new_rect.colliderect(obs) for obs in self.obstacles + door_areas)
                    if not collision:
                        break
                    # Essaye de placer les potions ailleurs si collision
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
        if self.map_loader.tmx_data:
            tmx_data = self.map_loader.tmx_data
            for layer in tmx_data.visible_layers:
                if hasattr(layer, 'tiles'):
                    for x, y, gid in layer.tiles():
                        tile = gid if isinstance(gid, pygame.Surface) else tmx_data.get_tile_image_by_gid(gid)
                        if tile:
                            surface.blit(tile, (x * tmx_data.tilewidth, y * tmx_data.tileheight))

        surface.blit(FONT.render(self.description, True, (255, 255, 255)), (20, 20))

        for _, door in self.doors:
            pygame.draw.rect(surface, (255, 0, 0), door)

        for enemy in self.enemies:
            enemy.draw(surface)
        for med in self.medicaments:
            med.draw(surface)

    def draw_contents(self, surface):
        for enemy in self.enemies:
            enemy.draw(surface)
        for med in self.medicaments:
            med.draw(surface)

