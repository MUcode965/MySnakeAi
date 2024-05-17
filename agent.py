import torch  # TODO perhaps gpu learning
import random
import numpy
from collections import deque
from pygame.math import Vector2
from game import SnakeAIGame
from model import Linear_QNet, QTrainer
from helper import plot


MAX_MEMORY = 200000
BATCH_SIZE = 3000
LR = 0.01  # Learning rate


class Agent:

    def __init__(self, gamma: float):
        self.num_of_games = 0
        self.epsilon = 0  # Randomness
        self.gamma = gamma  # Discount rate must be smaller then 1
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(12, 120, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    # TODO i'm stupid MOVE DIRECTION check works bettre
    def check_left(self, game) -> int:
        head = game.snake.body[0]
        free_space = 0
        x = -1
        while True:
            check_vec = head + Vector2(x, 0)
            x -= 1
            if game.check_fail(check_vec):
                break
            free_space += 1
        return free_space

    def check_right(self, game) -> int:
        head = game.snake.body[0]
        free_space = 0
        x = 1
        while True:
            check_vec = head + Vector2(x, 0)
            x += 1
            if game.check_fail(check_vec):
                break
            free_space += 1
        return free_space

    def check_up(self, game) -> int:
        head = game.snake.body[0]
        free_space = 0
        y = -1
        while True:
            check_vec = head + Vector2(0, y)
            y -= 1
            if game.check_fail(check_vec):
                break
            free_space += 1
        return free_space

    def check_down(self, game) -> int:
        head = game.snake.body[0]
        free_space = 0
        y = 1
        while True:
            check_vec = head + Vector2(0, y)
            y += 1
            if game.check_fail(check_vec):
                break
            free_space += 1
        return free_space

    def check_free_space_straight(self, game) -> int:
        moving_direction = game.snake.direction  # exp.: Vector2(0, 1)
        free_space = 0

        if moving_direction.x == 0:
            if moving_direction.y == 1:
                free_space = self.check_down(game)
            else:
                free_space = self.check_up(game)
        elif moving_direction.y == 0:
            if moving_direction.x == 1:
                free_space = self.check_right(game)
            else:
                free_space = self.check_left(game)

        return free_space

    def check_free_space_right(self, game) -> int:
        moving_direction = game.snake.direction
        free_space = 0

        # clock_wise = [right, Down, left, Up]
        # idx = clock_wise.index(moving_direction)

        if moving_direction.x == 0:
            if moving_direction.y == 1:
                free_space = self.check_right(game)
            else:
                free_space = self.check_left(game)
        elif moving_direction.y == 0:
            if moving_direction.x == 1:
                free_space = self.check_up(game)
            else:
                free_space = self.check_down(game)

        return free_space

    def check_free_space_left(self, game) -> int:
        moving_direction = game.snake.direction
        free_space = 0

        # clock_wise = [right, Down, left, Up]
        # idx = clock_wise.index(moving_direction)

        if moving_direction.x == 0:
            if moving_direction.y == 1:
                free_space = self.check_left(game)
            else:
                free_space = self.check_right(game)
        elif moving_direction.y == 0:
            if moving_direction.x == 1:
                free_space = self.check_down(game)
            else:
                free_space = self.check_up(game)

        return free_space

    def steps_until_fruit_right(self, game) -> int:
        steps = 0
        if game.fruit.pos.x > game.snake.body[0].x:
            steps = game.fruit.pos.x - game.snake.body[0].x

        return steps

    def steps_until_fruit_left(self, game) -> int:
        steps = 0
        if game.fruit.pos.x < game.snake.body[0].x:
            steps = game.snake.body[0].x - game.fruit.pos.x

        return steps

    def steps_until_fruit_up(self, game) -> int:
        steps = 0
        if game.fruit.pos.y < game.snake.body[0].y:
            steps = game.snake.body[0].y - game.fruit.pos.y

        return steps

    def steps_until_fruit_down(self, game) -> int:
        steps = 0
        if game.fruit.pos.y > game.snake.body[0].y:
            steps = game.fruit.pos.y - game.snake.body[0].y

        return steps

    def get_state(self, game, frame_iteration):
        head = game.snake.body[0]

        vec_l = Vector2(head.x - 1, head.y)
        vec_r = Vector2(head.x + 1, head.y)
        vec_u = Vector2(head.x, head.y - 1)
        vec_d = Vector2(head.x, head.y + 1)

        dir_l = game.snake.direction == Vector2(-1, 0)
        dir_r = game.snake.direction == Vector2(1, 0)
        dir_u = game.snake.direction == Vector2(0, -1)
        dir_d = game.snake.direction == Vector2(0, 1)

        state = [
            # Free space straight
            self.check_free_space_straight(game) / 100,

            # Free space right
            self.check_free_space_right(game) / 100,

            # Free space left
            self.check_free_space_left(game) / 100,

            # Move direction
            dir_l,
            dir_r,
            dir_u,
            dir_d,

            # Food location
            self.steps_until_fruit_left(game) / 100,  # food left
            self.steps_until_fruit_right(game) / 100,  # food right
            self.steps_until_fruit_up(game) / 100,  # food up
            self.steps_until_fruit_down(game) / 100,  # food down

            # Moves until self destruction
            (100 * len(game.snake.body) - frame_iteration) / 1000
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
        self.epsilon = 80 - self.num_of_games
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


def train(graphics: bool, graph: bool, fps, gamma: float):
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent(gamma)
    game = SnakeAIGame(graphics=graphics, fps=fps)

    while True:
        # get old state
        state_old = agent.get_state(game, game.frame_iterarion)

        # get move
        final_move = agent.get_action(state_old)

        # perform move and get new state
        reward, done, score = game.play_step(final_move)
        state_new = agent.get_state(game, game.frame_iterarion)

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
