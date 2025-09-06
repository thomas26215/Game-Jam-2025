import pygame
from pygame.locals import *
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, STATE_BACK,
    STATE_MENU, STATE_PLAY, STATE_PAUSE, STATE_GAME_OVER, STATE_OPTIONS,
    FONT
)

class ControlsMenu:
    def __init__(self, settings):
        self.settings = settings
        self.buttons = []
        self.current_selection = 0
        self.waiting_for_key = False
        self.waiting_for_gamepad = False
        self.key_to_change = None
        self.device_to_change = None
        
        # Charger l'image de fond
        try:
            self.background = pygame.image.load("right.png").convert()
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except:
            self.background = None
        
        self.update_buttons()
    
    def update_buttons(self):
        """Met à jour la liste des boutons avec les touches actuelles."""
        self.buttons = []
        
        # Fonction helper pour convertir les codes de touches en noms
        def key_name(key_code):
            key_names = {
                K_UP: "Flèches Haut", K_DOWN: "Flèches Bas", K_LEFT: "Flèches Gauche", K_RIGHT: "Flèches Droite",
                K_z: "Z", K_q: "Q", K_s: "S", K_d: "D",
                K_SPACE: "ESPACE", K_RETURN: "ENTRÉE",
                K_a: "A", K_b: "B", K_c: "C", K_e: "E", K_f: "F",
                K_g: "G", K_h: "H", K_i: "I", K_j: "J", K_k: "K",
                K_l: "L", K_m: "M", K_n: "N", K_o: "O", K_p: "P",
                K_r: "R", K_t: "T", K_u: "U", K_v: "V", K_w: "W",
                K_x: "X", K_y: "Y"
            }
            return key_names.get(key_code, f"KEY_{key_code}")
        
        def button_name(button_code):
            button_names = {
                0: "A/X", 1: "B/Circle", 2: "X/Square", 3: "Y/Triangle",
                4: "LB", 5: "RB", 6: STATE_BACK, 7: "Start",
                8: "LS", 9: "RS", 10: "DPad Up", 11: "DPad Down",
                12: "DPad Left", 13: "DPad Right"
            }
            return button_names.get(button_code, f"BTN_{button_code}")
        
        # Ajouter les boutons pour chaque action
        for action in self.settings.controls:
            action_name = {
                "move_up": "Haut",
                "move_down": "Bas", 
                "move_left": "Gauche",
                "move_right": "Droite",
                "attack": "Attaquer",
                "interact": "Interagir"  
            }.get(action, action)
            
            # Bouton pour clavier
            keyboard_keys = self.settings.get_control(action, "keyboard")
            keys_text = " + ".join([key_name(key) for key in keyboard_keys]) if keyboard_keys else "Aucune"
            self.buttons.append({
                "text": f"{action_name} (Clavier): {keys_text}",
                "action": action,
                "device": "keyboard"
            })
            
            # Bouton pour manette
            gamepad_keys = self.settings.get_control(action, "gamepad")
            buttons_text = " + ".join([button_name(btn) for btn in gamepad_keys]) if gamepad_keys else "Aucune"
            if "move_" not in action:
                self.buttons.append({
                    "text": f"{action_name} (Manette): {buttons_text}",
                    "action": action,
                    "device": "gamepad"
                })
        
        # Boutons spéciaux
        self.buttons.append({"text": "Réinitialiser", "action": "RESET", "device": None})
        self.buttons.append({"text": "Retour", "action": STATE_BACK, "device": None})
    
    def draw(self, surface):
        # Dessiner le fond
        if self.background:
            surface.blit(self.background, (0, 0))
        else:
            surface.fill((30, 30, 30))

        # Titre
        try:
            obra_font = pygame.font.Font("assets/ObraLetra.ttf", 25)
        except:
            obra_font = pygame.font.SysFont("Arial", 25)
        try:
            title = pygame.image.load("wordsGame/controle.png").convert_alpha()
            title = pygame.transform.scale(title, (int(title.get_width() * 0.4), int(title.get_height() * 0.4)))
            title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 130))
            surface.blit(title, title_rect)
        except:
            title_surface = obra_font.render("Contrôles", True, (255, 255, 0))
            title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 130))
            surface.blit(title_surface, title_rect)

        # Message d'attente
        if self.waiting_for_key:
            wait_text = obra_font.render("Appuyez sur une touche clavier...", True, (255, 100, 100))
            wait_rect = wait_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
            surface.blit(wait_text, wait_rect)
        elif self.waiting_for_gamepad:
            wait_text = obra_font.render("Appuyez sur un bouton de manette...", True, (255, 100, 100))
            wait_rect = wait_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
            surface.blit(wait_text, wait_rect)

        # Séparer clavier et manette
        keyboard_buttons = [b for b in self.buttons if b.get("device") == "keyboard"]
        gamepad_buttons = [b for b in self.buttons if b.get("device") == "gamepad"]
        # On suppose l'ordre : Réinitialiser puis Retour
        reset_btn = next((b for b in self.buttons if b.get("action") == "RESET"), None)
        back_btn = next((b for b in self.buttons if b.get("action") == STATE_BACK), None)

        # Liste ordonnée pour la sélection et la modification
        self.displayed_buttons = keyboard_buttons + gamepad_buttons
        if reset_btn:
            self.displayed_buttons.append(reset_btn)
        if back_btn:
            self.displayed_buttons.append(back_btn)
        selection_idx = self.current_selection

        # Affichage grille
        col_x = [SCREEN_WIDTH//2 - 220, SCREEN_WIDTH//2 + 220]
        start_y = 220
        row_height = 60
        max_rows = max(len(keyboard_buttons), len(gamepad_buttons))

        # Clavier à gauche
        for i, button in enumerate(keyboard_buttons):
            color = (0, 150, 0) if selection_idx == i else (44, 68, 132)
            if (self.waiting_for_key or self.waiting_for_gamepad) and selection_idx == i:
                color = (255, 100, 100)
            text_surface = obra_font.render(button["text"], True, color)
            y_pos = start_y + i * row_height
            button_rect = text_surface.get_rect(center=(col_x[0], y_pos))
            button_bg = pygame.Surface((text_surface.get_width() + 24, text_surface.get_height() + 14), pygame.SRCALPHA)
            pygame.draw.rect(button_bg, (220, 220, 220, 200), button_bg.get_rect(), border_radius=18)
            surface.blit(button_bg, (button_rect.x - 12, button_rect.y - 7))
            surface.blit(text_surface, button_rect)

        # Manette à droite
        for i, button in enumerate(gamepad_buttons):
            idx = len(keyboard_buttons) + i
            color = (0, 150, 0) if selection_idx == idx else (44, 68, 132)
            if (self.waiting_for_key or self.waiting_for_gamepad) and selection_idx == idx:
                color = (255, 100, 100)
            text_surface = obra_font.render(button["text"], True, color)
            y_pos = start_y + i * row_height
            button_rect = text_surface.get_rect(center=(col_x[1], y_pos))
            button_bg = pygame.Surface((text_surface.get_width() + 24, text_surface.get_height() + 14), pygame.SRCALPHA)
            pygame.draw.rect(button_bg, (220, 220, 220, 200), button_bg.get_rect(), border_radius=18)
            surface.blit(button_bg, (button_rect.x - 12, button_rect.y - 7))
            surface.blit(text_surface, button_rect)

        # Boutons spéciaux : Réinitialiser sous clavier, Retour sous manette
        special_y = start_y + max_rows * row_height + 40
        if reset_btn:
            idx = len(keyboard_buttons) + len(gamepad_buttons)
            color = (0, 150, 0) if selection_idx == idx else (44, 68, 132)
            if (self.waiting_for_key or self.waiting_for_gamepad) and selection_idx == idx:
                color = (255, 100, 100)
            text_surface = obra_font.render(reset_btn["text"], True, color)
            button_rect = text_surface.get_rect(center=(col_x[0], special_y))
            button_bg = pygame.Surface((text_surface.get_width() + 24, text_surface.get_height() + 14), pygame.SRCALPHA)
            pygame.draw.rect(button_bg, (220, 220, 220, 200), button_bg.get_rect(), border_radius=18)
            surface.blit(button_bg, (button_rect.x - 12, button_rect.y - 7))
            surface.blit(text_surface, button_rect)
        if back_btn:
            idx = len(keyboard_buttons) + len(gamepad_buttons) + (1 if reset_btn else 0)
            color = (0, 150, 0) if selection_idx == idx else (44, 68, 132)
            if (self.waiting_for_key or self.waiting_for_gamepad) and selection_idx == idx:
                color = (255, 100, 100)
            text_surface = obra_font.render(back_btn["text"], True, color)
            button_rect = text_surface.get_rect(center=(col_x[1], special_y))
            button_bg = pygame.Surface((text_surface.get_width() + 24, text_surface.get_height() + 14), pygame.SRCALPHA)
            pygame.draw.rect(button_bg, (220, 220, 220, 200), button_bg.get_rect(), border_radius=18)
            surface.blit(button_bg, (button_rect.x - 12, button_rect.y - 7))
            surface.blit(text_surface, button_rect)
    
    def handle_event(self, event):
        if self.waiting_for_key:
            if event.type == KEYDOWN:
                if event.key not in [K_ESCAPE]:
                    self.settings.set_control(self.key_to_change, "keyboard", [event.key])
                    self.update_buttons()
                self.waiting_for_key = False
                self.key_to_change = None
            return None

        if self.waiting_for_gamepad:
            if event.type == JOYBUTTONDOWN:
                self.settings.set_control(self.key_to_change, "gamepad", [event.button])
                self.update_buttons()
                self.waiting_for_gamepad = False
                self.key_to_change = None
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                self.waiting_for_gamepad = False
                self.key_to_change = None
            return None

        # Nouvelle logique grille
        keyboard_buttons = [b for b in self.buttons if b.get("device") == "keyboard"]
        gamepad_buttons = [b for b in self.buttons if b.get("device") == "gamepad"]
        reset_btn = next((b for b in self.buttons if b.get("action") == "RESET"), None)
        back_btn = next((b for b in self.buttons if b.get("action") == STATE_BACK), None)
        num_keyboard = len(keyboard_buttons)
        num_gamepad = len(gamepad_buttons)
        has_reset = reset_btn is not None
        has_back = back_btn is not None
        max_rows = max(num_keyboard, num_gamepad)

        def get_grid_pos(idx):
            # Colonne, ligne
            if idx < num_keyboard:
                return (0, idx)
            elif idx < num_keyboard + num_gamepad:
                return (1, idx - num_keyboard)
            elif idx == num_keyboard + num_gamepad and has_reset:
                return (0, max_rows)
            elif idx == num_keyboard + num_gamepad + (1 if has_reset else 0) and has_back:
                return (1, max_rows)
            return (0, 0)

        def get_idx_from_grid(col, row):
            if col == 0:
                if row < num_keyboard:
                    return row
                elif has_reset and row == max_rows:
                    return num_keyboard + num_gamepad
            elif col == 1:
                if row < num_gamepad:
                    return num_keyboard + row
                elif has_back and row == max_rows:
                    return num_keyboard + num_gamepad + (1 if has_reset else 0)
            return None

        def get_grid_pos(idx):
            # Colonne, ligne
            if idx < num_keyboard:
                return (0, idx)
            elif idx < num_keyboard + num_gamepad:
                return (1, idx - num_keyboard)
            elif idx == num_keyboard + num_gamepad and has_reset:
                return (0, max_rows)
            elif idx == num_keyboard + num_gamepad + (1 if has_reset else 0) and has_back:
                return (1, max_rows)
            return (0, 0)

        def get_idx_from_grid(col, row):
            if col == 0:
                if row < num_keyboard:
                    return row
                elif has_reset and row == max_rows:
                    return num_keyboard + num_gamepad
            elif col == 1:
                if row < num_gamepad:
                    return num_keyboard + row
                elif has_back and row == max_rows:
                    return num_keyboard + num_gamepad + (1 if has_reset else 0)
            return None

        if event.type == KEYDOWN:
            col, row = get_grid_pos(self.current_selection)
            if event.key == K_UP:
                if row > 0:
                    new_idx = get_idx_from_grid(col, row - 1)
                    if new_idx is not None:
                        self.current_selection = new_idx
                else:
                    # Si on est sur le bouton spécial, remonter à la dernière ligne de la colonne
                    new_idx = get_idx_from_grid(col, max_rows - 1)
                    if new_idx is not None:
                        self.current_selection = new_idx
            elif event.key == K_DOWN:
                if (col == 0 and row == num_keyboard - 1) or (col == 1 and row == num_gamepad - 1):
                    # Dernière ligne de la colonne : descendre sur le bouton spécial
                    new_idx = get_idx_from_grid(col, max_rows)
                    if new_idx is not None:
                        self.current_selection = new_idx
                elif row < max_rows:
                    new_idx = get_idx_from_grid(col, row + 1)
                    if new_idx is not None:
                        self.current_selection = new_idx
            elif event.key == K_LEFT:
                if col == 1:
                    # Même ligne colonne clavier
                    new_idx = get_idx_from_grid(0, row)
                    if new_idx is not None:
                        self.current_selection = new_idx
            elif event.key == K_RIGHT:
                if col == 0:
                    # Même ligne colonne manette
                    new_idx = get_idx_from_grid(1, row)
                    if new_idx is not None:
                        self.current_selection = new_idx
            elif event.key == K_RETURN:
                button = self.displayed_buttons[self.current_selection]
                action = button["action"]
                device = button.get("device")
                if action == "RESET":
                    self.settings.reset_controls()
                    self.update_buttons()
                elif action == STATE_BACK:
                    return STATE_BACK
                elif action in self.settings.controls and device:
                    self.key_to_change = action
                    if device == "keyboard":
                        self.waiting_for_key = True
                    elif device == "gamepad":
                        self.waiting_for_gamepad = True
            elif event.key == K_ESCAPE:
                return STATE_BACK
            elif event.key == K_RETURN:
                button = self.displayed_buttons[self.current_selection]
                action = button["action"]
                device = button.get("device")
                if action == "RESET":
                    self.settings.reset_controls()
                    self.update_buttons()
                elif action == STATE_BACK:
                    return STATE_BACK
                elif action in self.settings.controls and device:
                    self.key_to_change = action
                    if device == "keyboard":
                        self.waiting_for_key = True
                    elif device == "gamepad":
                        self.waiting_for_gamepad = True
            elif event.key == K_ESCAPE:
                return STATE_BACK

        # Navigation au joystick (stick analogique vertical/horizontal)
        elif event.type == JOYAXISMOTION:
            col, row = get_grid_pos(self.current_selection)
            if event.axis == 1:
                if event.value < -0.999999:
                    if row > 0:
                        new_idx = get_idx_from_grid(col, row - 1)
                        if new_idx is not None:
                            self.current_selection = new_idx
                    else:
                        new_idx = get_idx_from_grid(col, max_rows - 1)
                        if new_idx is not None:
                            self.current_selection = new_idx
                elif event.value > 0.999999:
                    if (col == 0 and row == num_keyboard - 1) or (col == 1 and row == num_gamepad - 1):
                        new_idx = get_idx_from_grid(col, max_rows)
                        if new_idx is not None:
                            self.current_selection = new_idx
                    elif row < max_rows:
                        new_idx = get_idx_from_grid(col, row + 1)
                        if new_idx is not None:
                            self.current_selection = new_idx
            elif event.axis == 0:
                if event.value < -0.999999:
                    if col == 1:
                        new_idx = get_idx_from_grid(0, row)
                        if new_idx is not None:
                            self.current_selection = new_idx
                elif event.value > 0.999999:
                    if col == 0:
                        new_idx = get_idx_from_grid(1, row)
                        if new_idx is not None:
                            self.current_selection = new_idx

        # Navigation à la croix directionnelle (D-Pad)
        elif event.type == JOYHATMOTION:
            col, row = get_grid_pos(self.current_selection)
            if event.value[1] == 1:
                if row > 0:
                    new_idx = get_idx_from_grid(col, row - 1)
                    if new_idx is not None:
                        self.current_selection = new_idx
                else:
                    new_idx = get_idx_from_grid(col, max_rows - 1)
                    if new_idx is not None:
                        self.current_selection = new_idx
            elif event.value[1] == -1:
                if (col == 0 and row == num_keyboard - 1) or (col == 1 and row == num_gamepad - 1):
                    new_idx = get_idx_from_grid(col, max_rows)
                    if new_idx is not None:
                        self.current_selection = new_idx
                elif row < max_rows:
                    new_idx = get_idx_from_grid(col, row + 1)
                    if new_idx is not None:
                        self.current_selection = new_idx
            elif event.value[0] == -1:
                if col == 1:
                    new_idx = get_idx_from_grid(0, row)
                    if new_idx is not None:
                        self.current_selection = new_idx
            elif event.value[0] == 1:
                if col == 0:
                    new_idx = get_idx_from_grid(1, row)
                    if new_idx is not None:
                        self.current_selection = new_idx

        # Validation avec bouton A ou Start
        elif event.type == JOYBUTTONDOWN:
            if event.button in (0, 7):
                button = self.displayed_buttons[self.current_selection]
                action = button["action"]
                device = button.get("device")
                if action == "RESET":
                    self.settings.reset_controls()
                    self.update_buttons()
                elif action == STATE_BACK:
                    return STATE_BACK
                elif action in self.settings.controls and device:
                    self.key_to_change = action
                    if device == "keyboard":
                        self.waiting_for_key = True
                    elif device == "gamepad":
                        self.waiting_for_gamepad = True

        return None
