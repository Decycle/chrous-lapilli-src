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
        if isinstance(action, int):
            self.board[action] = player
        else:
            org, new = action
            self.board[new] = self.board[org]
            self.board[org] = 0

    def is_adjacent(self, i, j):
        i_x = i % 3
        i_y = i // 3

        j_x = j % 3
        j_y = j // 3

        if abs(i_x - j_x) <= 1 and abs(i_y - j_y) <= 1:
            return True
        return False

    def isBoardWinning(self, board, player):
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
            if board[check[0]] == player and board[check[1]] == player and board[check[2]] == player:
                return True

        return False

    def isWinning(self, player):
        return self.isBoardWinning(self.board, player)

    def action_space(self, player):
        if sum([c == player for c in self.board]) < 3:
            return [i for i in range(9) if self.board[i] == 0]
        else:
            actions = []
            for i in range(9):
                if self.board[i] == player:
                    for j in range(9):
                        if self.board[j] == 0 and self.is_adjacent(i, j):
                            actions.append((i, j))

            if self.board[4] == player:
                new_actions = []
                for action in actions:
                    if action[0] == 4:
                        new_actions.append(action)
                        continue

                    new_board = self.board.copy()
                    new_board[action[1]] = new_board[action[0]]
                    new_board[action[0]] = 0

                    if self.isBoardWinning(new_board, player):
                        new_actions.append(action)

                return new_actions
            return actions


    def render(self):
        print('-------')
        for i in range(3):
            print('|', end='')
            for j in range(3):
                print(self.board[i * 3 + j], end='|')
            print(' ')
        print('-------')

class Agent:
    def __init__(self, player, lr=0.2, discount=0.9, init_epsilon=0.9, min_epsilon=0.3, epsilon_decay=0.999999):
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
        best_action = None
        best_value = -1000

        for action in game.action_space(self.player):
            board_copy = game.board.copy()

            if isinstance(action, int):
                board_copy[action] = self.player
            else:
                org, new = action
                board_copy[new] = board_copy[org]
                board_copy[org] = 0

            state = game.hash_board(board_copy)

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
            action = random.choice(game.action_space(self.player))
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

        action_space = game.action_space(self.player)

        while True:
            if isinstance(action_space[0], int):
                action = int(input('Enter action: '))
                if action in action_space:
                    return action
                print('Invalid action')
            else:
                action = input('Enter action: ').split()
                if len(action) != 2:
                    print('Invalid action')
                    continue

                action = (int(action[0]), int(action[1]))
                if action in action_space:
                    return action
                print('Invalid action')

def train(game, agent1, agent2, iters=100000):
    for _ in track(range(iters)):
        while True:
            action = agent1.act(game)
            game.step(action, agent1.player)
            agent1.states.append((game.hash(), action))

            if game.isWinning(agent1.player):
                agent1.learn(1)
                agent2.learn(0)
                break

            action = agent2.act(game)
            game.step(action, agent2.player)
            agent2.states.append((game.hash(), action))

            if game.isWinning(agent2.player):
                agent1.learn(0)
                agent2.learn(1)
                break

        agent1.reset()
        agent2.reset()
        game.reset()

def play(game, agent1, agent2):
    game.render()

    while True:
        action = agent1.act(game)
        game.step(action, agent1.player)
        game.render()

        if game.isWinning(agent1.player):
            print('Player', agent1.player, 'wins')
            break

        action = agent2.act(game)
        game.step(action, agent2.player)
        game.render()

        if game.isWinning(agent2.player):
            print('Player', agent2.player, 'wins')
            break

    game.reset()

game = Game()
agent1 = Agent(1)
agent2 = Agent(2)

# train(game, agent1, agent2, 10000000)

# agent1.save('agent1-2.pkl')
# agent2.save('agent2-2.pkl')

agent1 = Agent(1, init_epsilon=0, min_epsilon=0)
agent2 = Agent(2, init_epsilon=0, min_epsilon=0)

agent1.load('agent1-1.pkl')
agent2.load('agent2-2.pkl')


game.step(1, 1)
# player1 = Player(1)
# print(len(agent1.states_value))

play(game, agent2, agent1)