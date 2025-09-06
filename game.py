import pygame

from config import COLLECT_MEDECINE, FONT, SCREEN_HEIGHT, SCREEN_WIDTH
import draw_minimap
from infos_hud import InfoHUD
from player import Player
from room import draw_portal_if_boss_room, generate_random_grid, clear_all_medicaments_in_rooms


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
      
    def player_on_portal_interact(self, quest):
        keys = pygame.key.get_pressed()
        interact_pressed = any(keys[key] for key in self.settings.get_control("interact", "keyboard"))
        if self.player.joystick and not interact_pressed:
            interact_pressed = any(self.player.joystick.get_button(btn) for btn in self.settings.get_control("interact", "gamepad"))
        
        on_portal = draw_portal_if_boss_room(pygame.display.get_surface(), self.current_room, self.player, self.settings)
        
        if on_portal and interact_pressed and quest == COLLECT_MEDECINE:
            self.teleport_to_start()
            clear_all_medicaments_in_rooms(self.grid)
            return True
        return False  
        
    def draw(self, surface, quest):
        self.current_room.draw(surface)
        self.current_room.draw_contents(surface)
        draw_portal_if_boss_room(surface, self.current_room, self.player, self.settings)
        self.player.draw(surface)

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
        draw_minimap.draw_minimap(surface, self.grid, self.current_pos, self.visited_rooms)
        self.hud.set_lives(self.player.health)
        self.hud.draw(surface)

        if self.current_pos == (0, 0) and not self.has_taken_first_med:
            message = FONT.render("Récupérez la potion pour continuer !", True, (255, 0, 0))
            surface.blit(message, (SCREEN_WIDTH // 2 - message.get_width() // 2, 20))
