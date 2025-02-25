import json
import math
from copy import copy
from typing import List, Dict, Tuple

import pygame
from pygame.time import Clock

import simulation_handler
from lift_algorithms.lift import BaseLiftAlgorithm, LiftAction, Action
from user import User, UserQueue

#simulation dimensions
window_size = 1000
padding = 10
lift_width = 100

#simulation colours
background_color = (232, 249, 255)
lift_color = (154, 166, 178)
floor_color = (196, 217, 255)
floor_label_color = (161, 227, 249)
user_info_color = (10, 10, 10)

class SimulationGUI:
    """Uses pygame to display the simulation."""
    window: pygame.Surface
    clock: Clock
    quit = False

    user_image: pygame.Surface
    user_image_width: int
    user_image_height: int
    show_user_info: bool = False

    constants: Dict[str, int]
    future_users: UserQueue
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
    last_action: LiftAction = LiftAction(Action.wait)

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
        self.total_users = self.future_users.get_size()
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
        """
        Render everything to the pygame window then flip it
        :return:
        """
        # fill background
        self.win.fill(background_color)

        # draw simulation
        self.render_lift_shaft()
        self.render_floors()

        # update display
        pygame.display.flip()

    def render_lift_shaft(self):
        """
        Renders the lift and floor numbers to the pygame window
        """
        # render floor numbers in shaft
        for floor in range(self.total_floors):
            font = pygame.font.SysFont("monospace", int(self.get_floor_height() * 0.9))
            floor_label = font.render(str(self.total_floors - floor - 1), True, floor_label_color)
            self.win.blit(floor_label, (padding + (lift_width - floor_label.get_width()) / 2,
                                        self.get_floor_height() * floor + (
                                                self.get_floor_height() - floor_label.get_height()) / 2))

        # render lift
        lift_y = 1000 - padding - (self.get_floor_height() * (self.current_floor + 1))
        if self.current_action.action == Action.move_down:
            lift_y += self.get_floor_height() * self.get_percent_through_animation()
        elif self.current_action.action == Action.move_up:
            lift_y -= self.get_floor_height() * self.get_percent_through_animation()

        # render the lift
        pygame.draw.rect(self.win, lift_color, (padding, lift_y, lift_width, self.get_floor_height()))

        # render users in lift
        user_y = lift_y + self.get_floor_height()
        user_x = padding
        user_scale = min(self.get_floor_height() / self.user_image_height,
                         lift_width / (self.user_image_width * self.capacity))
        #work out who to show in the lift
        rendered_users = copy(self.lift_occupants)
        opacity = -1
        if self.current_action.action == Action.open_doors:
            people_leaving: bool =  not len(self.current_action.remove) == 0
            people_joining: bool =  not len(self.current_action.add) == 0
            #if just people joining fade them in over time
            if people_joining and not people_leaving:
                rendered_users.extend(self.current_action.add)
                opacity = 255 * self.get_percent_through_animation()
            # if just people leaving fade them out over the whole time
            elif people_joining and not people_joining:
                opacity = 255 * (1 - self.get_percent_through_animation())
            #else if people joining and leaving split animation time
            else:
                if  self.get_percent_through_animation() < 0.5:
                    opacity = 255 * (1 - self.get_percent_through_animation() * 2)
                else:
                    rendered_users.extend(self.current_action.add)
                    rendered_users = [user for user in rendered_users if (user not in self.current_action.remove)]
                    opacity = 255 * ( (self.get_percent_through_animation() - 0.5) * 2)

        #render each of the users in the lift
        for user in rendered_users:
            # enable opacity where needed
            if self.current_action.action == Action.open_doors and (self.current_action.add is not None and user in self.current_action.add) or (self.current_action.remove is not None and user in self.current_action.remove):
                self.render_user(user, (user_x, user_y), user_scale, opacity)
            else:
                self.render_user(user, (user_x, user_y), user_scale)
            user_x += self.user_image_width * user_scale

    def render_floors(self):
        """
        Renders floors and waiting users to pygame window
        """
        for floor in range(self.total_floors):
            floor_y = self.get_floor_height() * (floor + 1)
            # draw floor
            pygame.draw.rect(self.win, floor_color, (
                padding + lift_width, floor_y, window_size - (padding + lift_width),
                self.get_floor_height() * 0.1))

            # draw people on the floor
            users = self.floors[self.total_floors - 1 - floor]
            if len(users) == 0:
                continue

            user_x_offset = padding + lift_width + padding
            user_width_with_spacer = self.user_image_width * 1.05
            user_scale = min((self.get_floor_height() * 0.9) / self.user_image_height,
                             (window_size - (2 * padding + lift_width)) / (user_width_with_spacer * len(users)))
            for user in users:
                # check if user should fade out
                # check if the user is fading out
                opacity = -1
                if self.current_action.action == Action.open_doors and user in self.current_action.add:
                    opacity = 255 * (1 - self.get_percent_through_animation())
                # send the user to be rendered
                self.render_user(user, (user_x_offset, floor_y), user_scale, opacity)
                user_x_offset += user_width_with_spacer * user_scale

    def render_user(self, user: User, feet_pos: Tuple[float, float], scale: float, opacity=-1):
        """
        Renders a user on the pygame window
        :param user: user to render
        :param feet_pos: where to render the users feet
        :param scale: how big render the user
        :param opacity: the opacity of the user
        """
        user_surface = pygame.Surface((self.user_image_width, self.user_image_height), pygame.SRCALPHA)
        user_time = self.simulation_time - user.start_time
        # render user image
        user_surface.blit(self.user_image, (0, 0))

        # add relevant data if enabled
        if self.show_user_info:
            font = pygame.font.SysFont("monospace", 30)
            target_floor_text = font.render(f"End:{user.end_floor}", True, user_info_color)
            user_id_text = font.render(f"Id:{user.id}", True, user_info_color)
            user_time_text = font.render(f"T:{round(user_time)}", True, user_info_color)
            user_surface.blit(target_floor_text, ((self.user_image_width - target_floor_text.get_size()[0]) / 2, 0))
            user_surface.blit(user_id_text, ((self.user_image_width - user_id_text.get_size()[0]) / 2, 50))
            user_surface.blit(user_time_text, ((self.user_image_width - user_time_text.get_size()[0]) / 2, 100))

        # scale user
        user_surface = pygame.transform.scale(user_surface,
                                              (self.user_image_width * scale, self.user_image_height * scale))
        # fade the user if they are new
        if opacity != -1:
            user_surface.set_alpha(opacity)
        elif user_time < 1:
            user_surface.set_alpha(round(255 * user_time))
        # render to screen
        self.win.blit(user_surface, (feet_pos[0], feet_pos[1] - self.user_image_height * scale))

    def get_floor_height(self):
        """
        :return: how height the floor is.
        """
        return (window_size - 2 * padding) / self.total_floors

    def get_percent_through_animation(self):
        """
        calculates the percent through the animation
        :return: percent through the animation
        """
        return 1 - min((self.next_action_time - self.simulation_time) / self.get_action_length(), 1)

    def get_action_length(self) -> int:
        """
        calculates the length of the current action
        :return: length of the current action
        """
        if self.current_action.action == Action.wait:
            return 1
        elif self.current_action.action == Action.move_up or self.current_action.action == Action.move_down:
            return self.constants["time between floors"]
        elif self.current_action.action == Action.open_doors:
            people_change = len(self.current_action.add) + len(self.current_action.remove)
            return (self.constants["first pickup time"] if not self.last_action.action == Action.open_doors else 0) + \
                self.constants["extra pickup time"] * people_change

        raise Exception("Invalid action")

    def update(self):
        """
        Updates the simulation
        :return:
        """
        self.clock.tick(60)

        # add new users to floors
        # see if any new lift users have arrived since the last action
        while not self.future_users.is_empty() and self.future_users.peak().start_time <= self.simulation_time:
            user: User = self.future_users.pop()
            self.floors[user.start_floor].append(user)


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

            # update old action
            self.last_action = self.current_action
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
             Future: {self.future_users.get_size()}""")

    def get_user_input(self):
        """
        Listens to user input controlling the simulation
        :return:
        """
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
