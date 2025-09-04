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
    def __init__(self, position,
                 nb_medicaments=10, nb_ennemis=None):
        self.position = position

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

        # Génération du nom de TMX selon les directions, dans l'ordre left, right, up, down
        if directions:
            priority = ['left', 'right', 'up', 'down']
            directions_sorted = sorted(directions, key=lambda d: priority.index(d))
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

"""
def generate_random_grid(num_rooms=6):
    grid = {}
    start = (0, 0)
    # Salle de départ sans TMX
    grid[start] = Room(
        position=start,
        nb_medicaments=1,
        nb_ennemis=1
    )

    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    dx, dy = random.choice(directions)
    enemy_room_pos = (start[0] + dx, start[1] + dy)
    grid[enemy_room_pos] = Room(
        position=enemy_room_pos,
        nb_medicaments=0,
        nb_ennemis=2
    )

    forbidden_positions = {(start[0] + dx, start[1] + dy) for dx, dy in directions}
    forbidden_positions.discard(enemy_room_pos)
    current_positions = [enemy_room_pos]

    for i in range(2, num_rooms):
        base = random.choice(current_positions)
        r, c = base
        possible = [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]
        random.shuffle(possible)
        for pos in possible:
            if pos not in grid and pos not in forbidden_positions:
                grid[pos] = Room(
                    position=pos,
                    nb_medicaments=0
                )
                current_positions.append(pos)
                break

    # Salle finale
    farthest_pos = max(grid.keys(), key=lambda pos: abs(pos[0]) + abs(pos[1]))
    final_room = grid[farthest_pos]
    final_room.nb_enemies_in_room = 8
    final_room.is_final = True

    # Répartition des médicaments
    total_meds = 30
    all_rooms_except_start = [room for pos, room in grid.items() if pos != start]
    for _ in range(total_meds):
        room = random.choice(all_rooms_except_start)
        room.nb_medicaments += 1

    # Génération des portes
    for room in grid.values():
        room.generate_walls_and_doors(grid)

    return grid

"""
def generate_random_grid(num_rooms=6):
    grid = {}
    start = (0, 0)
    # Salle de départ sans TMX
    grid[start] = Room(
        position=start,
        nb_medicaments=1,
        nb_ennemis=1
    )

    # Première salle ennemis toujours à droite
    enemy_room_pos = (start[0], start[1] + 1)
    grid[enemy_room_pos] = Room(
        position=enemy_room_pos,
        nb_medicaments=0,
        nb_ennemis=2
    )

    current_positions = [enemy_room_pos]

    for i in range(2, num_rooms):
        base = current_positions[-1]  # toujours partir de la dernière salle
        r, c = base
        # On ne crée que des salles à droite
        new_pos = (r, c + 1)
        grid[new_pos] = Room(
            position=new_pos,
            nb_medicaments=0
        )
        current_positions.append(new_pos)

    # Salle finale
    farthest_pos = max(grid.keys(), key=lambda pos: pos[1])  # salle la plus à droite
    final_room = grid[farthest_pos]
    final_room.nb_enemies_in_room = 8
    final_room.is_final = True

    # Répartition des médicaments
    total_meds = 30
    all_rooms_except_start = [room for pos, room in grid.items() if pos != start]
    for _ in range(total_meds):
        room = random.choice(all_rooms_except_start)
        room.nb_medicaments += 1

    # Génération des portes
    for room in grid.values():
        room.generate_walls_and_doors(grid)

    return grid

def draw_portal_if_boss_room(surface, room, player):
    """
    Dessine un portail si la salle est finale et affiche un message si le joueur est dessus.
    """
    if hasattr(room, "is_final") and room.is_final:
        if not hasattr(room, "portail") or room.portail is None:
            from portail import Portail  # Import ici pour éviter les cycles
            room.portail = Portail(
                SCREEN_WIDTH // 2 - 100 // 2,  # x centré
                SCREEN_HEIGHT // 2 - 100 // 2, # y centré
                100, 100
            )
        # Dessin du portail
        room.portail.draw(surface)

        # Détection collision joueur-portail
        if player.hitbox.colliderect(room.portail.rect):
            message = FONT.render("Appuyez sur E pour rentrer", True, (255, 255, 0))
            msg_x = SCREEN_WIDTH // 2 - message.get_width() // 2
            msg_y = room.portail.rect.top - 30
            surface.blit(message, (msg_x, msg_y))
            return True  # Le joueur est sur le portail
    return False

