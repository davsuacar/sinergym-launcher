from copy import deepcopy

import gymnasium as gym
import numpy as np


class ExtremeFlowControlWrapper(gym.ActionWrapper):
    def __init__(self, env):
        super().__init__(env)

    def action(self, action):
        action_ = np.array(deepcopy(action))
        for i, action_value_ in enumerate(action_):
            if i < 5:
                minimum = self.env.action_space.low[i]
                maximum = self.env.action_space.high[i]
                action_[i] = maximum if abs(
                    action_value_ -
                    maximum) < abs(
                    action_value_ -
                    minimum) else minimum
        return np.array(action_, dtype=np.float32)