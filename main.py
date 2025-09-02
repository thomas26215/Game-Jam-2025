import pygame
from enemy import Enemy
from medicament import Medicament
from pygame.locals import *
import sys
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    WALL_THICKNESS, DOOR_SIZE,
    MINIMAP_SCALE, MINIMAP_MARGIN,
    STATE_MENU, STATE_PLAY,
    FONT
)
from room import Room
import random
import math

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Contagium")
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
                if dx > 0:
                    self.rect.right = wall.left
                elif dx < 0:
                    self.rect.left = wall.right

        # Mouvement vertical
        self.rect.y += dy
        for wall in walls:
            if self.rect.colliderect(wall):
                if dy > 0:
                    self.rect.bottom = wall.top
                elif dy < 0:
                    self.rect.top = wall.bottom

        # Limites écran
        self.rect.clamp_ip(pygame.Rect(0, 0, self.screen_width, self.screen_height))


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
    title = FONT.render("Contagium", True, (255, 255, 0))
    play_btn = FONT.render("Jouer", True, (255, 255, 255))
    quit_btn = FONT.render("Quitter", True, (255, 255, 255))
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 120))
    screen.blit(play_btn, (SCREEN_WIDTH // 2 - play_btn.get_width() // 2, 280))
    screen.blit(quit_btn, (SCREEN_WIDTH // 2 - quit_btn.get_width() // 2, 380))
    pygame.display.flip()
    return [(play_btn, 280), (quit_btn, 380)]


def menu_events(btns):
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            pygame.quit()
            sys.exit()
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for i, (btn, y) in enumerate(btns):
                bx = SCREEN_WIDTH // 2 - btn.get_width() // 2
                if bx < mx < bx + btn.get_width() and y < my < y + btn.get_height():
                    return i
    return None


def generate_random_grid(num_rooms=5):
    grid = {}
    start = (0, 0)
    grid[start] = Room(start, random_color(), "Salle de départ", nb_medicaments=3)
    current_positions = [start]
    for i in range(1, num_rooms):
        base = random.choice(current_positions)
        r, c = base
        possible = [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]
        random.shuffle(possible)
        for pos in possible:
            if pos not in grid:
                grid[pos] = Room(pos, random_color(), f"Salle {i+1}", nb_medicaments=random.randint(0, 3))
                current_positions.append(pos)
                break
    for room in grid.values():
        room.generate_walls_and_doors(grid)
    return grid


def random_color():
    return (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))


def main():
    state = STATE_MENU
    grid = generate_random_grid(num_rooms=5)
    current_pos, current_room = (0, 0), grid[(0, 0)]
    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT)
    
    # Générer contenus de la salle courante
    current_room.generate_contents(player, SCREEN_WIDTH, SCREEN_HEIGHT)

    while True:
        if state == STATE_MENU:
            btns = draw_menu()
            action = menu_events(btns)
            if action == 0:
                state = STATE_PLAY
            elif action == 1:
                pygame.quit()
                sys.exit()
        elif state == STATE_PLAY:
            for event in pygame.event.get():
                if event.type == QUIT:
                    state = STATE_MENU
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    state = STATE_MENU

            keys = pygame.key.get_pressed()
            player.update(keys, current_room.walls)



            # Mettre à jour ennemis et médicaments
            for enemy in current_room.enemies:
                enemy.update(current_room.walls)
                for med in current_room.medicaments:
                    med.update()  # mise à jour couleur
                    if player.rect.colliderect(med.rect):
                        med.collect()  # marque comme collecté

            current_room.update_medicaments_state()


            # Changer de salle si collision avec porte
            for direction, door in current_room.doors:
                if player.rect.colliderect(door):
                    r, c = current_pos
                    new_pos = {
                        'up': (r - 1, c), 'down': (r + 1, c),
                        'left': (r, c - 1), 'right': (r, c + 1)
                    }.get(direction, current_pos)
                    if new_pos in grid:
                        current_pos, current_room = new_pos, grid[new_pos]
                        current_room.generate_contents(player, SCREEN_WIDTH, SCREEN_HEIGHT)
                        if direction == 'up':
                            player.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - WALL_THICKNESS - player.rect.height // 2)
                        elif direction == 'down':
                            player.rect.center = (SCREEN_WIDTH // 2, WALL_THICKNESS + player.rect.height // 2)
                        elif direction == 'left':
                            player.rect.center = (SCREEN_WIDTH - WALL_THICKNESS - player.rect.width // 2, SCREEN_HEIGHT // 2)
                        elif direction == 'right':
                            player.rect.center = (WALL_THICKNESS + player.rect.width // 2, SCREEN_HEIGHT // 2)
                    break

            # Dessiner tout
            current_room.draw(screen)
            current_room.draw_contents(screen)
            screen.blit(player.surf, player.rect)
            for enemy in current_room.enemies:
                enemy.draw(screen)
            for med in current_room.medicaments:
                med.draw(screen)
            draw_minimap(screen, grid, current_pos)
            screen.blit(FONT.render(f"{current_room.description} {current_pos}", True, (255, 255, 255)), (10, SCREEN_HEIGHT - 50))
            pygame.display.flip()
            clock.tick(60)


if __name__ == "__main__":
    main()

