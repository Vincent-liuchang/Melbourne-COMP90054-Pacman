from captureAgents import CaptureAgent
import random, time, util
import numpy as np
import util
from capture import GameState

#################
# Team creation #
#################


def createTeam(firstIndex, secondIndex, isRed,
               first='myAgent', second='DummyAgent'):
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class myAgent(CaptureAgent):

    def registerInitialState(self, gameState):
        self.start = gameState.getAgentPosition(self.index)
        CaptureAgent.registerInitialState(self, gameState)
        self.initial_time = time.time()
        print("gameStart")
        self.setup()
        self.cost = 0
        self.totalFoodNumber = len(self.getFood(gameState).asList())

    '''
    Your initialization code goes here, if you need any.
    '''

    def getSuccessor(self, gameState, action):
        """
        Finds the next successor which is a grid position (location tuple).
        """
        successor = gameState.generateSuccessor(self.index, action)
        pos = successor.getAgentState(self.index).getPosition()
        if pos != util.nearestPoint(pos):
            # Only half a grid position was covered
            return successor.generateSuccessor(self.index, action)
        else:
            return successor

    def chooseAction(self, gameState):
        self.cost += 1
        foodLeft = len(self.getFood(gameState).asList())
        action = self.choose_action(gameState)

        if foodLeft <= 2:
            action = self.chooseActionHome(gameState)

        successor = self.getSuccessor(gameState, action)
        reward = self.getReward(gameState, action)
        # self.learn(gameState, action, reward, successor)
        return action

    def chooseActionHome(self, gameState):
        bestDist = 9999
        actions = gameState.getLegalActions(self.index)
        for action in actions:
            successor = self.getSuccessor(gameState, action)
            pos2 = successor.getAgentPosition(self.index)
            dist = self.getMazeDistance(self.start, pos2)
            if dist < bestDist:
                bestAction = action
                bestDist = dist
        return bestAction

    def getReward(self, gameState, action):
        timecost = -1
        successor = self.getSuccessor(gameState, action)
        foodReward = min(self.getFoodDistance(gameState)) - min(self.getFoodDistance(successor))
        foodNumChange = len(self.getFood(gameState).asList()) -len(self.getFood(successor).asList())
        capsuleNumChange = len(self.getFood(gameState).asList()) -len(self.getFood(successor).asList())
        beEaten = 0
        survive = 0
        stay = -1
        if successor.getAgentPosition(self.index) == successor.getInitialAgentPosition(self.index):
            beEaten = -50 + 8*(successor.getAgentState(self.index).numCarrying-gameState.getAgentState(self.index).numCarrying)
            foodReward = 0
        if min(self.getEnemyPacmanDistance(successor)) < 10:
            survive = 1 + 8*successor.getAgentState(self.index).numCarrying
        if successor.getAgentState(self.index).isPacman:
            stay = 0




        # rewardHome = 0
        # if gameState.getAgentState(self.index).numCarrying > (self.totalFoodNumber-2)/2:
        #     rewardHome = self.getHomeDistance(gameState) - self.getHomeDistance(successor)

        reward = stay + 8*foodNumChange + 10*capsuleNumChange + beEaten + 2*foodReward + survive
        score = abs((successor.getScore() - gameState.getScore()))*1000
        print(reward+score+timecost)
        return reward + score + timecost

    def final(self, gameState):
        with open('data.txt', 'w') as file:
            file.write(str(self.weights))

    def getHomeDistance(self, gameState):
        my_position = gameState.getAgentPosition(self.index)
        return self.getMazeDistance(my_position, self.start) + 1

    def getFoodDistance(self, gameState):
        my_position = gameState.getAgentPosition(self.index)
        food_list = self.getFood(gameState).asList()
        food_distance = []
        for x, y in food_list:
            food = tuple((x, y))
            food_distance.append(self.getMazeDistance(food, my_position))
        return food_distance

    def getCapsuleDistance(self, gameState):
        my_position = gameState.getAgentPosition(self.index)
        ca_list = self.getCapsules(gameState)
        if ca_list != []:
            ca_distance = []
            for x, y in ca_list:
                ca = tuple((x, y))
                ca_distance.append(self.getMazeDistance(ca, my_position))
        else:
            ca_distance = [0.1]
        return ca_distance

    def getEnemyPacmanDistance(self, gameState):
        my_position = gameState.getAgentPosition(self.index)
        enermy = self.getOpponents(gameState)
        enermy_distance = []
        for e in enermy:
            if not gameState.getAgentState(e).isPacman:
                enermy_position = gameState.getAgentPosition(e)
            else:
                enermy_position = None
            if enermy_position is not None:
                x, y = enermy_position
                enermy = tuple((x, y))
                enermy_distance.append(self.getMazeDistance(enermy, my_position))
            else:
                enermy_distance.append(10)
        return enermy_distance

    def getFeatures(self,gameState, action):
        successor = self.getSuccessor(gameState, action)
        features = {"food": min(self.getFoodDistance(gameState))-min(self.getFoodDistance(successor)),
                    "foodCarry": successor.getAgentState(self.index).numCarrying-gameState.getAgentState(self.index).numCarrying,
                    "foodNum": len(self.getFoodDistance(gameState))-len(self.getFoodDistance(successor)),
                    "distanceHome": self.getHomeDistance(gameState)-self.getHomeDistance(successor),
                    "capsule": min(self.getCapsuleDistance(gameState))-min(self.getCapsuleDistance(successor)),
                    "ghost": min(self.getEnemyPacmanDistance(successor))-min(self.getEnemyPacmanDistance(gameState)),
                    # "ways": len(successor.getLegalActions(self.index))/100,
                    }
        if successor.getAgentState(self.index).numCarrying < 3 or min(self.getEnemyPacmanDistance(successor)) > 5:
            features["distanceHome"] = 0
        if not gameState.getAgentState(self.index).isPacman:
            features["distanceHome"] = 0
        if min(self.getEnemyPacmanDistance(successor)) <= 5:
            features["food"] = 0
        if features["foodCarry"] < 0 and not successor.getAgentPosition(self.index) == successor.getInitialAgentPosition(self.index):
            features["foodCarry"] = -features["foodCarry"]
            features["food"] = 0
        if features["food"] < -1 and not successor.getAgentPosition(self.index) == successor.getInitialAgentPosition(self.index):
            features["food"] = 1
        if len(self.getFood(successor).asList()) <= 2:
            features["food"] = 0
        if successor.getAgentPosition(self.index) == successor.getInitialAgentPosition(self.index):
            features["foodNum"] = 0
            features["food"] = 0

        print("features", features)


        return util.Counter(features)

    def setup(self,actions=["North", "South", "West", "East","Stop"], learning_rate=0.1, reward_decay=1, e_greedy=0.9,
                 first=True,):
        self.actions = actions  # a list
        self.lr = learning_rate # 学习率
        self.gamma = reward_decay   # 奖励衰减
        self.epsilon = e_greedy     # 贪婪度
        if first:
            self.weights = util.Counter({"food": 10, "foodCarry": 100, "foodNum": 100,
                                         "distanceHome": 500,
                                         "capsule": 20, "ghost": 300})
        else:
            with open("data.txt")as data:
                self.weights = util.Counter(eval(data.readline().strip()))

    def choose_action(self, gameState):
        legal_actions = gameState.getLegalActions(self.index)
        Qvalue = [self.getFeatures(gameState, action) * self.weights for action in legal_actions]
        # print("Q",Qvalue)
        print(self.weights)
        if np.random.uniform() < self.epsilon:  # 选择 Q value 最高的 action
            action = legal_actions[Qvalue.index(max(Qvalue))]
        else:   # 随机选择 action
            action = np.random.choice(legal_actions)
        return action

    def learn(self, s, a, r, s_,):
        if s_.data._lose:
            correction = -abs(1000*self.lr*self.getScore(s_))
        elif s_.data._win:
            print("win")
            correction = abs(1000*self.lr*self.getScore(s_))
        else:
            legal_actions = s_.getLegalActions(self.index)
            Qvalue = [self.getFeatures(s_, action) * self.weights for action in legal_actions]
            correction = self.lr * (r + self.gamma * max(Qvalue) - self.getFeatures(s, a) * self.weights)
        for key, weights in self.weights.items():
            weights = weights + correction * self.getFeatures(s, a).get(key)
            self.weights[key] = weights


class DummyAgent(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """

  def registerInitialState(self, gameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on).

    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)

    IMPORTANT: This method may run for at most 15 seconds.
    """

    '''
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py.
    '''
    CaptureAgent.registerInitialState(self, gameState)

    '''
    Your initialization code goes here, if you need any.
    '''


  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    actions = gameState.getLegalActions(self.index)

    '''
    You should change this in your own agent.
    '''

    return "Stop"
