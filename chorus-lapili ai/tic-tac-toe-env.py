import random
import pickle
from rich.progress import track

class Game:
    def __init__(self):
        self.board = [0] * 9

    def reset(self):
        self.board = [0] * 9

    def hash_board(self, board):
        return ''.join([str(i) for i in board])

    def hash(self):
        return self.hash_board(self.board)

    def step(self, action, player):
        self.board[action] = player

    def action_space(self):
        return [i for i in range(9) if self.board[i] == 0]

    def reward(self, player):
        check_list = [
            [0, 1, 2],
            [3, 4, 5],
            [6, 7, 8],
            [0, 3, 6],
            [1, 4, 7],
            [2, 5, 8],
            [0, 4, 8],
            [2, 4, 6]
        ]

        for check in check_list:
            if self.board[check[0]] == player and self.board[check[1]] == player and self.board[check[2]] == player:
                return 1

        if len(self.action_space()) == 0:
            return 0

        return None


    def render(self):
        print('-------')
        for i in range(3):
            print('|', end='')
            for j in range(3):
                print(self.board[i * 3 + j], end='|')
            print(' ')
        print('-------')

class Agent:
    def __init__(self, player, lr=0.2, discount=0.9, init_epsilon=0.3, min_epsilon=0.3, epsilon_decay=0.999999):
        self.player = player
        self.states = []
        self.states_value = {}
        self.lr = lr
        self.discount = discount
        self.epsilon = init_epsilon
        self.min_epsilon = min_epsilon
        self.epsilon_decay = epsilon_decay

    def reset(self):
        self.states = []
        self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)

    def best_action(self, game):

        board_copy = game.board.copy()

        best_action = None
        best_value = -1000

        for action in game.action_space():
            board_copy[action] = self.player
            state = game.hash_board(board_copy)
            board_copy[action] = 0

            if state not in self.states_value:
                if best_value < 0:
                    best_value = 0
                    best_action = action
                continue

            if self.states_value[state] > best_value:
                best_value = self.states_value[state]
                best_action = action

        # print(best_value)
        return best_action

    def act(self, game):
        if random.random() < self.epsilon:
            action = random.choice(game.action_space())
        else:
            action = self.best_action(game)
        return action

    def learn(self, reward):
        for state, action in reversed(self.states):
            if state not in self.states_value:
                self.states_value[state] = 0

            self.states_value[state] += self.lr * (self.discount * reward - self.states_value[state])
            reward = self.states_value[state]

    def save(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self.states_value, f)

    def load(self, filename):
        with open(filename, 'rb') as f:
            self.states_value = pickle.load(f)

class Player:
    def __init__(self, player):
        self.player = player

    def act(self, game):
        while True:
            action = int(input('Enter action: '))
            if action in game.action_space():
                return action
            print('Invalid action')

def train(game, agent1, agent2, iters=100000):
    for _ in track(range(iters)):
        while True:
            action = agent1.act(game)
            game.step(action, agent1.player)
            agent1.states.append((game.hash(), action))

            reward = game.reward(agent1.player)
            if reward is not None:
                if reward == 1:
                    agent1.learn(1)
                    agent2.learn(0)
                else:
                    agent1.learn(0.1)
                    agent2.learn(0.5)
                break

            action = agent2.act(game)
            game.step(action, agent2.player)
            agent2.states.append((game.hash(), action))
            # game.render()

            reward = game.reward(agent2.player)
            if reward is not None:
                if reward == 1:
                    agent1.learn(0)
                    agent2.learn(1)
                else:
                    agent1.learn(0.1)
                    agent2.learn(0.5)
                break

        agent1.reset()
        agent2.reset()
        game.reset()

def play(game, player, agent2):
    game.render()

    while True:
        action = player.act(game)
        game.step(action, player.player)
        game.render()

        reward = game.reward(player.player)
        if reward is not None:
            if reward == 1:
                print('Player', player.player, 'wins')
            else:
                print('Draw')
            break

        action = agent2.act(game)
        game.step(action, agent2.player)
        game.render()

        reward = game.reward(agent2.player)
        if reward is not None:
            if reward == 1:
                print('Player', agent2.player, 'wins')
            else:
                print('Draw')
            break

    game.reset()

game = Game()
# game.render()

agent1 = Agent(1)
agent2 = Agent(2)

# train(game, agent1, agent2, iters=1000000)

# agent1.save('agent1.pickle')
# agent2.save('agent2.pickle')


agent1 = Agent(1, init_epsilon=0, min_epsilon=0)
agent2 = Agent(2, init_epsilon=0, min_epsilon=0)
agent1.load('agent1.pickle')
agent2.load('agent2.pickle')

print(len(agent1.states_value))
player = Player(2)
play(game, agent1, player)