import pygame
import random
from config import SCREEN_WIDTH, SCREEN_HEIGHT, DOOR_SIZE, FONT
from enemy import Enemy
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
        self.doors = []           # Portes
        self.enemies = []         # Ennemis

        # Médicaments
        self.nb_medicaments = nb_medicaments
        self.medicaments = []
        self.medicaments_positions = []  # Coordonnées mémorisées
        self.medicaments_state = {}      # État collecté ou non

        # Nombre d’ennemis fixe pour cette pièce
        self.nb_enemies_in_room = nb_ennemis

    def generate_walls_and_doors(self, grid):
        """
        Génère uniquement les portes selon la position de la pièce.
        """
        self.doors.clear()

        def has_neighbor(direction):
            r, c = self.position
            if direction == 'up': return (r - 1, c) in grid
            if direction == 'down': return (r + 1, c) in grid
            if direction == 'left': return (r, c - 1) in grid
            if direction == 'right': return (r, c + 1) in grid
            return False

        W, SW, SH, door_size = DOOR_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, DOOR_SIZE
        center_x, center_y = (SW - door_size) // 2, (SH - DOOR_SIZE) // 2

        if has_neighbor('up'):
            self.doors.append(('up', pygame.Rect(center_x, 0, door_size, W)))
        if has_neighbor('down'):
            self.doors.append(('down', pygame.Rect(center_x, SH - W, door_size, W)))
        if has_neighbor('left'):
            self.doors.append(('left', pygame.Rect(0, center_y, W, door_size)))
        if has_neighbor('right'):
            self.doors.append(('right', pygame.Rect(SW - W, center_y, W, door_size)))

    def generate_contents(self, player, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT):
        """
        Génère les contenus : ennemis, coffres, médicaments.
        """
        self.enemies.clear()
        self.medicaments.clear()

        # Définir nb ennemis si pas encore fait
        if self.nb_enemies_in_room is None:
            self.nb_enemies_in_room = random.randint(1, 4)

        margin = 50
        door_areas = [door for _, door in self.doors]

        # Génération des ennemis
        for _ in range(self.nb_enemies_in_room):
            while True:
                x = random.randint(margin, screen_width - margin)
                y = random.randint(margin, screen_height - margin)
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
                    activation_distance=200,
                    speed_close=1.5,
                    speed_far=0.75,
                    attack_range=50
                )
            )

        # Coffres (simple génération)
        for _ in range(random.randint(0, 2)):
            size = 30
            x = random.randint(50, screen_width - size - 50)
            y = random.randint(50, screen_height - size - 50)

        # Médicaments
        if not self.medicaments_positions:
            for _ in range(self.nb_medicaments):
                while True:
                    x = random.randint(20, screen_width - 20)
                    y = random.randint(20, screen_height - 20)
                    new_rect = pygame.Rect(x - 15, y - 15, 30, 30)
                    # Plus de collision avec murs internes
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
        for _, door in self.doors:
            pygame.draw.rect(surface, (255, 0, 0), door)
        for enemy in self.enemies:
            enemy.draw(surface)
        for med in self.medicaments:
            med.draw(surface)

    def draw_contents(self, surface):
        """Dessine le contenu dynamique seulement."""
        for enemy in self.enemies:
            enemy.draw(surface)
        for med in self.medicaments:
            med.draw(surface)

