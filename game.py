import pygame
import sys
import constants as c
from snake import Snake
from fruit import Fruit

# Initialize pygame
pygame.init()


class SnakeAIGame:

    def __init__(self, graphics: bool, fps: int):
        self.graphics = graphics
        self.fps = fps
        if self.graphics:
            # Game window and clock
            self.screen = pygame.display.set_mode(c.WINDOW_SIZE)
            pygame.display.set_caption("Snake")
        self.clock: pygame.time.Clock = pygame.time.Clock()

        # initialize the game
        self.reset()
        if self.graphics:
            # Drawing the Background
            self.draw_background()

    def reset(self):
        """
        Is used by the agent to reset the game
        """
        # initialize the game
        if self.graphics:
            self.snake: Snake = Snake(self.screen, graphics=self.graphics)
            self.fruit: Fruit = Fruit(self.snake, self.screen, graphics=self.graphics)
        else:
            self.snake: Snake = Snake(display=None, graphics=self.graphics)
            self.fruit: Fruit = Fruit(self.snake, display=None, graphics=self.graphics)
        self.fruit.randomize()
        self.score = 0
        self.frame_iterarion = 0

    def draw_background(self):
        """
        Draws a Background in a checked pattern
        """
        for y in range(c.CELL_NUMBER):
            for x in range(0, c.CELL_NUMBER, 2):
                if y % 2 == 0:
                    bg_tile1: pygame.Rect = pygame.Rect(x * c.CELL_SIZE, y * c.CELL_SIZE, c.CELL_SIZE, c.CELL_SIZE)
                    pygame.draw.rect(self.screen, (79, 255, 0), bg_tile1)
                    bg_tile2: pygame.Rect = pygame.Rect((x + 1) * c.CELL_SIZE, y * c.CELL_SIZE, c.CELL_SIZE, c.CELL_SIZE)
                    pygame.draw.rect(self.screen, (77, 250, 0), bg_tile2)

                else:
                    bg_tile1: pygame.Rect = pygame.Rect((x + 1) * c.CELL_SIZE, y * c.CELL_SIZE, c.CELL_SIZE, c.CELL_SIZE)
                    pygame.draw.rect(self.screen, (79, 255, 0), bg_tile1)
                    bg_tile2: pygame.Rect = pygame.Rect(x * c.CELL_SIZE, y * c.CELL_SIZE, c.CELL_SIZE, c.CELL_SIZE)
                    pygame.draw.rect(self.screen, (77, 250, 0), bg_tile2)

    def check_fail(self, vec=None):
        """
        Checks if the snake collides with the wall or itself
        :param vec: Is a Variable which is important for the agent to determ the state
        """
        if vec is None:
            vec = self.snake.body[0]
        if not 0 <= vec.x < c.CELL_NUMBER or not 0 <= vec.y < c.CELL_NUMBER:
            return True
        if vec in self.snake.body[1:]:
            return True

        return False
    def play_step(self, action):
        """
        One game iteration
        :param action: The input used by the agent
        :return: The bool game_over and also the reward for the agent and the reached score
        """
        self.frame_iterarion += 1
        # Userinput
        if self.graphics:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.fill((0, 0, 0))

        self.snake.move_snake(action)

        if self.graphics:
            # Drawing
            self.draw_background()
            self.snake.draw_snake()

        reward = 0
        game_over = False
        # Check if game over
        # Game over also when active for to long without eating
        if self.check_fail() or self.frame_iterarion > 87 * len(self.snake.body):
            game_over = True
            reward = -20
            return reward, game_over, self.score

        # Checking if food has been eaten
        if self.fruit.pos == self.snake.body[0]:
            self.fruit.randomize()
            self.snake.add_block()
            self.score += 1
            reward = 10

        if self.graphics:
            # update the fruit / Draw the fruit
            self.fruit.draw_fruit()

            # Update the screen
            pygame.display.flip()

        # fixes the updates per seconds (fps) to the speed var
        self.clock.tick(self.fps)

        return reward, game_over, self.score
