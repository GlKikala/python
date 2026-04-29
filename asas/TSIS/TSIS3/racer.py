import pygame
import random
from persistence import add_score

class RacerGame:
    def __init__(self, screen, username, settings):
        self.screen = screen
        self.username = username
        self.settings = settings
        self.clock = pygame.time.Clock()
        self.width, self.height = 400, 700

        self.player = pygame.Rect(180, 580, 40, 80)
        self.speed = 6
        self.base_speed = 6

        self.traffic = []
        self.obstacles = []
        self.powerups = []

        self.coins = 0
        self.score = 0
        self.distance = 0

        self.active_power = None
        self.power_timer = 0
        self.shield = False

        self.running = True

    def spawn_traffic(self):
        lane = random.choice([60, 160, 260])
        self.traffic.append(pygame.Rect(lane, -100, 40, 80))

    def spawn_obstacle(self):
        lane = random.choice([60, 160, 260])
        self.obstacles.append((pygame.Rect(lane, -50, 40, 40), random.choice(["oil", "barrier", "pothole"])))

    def spawn_powerup(self):
        lane = random.choice([60, 160, 260])
        kind = random.choice(["nitro", "shield", "repair"])
        self.powerups.append((pygame.Rect(lane, -40, 30, 30), kind, 300))

    def draw(self):
        self.screen.fill((60,60,60))
        pygame.draw.rect(self.screen, (255,0,0), self.player)

        for car in self.traffic:
            pygame.draw.rect(self.screen, (0,0,255), car)

        for obs, kind in self.obstacles:
            color = (0,0,0) if kind=="oil" else (255,255,0)
            pygame.draw.rect(self.screen, color, obs)

        for p, kind, _ in self.powerups:
            color = (0,255,255) if kind=="nitro" else (255,255,255) if kind=="shield" else (0,255,0)
            pygame.draw.rect(self.screen, color, p)

        font = pygame.font.SysFont("Arial", 24)
        self.screen.blit(font.render(f"Score: {self.score}", True, (255,255,255)), (10,10))
        self.screen.blit(font.render(f"Dist: {self.distance}", True, (255,255,255)), (10,40))
        self.screen.blit(font.render(f"Power: {self.active_power}", True, (255,255,255)), (10,70))

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.player.x > 50:
            self.player.x -= self.speed
        if keys[pygame.K_RIGHT] and self.player.x < 310:
            self.player.x += self.speed

        self.distance += 1
        self.score = self.coins * 10 + self.distance

        if random.randint(1, 40) == 1:
            self.spawn_traffic()
        if random.randint(1, 60) == 1:
            self.spawn_obstacle()
        if random.randint(1, 300) == 1:
            self.spawn_powerup()

        for car in self.traffic[:]:
            car.y += self.speed
            if car.colliderect(self.player):
                if self.shield:
                    self.shield = False
                    self.traffic.remove(car)
                else:
                    self.running = False
            elif car.y > 700:
                self.traffic.remove(car)

        for obs, kind in self.obstacles[:]:
            obs.y += self.speed
            if obs.colliderect(self.player):
                if kind == "oil":
                    self.player.x += random.choice([-40, 40])
                elif kind == "barrier":
                    self.running = False
                elif kind == "pothole":
                    self.speed = max(3, self.speed - 2)
                self.obstacles.remove((obs, kind))
            elif obs.y > 700:
                self.obstacles.remove((obs, kind))

        for item in self.powerups[:]:
            rect, kind, timer = item
            rect.y += self.speed
            timer -= 1

            if rect.colliderect(self.player):
                self.active_power = kind
                if kind == "nitro":
                    self.speed = 10
                    self.power_timer = 180
                elif kind == "shield":
                    self.shield = True
                elif kind == "repair":
                    self.speed = self.base_speed
                self.powerups.remove(item)
            elif timer <= 0 or rect.y > 700:
                self.powerups.remove(item)

        if self.active_power == "nitro":
            self.power_timer -= 1
            if self.power_timer <= 0:
                self.speed = self.base_speed
                self.active_power = None

    def game_over(self):
        add_score(self.username, self.score, self.distance)

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

        self.game_over()