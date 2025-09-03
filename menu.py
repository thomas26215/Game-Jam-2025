import pygame
from pygame.locals import *
from config import (
    SCREEN_WIDTH,
    STATE_MENU, STATE_PLAY, STATE_PAUSE, STATE_GAME_OVER, STATE_OPTIONS,
    FONT
)

# Créer une classe Menu pour une meilleure organisation
class Menu:
    def __init__(self):
        self.buttons = []
        self.current_selection = 0
        
    def add_button(self, text, action):
        button_surface = FONT.render(text, True, (255, 255, 255))
        self.buttons.append({"text": text, "surface": button_surface, "action": action})
    
    def draw(self, surface):
        surface.fill((30, 30, 30))
        title = FONT.render("Contagium", True, (255, 255, 0))
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 120))
        
        for i, button in enumerate(self.buttons):
            color = (255, 0, 0) if i == self.current_selection else (255, 255, 255)
            button_surface = FONT.render(button["text"], True, color)
            y_pos = 280 + i * 100
            surface.blit(button_surface, (SCREEN_WIDTH // 2 - button_surface.get_width() // 2, y_pos))
    
    def handle_event(self, event):
        if event.type == KEYDOWN:
            if event.key == K_UP:
                self.current_selection = (self.current_selection - 1) % len(self.buttons)
            elif event.key == K_DOWN:
                self.current_selection = (self.current_selection + 1) % len(self.buttons)
            elif event.key == K_RETURN:
                return self.buttons[self.current_selection]["action"]
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for i, button in enumerate(self.buttons):
                button_surface = button["surface"]
                bx = SCREEN_WIDTH // 2 - button_surface.get_width() // 2
                by = 280 + i * 100
                if bx < mx < bx + button_surface.get_width() and by < my < by + button_surface.get_height():
                    return button["action"]
        return None

# Initialisation des menus
def init_menus():
    main_menu = Menu()
    main_menu.add_button("Jouer", STATE_PLAY)
    main_menu.add_button("Options", STATE_OPTIONS)
    main_menu.add_button("Quitter", "QUIT")
    
    pause_menu = Menu()
    pause_menu.add_button("Reprendre", STATE_PLAY)
    pause_menu.add_button("Options", STATE_OPTIONS)
    pause_menu.add_button("Menu Principal", STATE_MENU)
    pause_menu.add_button("Quitter", "QUIT")
    
    options_menu = Menu()
    options_menu.add_button("Retour", "BACK")
    
    game_over_menu = Menu()
    game_over_menu.add_button("Rejouer", STATE_PLAY)
    game_over_menu.add_button("Menu Principal", STATE_MENU)
    game_over_menu.add_button("Quitter", "QUIT")
    
    return {
        STATE_MENU: main_menu,
        STATE_PAUSE: pause_menu,
        STATE_OPTIONS: options_menu,
        STATE_GAME_OVER: game_over_menu
    }