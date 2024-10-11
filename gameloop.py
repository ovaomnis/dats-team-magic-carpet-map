import pygame
import time
from schemas import CommandPlayer
from api import move

# Initialize pygame
pygame.init()

world = move([])
SCALE = 10

# Create a window (required for event handling, but can be small)
screen = pygame.display.set_mode((world.mapSize.x // SCALE, world.mapSize.y // SCALE))
commands: list[CommandPlayer] = []

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

def step():
    global world
    world = move([])

def draw_transports(surface: pygame.Surface):
    for transport in world.transports:
        scale_x = transport.x // SCALE
        scale_y = transport.y // SCALE
        pygame.draw.circle(surface, BLUE, (scale_x, scale_y), 2)

def draw_enemies(surface: pygame.Surface):
    for enemy in world.enemies:
        scale_x = enemy.x // SCALE
        scale_y = enemy.y // SCALE
        pygame.draw.circle(surface, RED, (scale_x, scale_y), 2)

def draw_anomalies(surface: pygame.Surface):
    if not hasattr(world, 'anomalies'):
        return

    for anomaly in world.anomalies:
        scale_x = anomaly.x // SCALE
        scale_y = anomaly.y // SCALE
        pygame.draw.circle(surface, RED, (scale_x, scale_y), 2)

# Your game loop
running = True
while running:
    screen.fill(WHITE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            print(f'Key pressed: {pygame.key.name(event.key)}')

    world = move(commands)
    draw_transports(screen)
    draw_enemies(screen)

    pygame.display.flip()


    # Game logic goes here (for now just printing "Hello")
    time.sleep(0.3)

# Quit pygame
pygame.quit()
