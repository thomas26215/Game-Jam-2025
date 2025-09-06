import pygame
from pygame.locals import *
import controlsMenu
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    STATE_MENU, STATE_PLAY, STATE_PAUSE, STATE_GAME_OVER, STATE_BACK ,STATE_OPTIONS,
    FONT
)



pygame.init()

def scan_joysticks():
    pygame.joystick.quit()
    pygame.joystick.init()
    joystick_count = pygame.joystick.get_count()
    for i in range(joystick_count):
        pygame.joystick.Joystick(i).init()



class Menu:
    def __init__(self, settings, title_image_path=None):
        scan_joysticks()
        self.settings = settings
        self.buttons = []
        self.current_selection = 0

        try:
            self.background = pygame.image.load("right.png").convert()
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except (pygame.error, FileNotFoundError):
            self.background = None

        self.title_image = None
        if title_image_path:
            try:
                self.title_image = pygame.image.load(title_image_path).convert_alpha()
            except (pygame.error, FileNotFoundError):
                self.title_image = None

        # --- Animation du rat ---
        try:
            self.rat_spritesheet = pygame.image.load("rat/rat_droite.png").convert_alpha()
            self.rat_frame_width = 240
            self.rat_frame_height = self.rat_spritesheet.get_height()
            self.rat_frames = []
            for i in range(12, 37):
                frame = pygame.Surface((self.rat_frame_width, self.rat_frame_height), pygame.SRCALPHA)
                frame.blit(self.rat_spritesheet, (0, 0),
                           (i * self.rat_frame_width, 0, self.rat_frame_width, self.rat_frame_height))
                self.rat_frames.append(frame)

            self.rat_current_frame = 0
            self.rat_animation_timer = 0
            self.rat_animation_speed = 100
            self.rat_x = SCREEN_WIDTH // 2 - self.rat_frame_width // 2
            self.rat_y = SCREEN_HEIGHT // 2 - self.rat_frame_height // 2
            self.rat_speed = 250
            self.rat_direction = 1
            self.rat_visible = True
        except (pygame.error, FileNotFoundError):
            self.rat_spritesheet = None

    def add_button(self, text, action):
        button_surface = FONT.render(text, True, (255, 255, 255))
        self.buttons.append({"text": text, "surface": button_surface, "action": action})

    def update(self, dt):
        if self.rat_spritesheet and self.rat_frames and self.rat_visible:
            self.rat_animation_timer += dt
            if self.rat_animation_timer >= self.rat_animation_speed:
                self.rat_animation_timer = 0
                self.rat_current_frame = (self.rat_current_frame + 1) % len(self.rat_frames)

            if self.rat_x < SCREEN_WIDTH:
                self.rat_x += self.rat_speed * (dt / 1000.0)
            else:
                self.rat_visible = False

    def draw(self, surface):
        # --- maj textes dynamiques ---
        for button in self.buttons:
            if button["action"] == "TOGGLE_MUSIC":
                button["text"] = f"Music: {'ON' if self.settings.music_on else 'OFF'}"
            elif button["action"] == "CHANGE_VOLUME":
                button["text"] = f"Volume: {int(self.settings.music_volume * 100)}%"
            elif button["action"] == "VISION_EASY":
                button["text"] = f"Facile (400){' (x)' if self.settings.vision_radius == 400 else ''}"
            elif button["action"] == "VISION_NORMAL":
                button["text"] = f"Normal (300){' (x)' if self.settings.vision_radius == 300 else ''}"
            elif button["action"] == "VISION_HIGH":
                button["text"] = f"Élevée (150){' (x)' if self.settings.vision_radius == 150 else ''}"

        if self.background:
            surface.blit(self.background, (0, 0))
        else:
            surface.fill((30, 30, 30))

        if self.rat_spritesheet and self.rat_frames and self.rat_visible:
            current_rat_frame = self.rat_frames[self.rat_current_frame]
            if self.rat_direction == -1:
                current_rat_frame = pygame.transform.flip(current_rat_frame, True, False)
            surface.blit(current_rat_frame, (int(self.rat_x), int(self.rat_y)))

        if self.title_image:
            original_width = self.title_image.get_width()
            original_height = self.title_image.get_height()
            new_width = int(original_width * 0.4)
            new_height = int(original_height * 0.4)
            scaled_title_image = pygame.transform.scale(self.title_image, (new_width, new_height))
            title_rect = scaled_title_image.get_rect(center=(SCREEN_WIDTH // 2, 120))
            surface.blit(scaled_title_image, title_rect)
        else:
            title = FONT.render("Contagium", True, (255, 255, 0))
            title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 120))
            title_bg = pygame.Surface((title.get_width() + 20, title.get_height() + 10))
            title_bg.set_alpha(128)
            title_bg.fill((0, 0, 0))
            surface.blit(title_bg, (title_rect.x - 10, title_rect.y - 5))
            surface.blit(title, title_rect)

        try:
            obra_font = pygame.font.Font("assets/ObraLetra.ttf", 36)
        except:
            obra_font = pygame.font.SysFont("Arial", 36)

        if self.buttons[0]["text"] == "Jouer":
            grid = [
                (SCREEN_WIDTH // 2 - 110, 300),
                (SCREEN_WIDTH // 2 + 110, 300),
                (SCREEN_WIDTH // 2 - 110, 400),
                (SCREEN_WIDTH // 2 + 110, 400),
                (SCREEN_WIDTH // 2, 500)
            ]
            for i, button in enumerate(self.buttons):
                color = (0, 150, 0) if i == self.current_selection else (44, 68, 132)
                text_surface = obra_font.render(button["text"], True, color)
                x, y = grid[i]
                button_rect = text_surface.get_rect(center=(x, y))
                button_bg = pygame.Surface((text_surface.get_width() + 24, text_surface.get_height() + 14), pygame.SRCALPHA)
                pygame.draw.rect(button_bg, (220, 220, 220, 200), button_bg.get_rect(), border_radius=18)
                surface.blit(button_bg, (button_rect.x - 12, button_rect.y - 7))
                surface.blit(text_surface, button_rect)
        else:
            # Organisation spécifique pour le menu options
            if self.buttons[0]["action"] == "TOGGLE_MUSIC":
                # Récupération des boutons
                music_btn = self.buttons[0]
                volume_btn = self.buttons[1]
                vision_btns = self.buttons[2:5]
                controls_btn = self.buttons[5]
                back_btn = self.buttons[6]

                # Musique
                idx = 0
                color = (0, 150, 0) if idx == self.current_selection else (44, 68, 132)
                text_surface = obra_font.render(music_btn["text"], True, color)
                y_pos = 280
                button_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
                button_bg = pygame.Surface((text_surface.get_width() + 24, text_surface.get_height() + 14), pygame.SRCALPHA)
                pygame.draw.rect(button_bg, (220, 220, 220, 200), button_bg.get_rect(), border_radius=18)
                surface.blit(button_bg, (button_rect.x - 12, button_rect.y - 7))
                surface.blit(text_surface, button_rect)

                # Volume
                idx = 1
                color = (0, 150, 0) if idx == self.current_selection else (44, 68, 132)
                text_surface = obra_font.render(volume_btn["text"], True, color)
                y_pos = 280 + 85
                button_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
                button_bg = pygame.Surface((text_surface.get_width() + 24, text_surface.get_height() + 14), pygame.SRCALPHA)
                pygame.draw.rect(button_bg, (220, 220, 220, 200), button_bg.get_rect(), border_radius=18)
                surface.blit(button_bg, (button_rect.x - 12, button_rect.y - 7))
                surface.blit(text_surface, button_rect)

                # Barre de volume
                if volume_btn["action"] == "VOLUME_SLIDER":
                    bar_width = 200
                    bar_height = 8
                    bar_x = SCREEN_WIDTH // 2 - bar_width // 2
                    bar_y = button_rect.centery + 40
                    pygame.draw.rect(surface, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height), border_radius=4)
                    fill_width = int(bar_width * self.settings.music_volume)
                    pygame.draw.rect(surface, (0, 200, 0), (bar_x, bar_y, fill_width, bar_height), border_radius=4)
                    knob_x = bar_x + fill_width - 5
                    knob_y = bar_y - 6
                    pygame.draw.rect(surface, (255, 255, 255), (knob_x, knob_y, 10, 20), border_radius=5)

                # Ligne des boutons vision (espacement augmenté)
                vision_y = 280 + 85 * 2
                # Ajout du texte 'Difficultés' centré avec espace avant et après
                try:
                    diff_font = pygame.font.Font("assets/ObraLetra.ttf", 32)
                except:
                    diff_font = pygame.font.SysFont("Arial", 25, bold=True)
                diff_text = diff_font.render("Difficultés", True, (255, 255, 255))
                # Espace avant
                diff_rect = diff_text.get_rect(center=(SCREEN_WIDTH // 2, vision_y - 10))
                surface.blit(diff_text, diff_rect)
                # Espace après (on décale la ligne de boutons de vision)
                vision_y_btns = vision_y + 30

                vision_spacing = 250
                vision_total_width = vision_spacing * (len(vision_btns) - 1)
                vision_start_x = SCREEN_WIDTH // 2 - vision_total_width // 2
                for i, button in enumerate(vision_btns):
                    idx = 2 + i
                    color = (0, 150, 0) if idx == self.current_selection else (44, 68, 132)
                    text_surface = obra_font.render(button["text"], True, color)
                    x_pos = vision_start_x + i * vision_spacing
                    button_rect = text_surface.get_rect(center=(x_pos, vision_y_btns))
                    button_bg = pygame.Surface((text_surface.get_width() + 24, text_surface.get_height() + 14), pygame.SRCALPHA)
                    pygame.draw.rect(button_bg, (220, 220, 220, 200), button_bg.get_rect(), border_radius=18)
                    surface.blit(button_bg, (button_rect.x - 12, button_rect.y - 7))
                    surface.blit(text_surface, button_rect)

                # Contrôles
                idx = 5
                color = (0, 150, 0) if idx == self.current_selection else (44, 68, 132)
                text_surface = obra_font.render(controls_btn["text"], True, color)
                y_pos = vision_y + 85
                button_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
                button_bg = pygame.Surface((text_surface.get_width() + 24, text_surface.get_height() + 14), pygame.SRCALPHA)
                pygame.draw.rect(button_bg, (220, 220, 220, 200), button_bg.get_rect(), border_radius=18)
                surface.blit(button_bg, (button_rect.x - 12, button_rect.y - 7))
                surface.blit(text_surface, button_rect)

                # Retour
                idx = 6
                color = (0, 150, 0) if idx == self.current_selection else (44, 68, 132)
                text_surface = obra_font.render(back_btn["text"], True, color)
                y_pos = vision_y + 85 * 2
                button_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
                button_bg = pygame.Surface((text_surface.get_width() + 24, text_surface.get_height() + 14), pygame.SRCALPHA)
                pygame.draw.rect(button_bg, (220, 220, 220, 200), button_bg.get_rect(), border_radius=18)
                surface.blit(button_bg, (button_rect.x - 12, button_rect.y - 7))
                surface.blit(text_surface, button_rect)
            else:
                # ...ancien affichage pour les autres menus...
                vision_actions = ("VISION_EASY", "VISION_NORMAL", "VISION_HIGH")
                vision_buttons = [b for b in self.buttons if b["action"] in vision_actions]
                other_buttons = [b for b in self.buttons if b["action"] not in vision_actions]
                if vision_buttons:
                    vision_y = 280
                    vision_spacing = 260
                    vision_total_width = vision_spacing * (len(vision_buttons) - 1)
                    vision_start_x = SCREEN_WIDTH // 2 - vision_total_width // 2
                    for i, button in enumerate(vision_buttons):
                        idx = self.buttons.index(button)
                        color = (0, 150, 0) if idx == self.current_selection else (44, 68, 132)
                        text_surface = obra_font.render(button["text"], True, color)
                        x_pos = vision_start_x + i * vision_spacing
                        button_rect = text_surface.get_rect(center=(x_pos, vision_y))
                        button_bg = pygame.Surface((text_surface.get_width() + 24, text_surface.get_height() + 14), pygame.SRCALPHA)
                        pygame.draw.rect(button_bg, (220, 220, 220, 200), button_bg.get_rect(), border_radius=18)
                        surface.blit(button_bg, (button_rect.x - 12, button_rect.y - 7))
                        surface.blit(text_surface, button_rect)
                start_y = 280 + 85 if vision_buttons else 280
                for i, button in enumerate(other_buttons):
                    idx = self.buttons.index(button)
                    color = (0, 150, 0) if idx == self.current_selection else (44, 68, 132)
                    text_surface = obra_font.render(button["text"], True, color)
                    y_pos = start_y + i * 85
                    button_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
                    button_bg = pygame.Surface((text_surface.get_width() + 24, text_surface.get_height() + 14), pygame.SRCALPHA)
                    pygame.draw.rect(button_bg, (220, 220, 220, 200), button_bg.get_rect(), border_radius=18)
                    surface.blit(button_bg, (button_rect.x - 12, button_rect.y - 7))
                    surface.blit(text_surface, button_rect)
                    if button["action"] == "VOLUME_SLIDER":
                        bar_width = 200
                        bar_height = 8
                        bar_x = SCREEN_WIDTH // 2 - bar_width // 2
                        bar_y = button_rect.centery + 40
                        pygame.draw.rect(surface, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height), border_radius=4)
                        fill_width = int(bar_width * self.settings.music_volume)
                        pygame.draw.rect(surface, (0, 200, 0), (bar_x, bar_y, fill_width, bar_height), border_radius=4)
                        knob_x = bar_x + fill_width - 5
                        knob_y = bar_y - 6
                        pygame.draw.rect(surface, (255, 255, 255), (knob_x, knob_y, 10, 20), border_radius=5)
                else:
                    # ...ancien affichage pour les autres menus...
                    vision_actions = ("VISION_EASY", "VISION_NORMAL", "VISION_HIGH")
                    vision_buttons = [b for b in self.buttons if b["action"] in vision_actions]
                    other_buttons = [b for b in self.buttons if b["action"] not in vision_actions]
                    if vision_buttons:
                        vision_y = 280
                        vision_spacing = 260
                        vision_total_width = vision_spacing * (len(vision_buttons) - 1)
                        vision_start_x = SCREEN_WIDTH // 2 - vision_total_width // 2
                        for i, button in enumerate(vision_buttons):
                            idx = self.buttons.index(button)
                            color = (0, 150, 0) if idx == self.current_selection else (44, 68, 132)
                            text_surface = obra_font.render(button["text"], True, color)
                            x_pos = vision_start_x + i * vision_spacing
                            button_rect = text_surface.get_rect(center=(x_pos, vision_y))
                            button_bg = pygame.Surface((text_surface.get_width() + 24, text_surface.get_height() + 14), pygame.SRCALPHA)
                            pygame.draw.rect(button_bg, (220, 220, 220, 200), button_bg.get_rect(), border_radius=18)
                            surface.blit(button_bg, (button_rect.x - 12, button_rect.y - 7))
                            surface.blit(text_surface, button_rect)
                    start_y = 280 + 85 if vision_buttons else 280
                    for i, button in enumerate(other_buttons):
                        idx = self.buttons.index(button)
                        color = (0, 150, 0) if idx == self.current_selection else (44, 68, 132)
                        text_surface = obra_font.render(button["text"], True, color)
                        y_pos = start_y + i * 85
                        button_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
                        button_bg = pygame.Surface((text_surface.get_width() + 24, text_surface.get_height() + 14), pygame.SRCALPHA)
                        pygame.draw.rect(button_bg, (220, 220, 220, 200), button_bg.get_rect(), border_radius=18)
                        surface.blit(button_bg, (button_rect.x - 12, button_rect.y - 7))
                        surface.blit(text_surface, button_rect)
                        if button["action"] == "VOLUME_SLIDER":
                            bar_width = 200
                            bar_height = 8
                            bar_x = SCREEN_WIDTH // 2 - bar_width // 2
                            bar_y = button_rect.centery + 40
                            pygame.draw.rect(surface, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height), border_radius=4)
                            fill_width = int(bar_width * self.settings.music_volume)
                            pygame.draw.rect(surface, (0, 200, 0), (bar_x, bar_y, fill_width, bar_height), border_radius=4)
                            knob_x = bar_x + fill_width - 5
                            knob_y = bar_y - 6
                            pygame.draw.rect(surface, (255, 255, 255), (knob_x, knob_y, 10, 20), border_radius=5)

    def handle_event(self, event):
        if event.type == KEYDOWN:
            # Navigation grid pour le menu principal "Jouer"
            if self.buttons and self.buttons[0]["text"] == "Jouer":
                # Grille :
                # 0 1
                # 2 3
                #   4
                grid = [
                    (0, 0), (0, 1),
                    (1, 0), (1, 1),
                    (2, 0)
                ]
                pos = grid[self.current_selection]
                if event.key == K_LEFT:
                    # Gauche
                    if pos == (0, 1): self.current_selection = 0
                    elif pos == (1, 1): self.current_selection = 2
                elif event.key == K_RIGHT:
                    # Droite
                    if pos == (0, 0): self.current_selection = 1
                    elif pos == (1, 0): self.current_selection = 3
                elif event.key == K_UP:
                    # Haut
                    if pos == (1, 0): self.current_selection = 0
                    elif pos == (1, 1): self.current_selection = 1
                    elif pos == (2, 0): self.current_selection = 2
                elif event.key == K_DOWN:
                    # Bas
                    if pos == (0, 0): self.current_selection = 2
                    elif pos == (0, 1): self.current_selection = 3
                    elif pos in [(1, 0), (1, 1)]: self.current_selection = 4
                elif event.key == K_RETURN:
                    return self.buttons[self.current_selection]["action"]
            # Navigation spéciale pour la ligne vision dans le menu options
            elif self.buttons and self.buttons[0]["action"] == "TOGGLE_MUSIC":
                # ...existing code for options menu navigation...
                vision_indices = [2, 3, 4]
                if self.current_selection in vision_indices:
                    if event.key == K_LEFT:
                        self.current_selection = vision_indices[(vision_indices.index(self.current_selection) - 1) % len(vision_indices)]
                    elif event.key == K_RIGHT:
                        self.current_selection = vision_indices[(vision_indices.index(self.current_selection) + 1) % len(vision_indices)]
                    elif event.key == K_UP:
                        self.current_selection = 1  # Volume
                    elif event.key == K_DOWN:
                        self.current_selection = 5  # Contrôles
                    elif event.key == K_RETURN:
                        action = self.buttons[self.current_selection]["action"]
                        if action == "VISION_EASY":
                            self.settings.set_vision_radius(400)
                            return None
                        elif action == "VISION_NORMAL":
                            self.settings.set_vision_radius(300)
                            return None
                        elif action == "VISION_HIGH":
                            self.settings.set_vision_radius(150)
                            return None
                        else:
                            return action
                else:
                    if event.key == K_UP:
                        if self.current_selection == 5:
                            self.current_selection = 4  # Dernier bouton vision
                        elif self.current_selection == 6:
                            self.current_selection = 5  # Contrôles
                        elif self.current_selection == 1:
                            self.current_selection = 0  # Musique
                        elif self.current_selection == 0:
                            self.current_selection = 6  # Retour
                        else:
                            self.current_selection = (self.current_selection - 1) % len(self.buttons)
                    elif event.key == K_DOWN:
                        if self.current_selection == 0:
                            self.current_selection = 1  # Volume
                        elif self.current_selection == 1:
                            self.current_selection = 2  # Premier bouton vision
                        elif self.current_selection == 4:
                            self.current_selection = 5  # Contrôles
                        elif self.current_selection == 5:
                            self.current_selection = 6  # Retour
                        elif self.current_selection == 6:
                            self.current_selection = 0  # Musique
                        else:
                            self.current_selection = (self.current_selection + 1) % len(self.buttons)
                    elif event.key == K_RETURN:
                        action = self.buttons[self.current_selection]["action"]
                        if action == "TOGGLE_MUSIC":
                            self.settings.toggle_music()
                            return None
                        elif action == "VOLUME_SLIDER":
                            return None
                        elif action == "CONTROLS":
                            return action
                        elif action == STATE_BACK:
                            return action
                    elif self.buttons[self.current_selection]["action"] == "VOLUME_SLIDER":
                        if event.key == K_LEFT:
                            self.settings.set_volume(self.settings.music_volume - 0.05)
                        elif event.key == K_RIGHT:
                            self.settings.set_volume(self.settings.music_volume + 0.05)
            else:
                # Navigation classique pour les autres menus
                if event.key == K_UP:
                    self.current_selection = (self.current_selection - 1) % len(self.buttons)
                elif event.key == K_DOWN:
                    self.current_selection = (self.current_selection + 1) % len(self.buttons)
                elif event.key == K_RETURN:
                    action = self.buttons[self.current_selection]["action"]
                    if action == "TOGGLE_MUSIC":
                        self.settings.toggle_music()
                        return None
                    elif action == "VOLUME_SLIDER":
                        return None
                    elif action == "VISION_EASY":
                        self.settings.set_vision_radius(400)
                        return None
                    elif action == "VISION_NORMAL":
                        self.settings.set_vision_radius(300)
                        return None
                    elif action == "VISION_HIGH":
                        self.settings.set_vision_radius(150)
                        return None
                    else:
                        return action
                elif self.buttons[self.current_selection]["action"] == "VOLUME_SLIDER":
                    if event.key == K_LEFT:
                        self.settings.set_volume(self.settings.music_volume - 0.05)
                    elif event.key == K_RIGHT:
                        self.settings.set_volume(self.settings.music_volume + 0.05)

        elif event.type == JOYAXISMOTION:
            if event.axis == 1:
                if event.value < -0.999999:
                    self.current_selection = (self.current_selection - 1) % len(self.buttons)
                elif event.value > 0.999999:
                    self.current_selection = (self.current_selection + 1) % len(self.buttons)

        elif event.type == JOYHATMOTION:
            if event.value[1] == 1:
                self.current_selection = (self.current_selection - 1) % len(self.buttons)
            elif event.value[1] == -1:
                self.current_selection = (self.current_selection + 1) % len(self.buttons)

        elif event.type == JOYBUTTONDOWN:
            if event.button in (0, 7):
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


def init_menus(settings):
    main_menu = Menu(settings, "wordsGame/contagium.png")
    main_menu.add_button("Jouer", STATE_PLAY)
    main_menu.add_button("Didacticiel", "TUTORIAL")
    main_menu.add_button("Options", STATE_OPTIONS)
    main_menu.add_button("Crédits", "CREDITS")
    main_menu.add_button("Quitter", "QUIT")

    pause_menu = Menu(settings, "wordsGame/playPause.png")
    pause_menu.add_button("Reprendre", STATE_PLAY)
    pause_menu.add_button("Options", STATE_OPTIONS)
    pause_menu.add_button("Menu Principal", STATE_MENU)
    pause_menu.add_button("Quitter", "QUIT")

    options_menu = Menu(settings, "wordsGame/options.png")
    options_menu.add_button("Music: ON", "TOGGLE_MUSIC")
    options_menu.add_button("Volume", "VOLUME_SLIDER")
    options_menu.add_button("Vision : Facile (400)", "VISION_EASY")
    options_menu.add_button("Vision : Normal (300)", "VISION_NORMAL")
    options_menu.add_button("Vision : Élevé (150)", "VISION_HIGH")
    options_menu.add_button("Contrôles", "CONTROLS")
    options_menu.add_button("Retour", STATE_BACK)

    game_over_menu = Menu(settings, "wordsGame/gameOver.png")
    game_over_menu.add_button("Rejouer", STATE_PLAY)
    game_over_menu.add_button("Menu Principal", STATE_MENU)
    game_over_menu.add_button("Quitter", "QUIT")

    controls_menu = controlsMenu.ControlsMenu(settings)
    return {
        STATE_MENU: main_menu,
        STATE_PAUSE: pause_menu,
        STATE_OPTIONS: options_menu,
        STATE_GAME_OVER: game_over_menu,
        "CONTROLS": controls_menu,
        "CREDITS": None,
        "TUTORIAL": None
    }

# --- Fonction d'affichage et gestion du menu didacticiel ---
def draw_tutorial_menu(surface):
    try:
        background = pygame.image.load("right.png").convert()
        background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except:
        background = None
    if background:
        surface.blit(background, (0, 0))
    else:
        surface.fill((20, 20, 20))

    # Titre
    try:
        obra_font = pygame.font.Font("assets/ObraLetra.ttf", 48)
    except:
        obra_font = pygame.font.SysFont("Arial", 48, bold=True)
    try:
        title = pygame.image.load("wordsGame/tutorial.png").convert_alpha()
        title = pygame.transform.scale(title, (int(title.get_width() * 0.4), int(title.get_height() * 0.4)))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 130))
        surface.blit(title, title_rect)
    except:
        title_surface = obra_font.render("Didacticiel", True, (255, 255, 0))
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 130))
        surface.blit(title_surface, title_rect)

    # Texte du didacticiel (à personnaliser)
    tutorial_text = (
        "Bienvenue dans Contagium !\n"
        "Ici, vous incarnez un médecin de la peste. Le dernier espoir d’une ville ravagée par la maladie.\n"
        "Votre mission : retrouver les potions dispersées à travers les rues désertées, afin de sauver les habitants encore en vie.\n"
        "Mais attention : la cité est envahie de pestiférés, des âmes désespérées ayant perdu leur conscience. Ne les laissez pas vous toucher, sous peine de devenir l’un d’eux !\n"
        "Une fois les potions récupérées, vous devrez trouver le portail du monde des pestiférés. Mais attention, c'est un aller sans retour.\n"
        "Vous aurez le nombre de potions ramassées affiché en haut à gauche de l’écran. Attention à ne pas les gaspiller !\n"
        "Souvenez-vous : votre but n’est pas de tuer les pestiférés… mais de les sauver en leur lançant les potions récupérées."
    )
    small_font = pygame.font.SysFont("Arial", 16)
    box_width = SCREEN_WIDTH - 200
    start_x = (SCREEN_WIDTH - box_width) // 2
    start_y = 220

    # Word wrap automatique
    def wrap_text(text, font, max_width):
        lines = []
        for paragraph in text.split("\n"):
            words = paragraph.split(" ")
            line = ""
            for word in words:
                test_line = line + (" " if line else "") + word
                if font.size(test_line)[0] <= max_width - 80:
                    line = test_line
                else:
                    if line:
                        lines.append(line)
                    line = word
            if line:
                lines.append(line)
        return lines

    wrapped_lines = wrap_text(tutorial_text, small_font, box_width)
    line_height = small_font.get_height() + 6
    box_height = len(wrapped_lines) * line_height + 2 * 30

    # Fond semi-transparent pour le texte
    bg_surface = pygame.Surface((box_width, box_height))
    bg_surface.set_alpha(180)
    bg_surface.fill((0, 0, 0))
    surface.blit(bg_surface, (start_x, start_y))

    for i, line in enumerate(wrapped_lines):
        text_surface = small_font.render(line, True, (255, 255, 255))
        text_rect = text_surface.get_rect(topleft=(start_x + 40, start_y + 30 + i * line_height))
        surface.blit(text_surface, text_rect)

    # Bouton Retour
    button_text = "Retour"
    try:
        button_font = pygame.font.Font("assets/ObraLetra.ttf", 32)
    except:
        button_font = pygame.font.SysFont("Arial", 32, bold=True)
    button_surface = button_font.render(button_text, True, (0, 150, 0))
    button_rect = button_surface.get_rect(center=(SCREEN_WIDTH // 2, start_y + box_height + 60))

    button_bg = pygame.Surface((button_surface.get_width() + 24, button_surface.get_height() + 14), pygame.SRCALPHA)
    pygame.draw.rect(button_bg, (0, 0, 0, 180), button_bg.get_rect(), border_radius=12)
    surface.blit(button_bg, (button_rect.x - 12, button_rect.y - 7))
    surface.blit(button_surface, button_rect)

def handle_tutorial_event(event):
    if event.type == KEYDOWN:
        if event.key in (K_RETURN, K_ESCAPE):
            return STATE_MENU
    elif event.type == JOYBUTTONDOWN:
        if event.button in (0, 7):
            return STATE_MENU
    elif event.type == MOUSEBUTTONDOWN and event.button == 1:
        return STATE_MENU
    return None
# --- Fonction d'affichage et gestion du menu crédits ---
def draw_credits_menu(surface):
    try:
        background = pygame.image.load("right.png").convert()
        background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except:
        background = None
    if background:
        surface.blit(background, (0, 0))
    else:
        surface.fill((20, 20, 20))

    # Main title
    try:
        obra_font = pygame.font.Font("assets/ObraLetra.ttf", 48)
    except:
        obra_font = pygame.font.SysFont("Arial", 48, bold=True)
    title = pygame.image.load("wordsGame/credits.png").convert_alpha()
    title = pygame.transform.scale(title, (int(title.get_width() * 0.4), int(title.get_height() * 0.4)))
    title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 130))
    surface.blit(title, title_rect)

    # Column headers and content
    developers_header = "Développeurs"
    resources_header = "Ressources externes"
    header_color = (30, 129, 176)  # HEX #1e81b0

    developers = [
        "Quentin Peguin - Chef de projet",
        "Thomas - Développeur en chef",
        "Sophie - Artiste",
        "Bryan - Testeur",
        "Maria - Designeuse de sprite"
    ]
    resources = [
        "Itch.io",
        "Craftpix.net",
        "Pixabay",
        "Pygame et VS Code"
    ]

    small_font = pygame.font.SysFont("Arial", 26)
    header_font = pygame.font.SysFont("Arial", 28, bold=True)
    padding = 20
    column_spacing = 100
    line_height = 36

    # Calculate box width properly including headers
    dev_width = max(small_font.size(line)[0] for line in developers)
    dev_header_width = header_font.size(developers_header)[0]
    dev_col_width = max(dev_width, dev_header_width)

    res_width = max(small_font.size(line)[0] for line in resources)
    res_header_width = header_font.size(resources_header)[0]
    res_col_width = max(res_width, res_header_width)

    box_width = dev_col_width + res_col_width + column_spacing + 2 * padding
    box_height = max(len(developers), len(resources)) * line_height + line_height * 2 + 2 * padding  # +1 for headers, +1 for merci text

    start_x = (SCREEN_WIDTH - box_width) // 2
    start_y = 200

    # Draw black background box
    bg_surface = pygame.Surface((box_width, box_height))
    bg_surface.set_alpha(180)
    bg_surface.fill((0, 0, 0))
    surface.blit(bg_surface, (start_x, start_y))

    # Column headers
    dev_header_surface = header_font.render(developers_header, True, header_color)
    dev_header_rect = dev_header_surface.get_rect(topleft=(start_x + padding, start_y + padding))
    surface.blit(dev_header_surface, dev_header_rect)

    res_header_surface = header_font.render(resources_header, True, header_color)
    res_header_rect = res_header_surface.get_rect(
        topleft=(start_x + padding + dev_col_width + column_spacing, start_y + padding)
    )
    surface.blit(res_header_surface, res_header_rect)

    # Column content
    for i, line in enumerate(developers):
        text_surface = small_font.render(line, True, (255, 255, 255))
        text_rect = text_surface.get_rect(topleft=(start_x + padding, start_y + padding + line_height + i * line_height))
        surface.blit(text_surface, text_rect)

    for i, line in enumerate(resources):
        text_surface = small_font.render(line, True, (255, 255, 255))
        text_rect = text_surface.get_rect(
            topleft=(start_x + padding + dev_col_width + column_spacing, start_y + padding + line_height + i * line_height)
        )
        surface.blit(text_surface, text_rect)

    # "Merci d'avoir joué..." inside the box
    thanks_text = "Merci d'avoir joué à notre jeu !"
    thanks_surface = small_font.render(thanks_text, True, (255, 255, 255))
    thanks_rect = thanks_surface.get_rect(center=(start_x + box_width // 2, start_y + box_height - padding - line_height // 2))
    surface.blit(thanks_surface, thanks_rect)

    # Return button below the box
    button_text = "Retour"
    try:
        button_font = pygame.font.Font("assets/ObraLetra.ttf", 32)
    except:
        button_font = pygame.font.SysFont("Arial", 32, bold=True)
    button_surface = button_font.render(button_text, True, (0, 150, 0))
    button_rect = button_surface.get_rect(center=(SCREEN_WIDTH // 2, start_y + box_height + 60))

    button_bg = pygame.Surface((button_surface.get_width() + 24, button_surface.get_height() + 14), pygame.SRCALPHA)
    pygame.draw.rect(button_bg, (0, 0, 0, 180), button_bg.get_rect(), border_radius=12)
    surface.blit(button_bg, (button_rect.x - 12, button_rect.y - 7))
    surface.blit(button_surface, button_rect)

def handle_credits_event(event):
    if event.type == KEYDOWN:
        if event.key in (K_RETURN, K_ESCAPE):
            return STATE_MENU
    elif event.type == JOYBUTTONDOWN:
        if event.button in (0, 7):
            return STATE_MENU
    elif event.type == MOUSEBUTTONDOWN and event.button == 1:
        return STATE_MENU
    return None
