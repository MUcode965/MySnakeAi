import pygame
import os
import constants as c
import numpy as np
from directions import Directions
from pygame.math import Vector2


# The snake object
class Snake:
    def __init__(self, display, graphics: bool):
        self.body: list = [Vector2(5, 10), Vector2(4, 10), Vector2(3, 10)]  # The snakes body
        self.direction: Vector2 = Directions.RIGHT  # The direction in which it moves is represented by a vector
        self.new_block: bool = False

        if graphics:
            self.display = display
            self._load_textures()

    def _load_textures(self) -> None:
        """
        Loading the snakes textures
        """
        # Head
        self.head_up = pygame.image.load(os.path.join("assets", "textures", "snake", "head_up.png")).convert_alpha()
        self.head_down = pygame.image.load(os.path.join("assets", "textures", "snake", "head_down.png")).convert_alpha()
        self.head_left = pygame.image.load(os.path.join("assets", "textures", "snake", "head_left.png")).convert_alpha()
        self.head_right = pygame.image.load(os.path.join("assets", "textures",
                                                         "snake", "head_right.png")).convert_alpha()

        # Tail
        self.tail_up = pygame.image.load(os.path.join("assets", "textures", "snake", "tail_up.png")).convert_alpha()
        self.tail_down = pygame.image.load(os.path.join("assets", "textures", "snake", "tail_down.png")).convert_alpha()
        self.tail_left = pygame.image.load(os.path.join("assets", "textures", "snake", "tail_left.png")).convert_alpha()
        self.tail_right = pygame.image.load(os.path.join("assets", "textures",
                                                         "snake", "tail_right.png")).convert_alpha()

        # Body parts
        self.body_vertical = pygame.image.load(os.path.join("assets", "textures",
                                                            "snake", "body_vertical.png")).convert_alpha()
        self.body_horizontal = pygame.image.load(os.path.join("assets", "textures",
                                                              "snake", "body_horizontal.png")).convert_alpha()

        self.body_bl = pygame.image.load(os.path.join("assets", "textures",
                                                      "snake", "body_bottomleft.png")).convert_alpha()
        self.body_br = pygame.image.load(os.path.join("assets", "textures",
                                                      "snake", "body_bottomright.png")).convert_alpha()
        self.body_tl = pygame.image.load(os.path.join("assets", "textures",
                                                      "snake", "body_topleft.png")).convert_alpha()
        self.body_tr = pygame.image.load(os.path.join("assets", "textures",
                                                      "snake", "body_topright.png")).convert_alpha()

    def draw_snake(self) -> None:
        """
        Draws the snake to the screen and handles the different body parts
        """
        self.update_head_graphics()
        self.update_tail_graphics()

        # Iterates through the body parts
        for index, block in enumerate(self.body):
            x_pos: int = int(block.x * c.CELL_SIZE)
            y_pos: int = int(block.y * c.CELL_SIZE)
            block_rect: pygame.Rect = pygame.Rect(x_pos, y_pos, c.CELL_SIZE, c.CELL_SIZE)

            # if it is the head
            if index == 0:
                self.display.blit(self.head, block_rect)
            elif index == len(self.body) - 1:  # if it is the tail
                self.display.blit(self.tail, block_rect)
            else:
                previous_block = self.body[index + 1] - block
                next_block = self.body[index - 1] - block
                if previous_block.x == next_block.x:  # the vertical parts
                    self.display.blit(self.body_vertical, block_rect)
                if previous_block.y == next_block.y:  # the horizontal parts
                    self.display.blit(self.body_horizontal, block_rect)
                else:  # the other parts
                    if previous_block.x == -1 and next_block.y == -1 or previous_block.y == -1 and next_block.x == -1:
                        self.display.blit(self.body_tl, block_rect)
                    if previous_block.x == -1 and next_block.y == 1 or previous_block.y == 1 and next_block.x == -1:
                        self.display.blit(self.body_bl, block_rect)
                    if previous_block.x == 1 and next_block.y == -1 or previous_block.y == -1 and next_block.x == 1:
                        self.display.blit(self.body_tr, block_rect)
                    if previous_block.x == 1 and next_block.y == 1 or previous_block.y == 1 and next_block.x == 1:
                        self.display.blit(self.body_br, block_rect)

    def update_tail_graphics(self) -> None:
        """
        Looks for the penultimate body part and gives the state in which the tail should be
        """
        tail_relation = self.body[-2] - self.body[-1]
        if tail_relation == Directions.RIGHT:
            self.tail = self.tail_left
        elif tail_relation == Directions.LEFT:
            self.tail = self.tail_right
        elif tail_relation == Directions.DOWN:
            self.tail = self.tail_up
        elif tail_relation == Directions.UP:
            self.tail = self.tail_down

    def update_head_graphics(self) -> None:
        """
        Looks for the second body part and gives the state in which the head should be
        """
        head_relation = self.body[1] - self.body[0]
        if head_relation == Directions.RIGHT:
            self.head = self.head_left
        elif head_relation == Directions.LEFT:
            self.head = self.head_right
        elif head_relation == Directions.DOWN:
            self.head = self.head_up
        elif head_relation == Directions.UP:
            self.head = self.head_down

    def move_snake(self, action=None) -> None:
        """
        Moves the snake
        :param action: Is the input of the agent which decides what move should be done
        """
        if action is not None:
            # action = [straight, right, left] expl: [0, 1 ,0] -> move to the right

            # A clock wise which is used to convert the action to the moving direction
            clock_wise = [Vector2(1, 0), Vector2(0, 1), Vector2(-1, 0), Vector2(0, -1)]
            idx = clock_wise.index(self.direction)

            if np.array_equal(action, [1, 0, 0]):
                new_dir = clock_wise[idx]  # No change
            elif np.array_equal(action, [0, 1, 0]):
                next_idx = (idx + 1) % 4
                new_dir = clock_wise[next_idx]  # Right turn
            else:  # [0, 0, 1]
                next_idx = (idx - 1) % 4
                new_dir = clock_wise[next_idx]  # Left turn

            self.direction = new_dir

        # Moving the snake in the direction which it's been set to
        if self.new_block:  # If food has been eaten
            body_copy: list = self.body[:]
            body_copy.insert(0, body_copy[0] + self.direction)
            self.body: list = body_copy[:]
            self.new_block: bool = False
        else:
            body_copy: list = self.body[:-1]
            body_copy.insert(0, body_copy[0] + self.direction)
            self.body: list = body_copy[:]

    def add_block(self) -> None:
        """
        Set the "food has been eaten" Variable to True
        """
        self.new_block: bool = True
