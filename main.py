import pygame
from draw_minimap import draw_minimap
from game import GameManager
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
                        if hasattr(game_manager, "end_timer"):
                            del game_manager.end_timer
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

            if game_manager.player_on_portal_interact(quest):
                quest = HEAL_INFECTED

            if game_manager.draw_end_sequence(screen) == True:
                state_stack[-1] = STATE_VICTORY
                quest = COLLECT_MEDECINE
            
            if game_manager.draw_end_sequence(screen) == False:
                state_stack[-1] = "FADE_TO_GAME_OVER"
                quest = COLLECT_MEDECINE

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

