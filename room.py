import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, WALL_THICKNESS, DOOR_SIZE, FONT


class Room:
    def __init__(self, position, color, description):
        self.position = position
        self.color = color
        self.description = description
        self.walls = []
        self.doors = []

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

    def draw(self, surface):
        surface.fill(self.color)
        surface.blit(FONT.render(self.description, True, (255, 255, 255)), (20, 20))
        for wall in self.walls: pygame.draw.rect(surface, (100, 100, 100), wall)
        for _, door in self.doors: pygame.draw.rect(surface, (255, 0, 0), door)
