import numpy as np
import pandas as pd


class QLearningTable:
    def __init__(self, actions =["North", "South", "West", "East","Stop"], learning_rate=0.1, reward_decay=0.9, e_greedy=1,
                 first = True,):
        self.actions = actions  # a list
        self.lr = learning_rate # 学习率
        self.gamma = reward_decay   # 奖励衰减
        self.epsilon = e_greedy     # 贪婪度
        if first:
            self.q_table = pd.DataFrame(columns=self.actions, dtype=np.float64)
            print(self.q_table)
        else:
            data = pd.read_csv("data.txt", sep='\t')
            self.q_table = pd.DataFrame(data)
            print(self.q_table)


    def choose_action123(self, gameState, captureAgent):
        observation = State(gameState, captureAgent)
        legal_actions = gameState.getLegalActions(captureAgent.index)
        # print(legal_actions)

        self.check_state_exist(observation) # 检测本 state 是否在 q_table 中存在(见后面标题内容)

        # 选择 action
        if np.random.uniform() < self.epsilon:  # 选择 Q value 最高的 action
            observation = str(observation.__dict__)
            state_action = self.q_table.loc[observation, legal_actions]

            # 同一个 state, 可能会有多个相同的 Q action value, 所以我们乱序一下
            action = np.random.choice(state_action[state_action == np.max(state_action)].index)

        else:   # 随机选择 action
            action = np.random.choice(legal_actions)

        return action

    def learn(self, s, a, r, s_, captureAgent):
        s = State(s, captureAgent)
        s_ = State(s_, captureAgent)

        self.check_state_exist(s_)
        s = str(s.__dict__)
        s_ = str(s_.__dict__)
        q_predict = self.q_table.loc[s, a]
        q_target = r + self.gamma * self.q_table.loc[s_, :].max()  # next state is not terminal

        self.q_table.loc[s, a] += self.lr * (q_target - q_predict)  # update
        print(self.q_table)


    def check_state_exist(self, state):
        state = str(state.__dict__)
        if state not in self.q_table.index:
            # append new state to q table
            self.q_table = self.q_table.append(
                pd.Series(
                    [0] * len(self.actions),
                    index=self.q_table.columns,
                    name=state,
                )
            )


class State:

    def __init__(self, gameState, captureAgent):
        my_position = gameState.getAgentPosition(captureAgent.index)
        food_list = captureAgent.getFood(gameState).asList()
        food_distace =[]
        for x,y in food_list:
            food = tuple((x, y))
            food_distace.append(captureAgent.getMazeDistance(food, my_position))

        # food_distace =[captureAgent.getMazeDistance(tuple((x,y)), my_position) for x,y in food_list]        #
        enermy_list = captureAgent.getOpponents(gameState)
        enermy_distance = []
        for enermy in enermy_list:
            if gameState.getAgentPosition(enermy) is None:
                enermy_distance.append(9999)
            else:
                enermy_distance.append(captureAgent.getMazeDistance(my_position, gameState.getAgentPosition(enermy)))

        self.food_num = len(food_list)
        # self.food_avg = sum(food_distace)/self.food_num
        self.food_min = min(food_distace)
        # self.enermy1 = enermy_distance[0]
        # self.enermy2 = enermy_distance[1]

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
