import torch  # TODO perhaps gpu learning
import random
import numpy
from collections import deque
from pygame.math import Vector2
from fruit import Fruit
from snake import Snake

from game import SnakeAIGame, Snake, Fruit
from model import Linear_QNet, QTrainer
from helper import plot


MAX_MEMORY = 200000
BATCH_SIZE = 1000
LR = 0.0001  # Learning rate


class Agent:

    def __init__(self, gamma: float):
        self.num_of_games = 0
        self.epsilon = 0  # Randomness
        self.gamma = gamma  # Discount rate must be smaller then 1
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(11, 128, 64, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def get_state(self, game):
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

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))  # pop left if Max is reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        self.epsilon = 87 - self.num_of_games
        final_move = [0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move
    # TODO fixed epsilon training sample


def train(graphics: bool, graph: bool, fps, gamma: float):
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent(gamma)
    game = SnakeAIGame(graphics=graphics, fps=fps)
    # TODO the beginning of the statistic

    while True:
        # get old state
        state_old = agent.get_state(game)

        # get move
        final_move = agent.get_action(state_old)

        # perform move and get new state
        reward, done, score = game.play_step(final_move)
        state_new = agent.get_state(game)

        # train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        # remember
        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            # train long memory, plot results
            game.reset()
            agent.num_of_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                agent.model.save()

            print("Game: ", agent.num_of_games, "Score: ", score, "Record: ",  record)

            if graph:
                plot_scores.append(score)
                total_score += score
                mean_scores = total_score / agent.num_of_games
                plot_mean_scores.append(mean_scores)
                plot(plot_scores, plot_mean_scores)
