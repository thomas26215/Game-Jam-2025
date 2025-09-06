import os
import pygame
import random
import pytmx
from config import SCREEN_WIDTH, SCREEN_HEIGHT, DOOR_SIZE, FONT
from enemy import Enemy
from gameSettings import GameSettings
from maploader import MapLoader
from medicament import Medicament



class Room:
    def __init__(self, position, nb_medicaments=10, nb_ennemis=None):
        self.position = position

        self.doors = []
        self.total_zombies = 0
        self.enemies = []
        self.enemies_data = []  # Stocke les infos de chaque ennemi, y compris alive et resurrected

        self.nb_medicaments = nb_medicaments
        self.medicaments = []
        self.medicaments_positions = []
        self.medicaments_state = {}

        self.obstacles = []

        self.map_loader = MapLoader()
        self.tmx_file = None  # TMX à charger plus tard
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
                    pass
        else:
            self.obstacles = []

    def generate_walls_and_doors(self, grid, forced_doors=None, exclusive=False):
        """Génère les portes selon la grille et éventuellement des portes forcées."""
        self.doors.clear()
        r, c = self.position
        SW, SH = SCREEN_WIDTH, SCREEN_HEIGHT

        directions = []

        if exclusive and forced_doors:  # Only keep the forced ones
            dirs = forced_doors
        else:
            dirs = []
            if (r - 1, c) in grid or (forced_doors and 'up' in forced_doors):
                dirs.append('up')
            if (r + 1, c) in grid or (forced_doors and 'down' in forced_doors):
                dirs.append('down')
            if (r, c - 1) in grid or (forced_doors and 'left' in forced_doors):
                dirs.append('left')
            if (r, c + 1) in grid or (forced_doors and 'right' in forced_doors):
                dirs.append('right')

        # Create actual Rect doors
        for d in dirs:
            if d == 'up':
                self.doors.append(('up', pygame.Rect(0, 0, SW, DOOR_SIZE)))
            elif d == 'down':
                self.doors.append(('down', pygame.Rect(0, SH - DOOR_SIZE, SW, DOOR_SIZE)))
            elif d == 'left':
                self.doors.append(('left', pygame.Rect(0, 0, DOOR_SIZE, SH)))
            elif d == 'right':
                self.doors.append(('right', pygame.Rect(SW - DOOR_SIZE, 0, DOOR_SIZE, SH)))

        if dirs:
            priority = ['left', 'right', 'up', 'down']
            directions_sorted = sorted(directions, key=lambda d: priority.index(d))
            if (self.position == (0, 0)) and ('right' in directions_sorted):
                print("Salle de départ, porte droite forcée")
                self.tmx_file = "maps/right.tmx"
            else:
                self.tmx_file = f"maps/{'_'.join(directions_sorted)}.tmx"
            #print("Chargement TMX :", self.tmx_file)
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

            spawn_margin = 250
            wall_margin = 20

            for _ in range(self.nb_enemies_in_room):
                while True:
                    x = random.randint(spawn_margin, screen_width - spawn_margin)
                    y = random.randint(spawn_margin, screen_height - spawn_margin)
                    new_rect = pygame.Rect(x - 15, y - 15, 30, 30)

                    collision = any(new_rect.colliderect(obs) for obs in self.obstacles + door_areas)
                    too_close_to_wall = any(
                        new_rect.inflate(wall_margin * 2, wall_margin * 2).colliderect(obs)
                        for obs in self.obstacles
                    )

                    if not collision and not too_close_to_wall:
                        break

                zombie_number = random.randint(1, 4)
                human_number = random.randint(1, 3)

                self.enemies_data.append({
                    "x": x,
                    "y": y,
                    "folder": f"zombies/Zombie_{zombie_number}",
                    "resurrected_sprites_folder": f"Humans/Homeless_{human_number}",
                    "alive": True,
                    "resurrected": False
                })

        for data in self.enemies_data:
            enemy = Enemy(
                data["x"], data["y"], player, screen_width, screen_height,
                sprites_folder=data["folder"],
                resurrected_sprites_folder=data.get("resurrected_sprites_folder"),
                frame_width=128,
                frame_height=128,
                activation_distance=200,
                speed_close=1.5,
                speed_far=0.75,
                attack_range=50,
                attack_damage=1,
                alive=data.get("alive", True),
                resurrected=data.get("resurrected", False)
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

    def update_enemies_state(self):
        """Met à jour l'état vivant/mort et resurrected des ennemis dans enemies_data."""
        for enemy, data in zip(self.enemies, self.enemies_data):
            data["alive"] = enemy.alive
            data["resurrected"] = enemy.resurrected

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
            pygame.draw.rect(surface, (255, 0, 0, 0), door)

        for enemy in self.enemies:
            enemy.draw(surface)
        for med in self.medicaments:
            med.draw(surface)

    def draw_contents(self, surface):
        for enemy in self.enemies:
            enemy.draw(surface)
        for med in self.medicaments:
            med.draw(surface)


def generate_random_grid(num_rooms=3):
    grid = {}
    start = (0, 0)

    # Salle de départ
    grid[start] = Room(position=start, nb_medicaments=1, nb_ennemis=0)
    grid[start].generate_walls_and_doors(grid, forced_doors=['right'], exclusive=True)

    # Salle à droite du départ
    enemy_room_pos = (0, 1)
    grid[enemy_room_pos] = Room(position=enemy_room_pos, nb_medicaments=0, nb_ennemis=2)
    grid[enemy_room_pos].generate_walls_and_doors(grid, forced_doors=['left'])

    current_positions = [enemy_room_pos]

    # Autres salles aléatoires
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    forbidden_positions = {(0, 0), enemy_room_pos}

    for _ in range(2, num_rooms):
        base = random.choice(current_positions)
        r, c = base
        possible = [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]
        random.shuffle(possible)
        for pos in possible:
            if pos not in grid and pos not in forbidden_positions:
                grid[pos] = Room(
                    position=pos,
                    nb_medicaments=0,
                    nb_ennemis=0
                )
                current_positions.append(pos)
                break

    # Salle finale
    farthest_pos = max(grid.keys(), key=lambda pos: abs(pos[0]) + abs(pos[1]))
    final_room = grid[farthest_pos]
    final_room.nb_enemies_in_room = 8
    final_room.is_final = True
    # Génère les portes et la map pour la salle finale (portail)
    final_room.generate_walls_and_doors(grid, forced_doors=['left'])

    # --- Répartition des zombies dans les 9 salles ---
    normal_rooms = [room for pos, room in grid.items() if pos != start and not getattr(room, "is_final", False)]
    total_zombies = random.randint(20, 37)
    print  ("Total zombies à répartir :", total_zombies)
    zombies_left = total_zombies

    for room in normal_rooms:
        room.nb_enemies_in_room = 0

    while zombies_left > 0:
        possible_rooms = [room for room in normal_rooms if room.nb_enemies_in_room < 5]
        if not possible_rooms:
            break  
        room = random.choice(possible_rooms)
        room.nb_enemies_in_room += 1
        zombies_left -= 1

    # Répartition des médicaments 
    total_meds = total_zombies
    #print("Total zombies:", total_zombies, "=> Médicaments:", total_meds)
    all_rooms_except_start = [room for pos, room in grid.items() if pos != start]
    for _ in range(total_meds):
        room = random.choice(all_rooms_except_start)
        room.nb_medicaments += 1

    # Génération portes des autres salles
    for pos, room in grid.items():
        if not getattr(room, "is_final", False):
            room.generate_walls_and_doors(grid)

    return grid

def draw_portal_if_boss_room(surface, room, player, settings):
    if hasattr(room, "is_final") and room.is_final:
        if not hasattr(room, "portail") or room.portail is None:
            from portail import Portail
            room.portail = Portail(
                SCREEN_WIDTH // 2 - 100 // 2,
                SCREEN_HEIGHT // 2 - 100 // 2,
                100, 100
            )
        room.portail.draw(surface)

        interact_keys = settings.get_control("interact", "keyboard")
        def key_name(key_code):
            key_names = {
                pygame.K_e: "E", pygame.K_f: "F", pygame.K_r: "R", pygame.K_g: "G",
                pygame.K_SPACE: "ESPACE", pygame.K_RETURN: "ENTRÉE",
                pygame.K_UP: "↑", pygame.K_DOWN: "↓", 
                pygame.K_LEFT: "←", pygame.K_RIGHT: "→"
            }
            return key_names.get(key_code, f"KEY_{key_code}")
        
        if interact_keys:
            keys_text = " ou ".join([key_name(key) for key in interact_keys])
            message = FONT.render(f"Appuyez sur {keys_text} pour rentrer", True, (255, 255, 0))
        else:
            message = FONT.render("Appuyez sur E pour rentrer", True, (255, 255, 0))

        if player.hitbox.colliderect(room.portail.rect):
            msg_x = SCREEN_WIDTH // 2 - message.get_width() // 2
            msg_y = room.portail.rect.top - 30
            surface.blit(message, (msg_x, msg_y))
            return True
    return False

