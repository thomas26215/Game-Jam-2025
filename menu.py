import pygame
from pygame.locals import *
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
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
                K_UP: "↑", K_DOWN: "↓", K_LEFT: "←", K_RIGHT: "→",
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
                4: "LB", 5: "RB", 6: "Back", 7: "Start",
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
            if(action_name == "Attaquer"):
                self.buttons.append({
                    "text": f"{action_name} (Manette): {buttons_text}",
                    "action": action,
                    "device": "gamepad"
                })
        
        # Boutons spéciaux
        self.buttons.append({"text": "Réinitialiser", "action": "RESET", "device": None})
        self.buttons.append({"text": "Retour", "action": "BACK", "device": None})
    
    def draw(self, surface):
        # Dessiner le fond
        if self.background:
            surface.blit(self.background, (0, 0))
        else:
            surface.fill((30, 30, 30))
        
        # Titre
        title = FONT.render("Configuration des contrôles", True, (255, 255, 0))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
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
                elif action == "BACK":
                    return "BACK"
                elif action in self.settings.controls and device:
                    self.key_to_change = action
                    if device == "keyboard":
                        self.waiting_for_key = True
                    elif device == "gamepad":
                        self.waiting_for_gamepad = True
            elif event.key == K_ESCAPE:
                return "BACK"
        
        return None

class Menu:
    def __init__(self, settings, title_image_path=None):
        self.settings = settings
        self.buttons = []
        self.current_selection = 0
        
        # Charger l'image de fond avec debug
        print("Tentative de chargement de right.png...")
        try:
            self.background = pygame.image.load("right.png").convert()
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
            print("✓ right.png chargé avec succès !")
        except pygame.error as e:
            print(f"✗ Impossible de charger right.png: {e}")
            self.background = None
        except FileNotFoundError:
            print("✗ Fichier right.png introuvable !")
            self.background = None
        
        # Charger l'image de titre personnalisée
        self.title_image = None
        if title_image_path:
            print(f"Tentative de chargement de {title_image_path}...")
            try:
                self.title_image = pygame.image.load(title_image_path).convert_alpha()
                print(f"✓ {title_image_path} chargé avec succès !")
            except pygame.error as e:
                print(f"✗ Impossible de charger {title_image_path}: {e}")
                self.title_image = None
            except FileNotFoundError:
                print(f"✗ Fichier {title_image_path} introuvable !")
                self.title_image = None
        
        # Animation du rat avec debug
        print("Tentative de chargement de rat/rat_droite.png...")
        try:
            self.rat_spritesheet = pygame.image.load("rat/rat_droite.png").convert_alpha()
            print("✓ rat/rat_droite.png chargé avec succès !")
            
            # Pour une spritesheet horizontale avec 55 frames de 240px de large
            self.rat_frame_width = 240
            self.rat_frame_height = self.rat_spritesheet.get_height()  # Hauteur complète de l'image
            self.rat_frames = []

            # Extraire les 27 premières frames horizontales
            for i in range(12, 37):
                frame = pygame.Surface((self.rat_frame_width, self.rat_frame_height), pygame.SRCALPHA)
                frame.blit(self.rat_spritesheet, (0, 0), (i * self.rat_frame_width, 0, self.rat_frame_width, self.rat_frame_height))
                self.rat_frames.append(frame)
            
            print(f"✓ {len(self.rat_frames)} frames extraites du sprite !")
            self.rat_current_frame = 0
            self.rat_animation_timer = 0
            self.rat_animation_speed = 100  # millisecondes entre chaque frame
            
            # Position et mouvement du rat
            self.rat_x = SCREEN_WIDTH // 2 - self.rat_frame_width // 2  # Commence au centre
            self.rat_y = SCREEN_HEIGHT // 2 - self.rat_frame_height // 2  # Milieu vertical
            self.rat_speed = 250  # pixels par seconde
            self.rat_direction = 1  # 1 pour droite, -1 pour gauche
            self.rat_visible = True  # Ajouter cette variable pour contrôler la visibilité

        except pygame.error as e:
            print(f"✗ Impossible de charger rat/rat_droite.png: {e}")
            self.rat_spritesheet = None
        except FileNotFoundError:
            print("✗ Fichier rat/rat_droite.png introuvable !")
            self.rat_spritesheet = None
        
    def add_button(self, text, action):
        button_surface = FONT.render(text, True, (255, 255, 255))
        self.buttons.append({"text": text, "surface": button_surface, "action": action})
    
    def update(self, dt):
        # Mettre à jour l'animation du rat
        if self.rat_spritesheet and self.rat_frames and self.rat_visible:
            # Animation des frames
            self.rat_animation_timer += dt
            if self.rat_animation_timer >= self.rat_animation_speed:
                self.rat_animation_timer = 0
                self.rat_current_frame = (self.rat_current_frame + 1) % len(self.rat_frames)
            
            # Mouvement du rat - disparaît quand il touche la droite
            if self.rat_x < SCREEN_WIDTH - self.rat_frame_width:
                self.rat_x += self.rat_speed * (dt / 1000.0)
            else:
                # Le rat a atteint le bord droit, il disparaît
                self.rat_visible = False

    def draw(self, surface):
        # Update button labels dynamically for options menu
        for button in self.buttons:
            if button["action"] == "TOGGLE_MUSIC":
                button["text"] = f"Music: {'ON' if self.settings.music_on else 'OFF'}"
                button["surface"] = FONT.render(button["text"], True, (255, 255, 255))
            elif button["action"] == "CHANGE_VOLUME":
                button["text"] = f"Volume: {int(self.settings.music_volume * 100)}%"
                button["surface"] = FONT.render(button["text"], True, (255, 255, 255))
        
        # Dessiner le fond
        if self.background:
            surface.blit(self.background, (0, 0))
        else:
            surface.fill((30, 30, 30))
        
        # Dessiner le rat animé seulement s'il est visible
        if self.rat_spritesheet and self.rat_frames and self.rat_visible:
            current_rat_frame = self.rat_frames[self.rat_current_frame]
            
            # Flip horizontal si le rat va vers la gauche
            if self.rat_direction == -1:
                current_rat_frame = pygame.transform.flip(current_rat_frame, True, False)
                
            surface.blit(current_rat_frame, (int(self.rat_x), int(self.rat_y)))
        
        # Titre avec image ou texte de fallback
        if self.title_image:
            # Réduire l'image à 40% de sa taille
            original_width = self.title_image.get_width()
            original_height = self.title_image.get_height()
            new_width = int(original_width * 0.4)
            new_height = int(original_height * 0.4)
            
            # Redimensionner l'image
            scaled_title_image = pygame.transform.scale(self.title_image, (new_width, new_height))
            
            # Centrer l'image redimensionnée
            title_rect = scaled_title_image.get_rect(center=(SCREEN_WIDTH // 2, 120))
            surface.blit(scaled_title_image, title_rect)
        else:
            # Fallback au texte si pas d'image
            title = FONT.render("Contagium", True, (255, 255, 0))
            title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 120))
            # Fond semi-transparent pour le titre
            title_bg = pygame.Surface((title.get_width() + 20, title.get_height() + 10))
            title_bg.set_alpha(128)
            title_bg.fill((0, 0, 0))
            surface.blit(title_bg, (title_rect.x - 10, title_rect.y - 5))
            surface.blit(title, title_rect)
        
        # Boutons avec fond semi-transparent (TOUJOURS affichés)
        for i, button in enumerate(self.buttons):
            color = (255, 0, 0) if i == self.current_selection else (255, 255, 255)
            button_surface = FONT.render(button["text"], True, color)
            y_pos = 280 + i * 100
            button_rect = button_surface.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
            
            # Fond semi-transparent pour les boutons
            button_bg = pygame.Surface((button_surface.get_width() + 20, button_surface.get_height() + 10))
            button_bg.set_alpha(128)
            button_bg.fill((0, 0, 0))
            surface.blit(button_bg, (button_rect.x - 10, button_rect.y - 5))
            surface.blit(button_surface, button_rect)
            
            # Draw slider if it's the volume option
            if button["action"] == "VOLUME_SLIDER":
                bar_width = 200
                bar_height = 8
                bar_x = SCREEN_WIDTH // 2 - bar_width // 2
                bar_y = y_pos + 40

                # Bar background
                pygame.draw.rect(surface, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
                # Fill based on volume
                fill_width = int(bar_width * self.settings.music_volume)
                pygame.draw.rect(surface, (0, 200, 0), (bar_x, bar_y, fill_width, bar_height))

                # Knob
                knob_x = bar_x + fill_width - 5
                knob_y = bar_y - 6
                pygame.draw.rect(surface, (255, 255, 255), (knob_x, knob_y, 10, 20))
        
    def handle_event(self, event):
        if event.type == KEYDOWN:
            if event.key == K_UP:
                self.current_selection = (self.current_selection - 1) % len(self.buttons)
            elif event.key == K_DOWN:
                self.current_selection = (self.current_selection + 1) % len(self.buttons)

            # Enter to activate a button
            elif event.key == K_RETURN:
                action = self.buttons[self.current_selection]["action"]
                if action == "TOGGLE_MUSIC":
                    self.settings.toggle_music()
                    return None
                elif action == "VOLUME_SLIDER":
                     # Do nothing, volume is adjusted with arrows only
                    return None
                else:
                    return action

            # Left/Right for adjusting volume if slider is selected
            elif self.buttons[self.current_selection]["action"] == "VOLUME_SLIDER":
                if event.key == K_LEFT:
                    self.settings.set_volume(self.settings.music_volume - 0.05)
                elif event.key == K_RIGHT:
                    self.settings.set_volume(self.settings.music_volume + 0.05)

        elif event.type == MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for i, button in enumerate(self.buttons):
                button_surface = button["surface"]
                bx = SCREEN_WIDTH // 2 - button_surface.get_width() // 2
                by = 280 + i * 100
                if bx < mx < bx + button_surface.get_width() and by < my < by + button_surface.get_height():
                    return button["action"]

        return None

# SORTIR cette fonction de la classe Menu !
def init_menus(settings):
    # Vérifier que les fichiers existent
    import os
    
    image_files = [
        "./wordsGame/contagium.png",
        "./wordsGame/playPause.png", 
        "./wordsGame/gameOver.png",
        "./wordsGame/victory.png"
    ]
    
    for img_file in image_files:
        if os.path.exists(img_file):
            print(f"✓ Fichier trouvé : {img_file}")
        else:
            print(f"✗ Fichier MANQUANT : {img_file}")
    
    main_menu = Menu(settings, "wordsGame/contagium.png")
    main_menu.add_button("Jouer", STATE_PLAY)
    main_menu.add_button("Options", STATE_OPTIONS)
    main_menu.add_button("Quitter", "QUIT")
    
    pause_menu = Menu(settings, "wordsGame/playPause.png")
    pause_menu.add_button("Reprendre", STATE_PLAY)
    pause_menu.add_button("Options", STATE_OPTIONS)
    pause_menu.add_button("Menu Principal", STATE_MENU)
    pause_menu.add_button("Quitter", "QUIT")
    
    options_menu = Menu(settings, "wordsGame/options.png")
    options_menu.add_button("Music: ON", "TOGGLE_MUSIC")
    options_menu.add_button("Volume", "VOLUME_SLIDER")
    options_menu.add_button("Contrôles", "CONTROLS")
    options_menu.add_button("Retour", "BACK")
    
    game_over_menu = Menu(settings, "wordsGame/gameOver.png")
    game_over_menu.add_button("Rejouer", STATE_PLAY)
    game_over_menu.add_button("Menu Principal", STATE_MENU)
    game_over_menu.add_button("Quitter", "QUIT")
    
    controls_menu = ControlsMenu(settings)
    
    return {
        STATE_MENU: main_menu,
        STATE_PAUSE: pause_menu,
        STATE_OPTIONS: options_menu,
        STATE_GAME_OVER: game_over_menu,
        "CONTROLS": controls_menu
    }
