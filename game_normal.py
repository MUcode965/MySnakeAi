import pygame
import sys
from directions import Directions
import constants as c
from fruit import Fruit
from snake import Snake


class SnakeGameNormal:

    def __init__(self):
        self.screen = pygame.display.set_mode(c.WINDOW_SIZE)
        pygame.display.set_caption("Snake")
        self.clock: pygame.time.Clock = pygame.time.Clock()

        # Objects
        self.snake: Snake = Snake(self.screen, graphics=True)
        self.fruit: Fruit = Fruit(self.snake, self.screen, graphics=True)
        self.score = 0

        self.draw_background()

    def draw_background(self) -> None:
        """
        Draws a checked patterned background
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

    def game_over(self) -> None:
        print("Your score: ", self.score)
        pygame.quit()
        sys.exit()

    def check_fail(self) -> bool:
        """
        Checks for the collision with the snake body or the wall
        :return: Bool that either says it collided with itself or the wall, or it didn't
        """
        if not 0 <= self.snake.body[0].x < c.CELL_NUMBER or not 0 <= self.snake.body[0].y < c.CELL_NUMBER:
            return True
        for block in self.snake.body[1:]:
            if block == self.snake.body[0]:
                return True

        return False

    def check_collision(self) -> None:
        """
        Check if the snake is eating a fruit
        """
        if self.fruit.pos == self.snake.body[0]:
            self.fruit.randomize()
            self.snake.add_block()
            self.score += 1

    def play_step(self) -> tuple[bool, int]:
        """
        One iteration of the snake game
        :return: The game over state and the score
        """
        # Userinput
        for event in pygame.event.get():
            # If the player closes the game
            if event.type == pygame.QUIT:
                self.game_over()
            # The key input for the direction in which the snake has to move
            keys = pygame.key.get_pressed()
            for key in keys:
                if keys[pygame.K_w] or keys[pygame.K_UP]:
                    if self.snake.direction.y == 1:
                        continue
                    self.snake.direction = Directions.UP
                if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                    if self.snake.direction.y == -1:
                        continue
                    self.snake.direction = Directions.DOWN
                if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                    if self.snake.direction.x == 1:
                        continue
                    self.snake.direction = Directions.LEFT
                if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                    if self.snake.direction.x == -1:
                        continue
                    self.snake.direction = Directions.RIGHT

        self.screen.fill((0, 0, 0))

        self.snake.move_snake()
        self.check_collision()

        # Drawing
        self.draw_background()
        self.snake.draw_snake()
        self.fruit.draw_fruit()

        # Checking
        game_over = False
        if self.check_fail():
            game_over = True
            return game_over, self.score

        pygame.display.flip()

        self.clock.tick(c.GAME_FPS)

        return game_over, self.score
