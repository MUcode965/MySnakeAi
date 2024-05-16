import pygame
import torch
from game_normal import SnakeGameNormal
from agent import train
from game import SnakeAIGame
from model import Linear_QNet
import numpy
from pygame import Vector2


def run_normal_game():
    game = SnakeGameNormal()

    # Game loop
    while True:
        game_over, score = game.play_step()

        if game_over:
            break

    print("Score: ", score)

    pygame.quit()


def run_ai_agent(*, graphics: bool, graph: bool, fps: int, gamma: float):
    train(graphics=graphics, graph=graph, fps=fps, gamma=gamma)


def get_state(game):
    head = game.snake.body[0]

    vec_l = Vector2(head.x - 1, head.y)
    vec_r = Vector2(head.x + 1, head.y)
    vec_u = Vector2(head.x, head.y - 1)
    vec_d = Vector2(head.x, head.y + 1)

    # TODO bigger area to check
    dir_l = game.snake.direction == Vector2(-1, 0)
    dir_r = game.snake.direction == Vector2(1, 0)
    dir_u = game.snake.direction == Vector2(0, -1)
    dir_d = game.snake.direction == Vector2(0, 1)

    state = [
        # Danger straight
        (dir_r and game.check_fail(vec_r)) or
        (dir_l and game.check_fail(vec_l)) or
        (dir_u and game.check_fail(vec_u)) or
        (dir_d and game.check_fail(vec_d)),

        # Danger right
        (dir_u and game.check_fail(vec_r)) or
        (dir_d and game.check_fail(vec_l)) or
        (dir_l and game.check_fail(vec_u)) or
        (dir_r and game.check_fail(vec_d)),

        # Danger left
        (dir_d and game.check_fail(vec_r)) or
        (dir_u and game.check_fail(vec_l)) or
        (dir_r and game.check_fail(vec_u)) or
        (dir_l and game.check_fail(vec_d)),

        # Move direction
        dir_l,
        dir_r,
        dir_u,
        dir_d,

        # Food location
        game.fruit.pos.x < game.snake.body[0].x,  # food left
        game.fruit.pos.x > game.snake.body[0].x,  # food right
        game.fruit.pos.y < game.snake.body[0].y,  # food up
        game.fruit.pos.y > game.snake.body[0].y  # food down
    ]

    return numpy.array(state, dtype=int)


def load_model_and_play(file_name: str, game_fps: int):
    file_path = f"SavedModels/{file_name}"
    model = Linear_QNet(11, 64, 32, 3)
    model.load_state_dict(torch.load(file_path))
    model.eval()
    game = SnakeAIGame(graphics=True, fps=game_fps)

    while True:

        state = get_state(game)
        final_move = [0, 0, 0]
        state0 = torch.tensor(state, dtype=torch.float)
        prediction = model(state0)
        move = torch.argmax(prediction).item()
        final_move[move] = 1

        # perform move
        reward, done, score = game.play_step(final_move)

        if done:
            break

    print("Score: ", score)

    pygame.quit()
