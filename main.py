import pygame
from pygame.locals import *
import sys
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    WALL_THICKNESS, DOOR_SIZE,
    MINIMAP_SCALE, MINIMAP_MARGIN,
    STATE_MENU, STATE_PLAY,
    FONT
)

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Isaac-like Base with Auto Walls, Doors & Minimap')
clock = pygame.time.Clock()


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, screen_width, screen_height):
        super().__init__()
        self.surf = pygame.Surface((50, 50))
        self.surf.fill((0, 128, 255))
        self.rect = self.surf.get_rect(center=(x, y))
        self.speed = 5
        self.screen_width = screen_width
        self.screen_height = screen_height

    def update(self, keys, walls):
        dx = dy = 0
        if keys[K_UP]:
            dy = -self.speed
        if keys[K_DOWN]:
            dy = self.speed
        if keys[K_LEFT]:
            dx = -self.speed
        if keys[K_RIGHT]:
            dx = self.speed

        # Mouvement horizontal
        self.rect.x += dx
        for wall in walls:
            if self.rect.colliderect(wall):
                if dx > 0: self.rect.right = wall.left
                elif dx < 0: self.rect.left = wall.right

        # Mouvement vertical
        self.rect.y += dy
        for wall in walls:
            if self.rect.colliderect(wall):
                if dy > 0: self.rect.bottom = wall.top
                elif dy < 0: self.rect.top = wall.bottom

        # Limites écran
        self.rect.clamp_ip(pygame.Rect(0, 0, self.screen_width, self.screen_height))


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


def draw_minimap(surface, grid, current_pos):
    rows = [r for r, _ in grid]
    cols = [c for _, c in grid]
    min_r, max_r, min_c, max_c = min(rows), max(rows), min(cols), max(cols)
    width, height = (max_c - min_c + 1) * MINIMAP_SCALE, (max_r - min_r + 1) * MINIMAP_SCALE
    x_offset, y_offset = SCREEN_WIDTH - width - MINIMAP_MARGIN, MINIMAP_MARGIN

    for (r, c) in grid:
        x, y = x_offset + (c - min_c) * MINIMAP_SCALE, y_offset + (r - min_r) * MINIMAP_SCALE
        color = (255, 0, 0) if (r, c) == current_pos else (200, 200, 200)
        pygame.draw.rect(surface, color, (x, y, MINIMAP_SCALE - 2, MINIMAP_SCALE - 2))


def draw_menu():
    screen.fill((30, 30, 30))
    title = FONT.render("Mon menu Isaac-like", True, (255, 255, 0))
    play_btn = FONT.render("Jouer", True, (255, 255, 255))
    quit_btn = FONT.render("Quitter", True, (255, 255, 255))
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 120))
    screen.blit(play_btn, (SCREEN_WIDTH // 2 - play_btn.get_width() // 2, 280))
    screen.blit(quit_btn, (SCREEN_WIDTH // 2 - quit_btn.get_width() // 2, 380))
    pygame.display.flip()
    return [(play_btn, 280), (quit_btn, 380)]


def menu_events(btns):
    for event in pygame.event.get():
        if event.type == QUIT: pygame.quit(); sys.exit()
        if event.type == KEYDOWN and event.key == K_ESCAPE: pygame.quit(); sys.exit()
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for i, (btn, y) in enumerate(btns):
                bx = SCREEN_WIDTH // 2 - btn.get_width() // 2
                if bx < mx < bx + btn.get_width() and y < my < y + btn.get_height():
                    return i
    return None


def main():
    state = STATE_MENU
    grid = {
        (0, 0): Room((0, 0), (40, 40, 100), "Salle 1 - Début"),
        (0, 1): Room((0, 1), (100, 40, 40), "Salle 2 - Danger"),
        (1, 0): Room((1, 0), (40, 100, 40), "Salle 3 - Repos"),
        (1, 1): Room((1, 1), (40, 100, 40), "Salle 4 - Repos"),
        (2, 1): Room((2, 1), (40, 100, 40), "Salle 5 - Repos")
    }

    for room in grid.values(): room.generate_walls_and_doors(grid)
    current_pos, current_room = (0, 0), grid[(0, 0)]
    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT)

    while True:
        if state == STATE_MENU:
            btns = draw_menu()
            action = menu_events(btns)
            if action == 0: state = STATE_PLAY
            elif action == 1: pygame.quit(); sys.exit()

        elif state == STATE_PLAY:
            for event in pygame.event.get():
                if event.type == QUIT: state = STATE_MENU
                elif event.type == KEYDOWN and event.key == K_ESCAPE: state = STATE_MENU

            player.update(pygame.key.get_pressed(), current_room.walls)

            for direction, door in current_room.doors:
                if player.rect.colliderect(door):
                    r, c = current_pos
                    new_pos = {
                        'up': (r - 1, c), 'down': (r + 1, c),
                        'left': (r, c - 1), 'right': (r, c + 1)
                    }.get(direction, current_pos)

                    if new_pos in grid:
                        current_pos, current_room = new_pos, grid[new_pos]
                        if direction == 'up': player.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - WALL_THICKNESS - player.rect.height // 2)
                        elif direction == 'down': player.rect.center = (SCREEN_WIDTH // 2, WALL_THICKNESS + player.rect.height // 2)
                        elif direction == 'left': player.rect.center = (SCREEN_WIDTH - WALL_THICKNESS - player.rect.width // 2, SCREEN_HEIGHT // 2)
                        elif direction == 'right': player.rect.center = (WALL_THICKNESS + player.rect.width // 2, SCREEN_HEIGHT // 2)
                    break

            current_room.draw(screen)
            screen.blit(player.surf, player.rect)
            draw_minimap(screen, grid, current_pos)
            screen.blit(FONT.render(f"{current_room.description} {current_pos}", True, (255, 255, 255)), (10, SCREEN_HEIGHT - 50))
            pygame.display.flip()
            clock.tick(60)


if __name__ == "__main__":
    main()

