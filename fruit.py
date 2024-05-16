import pygame
import random
import os
import constants as c
from pygame.math import Vector2


# The fruit object
class Fruit:
    def __init__(self, snake, display, graphics: bool):
        if graphics:
            self.screen = display
            # Loading the texture of the fruit
            self.fruit_image = pygame.image.load(os.path.join("assets", "textures", "food", "apple.png")).convert_alpha()
        self.snake = snake
        self.pos: Vector2

        self.randomize()

    def draw_fruit(self):
        """
        Draws fruit to the screen
        """
        fruit_rect: pygame.Rect = pygame.Rect(int(self.pos.x * c.CELL_SIZE), int(self.pos.y * c.CELL_SIZE), c.CELL_SIZE,
                                              c.CELL_SIZE)
        fruit_texture: pygame.Surface = pygame.transform.scale(self.fruit_image, (40, 40))
        self.screen.blit(fruit_texture, fruit_rect)

    def randomize(self):
        """
        Gives the fruit a random position
        """
        x: int = random.randint(0, c.CELL_NUMBER - 1)
        y: int = random.randint(0, c.CELL_NUMBER - 1)
        self.pos = Vector2(x, y)
        if self.pos in self.snake.body[:]:
            self.randomize()
