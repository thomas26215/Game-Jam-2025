# --- main.py avec gestion complète des menus ---
import pygame
from infos_hud import InfoHUD
from enemy import Enemy
from medicament import Medicament
from room import Room
from player import Player
import random
from menu import init_menus, Menu
import sys
from pygame.locals import *
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    MINIMAP_SCALE, MINIMAP_MARGIN,
    STATE_MENU, STATE_PLAY, STATE_PAUSE, STATE_GAME_OVER, STATE_OPTIONS,
    FONT
)

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Contagium")
clock = pygame.time.Clock()


# --- fonctions utilitaires ---
def draw_minimap(surface, grid, current_pos, visited_rooms):
    if not visited_rooms:
        return
    rows = [r for r, _ in visited_rooms]
    cols = [c for _, c in visited_rooms]
    min_r, max_r, min_c, max_c = min(rows), max(rows), min(cols), max(cols)
    width = (max_c - min_c + 1) * MINIMAP_SCALE
    height = (max_r - min_r + 1) * MINIMAP_SCALE
    x_offset, y_offset = SCREEN_WIDTH - width - MINIMAP_MARGIN, MINIMAP_MARGIN

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

    for (r, c) in visited_rooms:
        room = grid[(r, c)]
        x, y = x_offset + (c - min_c) * MINIMAP_SCALE, y_offset + (r - min_r) * MINIMAP_SCALE
        if (r, c) == current_pos:
            color = (255, 0, 0)
        elif getattr(room, "is_final", False):
            color = (255, 255, 0)
        else:
            color = (200, 200, 200)
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
    # Salle de départ sans TMX
    grid[start] = Room(
        position=start,
        tmx_file="maps/left_top.tmx",
        color=random_color(),
        description="Salle de départ",
        nb_medicaments=1,
        nb_ennemis=0
    )

    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    dx, dy = random.choice(directions)
    enemy_room_pos = (start[0] + dx, start[1] + dy)
    grid[enemy_room_pos] = Room(
        position=enemy_room_pos,
        tmx_file="maps/left_top.tmx",
        color=random_color(),
        description="Salle des ennemis",
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
                    tmx_file=None,
                    color=random_color(),
                    description=f"Salle {i+1}",
                    nb_medicaments=0
                )
                current_positions.append(pos)
                break

    # Salle finale
    farthest_pos = max(grid.keys(), key=lambda pos: abs(pos[0]) + abs(pos[1]))
    final_room = grid[farthest_pos]
    final_room.nb_enemies_in_room = 8
    final_room.description = "Salle Finale"
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


def random_color():
    return (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))


# --- boucle principale ---
def main():
    state = STATE_MENU
    menus = init_menus()
    
    # Initialisation des variables de jeu
    grid = None
    current_pos = None
    current_room = None
    player = None
    hud = None
    shadow_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    VISION_RADIUS = 300
    has_taken_first_med = False
    visited_rooms = set()
    
    # Initialisation du jeu
    def init_game():
        nonlocal grid, current_pos, current_room, player, hud, has_taken_first_med, visited_rooms
        
        grid = generate_random_grid(num_rooms=10)
        current_pos, current_room = (0, 0), grid[(0, 0)]

        player = Player(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, SCREEN_WIDTH, SCREEN_HEIGHT,
                        walk_spritesheet_path="player/walk.png",
                        idle_spritesheet_path="player/idle.png",
                        attack_spritesheet_path="player/attack.png",
                        hurt_spritesheet_path="player/damage.png",
                        death_spritesheets=["player/death1.png", "player/death2.png"],
                        frame_width=64, frame_height=64)

        current_room.generate_contents(player, SCREEN_WIDTH, SCREEN_HEIGHT)
        hud = InfoHUD(max_lives=3, current_lives=3)
        hud.set_poisoned(True)

        has_taken_first_med = False
        visited_rooms = set()
        visited_rooms.add(current_pos)
    
    running = True
    fade_start_time = None
    fade_duration = 5000  # 5 secondes en millisecondes
    while running:
        dt = clock.tick(60)  # Get delta time for animation
        
     # --- Fondu vers Game Over ---
        if state == "FADE_TO_GAME_OVER":
            if fade_start_time is None:
                fade_start_time = pygame.time.get_ticks()
            elapsed = pygame.time.get_ticks() - fade_start_time

            # Dessin du jeu figé
            current_room.draw(screen)
            current_room.draw_contents(screen)
            screen.blit(player.image, player.rect)
            for enemy in current_room.enemies:
                enemy.draw(screen)
            for med in current_room.medicaments:
                med.draw(screen)
            draw_minimap(screen, grid, current_pos, visited_rooms)
            hud.set_lives(player.health)
            hud.draw(screen)
            screen.blit(
                FONT.render(f"{current_room.description} {current_pos}", True, (255, 255, 255)),
                (10, SCREEN_HEIGHT - 50)
            )

            # Fondu noir progressif
            alpha = min(255, int(255 * (elapsed / fade_duration)))
            fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            fade_surface.set_alpha(alpha)
            fade_surface.fill((0, 0, 0))
            screen.blit(fade_surface, (0, 0))
            pygame.display.flip()

            if elapsed >= fade_duration:
                state = STATE_GAME_OVER
                fade_start_time = None
            continue
        
        
    # Gestion des menus
        if state in [STATE_MENU, STATE_PAUSE, STATE_OPTIONS, STATE_GAME_OVER]:
    
    
            # Update menu animation
            menus[state].update(dt)
            
            # Dessiner le menu approprié
            menus[state].draw(screen)
            pygame.display.flip()
            
            # Gérer les événements du menu
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                    break
                
                action = menus[state].handle_event(event)
                if action == "QUIT":
                    running = False
                    break
                elif action == "BACK":
                    # Retour au menu précédent
                    if state == STATE_OPTIONS:
                        state = STATE_MENU
                elif action is not None:
                    if action == STATE_PLAY and state == STATE_MENU:
                        # Nouvelle partie
                        init_game()
                    elif action == STATE_PLAY and state == STATE_GAME_OVER:
                        # Recommencer après un game over
                        init_game()
                    state = action

        # État de victoire
        elif state == "VICTORY":
            # Afficher écran de victoire
            
            # Titre de victoire
            victory_title = FONT.render("VICTOIRE !", True, (255, 255, 0))
            victory_text = FONT.render("Vous avez collecté 30 médicaments !", True, (255, 255, 255))
            
            screen.blit(victory_title, (SCREEN_WIDTH // 2 - victory_title.get_width() // 2, 100))
            screen.blit(victory_text, (SCREEN_WIDTH // 2 - victory_text.get_width() // 2, 150))
            
            # Afficher les boutons du menu de victoire
            if "VICTORY" not in menus:
                victory_menu = Menu()
                victory_menu.add_button("Rejouer", STATE_PLAY)
                victory_menu.add_button("Menu Principal", STATE_MENU)
                victory_menu.add_button("Quitter", "QUIT")
                menus["VICTORY"] = victory_menu
            
            # Dessiner les boutons manuellement
            for i, button in enumerate(menus["VICTORY"].buttons):
                color = (255, 0, 0) if i == menus["VICTORY"].current_selection else (255, 255, 255)
                button_surface = FONT.render(button["text"], True, color)
                y_pos = 280 + i * 100
                button_rect = button_surface.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
                
                # Fond semi-transparent pour les boutons
                button_bg = pygame.Surface((button_surface.get_width() + 20, button_surface.get_height() + 10))
                button_bg.set_alpha(128)
                button_bg.fill((0, 0, 0))
                screen.blit(button_bg, (button_rect.x - 10, button_rect.y - 5))
                screen.blit(button_surface, button_rect)
            
            pygame.display.flip()
            
            # Gérer les événements du menu de victoire
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                    break
                
                action = menus["VICTORY"].handle_event(event)
                if action == "QUIT":
                    running = False
                    break
                elif action == STATE_PLAY:
                    # Recommencer une nouvelle partie
                    init_game()
                    state = STATE_PLAY
                elif action == STATE_MENU:
                    state = STATE_MENU
        
        # État de jeu normal
        elif state == STATE_PLAY:
            # --- Gestion des événements ---
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                    break
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    state = STATE_PAUSE
                elif event.type == KEYDOWN and event.key == K_SPACE:
                    player.attack()
            
            if not running:
                break
                
            # Mise à jour du jeu
            keys = pygame.key.get_pressed()
            player.update(keys)

            # --- Vérification défaite (joueur mort) ---
            if player.health <= 0:
                state = "FADE_TO_GAME_OVER"
                fade_start_time = None
                continue

            # --- Vérification victoire (30 médicaments) ---
            if hud.meds_collected >= 30:
                state = "VICTORY"
                continue

            # --- Gestion des attaques du joueur ---
            if player.state == "attack" and hasattr(player, "attack_rect") and not player.has_hit_enemy:
                for enemy in current_room.enemies:
                    if enemy.alive and player.attack_rect.colliderect(enemy.rect):
                        enemy.take_damage()
                        player.has_hit_enemy = True  # ✅ Empêche les multi-dégâts par attaque
                        break  # ✅ Un seul ennemi touché par attaque

            # --- Mise à jour des ennemis ---
            for enemy in current_room.enemies:
                enemy.update()

            # --- Supprimer les ennemis morts ---
            current_room.enemies = [e for e in current_room.enemies if e.alive]

            # --- Médicaments ---
            for med in current_room.medicaments:
                med.update()
                if not med.collected and player.rect.colliderect(med.rect):
                    med.collect()
                    hud.add_med()
                    if current_pos == (0, 0):
                        has_taken_first_med = True

            current_room.update_medicaments_state()

            # --- Changement de salle ---
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
                            player.rect.bottom = SCREEN_HEIGHT - 60
                        elif direction == 'down':
                            player.rect.top = 60
                        elif direction == 'left':
                            player.rect.right = SCREEN_WIDTH - 60
                        elif direction == 'right':
                            player.rect.left = 60
                    break

            # --- Dessin ---
            current_room.draw(screen)
            current_room.draw_contents(screen)
            screen.blit(player.image, player.rect)
            for enemy in current_room.enemies:
                enemy.draw(screen)
            for med in current_room.medicaments:
                med.draw(screen)

            # Ombre dynamique
            shadow_surface.fill((0, 0, 0, 200))
            for r in range(VISION_RADIUS, 0, -2):
                t = r / VISION_RADIUS
                alpha = int(200 * (1 - (1 - t) ** 3))
                pygame.draw.circle(shadow_surface, (0, 0, 0, alpha), player.rect.center, r)
            screen.blit(shadow_surface, (0, 0))

            # Minimap + HUD
            draw_minimap(screen, grid, current_pos, visited_rooms)
            hud.set_lives(player.health)
            hud.draw(screen)

            # Texte salle actuelle
            screen.blit(
                FONT.render(f"{current_room.description} {current_pos}", True, (255, 255, 255)),
                (10, SCREEN_HEIGHT - 50)
            )

            # Message tuto
            if current_pos == (0, 0) and not has_taken_first_med:
                message = FONT.render("Récupérez le médicament pour continuer !", True, (255, 0, 0))
                msg_x = SCREEN_WIDTH // 2 - message.get_width() // 2
                msg_y = 20
                screen.blit(message, (msg_x, msg_y))

            pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()