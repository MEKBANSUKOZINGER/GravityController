import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("중력 방향 변경 및 공 충돌")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BALL_COLOR = (0, 100, 255)
PLATFORM_COLOR = (100, 50, 200)

FPS = 60
clock = pygame.time.Clock()

class Ball:
    def __init__(self, x, y, radius, mass, platforms):
        while True:
            self.x = random.randint(radius, WIDTH - radius)
            self.y = random.randint(radius, HEIGHT - radius)
            if not any(platform.collides_with_circle(self.x, self.y, radius) for platform in platforms):
                break
        self.radius = radius
        self.mass = mass
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)

    def move(self, gravity, platforms):
        self.vx += gravity[0]
        self.vy += gravity[1]

        next_x = self.x + self.vx
        next_y = self.y + self.vy

        for platform in platforms:
            if platform.collides_with_circle(next_x, next_y, self.radius):
                if platform.left <= self.x <= platform.right:
                    next_y = self.y
                    self.vy = -self.vy / 1.2 

                if platform.top <= self.y <= platform.bottom:
                    next_x = self.x
                    self.vx = -self.vx / 1.2 
                break 

        if next_x - self.radius < 0:
            next_x = self.radius
            self.vx = -self.vx / 1.2
        elif next_x + self.radius > WIDTH:
            next_x = WIDTH - self.radius
            self.vx = -self.vx / 1.2

        if next_y - self.radius < 0:
            next_y = self.radius
            self.vy = -self.vy / 1.2
        elif next_y + self.radius > HEIGHT:
            next_y = HEIGHT - self.radius
            self.vy = -self.vy / 1.2

        self.x = next_x
        self.y = next_y

    def draw(self, screen):
        pygame.draw.circle(screen, BALL_COLOR, (int(self.x), int(self.y)), self.radius)

class Platform:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.left = x
        self.right = x + width
        self.top = y
        self.bottom = y + height

    def draw(self, screen):
        pygame.draw.rect(screen, PLATFORM_COLOR, (self.x, self.y, self.width, self.height))

    def collides_with_circle(self, cx, cy, radius):
        nearest_x = max(self.left, min(cx, self.right))
        nearest_y = max(self.top, min(cy, self.bottom))
        dx = cx - nearest_x
        dy = cy - nearest_y
        return (dx * dx + dy * dy) < (radius * radius)

def handle_collision(ball1, ball2):
    dx = ball1.x - ball2.x
    dy = ball1.y - ball2.y
    distance = math.hypot(dx, dy)

    if distance < ball1.radius + ball2.radius:
        nx = dx / (distance + 0.01)
        ny = dy / (distance + 0.01)

        vx_rel = ball1.vx - ball2.vx
        vy_rel = ball1.vy - ball2.vy

        dot_product = vx_rel * nx + vy_rel * ny
        if dot_product > 0:
            return

        mass_sum = ball1.mass + ball2.mass
        ratio1 = 2 * ball2.mass / mass_sum
        ratio2 = 2 * ball1.mass / mass_sum

        ball1.vx -= ratio1 * dot_product * nx
        ball1.vy -= ratio1 * dot_product * ny
        ball2.vx += ratio2 * dot_product * nx
        ball2.vy += ratio2 * dot_product * ny

platforms = [
    Platform(random.randint(100, WIDTH - 200), random.randint(100, HEIGHT - 200), 200, 20)
    for _ in range(3)
]

balls = [Ball(random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50), radius=5, mass=10, platforms = platforms) for _ in range(100)]

gravity = [0, 1]

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        gravity = [0, -1]
    elif keys[pygame.K_DOWN]:
        gravity = [0, 1]
    elif keys[pygame.K_LEFT]:
        gravity = [-1, 0] 
    elif keys[pygame.K_RIGHT]:
        gravity = [1, 0]

    for ball in balls:
        ball.move(gravity, platforms)

    for i in range(len(balls)):
        for j in range(i + 1, len(balls)):
            handle_collision(balls[i], balls[j])

    screen.fill(WHITE)
    for ball in balls:
        ball.draw(screen)
    for platform in platforms:
        platform.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
