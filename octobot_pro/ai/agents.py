from collections import deque
import random
import numpy as np

from octobot_pro.ai.models import mlp

class DQNAgent:
    def __init__(self, action_size):
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95  # discount rate
        self.epsilon = 1.0  # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.model = mlp(action_size)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return [random.uniform(0, 100) for _ in range(self.action_size)]
        act_values = self.model.predict(state)
        return np.argmax(act_values[0])  # returns action

    def replay(self, batch_size=32, tensorboard_callback=None):
        """ vectorized implementation; 30x speed up compared with for loop """
        minibatch = random.sample(self.memory, batch_size)

        states = np.array([tup[0][0] for tup in minibatch])
        # actions = np.array([tup[1][0] for tup in minibatch])
        rewards = np.array([tup[2] for tup in minibatch])
        next_states = np.array([tup[3][0] for tup in minibatch])
        done = np.array([tup[4] for tup in minibatch])

        # Q(s', a)
        target = rewards + self.gamma * np.amax(self.model.predict(next_states), axis=1)
        # end state target is reward itself (no lookahead)
        target[done] = rewards[done]

        # Q(s, a)
        target_f = self.model.predict(states)

        # make the agent to approximately map the current state to future discounted reward
        target_f[range(batch_size), 0] = target
        target_f[range(batch_size), 1] = target
        target_f[range(batch_size), 2] = target
        target_f[range(batch_size), 3] = target

        self.model.fit(states, target_f, epochs=1, verbose=0, callbacks=[tensorboard_callback])

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def load(self, name):
        self.model.load_weights(name)

    def save(self, name):
        self.model.save_weights(name)