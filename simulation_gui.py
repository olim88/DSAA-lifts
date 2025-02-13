import json
import math
import sys
from typing import List, Dict, Tuple

import pygame
from pygame.time import Clock

import simulation_handler
from lift_algorithms.lift import BaseLiftAlgorithm, LiftAction, Action
from user import User

window_size = 1000

padding = 10

lift_width = 100


class SimulationGUI:
    window: pygame.Surface
    clock: Clock
    quit = False

    user_image: pygame.Surface
    user_image_width: int
    user_image_height: int
    show_user_info: bool = False

    constants: Dict[str, int]
    future_users: List[User]
    total_floors: int
    capacity: int
    algorithm: BaseLiftAlgorithm
    total_users: int
    finished_users: List[User]
    current_floor: int
    lift_occupants: List[User]
    floors: List[List[User]]

    simulation_speed: float = 2
    simulation_time: float = 0
    simulation_running: bool = True
    next_action_time: float = 0
    current_action: LiftAction = LiftAction(Action.wait)

    def __init__(self, algorithm: BaseLiftAlgorithm, simulation_id: int):
        # setup pygame
        pygame.init()
        pygame.display.set_caption(f"Lift Simulation of {algorithm.name}")
        self.clock = pygame.time.Clock()
        self.win = pygame.display.set_mode((window_size, window_size), pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.user_image = pygame.image.load('data/user_image.png').convert_alpha()
        self.user_image_width, self.user_image_height = self.user_image.get_size()

        # load the constants
        with open("data/constants.json", "r") as f:
            self.constants = json.load(f)

        # set up values
        (self.future_users, self.total_floors, self.capacity) = simulation_handler.open_simulation(simulation_id)
        self.algorithm = algorithm
        self.algorithm.set_capacity(self.capacity)
        self.total_users = len(self.future_users)
        self.finished_users: List[User] = []
        self.current_floor = self.constants["start floor"]
        self.lift_occupants = []
        self.floors = [[] for floor in range(self.total_floors)]

        self.run_main_loop()

    def run_main_loop(self):
        while not self.quit:
            # check finished
            if len(self.finished_users) == self.total_users:
                break
            self.update()
            self.render()
            self.get_user_input()

        pygame.quit()

    def render(self):
        # fill background
        self.win.fill((0, 0, 0))

        # draw simulation
        self.render_lift_shaft()
        self.render_floors()

        # update display
        pygame.display.flip()

    def render_lift_shaft(self):
        #render floor numbers in shaft
        for floor in range(self.total_floors):
            font = pygame.font.SysFont("monospace", int(self.get_floor_height() * 0.9))
            floor_label = font.render(str(self.total_floors - floor - 1), True, (255, 255, 255))
            self.win.blit(floor_label, (padding+(lift_width - floor_label.get_width())/2, self.get_floor_height() * floor  + (self.get_floor_height() - floor_label.get_height())/2))

        #render lift
        lift_y = 1000 - padding - (self.get_floor_height() * (self.current_floor + 1))
        if self.current_action.action == Action.move_down:
            lift_y += self.get_floor_height() * self.get_percent_through_animation()
        elif self.current_action.action == Action.move_up:
            lift_y -= self.get_floor_height() * self.get_percent_through_animation()

        pygame.draw.rect(self.win, 0x1212ff, (padding, lift_y, lift_width, self.get_floor_height()))

    def render_floors(self):
        for floor in range(self.total_floors):
            floor_y = self.get_floor_height() * (floor + 1)
            # draw floor
            pygame.draw.rect(self.win, 0xffffff, (
                padding + lift_width, floor_y, window_size - (padding + lift_width),
                self.get_floor_height() * 0.1))

            # draw people on the floor
            users = self.floors[self.total_floors - 1 - floor]  # todo handle users leaving the floor
            if len(users) == 0:
                continue

            user_x_offset = padding + lift_width + padding
            user_width_with_spacer = self.user_image_width * 1.05
            user_scale = min((self.get_floor_height() * 0.9) / self.user_image_height,
                             (window_size - (2 * padding + lift_width)) / (user_width_with_spacer * len(users)))
            for user in users:
                self.render_user(user, (user_x_offset, floor_y), user_scale)
                user_x_offset += user_width_with_spacer * user_scale

    def render_user(self, user: User, feet_pos: Tuple[float, float], scale: float):  # todo fade  out users
        user_surface = pygame.Surface((self.user_image_width, self.user_image_height), pygame.SRCALPHA)
        user_time = self.simulation_time - user.start_time
        # render user image
        user_surface.blit(self.user_image, (0, 0))

        # add relevant data if enabled
        if self.show_user_info:
            font = pygame.font.SysFont("monospace", 30)
            target_floor_text = font.render(f"End:{user.end_floor}", True, (255, 255, 255))
            user_id_text = font.render(f"Id:{user.id}", True, (255, 255, 255))
            user_time_text = font.render(f"T:{round(user_time)}", True, (255, 255, 255))
            user_surface.blit(target_floor_text, ((self.user_image_width - target_floor_text.get_size()[0]) / 2, 0))
            user_surface.blit(user_id_text, ((self.user_image_width - user_id_text.get_size()[0]) / 2, 50))
            user_surface.blit(user_time_text, ((self.user_image_width - user_time_text.get_size()[0]) / 2, 100))

        # scale user
        user_surface = pygame.transform.scale(user_surface,
                                              (self.user_image_width * scale, self.user_image_height * scale))
        # fade the user if they are new
        if user_time < 1:
            user_surface.set_alpha(round(255 * user_time))
        # render to screen
        self.win.blit(user_surface, (feet_pos[0], feet_pos[1] - self.user_image_height * scale))

    def get_floor_height(self):
        return (window_size - 2 * padding) / self.total_floors

    def get_percent_through_animation(self):
        return 1 - min((self.next_action_time - self.simulation_time) / self.get_action_length(), 1)

    def get_action_length(self) -> int:
        if self.current_action.action == Action.wait:
            return 1
        elif self.current_action.action == Action.move_up or self.current_action.action == Action.move_down:
            return self.constants["time between floors"]
        elif self.current_action.action == Action.open_doors:
            people_change = len(self.current_action.add) + len(self.current_action.remove)
            return self.constants["first pickup time"] + self.constants["extra pickup time"] * (people_change - 1)

        raise Exception("Invalid action")

    def update(self):
        self.clock.tick(60)

        # add new users to floors
        # see if any new lift users have arrived since the last action
        for user in self.future_users:
            if user.start_time <= self.simulation_time:
                self.floors[user.start_floor].append(user)
                self.future_users.remove(user)

        # if animation has finished for last simulation step get the next step
        if self.simulation_time >= self.next_action_time:
            # apply changes from old action
            if self.current_action.action == Action.move_up:
                self.current_floor += 1
            elif self.current_action.action == Action.move_down:
                self.current_floor -= 1
            elif self.current_action.action == Action.open_doors:
                # edit user timings
                for user in self.current_action.add:
                    user.set_user_start_traveling(math.floor(self.simulation_time))
                for user in self.current_action.remove:
                    user.set_user_end_traveling(math.floor(self.simulation_time))
                # remove from queue
                self.floors[self.current_floor] = [user for user in self.floors[self.current_floor] if
                                                   user not in self.current_action.add]
                # change lift occupants
                self.lift_occupants.extend(self.current_action.add)
                self.lift_occupants = [user for user in self.lift_occupants if user not in self.current_action.remove]
                # add to output
                self.finished_users.extend(self.current_action.remove)

            # get the next action
            self.current_action = self.algorithm.calculate(self.lift_occupants, self.floors,
                                                           math.floor(self.simulation_time), self.current_floor)

            # get time from action
            self.next_action_time = math.floor(self.simulation_time) + self.get_action_length()

        # update simulation time
        if self.simulation_running:
            self.simulation_time += self.simulation_speed / 60

        # update information
        pygame.display.set_caption(
            f"""Lift Simulation of {self.algorithm.name}.
             Time: {int(self.simulation_time)}.
             Paused: {not self.simulation_running}. 
             Speed: {self.simulation_speed}.
             Finished: {len(self.finished_users)}. In lift: {len(self.lift_occupants)}. 
             Waiting: {(sum(len(floor) for floor in self.floors))}, 
             Future: {len(self.future_users)}""")

    def get_user_input(self):
        # listen for user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                self.quit = True
            # keyboard
            if event.type == pygame.KEYDOWN:
                # pause / play simulation
                if event.key == pygame.K_SPACE:
                    self.simulation_running = not self.simulation_running
                # increase/decrease simulation speed
                if event.key == pygame.K_LEFT:
                    self.simulation_speed -= 1
                if event.key == pygame.K_RIGHT:
                    self.simulation_speed += 1
                # toggle user info
                if event.key == pygame.K_i:
                    self.show_user_info = not self.show_user_info


def run_simulation_gui(algorithm: BaseLiftAlgorithm, simulation_id: int) -> List[User]:
    # load the constants
    with open("data/constants.json", "r") as f:
        constants = json.load(f)
    # set up values
    (future_users, total_floors, capacity) = simulation_handler.open_simulation(simulation_id)
    algorithm.set_capacity(capacity)
    total_users = len(future_users)
    finished_users: List[User] = []
    current_time = 0
    current_floor = constants["start floor"]
    lift_occupants = []
    floors = [[] for floor in range(total_floors)]

    # run lift loop until simulation finished
    while True:
        # check to see if the lift has finished
        if len(finished_users) == total_users:
            break
        # see if any new lift users have arrived since the last action
        for user in future_users:
            if user.start_time <= current_time:
                floors[user.start_floor].append(user)
                future_users.remove(user)

        # send state to lift algorithm

    # return finished users
    return finished_users
