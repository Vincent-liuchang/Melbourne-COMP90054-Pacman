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
        # print("what do you want to do man????")
        print(gameState)
        self.start = gameState.getAgentPosition(self.index)
        CaptureAgent.registerInitialState(self, gameState)

        self.setup()
        self.cost = 1
        self.food = self.getFood(gameState).asList()
        self.totalFoodNumber = len(self.food)
        self.foodLeft = self.totalFoodNumber
        self.targetFood = self.getFood(gameState).asList()[0]
        self.carry = gameState.getAgentState(self.index).numCarrying
        self.setUpTarget(gameState)
        self.defence = False

    '''
    Your initialization code goes here, if you need any.
    '''

    def setUpTarget(self, gameState):
        a, b = self.targetFood
        for foodX, foodY in self.food:
            if self.index >= 2 and gameState.isOnRedTeam(self.index):
                if foodY < b:
                    b = foodY
                    self.targetFood = (foodX, foodY)
            elif gameState.isOnRedTeam(self.index):
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

    def changeNearestTarget(self, gameState):
        dis = self.getAllFoodDistance(gameState)
        foodList = self.getFood(gameState).asList()
        if len(foodList)>1:
            self.targetFood = foodList[dis.index(min(dis))]
        else:
            self.targetFood = foodList[0]

    def getSuccessor(self, gameState, action):
        """
        Finds the next successor which is a grid position (location tuple).
        """
        for ispacman,position,distance,scared in self.getEnermy(gameState):
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
        time1 = time.time()

        if not self.getEnermy(gameState)[0][0] and self.getEnermy(gameState)[1][0]:
            self.defence = False

        for ispacman,position,distance,scared in self.getEnermy(gameState):
            if (position is not None)and (not ispacman) and not scared:
                x,y = position
                gameState.data.layout.walls[x][y] = True
                gameState.data.layout.walls[x + 1][y] = True
                gameState.data.layout.walls[x][y + 1] = True
                gameState.data.layout.walls[x][y - 1] = True
                gameState.data.layout.walls[x-1][y] = True

        self.cost += 1
        self.food = self.getFood(gameState).asList()
        self.foodLeft = len(self.food)
        self.carry = gameState.getAgentState(self.index).numCarrying

        if self.targetFood not in self.food:
            if self.targetFood[0]== gameState.getAgentPosition((self.index+2)%4)[0] and self.targetFood[1] == gameState.getAgentPosition((self.index+2)%4)[1]:
                self.setUpTarget(gameState)
            else:
                self.changeNearestTarget(gameState)
            # print("food disappear, change to nearest")

        distance_to_target = self.getTargetFoodDistance(gameState)
        if distance_to_target > 10000:
            self.targetFood = random.choice(self.food)
            # print("no way to food, random change target")

        if (not self.getPreviousObservation() is None) and self.getPreviousObservation().getAgentState(self.index).isPacman and not gameState.getAgentState(self.index).isPacman:
            self.targetFood = random.choice(self.food)
            self.defence = True
            # print("go back and change target and defence")

        # print("Agent", self.index)
        # print("cost", self.cost)
        # print("target food", self.targetFood)
        # print("food distance", distance_to_target)
        # print("enemy", self.getEnermy(gameState))
        # print("carry", self.carry)

        action = self.choose_action(gameState)

        time2 = time.time()
        # print("calculateTime", time2-time1)
        return action

    def getHomeDistance(self, gameState):
        current_position = gameState.getAgentPosition(self.index)
        return self.getMazeDistance(current_position, self.start) + 1

    def getTargetFoodDistance(self, gameState):
        current_position = gameState.getAgentPosition(self.index)
        if self.targetFood not in self.getFood(gameState).asList():
            return 0
        food_distance = self.getMazeDistance(self.targetFood, current_position)
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
            ca_distance = [9999]
        return ca_distance

    def getEnermy(self, gameState):
        # pacman, position, distance, scared
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

    def getEnermyDistanceToMe(self, gameState):
        my_position = gameState.getAgentPosition(self.index)
        enermy = self.getOpponents(gameState)
        enermyDistance = []
        for e in enermy:
            enermy_position = gameState.getAgentPosition(e)
            if enermy_position == None:
                enermy_distance = 9999
                enermyDistance.append(enermy_distance)
            else:
                enermy_distance = self.getMazeDistance(enermy_position, my_position)
                enermyDistance.append(enermy_distance)
        return enermyDistance

    def getTeamateDistance(self, gameState):
        my_position = gameState.getAgentPosition(self.index)
        teamMate = gameState.getAgentPosition((self.index+2) % 4)
        return self.getMazeDistance(my_position, teamMate)

    def getFeatures(self, gameState, action):

        successor = self.getSuccessor(gameState, action)

        # features = {"food": self.getTargetFoodDistance(gameState)-self.getTargetFoodDistance(successor),
        #             "foodCarry": successor.getAgentState(self.index).numCarrying-gameState.getAgentState(self.index).numCarrying,
        #             "distanceHome": self.getHomeDistance(gameState)-self.getHomeDistance(successor),
        #             "capsule": min(self.getCapsuleDistance(gameState))-min(self.getCapsuleDistance(successor)),
        #             "ghostMin": self.getEnemyPacmanDistance(successor)[0]-self.getEnemyPacmanDistance(gameState)[0],
        #             "ghostMax": self.getEnemyPacmanDistance(successor)[1] - self.getEnemyPacmanDistance(gameState)[1],
        #             "ways": len(successor.getLegalActions(self.index))-len(gameState.getLegalActions(self.index)),
        #             "friend": self.getTeamateDistance(gameState) - self.getTeamateDistance(successor),
        #             "b": 1
        #             }

        features = {"food": 0,
                    "foodCarry": 0,
                    "distanceHome": 0,
                    "capsule": 0,
                    "ghostMin": 0,
                    "ghostMax": 0,
                    "ways": 0,
                    "friend": 0,
                    "b": 1
                    }

        if self.getTeamateDistance(successor) <= 5:
            features["friend"] = self.getTeamateDistance(gameState) - self.getTeamateDistance(successor)
        if min(self.getCapsuleDistance(gameState))-min(self.getCapsuleDistance(successor)) < -1:
            if self.getEnermy(gameState)[0][1] is not None or self.getEnermy(gameState)[1][1] is not None:
                features["capsule"] = 2000
        if (self.getEnermy(gameState)[0][0] and self.getEnermy(gameState)[0][1] is not None
                and self.getEnermyDistanceToMe(gameState)[0] < 4 and (not gameState.getAgentState(self.index).isPacman)
                and gameState.getAgentState(self.index).scaredTimer == 0) \
                or (self.getEnermy(gameState)[0][0] and self.defence and self.getEnermy(gameState)[0][1] is not None
                    and gameState.getAgentState(self.index).scaredTimer == 0):
            features["ghostMin"] = self.getEnermy(successor)[0][2] - self.getEnermy(gameState)[0][2]
            if features["ghostMin"] > 1:
                features["ghostMin"] = -1000
            # print("chaseA", action, features)
            return util.Counter(features)
        #chase pacman
        if self.getEnermy(gameState)[1][0] and self.getEnermy(gameState)[1][1] is not None \
                and self.getEnermyDistanceToMe(gameState)[1] < 4 and (not gameState.getAgentState(self.index).isPacman)\
                and gameState.getAgentState(self.index).scaredTimer == 0 \
                or (self.getEnermy(gameState)[1][0] and self.defence and self.getEnermy(gameState)[1][1] is not None
                    and gameState.getAgentState(self.index).scaredTimer == 0):
            features["ghostMax"] = self.getEnermy(successor)[1][2]-self.getEnermy(gameState)[1][2]
            if features["ghostMax"] > 1:
                features["ghostMax"] = -1000
            # print("chaseB", action, features)
            return util.Counter(features)
        # chase pacman
        if (self.getEnermyDistanceToMe(gameState)[0] < 4 and gameState.getAgentState(self.index).isPacman and not self.getEnermy(gameState)[0][3])\
                or (self.getEnermyDistanceToMe(gameState)[1] < 4 and gameState.getAgentState(self.index).isPacman and not self.getEnermy(gameState)[1][3]):
            self.changeNearestTarget(gameState)
            if len(self.getCapsules(gameState)) == 0:
                features["friend"] = self.getTeamateDistance(gameState) - self.getTeamateDistance(successor)
                features["distanceHome"] = self.getHomeDistance(gameState)-self.getHomeDistance(successor)
                features["ways"] = len(successor.getLegalActions(self.index))-len(gameState.getLegalActions(self.index))
                # print("escapeForHome", action, features)
                # print("distanceToHome", self.getHomeDistance(gameState))
                # print("distanceToHome", self.getHomeDistance(successor))
                # print(gameState)
            else:
                if features["capsule"] != 2000:
                    features["capsule"] = min(self.getCapsuleDistance(gameState))-min(self.getCapsuleDistance(successor))
                # print("escapeForCap", action, features)
            return util.Counter(features)
        if self.goBack(gameState, successor):
            features["friend"] = self.getTeamateDistance(gameState) - self.getTeamateDistance(successor)
            features["distanceHome"] = self.getHomeDistance(gameState) - self.getHomeDistance(successor)
            # print("goBack", action, features)
            return util.Counter(features)
        if self.beEaten(gameState, successor):
            features["ghostMin"] = -100
            features["ghostMax"] = -100
            features["distanceHome"] = -100
            # print("beEaten", action, features)
            return util.Counter(features)
        if self.goBackScore(gameState, successor) or successor.data._win:
            features["foodCarry"] = abs(features["foodCarry"])
            features["distanceHome"] = self.getHomeDistance(gameState) - self.getHomeDistance(successor)
            # print("goBackscore",action, features)
            return util.Counter(features)
        if self.getTargetFoodDistance(gameState)-self.getTargetFoodDistance(successor) < - 1\
                or successor.getAgentState(self.index).numCarrying-gameState.getAgentState(self.index).numCarrying == 1:
            # eating food
            features["food"] = self.getTargetFoodDistance(gameState)-self.getTargetFoodDistance(successor) < - 1
            features["foodCarry"] = successor.getAgentState(self.index).numCarrying-gameState.getAgentState(self.index).numCarrying== 1
            # print("eatingFood",action, features)
            return util.Counter(features)

        if self.goEat(gameState,successor):
            e1, e2 = self.getEnermy(successor)
            features["food"] = self.getTargetFoodDistance(gameState) - self.getTargetFoodDistance(successor)
            if features["capsule"] != 2000:
                features["capsule"] = min(self.getCapsuleDistance(gameState))-min(self.getCapsuleDistance(successor))
            if features["capsule"] < -1:
                features["capsule"] = 1
            if (not gameState.getAgentState(self.index).isPacman) and self.getEnermyDistanceToMe(gameState)[0] < 4 and (not e1[0]) and (not e1[3]) and (e1[1] is not None):
                # print("wondering")
                self.targetFood = random.choice(self.food)
                features["food"] = e1[2]/10
                features["capsule"] = 0
            if (not gameState.getAgentState(self.index).isPacman) and self.getEnermyDistanceToMe(gameState)[1] < 4 and e2[2] < e1[2] and (not e2[0]) and (not e2[3])  and (e2[1] is not None):
                # print("wondering")
                self.targetFood = random.choice(self.food)
                features["food"] = e2[2]/10
                features["capsule"] = 0
            features["foodCarry"] = successor.getAgentState(self.index).numCarrying - gameState.getAgentState(self.index).numCarrying

            # print("goEat",action, features)
            return util.Counter(features)

        # print("what???")
        return util.Counter(features)

    def goEat(self,gameState, successor):
        if gameState.getAgentState(self.index).numCarrying < self.totalFoodNumber - 2:
            return True
        return False

    def goBack(self,gameState, successor):
        if self.foodLeft <= 2:
            if gameState.getAgentState(self.index).numCarrying == 0:
                self.defence = True
            return True
        if (gameState.getAgentState(self.index).numCarrying > 11 and
                self.getMazeDistance(gameState.getAgentPosition(self.index), self.targetFood) > 21):
            return True
        if gameState.getAgentState(self.index).numCarrying > 21:
            return True
        if gameState.getAgentState(self.index).numCarrying >= 1 and self.cost >= 280:
            return True
        if self.getMazeDistance(gameState.getAgentPosition(self.index), self.targetFood) > 1000:
            self.targetFood = random.choice(self.getFood(gameState).asList())
            # print("no way!,go home, change another target")
            return True
        return False

    def goBackScore(self, gamestate, successor):
        if gamestate.getAgentState(self.index).numCarrying - successor.getAgentState(self.index).numCarrying >= 1 \
                and not successor.getAgentPosition(self.index) == successor.getInitialAgentPosition(self.index):
            return True
        return False

    def beEaten(self, gamestate, successor):
        if successor.getAgentPosition(self.index) == successor.getInitialAgentPosition(self.index) \
                and abs(self.getHomeDistance(gamestate)- self.getHomeDistance(successor)) > 1\
                or self.getEnermy(successor)[0][1] == 1 or self.getEnermy(successor)[1][1] == 1:
            return True
        return False

    def setup(self,actions=["North", "South", "West", "East","Stop"], learning_rate=0.01, reward_decay=0.9, e_greedy=1,
                 first=True,):
        self.actions = actions  # a list
        self.lr = learning_rate # 学习率
        self.gamma = reward_decay   # 奖励衰减
        self.epsilon = e_greedy     # 贪婪度
        self.weights = util.Counter({"food": 93.19970348920681,
                                    "foodCarry": 260.0637492041355,
                                    "distanceHome": 5138.773437266105,
                                    "capsule":  90,
                                    "ghostMin": -100,
                                    "ghostMax": -100,
                                    "ways": 5,
                                    "friend": -30,
                                    "b": 55.172944964376505})

    def choose_action(self, gameState):
        if gameState.getLegalActions(self.index) is not None:
            legal_actions = gameState.getLegalActions(self.index)
        else:
            legal_actions = ["Stop"]
        Qvalue = [self.getFeatures(gameState, action) * self.weights for action in legal_actions]
        # print("Q",Qvalue)
        if len(Qvalue) == 0:
            action = "Stop"
        elif np.random.uniform() < self.epsilon and len(Qvalue) != 0:  # 选择 Q value 最高的 action
            action = legal_actions[Qvalue.index(max(Qvalue))]
        else:   # 随机选择 action
            action = np.random.choice(legal_actions)
        return action
