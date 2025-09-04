import pygame
from config import DEFAULT_CONTROLS

class GameSettings:
    """Classe pour gérer toutes les configurations du jeu."""
    def __init__(self):
        self.controls = {}
        for action, bindings in DEFAULT_CONTROLS.items():
            self.controls[action] = {
                "keyboard": bindings["keyboard"].copy(),
                "gamepad": bindings["gamepad"].copy()
            }
        self.music_on = True
        self.music_volume = 0.5
    
    def reset_controls(self):
        """Remet les contrôles par défaut."""
        for action, bindings in DEFAULT_CONTROLS.items():
            self.controls[action] = {
                "keyboard": bindings["keyboard"].copy(),
                "gamepad": bindings["gamepad"].copy()
            }
    
    def set_control(self, action, device, keys):
        """Modifie une action de contrôle pour un device spécifique."""
        if action in self.controls and device in ["keyboard", "gamepad"]:
            self.controls[action][device] = keys if isinstance(keys, list) else [keys]
    
    def get_control(self, action, device="keyboard"):
        """Récupère les touches pour une action et un device."""
        if action in self.controls and device in self.controls[action]:
            return self.controls[action][device]
        return []
    
    def toggle_music(self):
        """Active/désactive la musique."""
        self.music_on = not self.music_on
        if self.music_on:
            pygame.mixer.music.play(loops=-1)
            pygame.mixer.music.set_volume(self.music_volume)
        else:
            pygame.mixer.music.stop()
    
    def set_volume(self, volume):
        """Modifie le volume de la musique."""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)