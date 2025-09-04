import pygame
from pygame.locals import *
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    STATE_MENU, STATE_PLAY, STATE_PAUSE, STATE_GAME_OVER, STATE_OPTIONS,
    FONT
)
# --- Options state ---
music_on = True
music_volume = 0.5 

# Créer une classe Menu pour une meilleure organisation
class Menu:
    def __init__(self, title_image_path=None):
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
        global music_on, music_volume

        # Update button labels dynamically for options menu
        for button in self.buttons:
            if button["action"] == "TOGGLE_MUSIC":
                button["text"] = f"Music: {'ON' if music_on else 'OFF'}"
                button["surface"] = FONT.render(button["text"], True, (255, 255, 255))
            elif button["action"] == "CHANGE_VOLUME":
                button["text"] = f"Volume: {int(music_volume * 100)}%"
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
            # Réduire l'image à 80% de sa taille
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
                fill_width = int(bar_width * music_volume)
                pygame.draw.rect(surface, (0, 200, 0), (bar_x, bar_y, fill_width, bar_height))

                # Knob
                knob_x = bar_x + fill_width - 5
                knob_y = bar_y - 6
                pygame.draw.rect(surface, (255, 255, 255), (knob_x, knob_y, 10, 20))

        
    def handle_event(self, event):
        global music_on, music_volume

        if event.type == KEYDOWN:
            if event.key == K_UP:
                self.current_selection = (self.current_selection - 1) % len(self.buttons)
            elif event.key == K_DOWN:
                self.current_selection = (self.current_selection + 1) % len(self.buttons)

            # Enter to activate a button
            elif event.key == K_RETURN:
                action = self.buttons[self.current_selection]["action"]
                if action == "TOGGLE_MUSIC":
                    music_on = not music_on
                    if music_on:
                        pygame.mixer.music.play(loops=-1)
                        pygame.mixer.music.set_volume(music_volume)
                    else:
                        pygame.mixer.music.stop()
                    return None
                elif action == "VOLUME_SLIDER":
                     # Do nothing, volume is adjusted with arrows only
                    return None
                else:
                    return action

            # Left/Right for adjusting volume if slider is selected
            elif self.buttons[self.current_selection]["action"] == "VOLUME_SLIDER":
                if event.key == K_LEFT:
                    music_volume = max(0.0, music_volume - 0.05)
                    pygame.mixer.music.set_volume(music_volume)
                elif event.key == K_RIGHT:
                    music_volume = min(1.0, music_volume + 0.05)
                    pygame.mixer.music.set_volume(music_volume)

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
def init_menus():
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
    
    main_menu = Menu("wordsGame/contagium.png")
    main_menu.add_button("Jouer", STATE_PLAY)
    main_menu.add_button("Options", STATE_OPTIONS)
    main_menu.add_button("Quitter", "QUIT")
    
    pause_menu = Menu("wordsGame/playPause.png")
    pause_menu.add_button("Reprendre", STATE_PLAY)
    pause_menu.add_button("Options", STATE_OPTIONS)
    pause_menu.add_button("Menu Principal", STATE_MENU)
    pause_menu.add_button("Quitter", "QUIT")
    
    options_menu = Menu("wordsGame/options.png")
    options_menu.add_button("Music: ON", "TOGGLE_MUSIC")
    options_menu.add_button("Volume", "VOLUME_SLIDER")
    options_menu.add_button("Retour", "BACK")
    
    game_over_menu = Menu("wordsGame/gameOver.png")
    game_over_menu.add_button("Rejouer", STATE_PLAY)
    game_over_menu.add_button("Menu Principal", STATE_MENU)
    game_over_menu.add_button("Quitter", "QUIT")
    
    return {
        STATE_MENU: main_menu,
        STATE_PAUSE: pause_menu,
        STATE_OPTIONS: options_menu,
        STATE_GAME_OVER: game_over_menu
    }