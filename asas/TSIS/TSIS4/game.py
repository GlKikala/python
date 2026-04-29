import random
import pygame

from db import get_personal_best
from ui import draw_text, FONT, SMALL_FONT, WHITE, BLACK


WIDTH = 700
HEIGHT = 700
TOP_PANEL = 80

CELL_SIZE = 20
COLS = WIDTH // CELL_SIZE
ROWS = (HEIGHT - TOP_PANEL) // CELL_SIZE

BASE_SPEED = 8
FOODS_FOR_NEXT_LEVEL = 4

NORMAL_FOOD_LIFETIME = 7000
POWERUP_LIFETIME = 8000
POWERUP_DURATION = 5000


class SnakeGame:
    def __init__(self, screen, clock, username, settings):
        self.screen = screen
        self.clock = clock
        self.username = username
        self.settings = settings

        self.snake_color = tuple(settings["snake_color"])
        self.grid_enabled = settings["grid"]

        # If database has an error, the game must still start.
        try:
            self.personal_best = get_personal_best(username)
        except Exception:
            self.personal_best = 0

        self.snake = [(8, 8), (7, 8), (6, 8)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)

        self.score = 0
        self.level = 1
        self.food_eaten_on_level = 0
        self.speed = BASE_SPEED

        self.obstacles = []
        self.normal_food = None
        self.poison_food = None
        self.powerup = None

        self.active_powerup = None
        self.powerup_end_time = 0
        self.shield = False

        self.game_over = False

        self.spawn_normal_food()
        self.spawn_poison_food()

    def grid_to_pixel(self, pos):
        x, y = pos
        return x * CELL_SIZE, TOP_PANEL + y * CELL_SIZE

    def is_inside(self, pos):
        x, y = pos
        return 0 <= x < COLS and 0 <= y < ROWS

    def occupied_cells(self):
        cells = set(self.snake)
        cells.update(self.obstacles)

        if self.normal_food:
            cells.add(self.normal_food["pos"])

        if self.poison_food:
            cells.add(self.poison_food["pos"])

        if self.powerup:
            cells.add(self.powerup["pos"])

        return cells

    def random_empty_cell(self):
        occupied = self.occupied_cells()

        while True:
            pos = (random.randint(0, COLS - 1), random.randint(0, ROWS - 1))

            if pos not in occupied:
                return pos

    def spawn_normal_food(self):
        """Weighted disappearing food from Practice 11 idea."""
        value = random.choice([1, 1, 1, 2, 2, 3, 5])
        colors = {
            1: (220, 0, 0),
            2: (255, 140, 0),
            3: (230, 230, 0),
            5: (150, 0, 220)
        }

        self.normal_food = {
            "pos": self.random_empty_cell(),
            "value": value,
            "color": colors[value],
            "spawn_time": pygame.time.get_ticks()
        }

    def spawn_poison_food(self):
        """Poison food shortens snake."""
        if random.random() < 0.55:
            self.poison_food = {
                "pos": self.random_empty_cell(),
                "spawn_time": pygame.time.get_ticks()
            }
        else:
            self.poison_food = None

    def spawn_powerup(self):
        """Only one power-up active on field."""
        if self.powerup is not None:
            return

        if random.random() < 0.015:
            self.powerup = {
                "pos": self.random_empty_cell(),
                "type": random.choice(["speed", "slow", "shield"]),
                "spawn_time": pygame.time.get_ticks()
            }

    def create_obstacles_for_level(self):
        """Starting from Level 3, create static obstacle blocks."""
        if self.level < 3:
            return

        self.obstacles.clear()

        count = min(8 + self.level * 2, 28)
        head = self.snake[0]

        safe_area = {
            head,
            (head[0] + 1, head[1]),
            (head[0] - 1, head[1]),
            (head[0], head[1] + 1),
            (head[0], head[1] - 1)
        }

        attempts = 0

        while len(self.obstacles) < count and attempts < 500:
            attempts += 1
            pos = (random.randint(1, COLS - 2), random.randint(1, ROWS - 2))

            if pos in self.snake:
                continue

            if pos in safe_area:
                continue

            if pos in self.obstacles:
                continue

            self.obstacles.append(pos)

    def change_level(self):
        self.level += 1
        self.food_eaten_on_level = 0
        self.speed += 1
        self.create_obstacles_for_level()

        self.spawn_normal_food()
        self.spawn_poison_food()
        self.powerup = None

    def activate_powerup(self, power_type):
        """Apply collected power-up."""
        now = pygame.time.get_ticks()

        self.active_powerup = power_type

        if power_type == "speed":
            self.powerup_end_time = now + POWERUP_DURATION

        elif power_type == "slow":
            self.powerup_end_time = now + POWERUP_DURATION

        elif power_type == "shield":
            self.shield = True
            self.powerup_end_time = 0

    def current_speed(self):
        if self.active_powerup == "speed":
            return self.speed + 4

        if self.active_powerup == "slow":
            return max(4, self.speed - 4)

        return self.speed

    def update_powerup_time(self):
        now = pygame.time.get_ticks()

        if self.active_powerup in ["speed", "slow"]:
            if now >= self.powerup_end_time:
                self.active_powerup = None
                self.powerup_end_time = 0

    def use_shield_or_die(self):
        """Shield ignores next wall/self/obstacle collision once."""
        if self.shield:
            self.shield = False
            self.active_powerup = None
            return False

        self.game_over = True
        return True

    def handle_input(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_UP or event.key == pygame.K_w:
            if self.direction != (0, 1):
                self.next_direction = (0, -1)

        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
            if self.direction != (0, -1):
                self.next_direction = (0, 1)

        elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
            if self.direction != (1, 0):
                self.next_direction = (-1, 0)

        elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
            if self.direction != (-1, 0):
                self.next_direction = (1, 0)

    def move(self):
        self.update_powerup_time()

        now = pygame.time.get_ticks()

        # Food disappears after timer
        if self.normal_food and now - self.normal_food["spawn_time"] > NORMAL_FOOD_LIFETIME:
            self.spawn_normal_food()

        if self.poison_food and now - self.poison_food["spawn_time"] > NORMAL_FOOD_LIFETIME:
            self.spawn_poison_food()

        if self.powerup and now - self.powerup["spawn_time"] > POWERUP_LIFETIME:
            self.powerup = None

        self.spawn_powerup()

        self.direction = self.next_direction

        head_x, head_y = self.snake[0]
        dx, dy = self.direction

        new_head = (head_x + dx, head_y + dy)

        # Wall collision
        if not self.is_inside(new_head):
            if self.use_shield_or_die():
                return
            new_head = self.snake[0]

        # Self collision
        if new_head in self.snake:
            if self.use_shield_or_die():
                return
            new_head = self.snake[0]

        # Obstacle collision
        if new_head in self.obstacles:
            if self.use_shield_or_die():
                return
            new_head = self.snake[0]

        self.snake.insert(0, new_head)

        ate_normal = self.normal_food and new_head == self.normal_food["pos"]
        ate_poison = self.poison_food and new_head == self.poison_food["pos"]
        ate_powerup = self.powerup and new_head == self.powerup["pos"]

        if ate_normal:
            value = self.normal_food["value"]
            self.score += value * 10
            self.food_eaten_on_level += 1

            self.spawn_normal_food()

            if self.food_eaten_on_level >= FOODS_FOR_NEXT_LEVEL:
                self.change_level()

        elif ate_poison:
            # Remove new growth and shorten by 2 more segments
            self.poison_food = None

            for _ in range(3):
                if self.snake:
                    self.snake.pop()

            if len(self.snake) <= 1:
                self.game_over = True
                return

            self.spawn_poison_food()

        elif ate_powerup:
            self.activate_powerup(self.powerup["type"])
            self.powerup = None
            self.snake.pop()

        else:
            self.snake.pop()

    def draw_grid(self):
        if not self.grid_enabled:
            return

        for x in range(0, WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, (220, 220, 220), (x, TOP_PANEL), (x, HEIGHT))

        for y in range(TOP_PANEL, HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, (220, 220, 220), (0, y), (WIDTH, y))

    def draw_cell(self, pos, color):
        x, y = self.grid_to_pixel(pos)
        rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, BLACK, rect, 1)

    def draw_hud(self):
        pygame.draw.rect(self.screen, (245, 245, 245), (0, 0, WIDTH, TOP_PANEL))
        pygame.draw.line(self.screen, BLACK, (0, TOP_PANEL), (WIDTH, TOP_PANEL), 2)

        draw_text(self.screen, f"Player: {self.username}", 10, 8)
        draw_text(self.screen, f"Score: {self.score}", 10, 40)

        draw_text(self.screen, f"Level: {self.level}", 220, 8)
        draw_text(self.screen, f"Speed: {self.current_speed()}", 220, 40)

        draw_text(self.screen, f"Best: {self.personal_best}", 390, 8)

        if self.active_powerup in ["speed", "slow"]:
            remaining = max(0, (self.powerup_end_time - pygame.time.get_ticks()) // 1000)
            power_text = f"Power: {self.active_powerup} {remaining}s"
        elif self.shield:
            power_text = "Power: shield"
        else:
            power_text = "Power: none"

        draw_text(self.screen, power_text, 390, 40)

    def draw(self):
        self.screen.fill((250, 250, 250))

        self.draw_hud()
        self.draw_grid()

        for block in self.obstacles:
            self.draw_cell(block, (90, 90, 90))

        if self.normal_food:
            self.draw_cell(self.normal_food["pos"], self.normal_food["color"])
            x, y = self.grid_to_pixel(self.normal_food["pos"])
            draw_text(self.screen, self.normal_food["value"], x + 5, y, BLACK, SMALL_FONT)

        if self.poison_food:
            self.draw_cell(self.poison_food["pos"], (100, 0, 0))
            x, y = self.grid_to_pixel(self.poison_food["pos"])
            draw_text(self.screen, "P", x + 5, y, WHITE, SMALL_FONT)

        if self.powerup:
            colors = {
                "speed": (0, 200, 255),
                "slow": (255, 180, 0),
                "shield": (120, 120, 255)
            }

            letters = {
                "speed": "B",
                "slow": "S",
                "shield": "H"
            }

            self.draw_cell(self.powerup["pos"], colors[self.powerup["type"]])
            x, y = self.grid_to_pixel(self.powerup["pos"])
            draw_text(self.screen, letters[self.powerup["type"]], x + 4, y, BLACK, SMALL_FONT)

        for i, segment in enumerate(self.snake):
            if i == 0:
                self.draw_cell(segment, (0, 120, 0))
            else:
                self.draw_cell(segment, self.snake_color)

    def run(self):
        while not self.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit", self.score, self.level

                self.handle_input(event)

            self.move()
            self.draw()

            pygame.display.flip()
            self.clock.tick(self.current_speed())

        return "game_over", self.score, self.level