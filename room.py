import pygame
import random
from config import SCREEN_WIDTH, SCREEN_HEIGHT, WALL_THICKNESS, DOOR_SIZE, FONT
from enemy import Enemy
from obstacle import Obstacle  # sépare bien tes classes Enemy et Obstacle en fichiers distincts

class Room:
    def __init__(self, position, color, description):
        self.position = position
        self.color = color
        self.description = description
        self.walls = []
        self.doors = []
        self.enemies = []
        self.obstacles = []
        self.internal_walls = []
        self.chests = []

    def generate_walls_and_doors(self, grid):
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
        center_x, center_y = (SW - door_size) // 2, (SH - door_size) // 2

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
        self.enemies.clear()
        self.obstacles.clear()
        self.internal_walls.clear()
        self.chests.clear()

        # Générer ennemis aléatoires
        for _ in range(random.randint(1, 4)):
            x = random.randint(WALL_THICKNESS + 50, screen_width - WALL_THICKNESS - 50)
            y = random.randint(WALL_THICKNESS + 50, screen_height - WALL_THICKNESS - 50)
            self.enemies.append(Enemy(x, y, player, screen_width, screen_height))

        # Générer obstacles blocs
        for _ in range(random.randint(0, 3)):
            w, h = random.choice([(60, 60), (40, 80), (80, 40)])
            x = random.randint(WALL_THICKNESS + 50, screen_width - WALL_THICKNESS - w - 50)
            y = random.randint(WALL_THICKNESS + 50, screen_height - WALL_THICKNESS - h - 50)
            self.obstacles.append(Obstacle(x, y, w, h))

        # Générer murs internes (patterns simples)
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
            self.internal_walls.append(pygame.Rect(x, y, w, h))

        # Générer coffres (petits rectangles jaunes)
        for _ in range(random.randint(0, 2)):
            size = 30
            x = random.randint(WALL_THICKNESS + 50, screen_width - WALL_THICKNESS - size - 50)
            y = random.randint(WALL_THICKNESS + 50, screen_height - WALL_THICKNESS - size - 50)
            self.chests.append(pygame.Rect(x, y, size, size))

    def draw(self, surface):
        surface.fill(self.color)
        surface.blit(FONT.render(self.description, True, (255, 255, 255)), (20, 20))
        for wall in self.walls:
            pygame.draw.rect(surface, (100, 100, 100), wall)
        for _, door in self.doors:
            pygame.draw.rect(surface, (255, 0, 0), door)

        # Dessiner murs internes
        for rect in self.internal_walls:
            pygame.draw.rect(surface, (120, 120, 120), rect)
        # Dessiner obstacles
        for obst in self.obstacles:
            obst.draw(surface)
        # Dessiner coffres
        for chest in self.chests:
            pygame.draw.rect(surface, (255, 215, 0), chest)  # couleur or
        # Dessiner ennemis
        for enemy in self.enemies:
            enemy.draw(surface)

    def draw_contents(self, surface):
        # Dessiner murs internes
        for rect in self.internal_walls:
            pygame.draw.rect(surface, (120, 120, 120), rect)
        # Dessiner obstacles
        for obst in self.obstacles:
            obst.draw(surface)
        # Dessiner coffres
        for chest in self.chests:
            pygame.draw.rect(surface, (255, 215, 0), chest)  # couleur or
        # Dessiner ennemis
        for enemy in self.enemies:
            enemy.draw(surface)


