import pygame
import random
from room import generate_random_grid, draw_portal_if_boss_room
from player import Player
from infos_hud import InfoHUD
from config import SCREEN_WIDTH, SCREEN_HEIGHT

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
        self.VISION_RADIUS = 300
        
    def init_game(self):
        self.grid = generate_random_grid(num_rooms=10)
        self.current_pos = (0, 0)
        self.current_room = self.grid[self.current_pos]
        
        self.player = Player(
            SCREEN_WIDTH//2, SCREEN_HEIGHT//2, self.settings,
            SCREEN_WIDTH, SCREEN_HEIGHT,
            walk_spritesheet_path="player/walk.png",
            idle_spritesheet_path="player/idle.png",
            attack_spritesheet_path="player/attack.png",
            hurt_spritesheet_path="player/damage.png",
            death_spritesheets=["player/death1.png", "player/death2.png"],
            frame_width=64, frame_height=64
        )
        self.current_room.generate_contents(self.player, SCREEN_WIDTH, SCREEN_HEIGHT)
        
        self.hud = InfoHUD(max_lives=3, current_lives=3)
        self.hud.set_poisoned(True)
        
        self.visited_rooms = set()
        self.visited_rooms.add(self.current_pos)
        self.has_taken_first_med = False
    
    def update_player(self, keys):
        self.player.update(keys, self.current_room)
    
    def check_player_attack(self):
        if self.player.state == "attack" and hasattr(self.player, "attack_rect") and not self.player.has_hit_enemy:
            for enemy in self.current_room.enemies:
                if enemy.alive and self.player.attack_rect.colliderect(enemy.rect):
                    enemy.take_damage()
                    self.player.has_hit_enemy = True
                    break
    
    def update_enemies(self):
        for enemy in self.current_room.enemies:
            enemy.update(self.current_room)
        self.current_room.enemies = [e for e in self.current_room.enemies if e.alive]
    
    def update_medicaments(self):
        for med in self.current_room.medicaments:
            med.update()
            if not med.collected and self.player.rect.colliderect(med.rect):
                med.collect()
                self.hud.add_med()
                if self.current_pos == (0, 0):
                    self.has_taken_first_med = True
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
                
                if self.current_pos == (0,0) and not self.has_taken_first_med:
                    return False
                
                if new_pos in self.grid:
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
    
    def draw(self, screen):
        self.current_room.draw(screen)
        self.current_room.draw_contents(screen)
        
        on_portal = draw_portal_if_boss_room(screen, self.current_room, self.player, self.settings)
        
        screen.blit(self.player.image, self.player.rect)
        pygame.draw.rect(screen, (255, 0, 0), self.player.hitbox, 2)
        
        for enemy in self.current_room.enemies:
            enemy.draw(screen)
            pygame.draw.rect(screen, (255, 0, 0), enemy.rect, 2)
        for med in self.current_room.medicaments:
            med.draw(screen)
        
        self.shadow_surface.fill((0, 0, 0, 255))
        for r in range(self.VISION_RADIUS, 0, -2):
            t = r / self.VISION_RADIUS
            alpha = int(255 * (1 - (1 - t) ** 3))
            pygame.draw.circle(self.shadow_surface, (0, 0, 0, alpha), self.player.rect.center, r)
        screen.blit(self.shadow_surface, (0, 0))
        
        draw_minimap(screen, self.grid, self.current_pos, self.visited_rooms)
        
        self.hud.set_lives(self.player.health)
        self.hud.draw(screen)
        
        if self.current_pos == (0,0) and not self.has_taken_first_med:
            message = FONT.render("Récupérez le médicament pour continuer !", True, (255, 0, 0))
            msg_x = SCREEN_WIDTH // 2 - message.get_width() // 2
            msg_y = 20
            screen.blit(message, (msg_x, msg_y))
    
    def player_on_portal_interact(self):
        keys = pygame.key.get_pressed()
        interact_pressed = any(keys[key] for key in self.settings.get_control("interact", "keyboard"))
        if self.player.joystick and not interact_pressed:
            interact_pressed = any(self.player.joystick.get_button(btn) for btn in self.settings.get_control("interact", "gamepad"))
        
        on_portal = draw_portal_if_boss_room(pygame.display.get_surface(), self.current_room, self.player, self.settings)
        
        if on_portal and interact_pressed:
            return True
        return False

