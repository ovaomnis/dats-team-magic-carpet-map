import numpy as np
import math
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,  # Установите DEBUG для более подробных логов
    format='%(asctime)s %(levelname)s:%(message)s'
)

# Функция для обнаружения близких транспортах (враги и свои)
def detect_nearby_transports(current_pos, transports_list, avoidance_radius=300, own_id=None):
    nearby_transports = []
    for transport in transports_list:
        if transport['status'] != 'alive':
            continue
        if 'id' in transport and transport['id'] == own_id:
            continue  # Пропускаем свой ковёр
        dx = transport['x'] - current_pos['x']
        dy = transport['y'] - current_pos['y']
        distance = math.hypot(dx, dy)
        if distance <= avoidance_radius:
            nearby_transports.append({
                'x': transport['x'],
                'y': transport['y'],
                'dx': dx,
                'dy': dy,
                'distance': distance,
                'velocity': transport.get('velocity', {'x': 0, 'y': 0}),
                'id': transport.get('id')  # Добавляем id для различения своих и врагов
            })
    return nearby_transports


# Функция для расчёта суммарного ускорения от аномалий
def calculate_anomaly_acceleration(current_pos, anomalies_list):
    total_acceleration = np.array([0.0, 0.0])
    for anomaly in anomalies_list:
        dx = anomaly['x'] - current_pos['x']
        dy = anomaly['y'] - current_pos['y']
        distance = math.hypot(dx, dy)
        if distance == 0:
            continue
        if distance > anomaly['effectiveRadius']:
            continue  # За пределами области воздействия
        strength = anomaly['strength']
        acceleration_magnitude = (abs(strength) ** 2) / (distance ** 2)
        direction = np.array([dx, dy]) / distance
        # Учитываем знак силы аномалии
        acceleration = np.sign(strength) * acceleration_magnitude * direction
        total_acceleration += acceleration
    return total_acceleration


# Функция для расчёта собственного ускорения с учётом избежания столкновений и аномалий
def calculate_acceleration(current_pos, target_pos, max_accel, max_speed, own_velocity, nearby_transports=[], anomalies=[],
                           own_id=None):
    # Вектор к цели (золото)
    dx = target_pos['x'] - current_pos['x']
    dy = target_pos['y'] - current_pos['y']
    target_vector = np.array([dx, dy])

    # Инициализируем векторы
    separation_vector = np.array([0.0, 0.0])

    for transport in nearby_transports:
        ex = current_pos['x'] - transport['x']
        ey = current_pos['y'] - transport['y']
        distance = transport['distance']
        if distance == 0:
            continue
        # Усиливаем разделение от врагов
        if 'id' not in transport or transport['id'] != own_id:
            # Это враг или чужой ковёр
            separation_force = 500
        else:
            # Это свой ковёр
            separation_force = 100
        separation_vector += np.array([ex, ey]) / (distance ** 2) * separation_force

    # Учитываем ускорение от аномалий
    anomaly_acceleration = calculate_anomaly_acceleration(current_pos, anomalies)

    # Комбинируем векторы
    combined_vector = target_vector + separation_vector + anomaly_acceleration

    # Нормализуем и масштабируем до max_accel
    norm = np.linalg.norm(combined_vector)
    if norm > 0:
        acceleration = combined_vector / norm * max_accel
    else:
        acceleration = np.array([0.0, 0.0])

    # Ограничиваем ускорение с учётом текущей скорости и maxSpeed
    total_velocity = np.array([own_velocity['x'], own_velocity['y']]) + acceleration
    total_speed = np.linalg.norm(total_velocity)
    if total_speed > max_speed:
        acceleration = (total_velocity / total_speed * max_speed) - np.array([own_velocity['x'], own_velocity['y']])

    logging.debug(f'Рассчитанное ускорение: ax={acceleration[0]}, ay={acceleration[1]}')
    return {'x': acceleration[0], 'y': acceleration[1]}


# Функция для поиска ближайшего врага в радиусе атаки
def find_nearest_enemy(current_pos, enemies_list, attack_range, min_attack_distance=50):
    nearest_enemy = None
    min_distance = float('inf')
    for enemy in enemies_list:
        if enemy['status'] != 'alive':
            continue
        dx = enemy['x'] - current_pos['x']
        dy = enemy['y'] - current_pos['y']
        distance = math.hypot(dx, dy)
        if attack_range >= distance >= min_attack_distance and distance < min_distance:
            min_distance = distance
            nearest_enemy = {
                'x': enemy['x'],
                'y': enemy['y'],
                'distance': distance,
                'health': enemy.get('health', 100)
            }
    if nearest_enemy:
        logging.info(
            f'Обнаружен враг на позиции x={nearest_enemy["x"]}, y={nearest_enemy["y"]}, расстояние {nearest_enemy["distance"]:.2f}'
        )
    return nearest_enemy


# Функция для проверки, безопасно ли атаковать (нет ли своих ковров в радиусе поражения)
def is_safe_to_fire(fire_position, own_transports, safe_radius=30):
    for transport in own_transports:
        dx = transport['x'] - fire_position['x']
        dy = transport['y'] - fire_position['y']
        distance = math.hypot(dx, dy)
        if distance <= safe_radius:
            return False
    return True


# Функция для выбора лучшей монеты с учётом ценности и расстояния
def find_best_gold(current_pos, bounties_list, max_distance=5000, alpha=1.5, beta=0.1):
    max_priority = -float('inf')
    best_gold = None
    for bounty in bounties_list:
        dx = bounty['x'] - current_pos['x']
        dy = bounty['y'] - current_pos['y']
        distance = math.hypot(dx, dy)
        if distance > max_distance:
            continue
        value = bounty.get('points', 0)
        if distance == 0:
            distance = 0.1
        center_distance = math.hypot(bounty['x'], bounty['y'])
        # Приоритет увеличивается с удалением от центра
        priority = value / (distance ** alpha) + beta * center_distance
        if priority > max_priority:
            max_priority = priority
            best_gold = {
                'x': bounty['x'],
                'y': bounty['y'],
                'radius': bounty.get('radius', 0),
                'points': value,
                'distance': distance,
                'priority': priority
            }
    if best_gold:
        logging.info(
            f'Выбрана монета на позиции x={best_gold["x"]}, y={best_gold["y"]}, стоимостью {best_gold["points"]}, расстояние {best_gold["distance"]:.2f}, приоритет {best_gold["priority"]:.2f}')
    else:
        logging.info('Нет подходящих монет для сбора.')
    return best_gold