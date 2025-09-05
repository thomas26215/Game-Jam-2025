# --- main.py avec gestion complète des menus ---
import pygame
from infos_hud import InfoHUD
from portail import Portail
from room import generate_random_grid, draw_portal_if_boss_room
from player import Player
from menu import Menu, init_menus
import sys
from pygame.locals import *
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    MINIMAP_SCALE, MINIMAP_MARGIN,
    STATE_MENU, STATE_PLAY, STATE_PAUSE, STATE_GAME_OVER, STATE_BACK, STATE_VICTORY, STATE_OPTIONS,
    FONT
)
from gameSettings import GameSettings

pygame.init()

pygame.joystick.init()
for i in range(pygame.joystick.get_count()):
    pygame.joystick.Joystick(i).init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Contagium")
clock = pygame.time.Clock()

# Musique d'ambiance
pygame.mixer.music.load("bruitages/medieval-ambient-236809.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(loops=-1)

# Fonction draw_minimap utilitaire (reste en dehors de GameManager)
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

# Classe GameManager centralisant la logique de jeu
class GameManager:
    def __init__(self, settings):
        self.settings = settings
        self.grid = None
        self.current_pos = None
        self.current_room = None
        self.player = None
        self.hud = None
        self.visited_rooms = set()
        self.has_taken_first_med = False

        self.shadow_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.VISION_RADIUS = 300

    def init_game(self):
        self.grid = generate_random_grid(num_rooms=10)
        self.current_pos = (0, 0)
        self.current_room = self.grid[self.current_pos]

        self.player = Player(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, self.settings,
            SCREEN_WIDTH, SCREEN_HEIGHT,
            walk_spritesheet_path="player/walk.png",
            idle_spritesheet_path="player/idle.png",
            attack_spritesheet_path="player/attack.png",
            hurt_spritesheet_path="player/damage.png",
            death_spritesheets=["player/death1.png", "player/death2.png"],
            frame_width=64, frame_height=64
        )
        self.current_room.generate_contents(self.player, SCREEN_WIDTH, SCREEN_HEIGHT)

        self.hud = InfoHUD(max_lives=3, current_lives=3)
        self.hud.set_poisoned(True)

        self.visited_rooms = set()
        self.visited_rooms.add(self.current_pos)
        self.has_taken_first_med = False

    def update_player(self, keys):
        self.player.update(keys, self.current_room)

    def check_player_attack(self):
        if self.player.state == "attack" and hasattr(self.player, "attack_rect") and not self.player.has_hit_enemy:
            for enemy in self.current_room.enemies:
                if enemy.alive and self.player.attack_rect.colliderect(enemy.rect):
                    enemy.take_damage()
                    self.player.has_hit_enemy = True
                    break

    def update_enemies(self):
        for enemy in self.current_room.enemies:
            enemy.update(self.current_room)
        self.current_room.enemies = [e for e in self.current_room.enemies if e.alive]

    def update_medicaments(self):
        for med in self.current_room.medicaments:
            med.update()
            if not med.collected and self.player.rect.colliderect(med.rect):
                med.collect()
                self.hud.add_med()
                if self.current_pos == (0, 0):
                    self.has_taken_first_med = True
        self.current_room.update_medicaments_state()

    def try_change_room(self):
        player_points = [
            self.player.hitbox.topleft,
            self.player.hitbox.topright,
            self.player.hitbox.bottomleft,
            self.player.hitbox.bottomright,
            self.player.hitbox.midtop,
            self.player.hitbox.midbottom,
            self.player.hitbox.midleft,
            self.player.hitbox.midright
        ]
        for direction, door in self.current_room.doors:
            if any(door.collidepoint(p) for p in player_points):
                r, c = self.current_pos
                new_pos = {
                    'up': (r - 1, c),
                    'down': (r + 1, c),
                    'left': (r, c - 1),
                    'right': (r, c + 1)
                }.get(direction, self.current_pos)

                if self.current_pos == (0, 0) and not self.has_taken_first_med:
                    return False

                if new_pos in self.grid:
                    self.current_pos = new_pos
                    self.current_room = self.grid[new_pos]
                    self.visited_rooms.add(new_pos)
                    self.current_room.generate_contents(self.player, SCREEN_WIDTH, SCREEN_HEIGHT)
                    self.reposition_player(direction)
                    return True
        return False

    def reposition_player(self, direction):
        if direction == 'up':
            self.player.rect.bottom = SCREEN_HEIGHT - 60
        elif direction == 'down':
            self.player.rect.top = 60
        elif direction == 'left':
            self.player.rect.right = SCREEN_WIDTH - 60
        elif direction == 'right':
            self.player.rect.left = 60
        self.player.hitbox.center = self.player.rect.center

    def teleport_to_start(self):
        """Ramène le joueur dans la salle (0,0)"""
        self.current_pos = (0, 0)
        self.current_room = self.grid[self.current_pos]
        self.current_room.generate_contents(self.player, SCREEN_WIDTH, SCREEN_HEIGHT)

        # Repositionner le joueur au centre
        self.player.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.player.hitbox.center = self.player.rect.center

        # Marquer la salle comme visitée
        self.visited_rooms.add(self.current_pos)


    def draw(self, screen):
        self.current_room.draw(screen)
        self.current_room.draw_contents(screen)

        on_portal = draw_portal_if_boss_room(screen, self.current_room, self.player, self.settings)

        screen.blit(self.player.image, self.player.rect)
        pygame.draw.rect(screen, (255, 0, 0), self.player.hitbox, 2)

        for enemy in self.current_room.enemies:
            enemy.draw(screen)
            pygame.draw.rect(screen, (255, 0, 0), enemy.rect, 2)

        for med in self.current_room.medicaments:
            med.draw(screen)

        self.shadow_surface.fill((0, 0, 0, 255))
        for r in range(self.VISION_RADIUS, 0, -2):
            t = r / self.VISION_RADIUS
            alpha = int(255 * (1 - (1 - t) ** 3))
            pygame.draw.circle(self.shadow_surface, (0, 0, 0, alpha), self.player.rect.center, r)

        screen.blit(self.shadow_surface, (0, 0))

        draw_minimap(screen, self.grid, self.current_pos, self.visited_rooms)

        self.hud.set_lives(self.player.health)
        self.hud.draw(screen)

        if self.current_pos == (0, 0) and not self.has_taken_first_med:
            message = FONT.render("Récupérez le médicament pour continuer !", True, (255, 0, 0))
            msg_x = SCREEN_WIDTH // 2 - message.get_width() // 2
            msg_y = 20
            screen.blit(message, (msg_x, msg_y))

    def player_on_portal_interact(self):
        keys = pygame.key.get_pressed()
        interact_pressed = any(keys[key] for key in self.settings.get_control("interact", "keyboard"))
        if self.player.joystick and not interact_pressed:
            interact_pressed = any(self.player.joystick.get_button(btn) for btn in self.settings.get_control("interact", "gamepad"))
        
        on_portal = draw_portal_if_boss_room(pygame.display.get_surface(), self.current_room, self.player, self.settings)
        print(on_portal, interact_pressed)
        
        if on_portal and interact_pressed:
            # Téléporter le joueur dans la salle (0,0) au lieu de terminer
            self.current_pos = (0, 0)
            self.current_room = self.grid[self.current_pos]
            self.current_room.generate_contents(self.player, SCREEN_WIDTH, SCREEN_HEIGHT)
            
            # Repositionner le joueur au centre
            self.player.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            self.player.hitbox.center = self.player.rect.center
            
            # Marquer la salle comme visitée
            self.visited_rooms.add(self.current_pos)
            
            return True  # Interaction réussie
        return False



# --- boucle principale ---
def main():
    settings = GameSettings()  # Créer l'instance des settings
    state = STATE_MENU
    menus = init_menus(settings)  # Passer les settings aux menus

    game_manager = GameManager(settings)

    running = True
    fade_start_time = None
    fade_duration = 5000  # 5 secondes en millisecondes

    while running:
        dt = clock.tick(60)  # Frame rate

        # --- Fondu vers Game Over ---
        if state == "FADE_TO_GAME_OVER":
            if fade_start_time is None:
                fade_start_time = pygame.time.get_ticks()
            elapsed = pygame.time.get_ticks() - fade_start_time

            # Dessin figé
            game_manager.current_room.draw(screen)
            game_manager.current_room.draw_contents(screen)
            screen.blit(game_manager.player.image, game_manager.player.rect)
            for enemy in game_manager.current_room.enemies:
                enemy.draw(screen)
            for med in game_manager.current_room.medicaments:
                med.draw(screen)

            draw_minimap(screen, game_manager.grid, game_manager.current_pos, game_manager.visited_rooms)

            game_manager.hud.set_lives(game_manager.player.health)
            game_manager.hud.draw(screen)

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
        elif state in [STATE_MENU, STATE_PAUSE, STATE_OPTIONS, STATE_GAME_OVER]:
            menus[state].update(dt)
            menus[state].draw(screen)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                    break

                action = menus[state].handle_event(event)
                if action == "QUIT":
                    running = False
                    break
                elif action == STATE_BACK:
                    # Retour au menu précédent
                    if state == STATE_OPTIONS:
                        state = STATE_MENU
                elif action == "CONTROLS":
                    state = "CONTROLS"
                elif action is not None:
                    if action == STATE_PLAY and state in [STATE_MENU, STATE_GAME_OVER]:
                        game_manager.init_game()
                    state = action

        # Menu de contrôles
        elif state == "CONTROLS":
            menus["CONTROLS"].draw(screen)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                    break

                action = menus["CONTROLS"].handle_event(event)
                if action == STATE_BACK:
                    state = STATE_OPTIONS

        # État de victoire
        elif state == STATE_VICTORY:
            # Afficher les boutons du menu de victoire
            if STATE_VICTORY not in menus:
                victory_menu = Menu(settings, "wordsGame/victory.png")
                victory_menu.add_button("Rejouer", STATE_PLAY)
                victory_menu.add_button("Menu Principal", STATE_MENU)
                victory_menu.add_button("Quitter", "QUIT")
                menus[STATE_VICTORY] = victory_menu
            
            # Dessiner le menu de victoire avec l'image
            menus[STATE_VICTORY].draw(screen)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                    break
                
                action = menus[STATE_VICTORY].handle_event(event)
                if action == "QUIT":
                    running = False
                    break
                elif action == STATE_PLAY:
                    game_manager.init_game()
                    state = STATE_PLAY
                elif action == STATE_MENU:
                    state = STATE_MENU

        # État de jeu normal
        elif state == STATE_PLAY:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                    break
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    state = STATE_PAUSE
                elif event.type == KEYDOWN and event.key == K_SPACE:
                    game_manager.player.attack()

            if not running:
                break

            keys = pygame.key.get_pressed()

            game_manager.update_player(keys)
            game_manager.check_player_attack()
            game_manager.update_enemies()
            game_manager.update_medicaments()
            game_manager.try_change_room()

            game_manager.draw(screen)

            if game_manager.player_on_portal_interact():
                game_manager.teleport_to_start()

            pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

