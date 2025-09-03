import pygame
import random
from config import SCREEN_WIDTH, SCREEN_HEIGHT, WALL_THICKNESS, DOOR_SIZE, FONT
from enemy import Enemy
from obstacle import Obstacle
from medicament import Medicament

class Room:
    def __init__(self, position, color, description, nb_medicaments=1000, nb_ennemis=None):
        """
        Initialise une pièce avec sa position, sa couleur, sa description,
        le nombre de médicaments et d'ennemis (aléatoire si non précisé).
        """
        self.position = position
        self.color = color
        self.description = description
        
        # Listes dynamiques pour le rendu
        self.walls = []          # Murs extérieurs
        self.doors = []          # Portes
        self.enemies = []        # Ennemis
        self.obstacles = []      # Obstacles
        self.internal_walls = [] # Murs internes

        # Médicaments
        self.nb_medicaments = nb_medicaments
        self.medicaments = []
        self.medicaments_positions = []  # Coordonnées mémorisées
        self.medicaments_state = {}      # État collecté ou non

        # Positions sauvegardées pour recréer les mêmes obstacles/murs
        self.internal_walls_positions = []  
        self.obstacles_positions = []       

        # Nombre d’ennemis fixe pour cette pièce
        self.nb_enemies_in_room = nb_ennemis

    def generate_walls_and_doors(self, grid):
        """
        Génère les murs extérieurs et les portes selon la position de la pièce
        et la grille de toutes les pièces existantes.
        """
        self.walls.clear()
        self.doors.clear()

        def has_neighbor(direction):
            r, c = self.position
            if direction == 'up': return (r - 1, c) in grid
            if direction == 'down': return (r + 1, c) in grid
            if direction == 'left': return (r, c - 1) in grid
            if direction == 'right': return (r, c + 1) in grid
            return False

        W, SW, SH, door_size = WALL_THICKNESS, SCREEN_WIDTH, SCREEN_HEIGHT, DOOR_SIZE
        center_x, center_y = (SW - door_size) // 2, (SH - DOOR_SIZE) // 2

        if has_neighbor('up'):
            self.doors.append(('up', pygame.Rect(center_x, 0, door_size, W)))
        else:
            self.walls.append(pygame.Rect(0, 0, SW, W))
        if has_neighbor('down'):
            self.doors.append(('down', pygame.Rect(center_x, SH - W, door_size, W)))
        else:
            self.walls.append(pygame.Rect(0, SH - W, SW, W))
        if has_neighbor('left'):
            self.doors.append(('left', pygame.Rect(0, center_y, W, door_size)))
        else:
            self.walls.append(pygame.Rect(0, 0, W, SH))
        if has_neighbor('right'):
            self.doors.append(('right', pygame.Rect(SW - W, center_y, W, door_size)))
        else:
            self.walls.append(pygame.Rect(SW - W, 0, W, SH))

    def generate_contents(self, player, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT):
        """
        Génère les contenus : ennemis, obstacles, murs internes, coffres, médicaments.
        Les positions et états sont mémorisés.
        """
        self.internal_walls.clear()
        self.obstacles.clear()
        self.medicaments.clear()

        # Définir nb ennemis si pas encore fait
        if self.nb_enemies_in_room is None:
            self.nb_enemies_in_room = random.randint(1, 4)

        # Génération des ennemis
        self.enemies.clear()
        margin = 50
        door_areas = [door for _, door in self.doors]
        for _ in range(self.nb_enemies_in_room):
            while True:
                x = random.randint(WALL_THICKNESS + margin, screen_width - WALL_THICKNESS - margin)
                y = random.randint(WALL_THICKNESS + margin, screen_height - WALL_THICKNESS - margin)
                new_rect = pygame.Rect(x - 15, y - 15, 30, 30)
                if not any(new_rect.colliderect(door.inflate(50, 50)) for door in door_areas):
                    break
            self.enemies.append(
                Enemy(
                    x, y, player,
                    screen_width, screen_height,
                    walk_spritesheet_path="zombies/Zombie_1/Walk.png",
                    attack_spritesheet_path="zombies/Zombie_1/Attack.png",
                    frame_width=128,
                    frame_height=128,
                    activation_distance=200,  # optionnel, par défaut
                    speed_close=1.5,          # optionnel
                    speed_far=0.75,           # optionnel
                    attack_range=50           # optionnel
                )
            )
            
        # Obstacles
        if not self.obstacles_positions:
            for _ in range(random.randint(0, 3)):
                w, h = random.choice([(60, 60), (40, 80), (80, 40)])
                x = random.randint(WALL_THICKNESS + 50, screen_width - WALL_THICKNESS - w - 50)
                y = random.randint(WALL_THICKNESS + 50, screen_height - WALL_THICKNESS - h - 50)
                self.obstacles_positions.append((x, y, w, h))
        for x, y, w, h in self.obstacles_positions:
            self.obstacles.append(Obstacle(x, y, w, h))

        # Murs internes
        if not self.internal_walls_positions:
            for _ in range(random.randint(1, 3)):
                vertical = random.choice([True, False])
                if vertical:
                    w = WALL_THICKNESS
                    h = random.randint(100, 200)
                    x = random.randint(WALL_THICKNESS + 100, screen_width - WALL_THICKNESS - 100)
                    y = random.randint(WALL_THICKNESS + 50, screen_height - WALL_THICKNESS - h - 50)
                else:
                    w = random.randint(100, 200)
                    h = WALL_THICKNESS
                    x = random.randint(WALL_THICKNESS + 50, screen_width - WALL_THICKNESS - w - 50)
                    y = random.randint(WALL_THICKNESS + 100, screen_height - WALL_THICKNESS - 100)
                self.internal_walls_positions.append((x, y, w, h))
        for x, y, w, h in self.internal_walls_positions:
            self.internal_walls.append(pygame.Rect(x, y, w, h))

        # Coffres
        for _ in range(random.randint(0, 2)):
            size = 30
            x = random.randint(WALL_THICKNESS + 50, screen_width - WALL_THICKNESS - size - 50)
            y = random.randint(WALL_THICKNESS + 50, screen_height - WALL_THICKNESS - size - 50)

        # Médicaments
        if not self.medicaments_positions:
            for _ in range(self.nb_medicaments):
                while True:
                    x = random.randint(WALL_THICKNESS + 20, screen_width - WALL_THICKNESS - 20)
                    y = random.randint(WALL_THICKNESS + 20, screen_height - WALL_THICKNESS - 20)
                    new_rect = pygame.Rect(x - 15, y - 15, 30, 30)
                    collision = False
                    for rect in self.internal_walls + [ob.rect for ob in self.obstacles]:
                        if new_rect.colliderect(rect):
                            collision = True
                            break
                    if not collision:
                        break
                self.medicaments_positions.append((x, y))
                self.medicaments_state[(x, y)] = False
        for pos in self.medicaments_positions:
            x, y = pos
            med = Medicament(x, y, player, screen_width, screen_height, spritesheet_path="potion/PotionBlue.png", frame_width=22, frame_height=37)
            med.collected = self.medicaments_state[pos]
            self.medicaments.append(med)

    def update_medicaments_state(self):
        """Met à jour l’état des médicaments collectés."""
        for med, pos in zip(self.medicaments, self.medicaments_positions):
            self.medicaments_state[pos] = med.collected

    def draw(self, surface):
        """Dessine toute la pièce."""
        surface.fill(self.color)
        surface.blit(FONT.render(self.description, True, (255, 255, 255)), (20, 20))
        for wall in self.walls:
            pygame.draw.rect(surface, (100, 100, 100), wall)
        for _, door in self.doors:
            pygame.draw.rect(surface, (255, 0, 0), door)
        for rect in self.internal_walls:
            pygame.draw.rect(surface, (120, 120, 120), rect)
        for obst in self.obstacles:
            obst.draw(surface)
        for enemy in self.enemies:
            enemy.draw(surface)
        for med in self.medicaments:
            med.draw(surface)

    def draw_contents(self, surface):
        """Dessine le contenu dynamique seulement."""
        for rect in self.internal_walls:
            pygame.draw.rect(surface, (120, 120, 120), rect)
        for obst in self.obstacles:
            obst.draw(surface)
        for enemy in self.enemies:
            enemy.draw(surface)
        for med in self.medicaments:
            med.draw(surface)

