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
        title = pygame.image.load("wordsGame/controle.png").convert_alpha()
        title = pygame.transform.scale(title, (int(title.get_width() * 0.4), int(title.get_height() * 0.4)))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 130))
        surface.blit(title, title_rect)
        
        # Message d'attente
        if self.waiting_for_key:
            wait_text = FONT.render("Appuyez sur une touche clavier...", True, (255, 100, 100))
            wait_rect = wait_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
            surface.blit(wait_text, wait_rect)
        elif self.waiting_for_gamepad:
            wait_text = FONT.render("Appuyez sur un bouton de manette...", True, (255, 100, 100))
            wait_rect = wait_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
            surface.blit(wait_text, wait_rect)
        
        # Boutons (plus compacts)
        for i, button in enumerate(self.buttons):
            color = (255, 0, 0) if i == self.current_selection else (255, 255, 255)
            if (self.waiting_for_key or self.waiting_for_gamepad) and i == self.current_selection:
                color = (255, 100, 100)
            
            # Police plus petite pour plus de boutons
            small_font = pygame.font.SysFont("Arial", 24)
            button_surface = small_font.render(button["text"], True, color)
            y_pos = 120 + i * 35  # Espacement réduit
            button_rect = button_surface.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
            
            # Fond semi-transparent
            button_bg = pygame.Surface((button_surface.get_width() + 20, button_surface.get_height() + 5))
            button_bg.set_alpha(128)
            button_bg.fill((0, 0, 0))
            surface.blit(button_bg, (button_rect.x - 10, button_rect.y - 2))
            surface.blit(button_surface, button_rect)
    
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
        
        # Navigation clavier
        if event.type == KEYDOWN:
            if event.key == K_UP:
                self.current_selection = (self.current_selection - 1) % len(self.buttons)
            elif event.key == K_DOWN:
                self.current_selection = (self.current_selection + 1) % len(self.buttons)
            elif event.key == K_RETURN:
                button = self.buttons[self.current_selection]
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

        # Navigation au joystick (stick analogique vertical)
        elif event.type == JOYAXISMOTION:
            if event.axis == 1:
                if event.value < -0.999999:  # stick vers le haut
                    self.current_selection = (self.current_selection - 1) % len(self.buttons)
                elif event.value > 0.999999:  # stick vers le bas
                    self.current_selection = (self.current_selection + 1) % len(self.buttons)

        # Navigation à la croix directionnelle (D-Pad)
        elif event.type == JOYHATMOTION:
            # event.value = (x, y) => y = 1 haut, -1 bas
            if event.value[1] == 1:
                self.current_selection = (self.current_selection - 1) % len(self.buttons)
            elif event.value[1] == -1:
                self.current_selection = (self.current_selection + 1) % len(self.buttons)

        # Validation avec bouton A ou Start
        elif event.type == JOYBUTTONDOWN:
            if event.button in (0, 7):
                button = self.buttons[self.current_selection]
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
