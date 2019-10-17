from captureAgents import CaptureAgent
import random, time, util
import numpy as np
import util

#################
# Team creation #
#################


def createTeam(firstIndex, secondIndex, isRed,
               first='myAgent', second='myAgent'):
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class myAgent(CaptureAgent):

    def registerInitialState(self, gameState):
        self.start = gameState.getAgentPosition(self.index)
        CaptureAgent.registerInitialState(self, gameState)
        self.initial_time = time.time()
        self.setup()
        self.cost = 1
        self.food = self.getFood(gameState).asList()
        self.totalFoodNumber = len(self.food)
        self.targetFood = self.getFood(gameState).asList()[0]
        a, b = self.targetFood
        print(self.index)
        for foodX,foodY in self.food:
            if self.index >= 2 and gameState.isOnRedTeam:
                if foodY < b:
                    b = foodY
                    self.targetFood = (foodX, foodY)
            elif gameState.isOnRedTeam:
                if foodY > b:
                    b = foodY
                    self.targetFood = (foodX, foodY)
            elif self.index >= 2:
                if foodY <= b:
                    b = foodY
                    self.targetFood = (foodX, foodY)
            else:
                if foodY >= b:
                    b = foodY
                    self.targetFood = (foodX, foodY)

    '''
    Your initialization code goes here, if you need any.
    '''

    def getSuccessor(self, gameState, action):
        """
        Finds the next successor which is a grid position (location tuple).
        """
        for ispacman, position, distance, scared in self.getEnermy(gameState):
            if (position is not None)and (not ispacman) and distance < 10 and not scared:
                x,y = position
                gameState.data.layout.walls[x][y] = True
                gameState.data.layout.walls[x + 1][y] = True
                gameState.data.layout.walls[x][y + 1] = True
                gameState.data.layout.walls[x][y - 1] = True
                gameState.data.layout.walls[x-1][y] = True

        successor = gameState.generateSuccessor(self.index, action)

        pos = successor.getAgentState(self.index).getPosition()
        if pos != util.nearestPoint(pos):
            # Only half a grid position was covered
            return successor.generateSuccessor(self.index, action)
        else:
            return successor

    def chooseAction(self, gameState):
        print("cost", self.cost)

        for ispacman,position,distance,scared in self.getEnermy(gameState):
            if (position is not None)and (not ispacman) and distance < 10 and not scared:
                x,y = position
                gameState.data.layout.walls[x][y] = True
                gameState.data.layout.walls[x + 1][y] = True
                gameState.data.layout.walls[x][y + 1] = True
                gameState.data.layout.walls[x][y - 1] = True
                gameState.data.layout.walls[x-1][y] = True
        self.cost += 1
        self.foodLeft = len(self.getFood(gameState).asList())
        action = self.choose_action(gameState)

        distance_to_target = self.getMazeDistance(gameState.getAgentPosition(self.index), self.targetFood)

        print("target food", self.targetFood)
        print("food distance", distance_to_target)

        if distance_to_target > 10000:
            self.targetFood = random.choice(self.getFood(gameState).asList())
        time1 = time.time()

        # print("enemy", self.getEnermy(gameState))

        if (not self.getPreviousObservation() is None) and self.getPreviousObservation().getAgentState(self.index).isPacman and not gameState.getAgentState(self.index).isPacman:
            self.targetFood = random.choice(self.getFood(gameState).asList())
            print("change target")
        time2 = time.time()
        print("calculateTime", time2-time1)

        return action

    def chooseActionHome(self, gameState):
        bestDist = 9999
        if gameState.getLegalActions(self.index) is not None:
            actions = gameState.getLegalActions(self.index)
        else:
            actions = ["Stop"]
        for action in actions:
            successor = self.getSuccessor(gameState, action)
            pos2 = successor.getAgentPosition(self.index)
            dist = self.getMazeDistance(self.start, pos2)
            if dist < bestDist:
                bestAction = action
                bestDist = dist
        return bestAction

    def getReward(self, gameState, action):
        successor = self.getSuccessor(gameState, action)
        foodReward = self.getFoodDistance(gameState) - self.getFoodDistance(successor)
        foodNumChange = len(self.getFood(gameState).asList()) - len(self.getFood(successor).asList())
        capsuleNumChange = len(self.getFood(gameState).asList()) - len(self.getFood(successor).asList())

        beEaten = 0
        if self.beEaten(gameState, successor):
            beEaten = -1000
        stay = 0
        if successor.getAgentState(self.index).isPacman:
            stay = 0.01

        reward = stay + 80*foodNumChange + 100*capsuleNumChange + max(foodReward, 0)*10 + beEaten
        score = abs((successor.getScore() - gameState.getScore()))*500
        return score + reward

    def final(self, gameState):
        with open('data.txt', 'w') as file:
            file.write(str(self.weights))

    def getHomeDistance(self, gameState):
        my_position = gameState.getAgentPosition(self.index)
        return self.getMazeDistance(my_position, self.start) + 1

    def getFoodDistance(self, gameState):
        my_position = gameState.getAgentPosition(self.index)
        foodList = self.getFood(gameState).asList()
        dis = self.getAllFoodDistance(gameState)
        if self.targetFood not in self.getFood(gameState).asList() and len(foodList) > 1:
            self.targetFood = foodList[dis.index(min(dis))]
        food_distance = self.getMazeDistance(self.targetFood, my_position)
        return food_distance

    def getAllFoodDistance(self, gameState):
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
        enermyState = self.getEnermy(gameState)
        enermy_distance = [enermyState[0][2], enermyState[1][2]]
        return enermy_distance

    def getEnermy(self, gameState):
        my_position = gameState.getAgentPosition(self.index)
        enermy = self.getOpponents(gameState)
        enermyState = []
        for e in enermy:
            enermy_position = gameState.getAgentPosition(e)
            enermy_scared = gameState.getAgentState(e).scaredTimer > 0
            if enermy_position == None:
                enermy_distance = gameState.getAgentDistances()[e]
                enermyState.append((gameState.getAgentState(e).isPacman, enermy_position, enermy_distance, enermy_scared))
            else:
                enermy_distance = self.getMazeDistance(enermy_position, my_position)
                enermyState.append((gameState.getAgentState(e).isPacman, enermy_position, enermy_distance, enermy_scared))
        return enermyState

    def getTeamateDistance(self, gameState):
        my_position = gameState.getAgentPosition(self.index)
        teamMate = gameState.getAgentPosition((self.index+2)%4)
        return self.getMazeDistance(my_position,teamMate)

    def getFeatures(self,gameState, action):

        successor = self.getSuccessor(gameState, action)

        features = {"food": self.getFoodDistance(gameState)-self.getFoodDistance(successor),
                    "foodCarry": successor.getAgentState(self.index).numCarrying-gameState.getAgentState(self.index).numCarrying,
                    # "foodLeft": len(self.getAllFoodDistance(gameState))-len(self.getAllFoodDistance(successor)),
                    "distanceHome": self.getHomeDistance(gameState)-self.getHomeDistance(successor),
                    "capsule": min(self.getCapsuleDistance(gameState))-min(self.getCapsuleDistance(successor)),
                    "ghostMin": self.getEnemyPacmanDistance(successor)[0]-self.getEnemyPacmanDistance(gameState)[0],
                    "ghostMax": self.getEnemyPacmanDistance(successor)[1] - self.getEnemyPacmanDistance(gameState)[1],
                    "ways": len(successor.getLegalActions(self.index))-len(gameState.getLegalActions(self.index)),
                    "friend": self.getTeamateDistance(gameState) - self.getTeamateDistance(successor),
                    "b": 1
                    }

        if self.cost < 5 or self.foodLeft <= 2 or self.getTeamateDistance(successor) >= 5:
            features["friend"] = 0
        if features["capsule"] < -1 or features["capsule"] == 0.9:
            features["capsule"] = 2000
        if self.getEnermy(gameState)[0][2] < 6 and self.getEnermy(gameState)[0][1] is not None \
                and self.getEnermy(gameState)[0][0] and (not gameState.getAgentState(self.index).isPacman)\
                and gameState.getAgentState(self.index).scaredTimer == 0:
            features["food"] = 0
            features["ways"] = 0
            features["foodCarry"] = 0
            features["capsule"] = 0
            features["ghostMax"] = 0
            features["distanceHome"] = 0
            if features["ghostMin"] > 1:
                features["ghostMin"] = -10
            print("chaseA", action, features)
            return util.Counter(features)
        #chase pacman
        if self.getEnermy(gameState)[1][2] < 6 and self.getEnermy(gameState)[1][1] is not None \
                and self.getEnermy(gameState)[1][0] and not gameState.getAgentState(self.index).isPacman\
                and gameState.getAgentState(self.index).scaredTimer == 0:
            features["food"] = 0
            features["ways"] = 0
            features["foodCarry"] = 0
            features["capsule"] = 0
            features["ghostMin"] = 0
            features["distanceHome"] = 0
            if features["ghostMax"] > 1:
                features["ghostMax"] = -10
            print("chaseB", action, features)
            return util.Counter(features)
        # chase pacman
        if (self.getEnermy(gameState)[0][2] < 4 and gameState.getAgentState(self.index).isPacman and not self.getEnermy(gameState)[0][3])\
                or (self.getEnermy(gameState)[1][2] < 4 and gameState.getAgentState(self.index).isPacman and not self.getEnermy(gameState)[1][3]):
            features["food"] = 0
            features["foodCarry"] = 0
            features["capsule"] = 0
            features["ghostMin"] = 0
            features["ghostMax"] = 0
            print("home",self.getHomeDistance(gameState))
            print("escape", action, features)
            return util.Counter(features)
        if self.goBack(gameState, successor):
            features["food"] = 0
            features["ways"] = 0
            features["foodCarry"] = 0
            features["capsule"] = 0
            features["ghostMin"] = 0
            features["ghostMax"] = 0
            print("goBack",action, features)
            return util.Counter(features)
        if self.beEaten(gameState, successor):
            features["food"] = 0
            features["foodCarry"] = 0
            features["capsule"] = 0
            features["ghostMin"] = -10
            features["ghostMax"] = -10
            features["distanceHome"] = -10
            print("beEaten", action, features)
            return util.Counter(features)
        if self.goBackScore(gameState, successor) or successor.data._win:
            features["food"] = 0
            features["foodCarry"] = abs(features["foodCarry"])
            features["ways"] = 0
            features["capsule"] = 0
            features["ghostMin"] = 0
            features["ghostMax"] = 0
            print("goBackscore",action, features)
            return util.Counter(features)
        if features["food"] < - 1 or features["foodCarry"] == 1:  # eating food
            features["food"] = 0
            features["capsule"] = 0
            features["ghostMin"] = 0
            features["ghostMax"] = 0
            features["distanceHome"] = 0
            print("eatingFood",action, features)
            return util.Counter(features)

        if self.goEat(gameState,successor):
            e1, e2 = self.getEnermy(successor)
            if (not gameState.getAgentState(self.index).isPacman) and e1[2] < 5 and (not e1[0]) and not e1[3]:
                print("wondering")
                features["capsule"] = 0
                features["food"] = e1[2]/10
            if (not gameState.getAgentState(self.index).isPacman) and e2[2] < 5 and e2[2] < e1[2] and (not e2[0]) and not e2[3]:
                print("wondering")
                features["capsule"] = 0
                features["food"] = e2[2]/10
            features["distanceHome"] = 0
            features["ways"] = 0
            features["ghostMin"] = 0
            features["ghostMax"] = 0
            print("goEat",action, features)
            return util.Counter(features)

        print("what???")
        return util.Counter(features)

    def goEat(self,gameState, successor):
        if gameState.getAgentState(self.index).numCarrying < self.totalFoodNumber - 2:
            return True
        return False

    def goBack(self,gameState, successor):
        if self.foodLeft <= 2:
            return True
        if (gameState.getAgentState(self.index).numCarrying > 11 and
                self.getMazeDistance(gameState.getAgentPosition(self.index), self.targetFood) > 21):
            return True
        if gameState.getAgentState(self.index).numCarrying > 11 and gameState.getAgentState((self.index+2) % 4).isPacman:
            return True
        if gameState.getAgentState(self.index).numCarrying >= 1 and self.cost >= 280:
            return True
        if self.getMazeDistance(gameState.getAgentPosition(self.index), self.targetFood) > 1000:
            self.targetFood = random.choice(self.getFood(gameState).asList())
            print("no way!,go home, change another target")
            return True
        return False

    def goBackScore(self, gamestate, successor):
        if gamestate.getAgentState(self.index).numCarrying - successor.getAgentState(self.index).numCarrying >= 1 \
                and not successor.getAgentPosition(self.index) == successor.getInitialAgentPosition(self.index):
            return True
        return False

    def beEaten(self, gamestate, successor):
        if successor.getAgentPosition(self.index) == successor.getInitialAgentPosition(self.index) \
                and abs(self.getHomeDistance(gamestate)- self.getHomeDistance(successor)) > 1 or self.getEnemyPacmanDistance(successor) == 1:
            return True
        return False

    def setup(self,actions=["North", "South", "West", "East","Stop"], learning_rate=0.01, reward_decay=0.9, e_greedy=1,
                 first=True,):
        self.actions = actions  # a list
        self.lr = learning_rate # 学习率
        self.gamma = reward_decay   # 奖励衰减
        self.epsilon = e_greedy     # 贪婪度
        if first:
            self.weights = util.Counter({"food": 93.19970348920681,
                                         "foodCarry": 260.0637492041355,
                                         "distanceHome": 5138.773437266105,
                                         "capsule":  90,
                                         "ghostMin": -100,
                                         "ghostMax": -100,
                                         "ways": 0,
                                         "friend": -30,
                                         "b": 55.172944964376505})
        else:
            with open("data.txt")as data:
                self.weights = util.Counter(eval(data.readline().strip()))

    def choose_action(self, gameState):
        if gameState.getLegalActions(self.index) is not None:
            legal_actions = gameState.getLegalActions(self.index)
        else:
            legal_actions = ["Stop"]
        Qvalue = [self.getFeatures(gameState, action) * self.weights for action in legal_actions]
        print("Q",Qvalue)
        if len(Qvalue) == 0:
            action = "Stop"
        elif np.random.uniform() < self.epsilon and len(Qvalue) != 0:  # 选择 Q value 最高的 action
            action = legal_actions[Qvalue.index(max(Qvalue))]
        else:   # 随机选择 action
            action = np.random.choice(legal_actions)
        return action

    def learn(self, s, a, r, s_,):
        # if s_.data._lose:
        #     correction = -abs(1000*self.lr*self.getScore(s_))
        if s_.data._win:
            print("win")
            correction = abs(1000*self.lr*self.getScore(s_))
        else:
            legal_actions = s_.getLegalActions(self.index)
            Qvalue = [self.getFeatures(s_, action) * self.weights for action in legal_actions]
            correction = self.lr * (r + self.gamma * max(Qvalue) - self.getFeatures(s, a) * self.weights)
        for key, weights in self.weights.items():
            weights = weights + correction * self.getFeatures(s, a).get(key)
            self.weights[key] = weights
