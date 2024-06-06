import pygame
import numpy as np
import os
import random
import math
import time

MANUAL = False
MAP = 'p15.png'

# Initial settings
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)

DRONE_COLOR = (0, 0, 128)

DRONE_RADIUS_CM = 10
CM_IN_PIXEL = 2.5
DRONE_RADIUS = int(DRONE_RADIUS_CM / CM_IN_PIXEL)
SENSORS_LENGTH = int(300 / CM_IN_PIXEL)

FPS = 10
green = (0, 255, 0)
blue = (0, 0, 128)
TOTAL_BATTERY_SEC = 8 * 60

MAX_BATTERY_TO_RETURN = 50

# Sensor characteristics from the provided spreadsheet
SENSOR_DATA = {
    'left': {'min': 0, 'max': 300, 'unit': 'cm', 'Hz': 10, 'error': 0.02, 'wrong_data': 0.01},
    'right': {'min': 0, 'max': 300, 'unit': 'cm', 'Hz': 10, 'error': 0.02, 'wrong_data': 0.01},
    'forward': {'min': 0, 'max': 300, 'unit': 'cm', 'Hz': 10, 'error': 0.02, 'wrong_data': 0.01},
    'backward': {'min': 0, 'max': 300, 'unit': 'cm', 'Hz': 10, 'error': 0.02, 'wrong_data': 0.01},
    'imu': {'min': 0, 'max': 360, 'unit': '*', 'Hz': 10, 'error': 0.02},
    'optical_flow': {'min': 0, 'max': 3, 'unit': '*', 'Hz': 10, 'error': 0.02},
    'battery': {'min': 0, 'max': 100, 'unit': '%', 'Hz': 1, 'error': 0.01},
}


# Define the Drone class
class Drone:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.last_x = x
        self.last_y = y
        self.angle = 0

        self.vel = 0
        self.angular_vel = 0

        self.acc = 1
        self.max_speed = 2
        self.angular_acc = 1  #1
        self.max_angular_acc = 3

        self.covered_area = None

        # Initialize sensor readings
        self.sensors = {
            'left': SENSOR_DATA['left']['max'],
            'right': SENSOR_DATA['right']['max'],
            'forward': SENSOR_DATA['forward']['max'],
            'backward': SENSOR_DATA['backward']['max'],
            'imu': 0.0,
            'optical_flow': 0.0,
            'battery': 100
        }
        self.sensors_real = {
            'left': SENSOR_DATA['left']['max'],
            'right': SENSOR_DATA['right']['max'],
            'forward': SENSOR_DATA['forward']['max'],
            'backward': SENSOR_DATA['backward']['max'],
        }
        # Timers to track the update frequency for each sensor
        self.sensor_timers = {
            'left': time.time(),
            'right': time.time(),
            'forward': time.time(),
            'backward': time.time(),
            'imu': time.time(),
            'optical_flow': time.time(),
            'battery': time.time()
        }
        self.time_multiplier = 1.0  # Default: real-time speed
        self.start_time = time.time()

        # List to track the positions visited by the drone
        self.path = []

    def update(self, map_data):
        # Update the angle
        self.angle += (self.angular_vel * self.time_multiplier)
        self.angle %= 360

        # Calculate the new position based on the velocity and angle
        new_x = self.x + (self.vel * self.time_multiplier) * math.cos(math.radians(self.angle))
        new_y = self.y - (self.vel * self.time_multiplier) * math.sin(math.radians(self.angle))

        # Check for collisions with boundaries
        if new_x < 0:
            new_x = 0
        if new_x > map_data.get_width() - DRONE_RADIUS:
            new_x = map_data.get_width() - DRONE_RADIUS
        if new_y < 0:
            new_y = 0
        if new_y > map_data.get_height() - DRONE_RADIUS:
            new_y = map_data.get_height() - DRONE_RADIUS

        self.last_x = self.x
        self.last_y = self.y

        # Check for collisions with black areas
        if not check_collision(new_x, new_y, map_data):
            self.x = new_x
            self.y = new_y

    def draw(self, win, map_data):
        angle_ofset = -90
        for angle_index in ['right', 'forward', 'left']:
            orientation = (self.angle + angle_ofset) % 360
            # Draw the direction indicator
            end_x = self.x + self.sensors_real[angle_index] / CM_IN_PIXEL * 2 * math.cos(math.radians(orientation))
            end_y = self.y - self.sensors_real[angle_index] / CM_IN_PIXEL * 2 * math.sin(math.radians(orientation))
            pygame.draw.line(map_data, YELLOW, (self.x, self.y), (end_x, end_y), 4)
            angle_ofset += 90

        # Draw the drone as a blue circle
        pygame.draw.circle(win, DRONE_COLOR, (self.x, self.y), DRONE_RADIUS)

        # Draw the direction indicator
        end_x = self.x + DRONE_RADIUS * 2 * math.cos(math.radians(self.angle))
        end_y = self.y - DRONE_RADIUS * 2 * math.sin(math.radians(self.angle))
        pygame.draw.line(win, RED, (self.x, self.y), (end_x, end_y), 1)

    def display_sensors_data(self, win):
        font = pygame.font.Font('freesansbold.ttf', 15)
        sensors_data = ""
        for key, value in self.sensors.items():
            sensors_data += f"{key}: {value:4.2f}{SENSOR_DATA[key].get('unit', '')}  |  "
        text = font.render(sensors_data, True, green, blue)
        textRect = text.get_rect()
        textRect.bottomleft = (0, win.get_height())
        win.blit(text, textRect)

    def update_sensors(self, map_data):
        current_time = time.time()
        directions = ['left', 'right', 'forward', 'backward']
        angles = [90, -90, 0, 180]  # Angles for left, right, forward, backward relative to the drone's orientation

        for dir, angle_offset in zip(directions, angles):
            sensor_specs = SENSOR_DATA[dir]
            self.sensors_real[dir] = self.measure_distance(map_data, angle_offset, sensor_specs)

            period = 1.0 / (sensor_specs['Hz'] * self.time_multiplier)
            if current_time - self.sensor_timers[dir] >= period:
                self.sensors[dir] = self.add_wrong_value(self.sensors_real[dir], sensor_specs)
                self.sensor_timers[dir] = current_time

        sensor_specs = SENSOR_DATA['battery']
        period = 1.0 / (sensor_specs['Hz'] * self.time_multiplier)
        if current_time - self.sensor_timers['battery'] >= period:
            total_sec = int(time.time() - self.start_time)
            self.sensors['battery'] = int(100 - ((total_sec / TOTAL_BATTERY_SEC) * 100))
            self.sensor_timers['battery'] = current_time

        sensor_specs = SENSOR_DATA['imu']
        period = 1.0 / (sensor_specs['Hz'] * self.time_multiplier)
        if current_time - self.sensor_timers['imu'] >= period:
            self.sensors['imu'] = self.angle + np.random.normal(0, sensor_specs['error'])
            self.sensor_timers['imu'] = current_time

        sensor_specs = SENSOR_DATA['optical_flow']
        period = 1.0 / (sensor_specs['Hz'] * self.time_multiplier)
        if current_time - self.sensor_timers['optical_flow'] >= period:
            if self.vel != 0 and (self.x == self.last_x and self.y == self.last_y):
                self.sensors['optical_flow'] = 0.0
            else:
                self.sensors['optical_flow'] = self.vel + np.random.normal(0, sensor_specs['error'])
            self.sensor_timers['optical_flow'] = current_time

    def measure_distance(self, map_data, angle_offset, sensor_specs):
        # Calculate the angle for the given direction relative to the drone's orientation
        sensor_angle = (self.angle + angle_offset) % 360
        rad_angle = math.radians(sensor_angle)

        # Calculate the step increments in x and y direction
        dx = math.cos(rad_angle)
        dy = -math.sin(rad_angle)

        # Measure the distance to the nearest obstacle in the given direction
        x, y = self.x, self.y
        distance = 0
        while 0 <= x < map_data.get_width() and 0 <= y < map_data.get_height() and distance < sensor_specs[
            'max'] / CM_IN_PIXEL:
            if map_data.get_at((round(x), round(y))) == BLACK:
                break
            x += dx
            y += dy
            distance += 1

        return distance

    def add_wrong_value(self, distance, sensor_specs):
        # Adding sensor error and simulating wrong data
        if random.random() < sensor_specs['wrong_data']:
            distance = random.uniform(sensor_specs['min'], sensor_specs['max'])
        else:
            distance += np.random.normal(0, sensor_specs['error'] * distance)
        return max(sensor_specs['min'], min(distance, sensor_specs['max']))

    def rotate_right(self):
        if self.angular_vel >= 0:
            self.angular_vel = -self.angular_acc
        else:
            self.angular_vel = max(-self.max_angular_acc, self.angular_vel - self.angular_acc)

    def rotate_left(self):
        if self.angular_vel <= 0:
            self.angular_vel = self.angular_acc
        else:
            self.angular_vel = min(self.max_angular_acc, self.angular_vel + self.angular_acc)

    def move_forward(self):
        if self.vel <= 0:
            self.vel = self.acc
        else:
            self.vel = min(self.vel + self.acc, self.max_speed)

    def move_backward(self):
        self.vel = -self.acc

    def stop(self):
        self.vel = 0

    def stop_rotation(self):
        self.angular_vel = 0


class DroneController:
    def __init__(self, drone: Drone, win, time_multiplier=1.0):
        self.drone = drone
        self.win = win
        self.time_multiplier = time_multiplier

        self.going_home = False
        self.done_going_home = False
        self.is_turning_180 = False
        self.last_angle = 0
        self.is_returning = False

        self.current_x = 0
        self.current_y = 0

        self.step_counter = 0
        self.checkpoint_interval = 50
        self.checkpoints = []
        self.window_checkpoints = []
        self.should_keep_rotating = False
        self.fix_collision_step = 0

        self.add_checkpoint()

    def control(self):
        self.update_position(self.drone.sensors['imu'], self.drone.sensors['optical_flow'])
        self.step_counter += 1

        if MANUAL:
            self.handle_keys()
        else:
            self.autonomous_control()

    def add_checkpoint(self):
        self.checkpoints.append((self.current_x, self.current_y))
        self.window_checkpoints.append((self.drone.x, self.drone.y))

    def draw(self):
        for pos in self.window_checkpoints:
            pygame.draw.circle(self.win, (100, 100, 100), (pos[0], pos[1]), 2)

    def handle_keys(self):
        # Handle keyboard input for manual control
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.drone.angular_vel = self.drone.angular_acc
        elif keys[pygame.K_RIGHT]:
            self.drone.angular_vel = -self.drone.angular_acc
        else:
            self.drone.angular_vel = 0

        if keys[pygame.K_UP]:
            self.drone.vel = min(self.drone.vel + self.drone.acc, self.drone.max_speed)
        elif keys[pygame.K_DOWN]:
            self.drone.vel = max(self.drone.vel - self.drone.acc, -self.drone.max_speed)
        else:
            self.drone.vel = 0

    def update_position(self, orientation, flow):
        # Calculate the new position based on the velocity and angle
        new_x = self.current_x + (flow * self.time_multiplier) * math.cos(math.radians(orientation))
        new_y = self.current_y - (flow * self.time_multiplier) * math.sin(math.radians(orientation))

        self.current_x = new_x
        self.current_y = new_y

    def display_controller_position(self, win):
        font = pygame.font.Font('freesansbold.ttf', 15)
        position = f"{self.current_x:4.0f}:{self.current_y:4.0f} -- {self.drone.x:4.0f}:{self.drone.y:4.0f}"
        text = font.render(position, True, green, blue)
        textRect = text.get_rect()
        textRect.bottomright = (win.get_width(), win.get_height())
        win.blit(text, textRect)

    def rotate_to_position(self, drone, target_x, target_y):
        orientation = drone.sensors['imu']

        dx = target_x - self.current_x
        dy = target_y - self.current_y
        angle_radians = math.atan2(dy, dx)
        angle_degrees = -math.degrees(angle_radians)
        if angle_degrees < 0:
            angle_degrees += 360

        # Rotate the drone
        if abs((orientation - angle_degrees)) % 360 > 20:  # A small threshold to prevent jitter
            print("Turing to checkpoint")
            difference = (angle_degrees - orientation) % 360
            if difference < 0:
                difference += 360

            # Determine the shortest turn direction
            if difference > 180:
                drone.rotate_right()
            else:
                drone.rotate_left()
            drone.stop()
            return True

        return False

    def there_is_close_checkpoint(self):
        for point in self.checkpoints:
            dest = math.dist(point, (self.current_x, self.current_y))
            if dest < 20:
                return True
        return False

    def autonomous_control(self):
        if self.done_going_home:
            return

        distance_forward = self.drone.sensors['forward']
        distance_left = self.drone.sensors['left']
        distance_right = self.drone.sensors['right']
        distance_backward = self.drone.sensors['backward']
        battery = self.drone.sensors['battery']
        flow = self.drone.sensors['optical_flow']
        orientation = self.drone.sensors['imu']

        front_threshold = 20
        right_far_threshold = 40
        right_threshold = 15
        tunnel_threshold = 60

        if self.step_counter < self.fix_collision_step or (self.drone.vel > 0 and flow <= 0.5):
            if self.step_counter > self.fix_collision_step:
                self.fix_collision_step = self.step_counter + 5

            print("collision! -- move_backward")
            self.drone.move_backward()
            self.drone.rotate_left()
            return

        if self.going_home:
            dest_x, dest_y = self.checkpoints[len(self.checkpoints) - 1]

            # Check if the drone has reached the target
            distance_to_target = math.dist((dest_x, dest_y), (self.current_x, self.current_y))
            if distance_to_target < 10:  # Threshold distance to consider as reached
                if len(self.checkpoints) > 0:
                    print("Reached checkpoint")
                    self.checkpoints.pop()

                if len(self.checkpoints) == 0:
                    print("Done")
                    self.done_going_home = True  # Reached the starting point

                return

            if self.step_counter % 70 or self.should_keep_rotating:
                if self.rotate_to_position(self.drone, dest_x, dest_y):
                    self.should_keep_rotating = True
                else:
                    self.should_keep_rotating = False
                return

        if not self.going_home and battery <= MAX_BATTERY_TO_RETURN:
            self.going_home = True
            self.drone.stop()
            print("Start returning home")
            return

        if distance_forward < front_threshold:
            self.drone.stop()
            self.drone.rotate_left()
            print("too close")

        elif distance_left + distance_right < tunnel_threshold:
            print("tunnel mode")
            if distance_left < distance_right - 10:
                self.drone.rotate_right()
            elif distance_right < distance_left - 10:
                self.drone.rotate_left()
            else:
                self.drone.stop_rotation()
            self.drone.move_forward()

        elif distance_right > right_far_threshold:
            print("too far from right")
            self.drone.rotate_right()
            self.drone.move_forward()

        elif distance_right < right_threshold:
            print("too close to right")
            self.drone.rotate_left()
            self.drone.move_forward()

        else:
            print("forward")
            self.drone.move_forward()
            self.drone.stop_rotation()

        if self.step_counter % self.checkpoint_interval == 0 and not self.going_home:
            if not self.there_is_close_checkpoint():
                self.add_checkpoint()


def load_map(map_file):
    return pygame.image.load(map_file)


def find_starting_position(map_data):
    for y in range(50, map_data.get_height() - 20):
        for x in range(50, map_data.get_width() - 20):
            if not check_collision(x, y, map_data):
                return x, y
    return None, None


def check_collision(new_x, new_y, map_data):
    for angle in range(0, 360, 5):
        X = new_x + ((DRONE_RADIUS + 1) * math.cos(math.radians(angle)))
        Y = new_y + ((DRONE_RADIUS + 1) * math.sin(math.radians(angle)))
        if map_data.get_at((round(X), round(Y))) == BLACK:
            return True
    return False


def main():
    pygame.init()
    map_file = os.path.join("Maps", MAP)
    black_map_data = load_map(map_file)
    black_map_data.set_colorkey(WHITE)
    map_data = load_map(map_file)
    width = map_data.get_width()
    height = map_data.get_height()
    win = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Drone Simulation")
    clock = pygame.time.Clock()
    start_x, start_y = find_starting_position(map_data)
    if start_x is None or start_y is None:
        print("No valid starting position found on the map.")
        return
    drone = Drone(start_x, start_y)
    controller = DroneController(drone, win)
    run = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        drone.update_sensors(black_map_data)
        controller.control()
        drone.update(black_map_data)
        win.fill(WHITE)
        win.blit(map_data, (0, 0))
        drone.draw(win, map_data)
        map_data.blit(black_map_data, (0, 0))
        controller.draw()
        drone.display_sensors_data(win)
        controller.display_controller_position(win)
        pygame.display.update()
    pygame.quit()


if __name__ == "__main__":
    main()
