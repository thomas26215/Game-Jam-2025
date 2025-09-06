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
    FONT,
    COLLECT_MEDECINE, HEAL_INFECTED
)
from gameSettings import GameSettings

pygame.init()

pygame.joystick.init()
for i in range(pygame.joystick.get_count()):
    pygame.joystick.Joystick(i).init()

# --- plein écran natif ---
info = pygame.display.Info()
screen = pygame.display.set_mode((info.current_w, info.current_h))
pygame.display.set_caption("Contagium")

# surface logique du jeu
game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

# coordonnées pour centrer la surface logique sur l’écran
center_x = (info.current_w - SCREEN_WIDTH) // 2
center_y = (info.current_h - SCREEN_HEIGHT) // 2

clock = pygame.time.Clock()

# Musique
pygame.mixer.music.load("bruitages/medieval-ambient-236809.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(loops=-1)

# --- minimap ---
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

# --- GameManager identique ---
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
        self.VISION_RADIUS = self.settings.vision_radius

    def init_game(self):
        self.grid = generate_random_grid(num_rooms=10)
        self.current_pos = (0, 0)
        self.current_room = self.grid[self.current_pos]
        self.hud = InfoHUD(max_lives=3, current_lives=3)
        self.hud.set_poisoned(True)
        self.player = Player(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, self.settings,
            SCREEN_WIDTH, SCREEN_HEIGHT,
            walk_spritesheet_path="player/walk.png",
            idle_spritesheet_path="player/idle.png",
            attack_spritesheet_path="player/attack.png",
            hurt_spritesheet_path="player/damage.png",
            death_spritesheets=["player/death1.png", "player/death2.png"],
            frame_width=64, frame_height=64,
            throw_spritesheet_path="player/attack_potion.png",
            hud=self.hud
        )
        self.current_room.generate_contents(self.player, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.visited_rooms = {self.current_pos}
        self.has_taken_first_med = False

    def update_player(self, keys):
        self.player.update(keys, self.current_room)

    def check_player_attack(self, quest=COLLECT_MEDECINE):
        """
        Applique les dégâts aux ennemis si le joueur attaque (normale ou splash).
        L'attaque normale et le splash utilisent la même logique,
        seule l'animation diffère.
        """
        if (self.player.state in ["attack", "throw"] and 
            hasattr(self.player, "attack_rect") and 
            not self.player.has_hit_enemy):
            
            attack_rect = self.player.attack_rect
            for enemy in self.current_room.enemies:
                if enemy.alive and attack_rect.colliderect(enemy.hitbox):
                    damage = 1 if quest == COLLECT_MEDECINE else 3
                    enemy.take_damage(damage=damage)
                    # print("quéte:", quest, " - Ennemi touché ! Vie restante :", enemy.health)
                    # On ne touche qu’un ennemi par frame pour éviter multi-hit
                    break
            
            self.player.has_hit_enemy = True


    def update_enemies(self):
        for enemy in self.current_room.enemies:
            enemy.update(self.current_room)
        # Mettre à jour l'état dans la salle pour sauvegarder les morts
        if hasattr(self.current_room, "update_enemies_state"):
            self.current_room.update_enemies_state()
        # Supprimer les ennemis morts
        self.current_room.enemies = [e for e in self.current_room.enemies if e.alive]

    def update_medicaments(self):
        for med in self.current_room.medicaments:
            med.update()
            if not med.collected and self.player.rect.colliderect(med.rect):
                med.collect()
                self.hud.add_med()
                if self.current_pos == (0, 0):
                    self.has_taken_first_med = True
        if hasattr(self.current_room, "update_medicaments_state"):
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
                    # 🔹 Sauvegarder l'état des ennemis avant de quitter
                    if hasattr(self.current_room, "update_enemies_state"):
                        self.current_room.update_enemies_state()
                    
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
        # 🔹 Sauvegarder l'état des ennemis actuels
        if hasattr(self.current_room, "update_enemies_state"):
            self.current_room.update_enemies_state()
        
        self.current_pos = (0, 0)
        self.current_room = self.grid[self.current_pos]
        self.current_room.generate_contents(self.player, SCREEN_WIDTH, SCREEN_HEIGHT)

        # Repositionner le joueur au centre
        self.player.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.player.hitbox.center = self.player.rect.center

        # Marquer la salle comme visitée
        self.visited_rooms.add(self.current_pos)
        
    def draw(self, surface, quest):
        self.current_room.draw(surface)
        self.current_room.draw_contents(surface)
        draw_portal_if_boss_room(surface, self.current_room, self.player, self.settings)
        surface.blit(self.player.image, self.player.rect)

        for enemy in self.current_room.enemies:
            enemy.draw(surface)

        for med in self.current_room.medicaments:
            med.draw(surface)

        vision_radius = self.settings.vision_radius
        if quest == COLLECT_MEDECINE:
            self.shadow_surface.fill((0, 0, 0, 255))
            for r in range(vision_radius, 0, -2):
                t = r / vision_radius
                alpha = int(255 * (1 - (1 - t) ** 3))
                pygame.draw.circle(self.shadow_surface, (0, 0, 0, alpha), self.player.rect.center, r)
        else:
            self.shadow_surface.fill((0, 82, 0, 255))
            for r in range(vision_radius, 0, -2):
                t = r / vision_radius
                alpha = int(255 * (1 - (1 - t) ** 3))
                pygame.draw.circle(self.shadow_surface, (0, 82, 0, alpha), self.player.rect.center, r)

        surface.blit(self.shadow_surface, (0, 0))
        draw_minimap(surface, self.grid, self.current_pos, self.visited_rooms)
        self.hud.set_lives(self.player.health)
        self.hud.draw(surface)

        if self.current_pos == (0, 0) and not self.has_taken_first_med:
            message = FONT.render("Récupérez la potion pour continuer !", True, (255, 0, 0))
            surface.blit(message, (SCREEN_WIDTH // 2 - message.get_width() // 2, 20))


    # --- fonctions utilitaires pile ---
def push_state(stack, new_state):
    stack.append(new_state)

def pop_state(stack, fallback=STATE_MENU):
    """Retire l’état courant et renvoie l’état précédent ou fallback."""
    if len(stack) > 1:
        stack.pop()
    return stack[-1] if stack else fallback

# --- boucle principale ---
def main():
    settings = GameSettings()
    quest = COLLECT_MEDECINE
    menus = init_menus(settings)
    game_manager = GameManager(settings)
    running = True

    # pile contenant toujours l’état courant en dernière position
    state_stack = [STATE_MENU]

    fade_start_time = None
    fade_duration = 5000

    while running:
        dt = clock.tick(60)
        state = state_stack[-1]     # état actif

        # ----------- Transition de fade -----------
        if state == "FADE_TO_GAME_OVER":
            if fade_start_time is None:
                fade_start_time = pygame.time.get_ticks()
            elapsed = pygame.time.get_ticks() - fade_start_time

            game_surface.fill((0, 0, 0))
            game_manager.current_room.draw(game_surface)
            game_manager.current_room.draw_contents(game_surface)
            game_surface.blit(game_manager.player.image, game_manager.player.rect)
            for enemy in game_manager.current_room.enemies:
                enemy.draw(game_surface)
            for med in game_manager.current_room.medicaments:
                med.draw(game_surface)

            draw_minimap(game_surface, game_manager.grid, game_manager.current_pos, game_manager.visited_rooms)
            game_manager.hud.set_lives(game_manager.player.health)
            game_manager.hud.draw(game_surface)

            alpha = min(255, int(255 * (elapsed / fade_duration)))
            fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            fade_surface.set_alpha(alpha)
            fade_surface.fill((0, 0, 0))
            game_surface.blit(fade_surface, (0, 0))

            screen.fill((0, 0, 0))
            screen.blit(game_surface, (center_x, center_y))
            pygame.display.flip()

            if elapsed >= fade_duration:
                state_stack[-1] = STATE_GAME_OVER
                fade_start_time = None
            continue


        # ----------- Menus & sous-menus -----------
        if state in [STATE_MENU, STATE_PAUSE, STATE_OPTIONS, STATE_GAME_OVER, STATE_VICTORY, "CONTROLS"]:
            game_surface.fill((0, 0, 0))
            if state in menus and hasattr(menus[state], "update"):
                menus[state].update(dt)
            if state in menus:
                menus[state].draw(game_surface)

            screen.fill((0, 0, 0))
            screen.blit(game_surface, (center_x, center_y))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False

                action = menus[state].handle_event(event) if state in menus else None

                if action == "QUIT":
                    running = False

                elif action == STATE_PLAY:
                    # Si on lance une partie depuis le menu principal ou le game over
                    if state in [STATE_MENU, STATE_GAME_OVER]:
                        game_manager.init_game()
                        state_stack = [STATE_PLAY]   # on remplace la pile par PLAY
                    else:
                        state_stack[-1] = STATE_PLAY

                elif action == STATE_BACK:
                    # retour à l’écran précédent
                    new_state = pop_state(state_stack)
                    state_stack[-1] = new_state

                elif action in ("CONTROLS", STATE_OPTIONS, "CREDITS", "TUTORIAL"):
                    # tout sous-menu : on empile
                    push_state(state_stack, action)

                elif action:
                    # tout autre état générique
                    push_state(state_stack, action)

        # ----------- Menu crédits séparé -----------
        elif state == "CREDITS":
            game_surface.fill((0, 0, 0))
            from menu import draw_credits_menu, handle_credits_event
            draw_credits_menu(game_surface)
            screen.fill((0, 0, 0))
            screen.blit(game_surface, (center_x, center_y))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                action = handle_credits_event(event)
                if action == STATE_BACK or action == STATE_MENU:
                    pop_state(state_stack)

        # ----------- Menu didacticiel séparé -----------
        elif state == "TUTORIAL":
            game_surface.fill((0, 0, 0))
            from menu import draw_tutorial_menu, handle_tutorial_event
            draw_tutorial_menu(game_surface)
            screen.fill((0, 0, 0))
            screen.blit(game_surface, (center_x, center_y))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                action = handle_tutorial_event(event)
                if action == STATE_MENU:
                    pop_state(state_stack)

        # ----------- Jeu en cours -----------
        elif state == STATE_PLAY:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    push_state(state_stack, STATE_PAUSE)
                elif event.type == KEYDOWN and event.key in settings.get_control("attack", "keyboard"):
                    if quest == COLLECT_MEDECINE:
                        game_manager.player.attack(COLLECT_MEDECINE)
                    else:
                        game_manager.player.attack(HEAL_INFECTED)
                elif event.type == JOYBUTTONDOWN and event.button in settings.get_control("attack", "gamepad"):
                    if quest == COLLECT_MEDECINE:
                        game_manager.player.attack(COLLECT_MEDECINE)
                    else:
                        game_manager.player.attack(HEAL_INFECTED)

            keys = pygame.key.get_pressed()
            game_manager.update_player(keys)
            game_manager.check_player_attack(quest)
            game_manager.update_enemies()
            game_manager.update_medicaments()
            game_manager.try_change_room()

            if game_manager.player.health <= 0:
                state_stack[-1] = "FADE_TO_GAME_OVER"
                quest = COLLECT_MEDECINE
                fade_start_time = None

            game_surface.fill((0, 0, 0))
            game_manager.draw(game_surface, quest)

            screen.fill((0, 0, 0))
            screen.blit(game_surface, (center_x, center_y))
            pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()