# --- main.py corrigé ---
import pygame
from infos_hud import InfoHUD
from enemy import Enemy
from medicament import Medicament
from room import Room
from player import Player
import random
import math
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
pygame.display.set_caption("Contagium")
clock = pygame.time.Clock()


def draw_minimap(surface, grid, current_pos, visited_rooms):
    if not visited_rooms:
        return
    rows = [r for r, _ in visited_rooms]
    cols = [c for _, c in visited_rooms]
    min_r, max_r, min_c, max_c = min(rows), max(rows), min(cols), max(cols)
    width = (max_c - min_c + 1) * MINIMAP_SCALE
    height = (max_r - min_r + 1) * MINIMAP_SCALE
    x_offset, y_offset = SCREEN_WIDTH - width - MINIMAP_MARGIN, MINIMAP_MARGIN

    # 🔹 Dessiner les connexions
    for (r, c) in visited_rooms:
        room = grid[(r, c)]
        x, y = x_offset + (c - min_c) * MINIMAP_SCALE + MINIMAP_SCALE // 2, \
               y_offset + (r - min_r) * MINIMAP_SCALE + MINIMAP_SCALE // 2
        for direction, _ in room.doors:
            dr, dc = {'up': (-1, 0), 'down': (1, 0), 'left': (0, -1), 'right': (0, 1)}[direction]
            neighbor = (r + dr, c + dc)
            if neighbor in visited_rooms:
                nx = x_offset + (neighbor[1] - min_c) * MINIMAP_SCALE + MINIMAP_SCALE // 2
                ny = y_offset + (neighbor[0] - min_r) * MINIMAP_SCALE + MINIMAP_SCALE // 2
                pygame.draw.line(surface, (100, 100, 100), (x, y), (nx, ny), 2)

    # 🔹 Dessiner les salles
    for (r, c) in visited_rooms:
        room = grid[(r, c)]
        x, y = x_offset + (c - min_c) * MINIMAP_SCALE, y_offset + (r - min_r) * MINIMAP_SCALE
        if (r, c) == current_pos:
            color = (255, 0, 0)  # salle actuelle
        elif getattr(room, "is_final", False):
            color = (255, 255, 0)  # salle finale
        else:
            color = (200, 200, 200)  # salle normale
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


def generate_random_grid(num_rooms=6):
    grid = {}
    start = (0, 0)
    grid[start] = Room(start, random_color(), "Salle de départ", nb_medicaments=1, nb_ennemis=0)
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    dx, dy = random.choice(directions)
    enemy_room_pos = (start[0] + dx, start[1] + dy)
    grid[enemy_room_pos] = Room(enemy_room_pos, random_color(), "Salle des ennemis", nb_medicaments=0, nb_ennemis=2)

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
                grid[pos] = Room(pos, random_color(), f"Salle {i+1}", nb_medicaments=0)
                current_positions.append(pos)
                break

    farthest_pos = max(grid.keys(), key=lambda pos: abs(pos[0]) + abs(pos[1]))
    final_room = grid[farthest_pos]
    final_room.nb_enemies_in_room = 8
    final_room.description = "Salle Finale"
    final_room.is_final = True
    total_meds = 30
    all_rooms_except_start = [room for pos, room in grid.items() if pos != start]
    for _ in range(total_meds):
        room = random.choice(all_rooms_except_start)
        room.nb_medicaments += 1
    for room in grid.values():
        room.generate_walls_and_doors(grid)
    return grid


def random_color():
    return (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))


def main():
    state = STATE_MENU
    grid = generate_random_grid(num_rooms=10)
    current_pos, current_room = (0, 0), grid[(0, 0)]
    player = Player(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, SCREEN_WIDTH, SCREEN_HEIGHT,
                    walk_spritesheet_path="player/idle.png",
                    idle_spritesheet_path="player/idle.png",
                    frame_width=64, frame_height=64)

    current_room.generate_contents(player, SCREEN_WIDTH, SCREEN_HEIGHT)
    hud = InfoHUD()
    has_taken_first_med = False
    visited_rooms = set()
    visited_rooms.add(current_pos)

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

            for enemy in current_room.enemies:
                enemy.update(current_room.walls)
            for med in current_room.medicaments:
                med.update()
                if player.rect.colliderect(med.rect):
                    med.collect()
                    if current_pos == (0, 0):
                        has_taken_first_med = True

            current_room.update_medicaments_state()

            for direction, door in current_room.doors:
                if player.rect.colliderect(door):
                    r, c = current_pos
                    new_pos = {
                        'up': (r - 1, c), 'down': (r + 1, c),
                        'left': (r, c - 1), 'right': (r, c + 1)
                    }.get(direction, current_pos)
                    if current_pos == (0, 0) and not has_taken_first_med:
                        break
                    if new_pos in grid:
                        current_pos, current_room = new_pos, grid[new_pos]
                        visited_rooms.add(current_pos)
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

            current_room.draw(screen)
            current_room.draw_contents(screen)

            # 🔹 Correction : utiliser player.image au lieu de player.surf
            screen.blit(player.image, player.rect)

            for enemy in current_room.enemies:
                enemy.draw(screen)
            for med in current_room.medicaments:
                med.draw(screen)
            draw_minimap(screen, grid, current_pos, visited_rooms)
            hud.draw(screen)
            screen.blit(FONT.render(f"{current_room.description} {current_pos}", True, (255, 255, 255)), (10, SCREEN_HEIGHT - 50))

            if current_pos == (0, 0) and not has_taken_first_med:
                message = FONT.render("Récupérez le médicament pour continuer !", True, (255, 0, 0))
                msg_x = SCREEN_WIDTH // 2 - message.get_width() // 2
                msg_y = 20
                screen.blit(message, (msg_x, msg_y))

            pygame.display.flip()
            clock.tick(60)


if __name__ == "__main__":
    main()

