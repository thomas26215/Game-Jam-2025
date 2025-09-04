import pygame
import random

class PoisonParticle:
    """Particule animée de poison autour d'un cœur vide."""
    def __init__(self, x, y):
        self.x = x + random.randint(-5, 5)
        self.y = y + random.randint(-5, 5)
        self.radius = random.randint(2, 5)
        self.color = (100, 255, 120)  # Vert toxique
        self.dx = random.uniform(-0.5, 0.5)
        self.dy = random.uniform(-0.8, -0.3)
        self.life = random.randint(18, 35)

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.radius *= 0.96
        self.life -= 1

    def is_alive(self):
        return self.life > 0 and self.radius > 0.8

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.radius))

class InfoHUD:
    """
    HUD avec effet poison sur les cœurs vides : particules animées autour des vies manquantes.
    """
    def __init__(self, max_lives=5, current_lives=None):
        self.max_lives = max_lives
        self.lives_left = current_lives if current_lives is not None else max_lives
        self.meds_collected = 0
        self.poisoned = False  # Active l'effet sur les cœurs vides
        self.font = pygame.font.SysFont(None, 32)
        self.heart_full_color = (220, 20, 60)
        self.heart_empty_color = (50, 205, 50)
        self.poison_particles = [[] for _ in range(self.max_lives)]

    def set_lives(self, lives):
        self.lives_left = max(0, min(lives, self.max_lives))

    def lose_life(self):
        if self.lives_left > 0:
            self.lives_left -= 1

    def gain_life(self):
        if self.lives_left < self.max_lives:
            self.lives_left += 1

    def add_med(self):
        self.meds_collected += 1

    def set_poisoned(self, poisoned=True):
        self.poisoned = poisoned

    def draw(self, screen):
        for i in range(self.max_lives):
            color = self.heart_full_color if i < self.lives_left else self.heart_empty_color
            x, y = 30 + i * 40, 30
            self.draw_heart(screen, x, y, 30, color)

            # Effet poison UNIQUEMENT sur les coeurs manquants (vides)
            if self.poisoned and i >= self.lives_left:
                # Nettoyage des particules mortes
                self.poison_particles[i] = [p for p in self.poison_particles[i] if p.is_alive()]
                # Génération de nouvelles particules chaque frame (densité effet poison)
                for _ in range(2):
                    self.poison_particles[i].append(PoisonParticle(x, y + 15))
                # Animation et affichage des particules
                for p in self.poison_particles[i]:
                    p.update()
                    p.draw(screen)

        txt = self.font.render(f"Médicaments : {self.meds_collected}", True, (255,255,255))
        screen.blit(txt, (30, 70))

    def draw_heart(self, surface, x, y, size, color):
        r = size // 2
        pygame.draw.circle(surface, color, (x - r // 2, y), r // 2)
        pygame.draw.circle(surface, color, (x + r // 2, y), r // 2)
        points = [(x - r, y), (x + r, y), (x, y + r + 6)]
        pygame.draw.polygon(surface, color, points)

