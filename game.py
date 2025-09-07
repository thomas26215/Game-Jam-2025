import pygame

from config import COLLECT_MEDECINE, FONT, SCREEN_HEIGHT, SCREEN_WIDTH
import draw_minimap
from infos_hud import InfoHUD
from player import Player
from room import draw_portal_if_boss_room, generate_random_grid, clear_all_medicaments_in_rooms, generate_boss_room_for
import random


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
        self.total_zombies = random.randint(20, 40)
        self.is_portal_active = True

    def init_game(self):
        self.grid = generate_random_grid(num_rooms=2, total_zombies = self.total_zombies)
        self.current_pos = (0, 0)
        self.resurrected_count = 0 #Compteur de ressuscités
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
                    if quest == COLLECT_MEDECINE:
                        damage = 1
                        enemy.take_damage(damage=damage)
                    else:  # 🔹 En mode HEAL_INFECTED
                        if enemy.health > 0:  # Convention : vie < 0 = "ressuscité"
                            self.resurrected_count += 1
                        enemy.take_damage(damage=3)
                    
                    break  # On évite le double-hit
            self.player.has_hit_enemy = True
            print("Nombre de ressuscités :", self.resurrected_count)


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

        if self.is_portal_active:
            on_portal = draw_portal_if_boss_room(pygame.display.get_surface(), self.current_room, self.player, self.settings)
        else:
            on_portal = draw_portal_if_boss_room(pygame.display.get_surface(), self.current_room, self.player, self.settings, is_active = False)

        if on_portal and interact_pressed:
            if quest == COLLECT_MEDECINE:
                # Mode normal : téléportation au départ
                self.teleport_to_start()
                clear_all_medicaments_in_rooms(self.grid)
                return True
            else:  
                self.is_portal_active = False
                # 🔹 Mode HEAL_INFECTED
                from room import generate_boss_room_for
                from enemy import Enemy

                # Trouver la salle finale
                final_room = next((room for room in self.grid.values() if getattr(room, "is_final", False)), None)
                if final_room:
                    # Régénérer la salle du boss
                    generate_boss_room_for(final_room, self.grid)

                    self.player.make_invisible_and_immobile()  # 3 sec d'invisibilité et immobilité

                    # Générer les ressuscités
                    for _ in range(self.resurrected_count):
                        x = random.randint(50, SCREEN_WIDTH - 50)
                        y = random.randint(50, SCREEN_HEIGHT - 50)
                        human = Enemy(
                            x, y, self.player,
                            SCREEN_WIDTH, SCREEN_HEIGHT,
                            sprites_folder="Humans/Homeless_1",
                            base_health=2,
                            is_final_scene=True,
                            frame_width=128,
                            frame_height=128,
                        )
                        final_room.enemies.append(human)

                    # ⏱️ Lancer le compte à rebours (10 sec)
                    self.end_timer = pygame.time.get_ticks()
                    self.show_end_message = False

                return True

        return False

    def draw_end_sequence(self, surface):
        """Affiche le fondu noir et le message de fin après 10s, puis retourne True après 5s de message."""
        if hasattr(self, "end_timer"):
            elapsed = pygame.time.get_ticks() - self.end_timer

            # Étape 1 : après 5 sec → afficher fondu + texte
            if elapsed > 5000:
                fade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                fade.fill((0, 0, 0))
                fade.set_alpha(220)
                surface.blit(fade, (0, 0))

                # Texte du message final
                font = pygame.font.SysFont("Arial", 32, bold=True)
                saved = self.resurrected_count
                perished = max(0,  - self.resurrected_count)
                win = False
                
                if saved == self.total_zombies:
                    lines = [
                        "Félicitations !",
                        "Vous avez sauvés toutes les personnes infectées.",
                        f"Vous êtes un grand médecin !"
                    ]
                    win = True
                elif saved < self.total_zombies :
                    lines = [
                        f"{self.total_zombies-saved} personnes ont péri par votre faute.",
                        "Réessayez pour sauver plus de personnes."
                    ]
                else:
                    lines = [
                        "Réessayez pour sauver plus de personnes."
                    ]

                y = SCREEN_HEIGHT // 2 - len(lines) * 20
                for line in lines:
                    text_surf = font.render(line, True, (255, 255, 255))
                    rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, y))
                    surface.blit(text_surf, rect)
                    y += 50

                # Étape 2 : attendre 5 sec supplémentaires avant retour
                if elapsed > 10000:  
                    return win  # ✅ Signale à main() que la séquence de fin est terminée

        return None



        
    def draw(self, surface, quest):
        self.current_room.draw(surface)
        self.current_room.draw_contents(surface)
        if self.is_portal_active:
            draw_portal_if_boss_room(surface, self.current_room, self.player, self.settings)
        else:
            draw_portal_if_boss_room(surface, self.current_room, self.player, self.settings, is_active = False)

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

        # 🔹 Dessiner la séquence de fin si timer actif
        self.draw_end_sequence(surface)


