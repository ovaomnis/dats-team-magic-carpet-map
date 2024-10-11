import pygame
import time
from schemas import CommandPlayer, Coordinate, Vector, CommandTransport
from api import move

from engine import (
    detect_nearby_transports,
    calculate_anomaly_acceleration,
    calculate_acceleration,
    find_nearest_enemy,
    is_safe_to_fire,
    find_best_gold
)

# Initialize pygame
pygame.init()

world = move([])
SCALE = 10
VIEWPORT = .2

selected_transport = 0

# Create a window (required for event handling, but can be small)
WIDTH = world.mapSize.x // SCALE
HEIGHT = world.mapSize.y // SCALE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
sahara = pygame.Surface((WIDTH, HEIGHT))

font = pygame.font.Font(None, 16)

# Colors
WHITE = (255, 255, 255)
BLUE = [0, 0, 255]
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 200, 0)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)


def step():
    global world
    world = move([])


def draw_stats(surface: pygame.Surface):
    texts = [
        font.render(f'map size: {world.mapSize}', True, BLACK),
        font.render(f'points: {world.points}', True, BLACK),
    ]
    for i, text in enumerate(texts):
        surface.blit(text, (10, 10 + i * 16))


def draw_transports(surface: pygame.Surface):
    for i, transport in enumerate(world.transports):
        scale_x = transport.x // SCALE
        scale_y = transport.y // SCALE
        pygame.draw.circle(surface, DARK_GREEN, (scale_x, scale_y), world.transportRadius // 2)
        if i == selected_transport:
            pygame.draw.line(surface, DARK_GREEN, (scale_x, scale_y), (scale_x + 3, scale_y - 10))

def draw_enemies(surface: pygame.Surface):
    for enemy in world.enemies:
        scale_x = enemy.x // SCALE
        scale_y = enemy.y // SCALE
        pygame.draw.circle(surface, BLACK, (scale_x, scale_y), world.transportRadius // 2)


def draw_anomalies(surface: pygame.Surface):
    if not hasattr(world, 'anomalies'):
        return

    for anomaly in world.anomalies:
        scale_x = anomaly.x // SCALE
        scale_y = anomaly.y // SCALE
        radius = anomaly.radius // SCALE
        effective_radius = anomaly.effectiveRadius // SCALE
        transparent_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        eff_asurface = pygame.Surface((effective_radius * 2, effective_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(transparent_surface, [*RED, 255 * .3], (radius, radius), radius)
        pygame.draw.circle(eff_asurface, [*BLUE, 255 * .08], (effective_radius, effective_radius),
                           effective_radius)
        surface.blit(eff_asurface, (scale_x - effective_radius, scale_y - effective_radius))
        surface.blit(transparent_surface, (scale_x - radius, scale_y - radius))

def draw_bounties(surface: pygame.Surface):
    if not hasattr(world, 'bounties'):
        return

    for bounty in world.bounties:
        scale_x = bounty.x // SCALE
        scale_y = bounty.y // SCALE
        pygame.draw.circle(surface, GOLD, (scale_x, scale_y), 2)


# Your game loop
running = True
while running:
    screen.fill(WHITE)
    sahara.fill(WHITE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            print(f'Key pressed: {pygame.key.name(event.key)}')

    world = move([])  # Получаем состояние без отправки команд
    max_accel = world.maxAccel
    max_speed = world.maxSpeed
    avoidance_radius = 300
    attack_range = world.attackRange

    commands = []

    for transport in world.transports:
        if transport.status != 'alive':
            continue

        current_pos = {'x': transport.x, 'y': transport.y}
        own_velocity = {
            'x': transport.velocity.x if transport.velocity else 0,
            'y': transport.velocity.y if transport.velocity else 0
        }
        own_id = transport.id

        # Находим лучшую монету для сбора
        bounties = [bounty.model_dump() for bounty in world.bounties] if world.bounties else []
        best_gold = find_best_gold(current_pos, bounties)

        if best_gold:
            target_pos = {'x': best_gold['x'], 'y': best_gold['y']}
        else:
            # Если нет монет, движемся к центру карты
            target_pos = {'x': world.mapSize.x // 2, 'y': world.mapSize.y // 2}

        # Объединяем свои транспорты и врагов для обнаружения близких объектов
        transports = [t.model_dump() for t in world.transports]
        enemies = [e.model_dump() for e in world.enemies] if world.enemies else []
        nearby_transports = detect_nearby_transports(current_pos, transports + enemies, avoidance_radius, own_id=own_id)

        # Аномалии
        anomalies = [a.model_dump() for a in world.anomalies] if world.anomalies else []

        # Рассчитываем ускорение
        acceleration = calculate_acceleration(
            current_pos,
            target_pos,
            max_accel,
            max_speed,
            own_velocity,
            nearby_transports=nearby_transports,
            anomalies=anomalies,
            own_id=own_id
        )

        # Проверяем возможность атаки
        nearest_enemy = find_nearest_enemy(current_pos, enemies, attack_range)
        attack_command = None
        if nearest_enemy and is_safe_to_fire(nearest_enemy, transports):
            attack_command = {'x': nearest_enemy['x'], 'y': nearest_enemy['y']}

        # Формируем команду для транспорта
        command = CommandTransport(
            id=own_id,
            acceleration=Vector(x=acceleration['x'], y=acceleration['y']),
            attack=Coordinate(x=attack_command['x'], y=attack_command['y']) if attack_command else None,
            activateShield=None
        )

        commands.append(command)

    world = move(commands)
    draw_transports(sahara)
    draw_enemies(sahara)
    draw_anomalies(sahara)
    draw_bounties(sahara)

    screen.blit(sahara, (0, 0))

    # Get the transport's position
    transport_x = world.transports[selected_transport].x // SCALE
    transport_y = world.transports[selected_transport].y // SCALE

    draw_stats(screen)

    pygame.display.flip()

    # Game logic goes here (for now just printing "Hello")
    time.sleep(0.3)

# Quit pygame
pygame.quit()
