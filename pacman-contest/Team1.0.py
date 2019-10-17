from captureAgents import CaptureAgent
import random, time, util
import numpy as np
import util

#################
# Team creation #
#################


def createTeam(firstIndex, secondIndex, isRed,first='myAgent', second='myAgent'):
    return [eval(first)(firstIndex), eval(second)(secondIndex)]

targetFood = None
##########
# Agents #
##########


class myAgent(CaptureAgent):

    def registerInitialState(self, gameState):
        print(gameState)
        print("Don't spy on me")
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
        self.myPosition = gameState.getAgentPosition(self.index)
        self.myDistance = self.computeDistances(gameState)
        global targetFood
        targetFood = self.targetFood


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
        if len(foodList) > 1:
            self.targetFood = foodList[dis.index(min(dis))]
        elif len(foodList) != 0:
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
        global targetFood
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
        self.myDistance = self.computeDistances(gameState)
        self.myPosition = gameState.getAgentPosition(self.index)

        if self.targetFood[0] == targetFood[0] and self.targetFood[1] == targetFood[1] \
                and self.getMazeDistance(self.myPosition, self.targetFood) > self.getMazeDistance(gameState.getAgentPosition((self.index+2) % 4),self.targetFood):
             if len(self.food) > 0:
                 self.targetFood = random.choice(self.food)
             print("same target, change to another group")
        if self.targetFood not in self.food:
            if self.targetFood[0] == gameState.getAgentPosition((self.index+2) % 4)[0] and self.targetFood[1] == gameState.getAgentPosition((self.index+2)%4)[1]:
                self.setUpTarget(gameState)
            else:
                self.changeNearestTarget(gameState)
            # print("food disappear, change to nearest")

        distance_to_target = self.getTargetFoodDistance(gameState)
        while distance_to_target > 10000:
            if min(self.getAllFoodDistance(gameState)) > 10000:
                break
            food = self.food
            food.remove(self.targetFood)
            self.targetFood = random.choice(food)
            distance_to_target = self.getTargetFoodDistance(gameState)
            # print("no way to food, random change target")

        if (not self.getPreviousObservation() is None) and self.getPreviousObservation().getAgentState(self.index).isPacman and not gameState.getAgentState(self.index).isPacman:
            if self.getPreviousObservation().getAgentState(self.index).numCarrying == 0:
                self.targetFood = random.choice(self.food)
                if min(self.getEnermyDistanceToMe(gameState)) <= 10:
                    self.defence = True
            # print("go back and change target and defence")

        print("Agent", self.index)
        print("cost", self.cost)
        # print("target food", self.targetFood)
        # print("food distance", distance_to_target)
        # print("home distance", self.myDistance[self.start])
        # print("enemy", self.getEnermy(gameState))
        # print("carry", self.carry)
        # print("position",gameState.getAgentPosition(self.index))

        action = self.choose_action(gameState)

        time2 = time.time()
        print("calculateTime", time2-time1)
        targetFood = self.targetFood
        return action

    def getHomeDistance(self, gameState):
        current_position = gameState.getAgentPosition(self.index)

        if current_position[0] == self.myPosition[0] and current_position[1] == self.myPosition[1]:
            home_distance = self.myDistance[self.start]
        else:
            home_distance = self.computeDistances(gameState)[self.start]
        return home_distance+1

    def getHome(self, gameState):
        current_position = gameState.getAgentPosition(self.index)
        return self.getMazeDistance(current_position, self.start) + 1

    def getTargetFoodDistance(self, gameState):
        current_position = gameState.getAgentPosition(self.index)
        if self.targetFood not in self.getFood(gameState).asList():
            return 0
        # food_distance = self.getMazeDistance(self.targetFood, current_position)
        if current_position[0] == self.myPosition[0] and current_position[1] == self.myPosition[1]:
            if self.targetFood in self.myDistance:
                food_distance = self.myDistance[self.targetFood]
            else:
                food_distance = 99999
        else:
            myDistance = self.computeDistances(gameState)
            if self.targetFood in myDistance:
                food_distance = myDistance[self.targetFood]
            else:
                food_distance = 99999
        return food_distance

    def getAllFoodDistance(self, gameState):
        food_list = self.getFood(gameState).asList()
        food_distance = []
        for x, y in food_list:
            food = tuple((x, y))
            if food in self.myDistance:
                food_distance.append(self.myDistance[food])
            else:
                food_distance.append(99999)

        return food_distance

    def getCapsuleDistance(self, gameState):
        my_position = gameState.getAgentPosition(self.index)
        ca_list = self.getCapsules(gameState)

        if my_position[0] == self.myPosition[0] and my_position[1] == self.myPosition[1] or len(self.getCapsules(gameState)) == 0:
            myDistance = self.myDistance
        else:
            myDistance = self.computeDistances(gameState)

        if ca_list != []:
            ca_distance = []
            for x, y in ca_list:
                ca = tuple((x, y))
                if ca in myDistance:
                    ca_distance.append(myDistance[ca])
                else:
                    ca_distance.append(99999)
        else:
            ca_distance = [99999]
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
                enermy_distance = 99999
                enermyDistance.append(enermy_distance)
            else:
                enermy_distance = self.getMazeDistance(enermy_position, my_position)
                enermyDistance.append(enermy_distance)
        return enermyDistance

    def getTeamateDistance(self, gameState):
        my_position = gameState.getAgentPosition(self.index)
        teamMate = gameState.getAgentPosition((self.index+2) % 4)
        return self.getMazeDistance(my_position, teamMate)

#    def foodSafe(self):
#        return self.targetFood in self.safeFood
#
#    def initialSafeFood(self, gameState):
#        safeFood = []
#        for food in self.food:
#            x, y = food
#            myState = gameState.deepCopy()
#            myState.data.layout.walls[x][y] = True
#            safeMap = self.bfs(myState, self.start)
#            count = 0
#            if (x, y + 1) in safeMap and safeMap[(x, y + 1)] < 10000:
#                count += 1
#            if (x + 1, y) in safeMap and safeMap[(x + 1, y)] < 10000:
#                count += 1
#            if (x - 1, y) in safeMap and safeMap[(x - 1, y)] < 10000:
#                count += 1
#            if (x, y - 1) in safeMap and safeMap[(x, y - 1)] < 10000:
#                count += 1
#            if count >= 2:
#                safeFood.append(food)
#        # print("initialSafeFood", safeFood)
#        return safeFood

    def bfs(self, gameState, position):
        pos1 = position
        allNodes = gameState.data.layout.walls.asList(False)

        dist = {}
        closed = {}
        for node in allNodes:
            dist[node] = 99999
        import util
        queue = util.PriorityQueue()
        queue.push(pos1, 0)
        dist[pos1] = 0
        while not queue.isEmpty():
            node = queue.pop()
            if node in closed:
                continue
            closed[node] = True
            nodeDist = dist[node]
            adjacent = []
            x, y = node
            if not gameState.data.layout.isWall((x, y + 1)):
                adjacent.append((x, y + 1))
            if not gameState.data.layout.isWall((x, y - 1)):
                adjacent.append((x, y - 1))
            if not gameState.data.layout.isWall((x + 1, y)):
                adjacent.append((x + 1, y))
            if not gameState.data.layout.isWall((x - 1, y)):
                adjacent.append((x - 1, y))
            for other in adjacent:
                if not other in dist:
                    continue
                oldDist = dist[other]
                newDist = nodeDist + 1
                if newDist < oldDist:
                    dist[other] = newDist
                    queue.push(other, newDist)
        return dist

    def computeDistances(self, gameState):
        # print("跑了一次")
        pos1 = gameState.getAgentPosition(self.index)
        return self.bfs(gameState,pos1)



    def getFeatures(self, gameState, action):
        # print("start get features")
        successor = self.getSuccessor(gameState, action)

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
        if len(self.getCapsules(gameState))-len(self.getCapsules(successor)) == 1:
            if (not self.getEnermy(gameState)[0][3]) or (not self.getEnermy(gameState)[1][3]):
                features["capsule"] = 2000
        if (self.getEnermy(gameState)[0][0] and self.getEnermy(gameState)[0][1] is not None
                and self.getEnermyDistanceToMe(gameState)[0] < 4 and (not gameState.getAgentState(self.index).isPacman)
                and gameState.getAgentState(self.index).scaredTimer == 0 and (not self.getEnermy(gameState)[0][3]) and len(self.getCapsulesYouAreDefending(gameState)) == 0)\
                or (self.getEnermy(gameState)[0][0] and self.defence and self.getEnermy(gameState)[0][1] is not None
                    and gameState.getAgentState(self.index).scaredTimer == 0 and (not gameState.getAgentState(self.index).isPacman)):
            features["ghostMin"] = self.getEnermy(successor)[0][2] - self.getEnermy(gameState)[0][2]
            if features["ghostMin"] > 1:
                features["ghostMin"] = -1000
            # print("chaseA", action, features)
            return util.Counter(features)
        #chase pacman
        if (self.getEnermy(gameState)[1][0] and self.getEnermy(gameState)[1][1] is not None\
                and self.getEnermyDistanceToMe(gameState)[1] < 4 and (not gameState.getAgentState(self.index).isPacman)\
                and gameState.getAgentState(self.index).scaredTimer == 0 and (not self.getEnermy(gameState)[0][3]) and len(self.getCapsulesYouAreDefending(gameState)) == 0)\
                or (self.getEnermy(gameState)[1][0] and self.defence and self.getEnermy(gameState)[1][1] is not None
                    and gameState.getAgentState(self.index).scaredTimer == 0 and (not gameState.getAgentState(self.index).isPacman)):
            features["ghostMax"] = self.getEnermy(successor)[1][2]-self.getEnermy(gameState)[1][2]
            if features["ghostMax"] > 1:
                features["ghostMax"] = -1000
            # print("chaseB", action, features)
            return util.Counter(features)
        # chase pacman

        if (self.getEnermyDistanceToMe(gameState)[0] < 4 and gameState.getAgentState(self.index).isPacman and not self.getEnermy(gameState)[0][3])\
            or (self.getEnermyDistanceToMe(gameState)[1] < 4 and gameState.getAgentState(self.index).isPacman and not self.getEnermy(gameState)[1][3])\
            or (self.myDistance[self.start] > 10000 and min(self.getCapsuleDistance(gameState)) > 10000):
            if len(self.food) != 0:
                self.targetFood = random.choice(self.getFood(gameState).asList())
            if len(self.getCapsules(gameState)) == 0 or min(self.getCapsuleDistance(gameState)) > 10000:
                features["friend"] = self.getTeamateDistance(gameState) - self.getTeamateDistance(successor)
                features["ways"] = len(successor.getLegalActions(self.index))-len(gameState.getLegalActions(self.index))
                if self.getHomeDistance(gameState) < 10000:
                    features["distanceHome"] = self.getHomeDistance(gameState) - self.getHomeDistance(successor)
                else:
                    print("no way home, try your skills, be Messi")
                    features["distanceHome"] = self.getHome(gameState) - self.getHome(successor)
                    features["ways"] = 0
                # print("escapeForHome", action, features)
                # print("distanceToHome", self.getHomeDistance(gameState))
                # print(gameState)
            else:
                if features["capsule"] != 2000:
                    features["capsule"] = min(self.getCapsuleDistance(gameState))-min(self.getCapsuleDistance(successor))
                # print("escapeForCap", action, features)
            return util.Counter(features)

        if self.goBackScore(gameState, successor) or successor.data._win:
            features["foodCarry"] = abs(successor.getAgentState(self.index).numCarrying-gameState.getAgentState(self.index).numCarrying) * 300
            features["distanceHome"] = self.getHomeDistance(gameState) - self.getHomeDistance(successor)
            # print("goBackscore",action, features)
            return util.Counter(features)
        if self.goBack(gameState, successor):
            e1, e2 = self.getEnermy(gameState)
            features["friend"] = self.getTeamateDistance(gameState) - self.getTeamateDistance(successor)
            features["distanceHome"] = self.getHomeDistance(gameState) - self.getHomeDistance(successor)
            if self.saveFriend(gameState) and gameState.getAgentState((self.index+2) % 4).isPacman:
                # print("Save your friend")
                features["capsule"] = 2 * features["capsule"]
            if not gameState.getAgentState(self.index).isPacman:
                features["distanceHome"] = 0
                features["b"] = 0
                features["friend"] = 0
                # print("finish and stay for defend")
                if gameState.getAgentState(self.index).scaredTimer > 0:
                    if e1[0] and (e1[1] is not None):
                        features["ghostMin"] = abs(e1[2] - 2)
                    if e2[0] and (e2[1] is not None):
                        features["ghostMin"] = abs(e2[2] - 2)
            # print("goBack", action, features)
            return util.Counter(features)
        if successor.getAgentState(self.index).numCarrying-gameState.getAgentState(self.index).numCarrying == 1:
            # eating food
            features["food"] = 1
            features["foodCarry"] = successor.getAgentState(self.index).numCarrying-gameState.getAgentState(self.index).numCarrying
            # print("eatingFood", action, features)
            return util.Counter(features)
        if self.goEat(gameState,successor):
            # print("food Safe")
            e1, e2 = self.getEnermy(successor)
            if self.getTargetFoodDistance(gameState) == 99999:
                features["food"] = self.getMazeDistance(self.myPosition, self.targetFood) - self.getMazeDistance(successor.getAgentPosition(self.index), self.targetFood)
            else:
                features["food"] = self.getTargetFoodDistance(gameState) - self.getTargetFoodDistance(successor)
            if features["capsule"] != 2000:
                features["capsule"] = min(self.getCapsuleDistance(gameState)) - min(self.getCapsuleDistance(successor))
            if features["capsule"] < -1:
                features["capsule"] = 1
            if (not gameState.getAgentState(self.index).isPacman) and self.getEnermyDistanceToMe(gameState)[0] < 4 and (not e1[0]) and (not e1[3]) and (e1[1] is not None):
                print("wondering")
                if len(self.food) != 0:
                    self.targetFood = random.choice(self.food)
                features["food"] = e1[2]/10
                features["capsule"] = 0
            if (not gameState.getAgentState(self.index).isPacman) and self.getEnermyDistanceToMe(gameState)[1] < 4 and e2[2] < e1[2] and (not e2[0]) and (not e2[3])  and (e2[1] is not None):
                print("wondering")
                if len(self.food) != 0:
                    self.targetFood = random.choice(self.food)
                features["food"] = e2[2]/10
                features["capsule"] = 0
            features["foodCarry"] = successor.getAgentState(self.index).numCarrying - gameState.getAgentState(self.index).numCarrying
            #
            if self.saveFriend(gameState) and min(self.getCapsuleDistance(gameState)) < 10000:
                # print("Save your friend")
                features["capsule"] = 2 * features["capsule"]
            # print("goEat", action, features)
            return util.Counter(features)

        print("what???")
        return util.Counter(features)

    def saveFriend(self,gameState):
        e1, e2 = self.getEnermy(gameState)
        if (not e1[0]) and e1[1] is not None and self.getMazeDistance(gameState.getAgentPosition((self.index+2) % 4), e1[1]) < 4 and not e1[3]:
            return True
        if (not e2[0]) and e2[1] is not None and self.getMazeDistance(gameState.getAgentPosition((self.index+2) % 4), e2[1]) < 4 and not e2[3]:
            return True
        return False

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
        if self.targetFood in self.myDistance and self.myDistance[self.targetFood] > 10000 and min(self.getAllFoodDistance(gameState)) < 10000 :
            if len(self.food) != 0:
                self.targetFood = random.choice(self.getFood(gameState).asList())
            print("no way!,go home, change another target")
            return True
        return False

    def goBackScore(self, gamestate, successor):
        if gamestate.getAgentState(self.index).numCarrying - successor.getAgentState(self.index).numCarrying > 1 \
                and not successor.getAgentPosition(self.index) == successor.getInitialAgentPosition(self.index):
            return True
        if gamestate.getAgentState(self.index).numCarrying - successor.getAgentState(self.index).numCarrying == 1 \
        and self.foodLeft <= 2 and not successor.getAgentPosition(self.index) == successor.getInitialAgentPosition(self.index):
            return True
        return False

    def beEaten(self, gamestate, successor):
        if successor.getAgentPosition(self.index) == successor.getInitialAgentPosition(self.index) \
                and abs(self.getHome(gamestate) - self.getHome(successor)) > 1\
                or self.getEnermy(successor)[0][2] == 1 or self.getEnermy(successor)[1][2] == 1:
            return True
        return False

    def setup(self,actions=["North", "South", "West", "East","Stop"], learning_rate=0.01, reward_decay=0.9, e_greedy=1,
                 first=True,):
        self.actions = actions  # a list
        self.lr = learning_rate # 学习率
        self.gamma = reward_decay   # 奖励衰减
        self.epsilon = e_greedy     # 贪婪度
        self.weights = util.Counter({"food": 93.19970348920681,
                                    "foodCarry": 87.0637492041355,
                                    "distanceHome": 5138.773437266105,
                                    "capsule":  87,
                                    "ghostMin": -100,
                                    "ghostMax": -100,
                                    "ways": 5,
                                    "friend": -3,
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
            if max(Qvalue) == 0:
                action = "Stop"
            else:
                action = legal_actions[Qvalue.index(max(Qvalue))]
        else:   # 随机选择 action
            action = np.random.choice(legal_actions)
        return action
