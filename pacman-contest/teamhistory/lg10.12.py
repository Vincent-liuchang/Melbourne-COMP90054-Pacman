# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).
import math

from captureAgents import CaptureAgent
import random, time, util
import distanceCalculator
import copy
from game import Directions
import game

# no capsule map
# 回家距离
# 边线被吃
#################
# Team creation #
#################
position1 = 1
foods = {}
def createTeam(firstIndex, secondIndex, isRed,
               first='MonteCarloOffensiveAgent', second='MonteCarloOffensiveAgent'):
    """
    This function should return a list of two agents that will form the````````
    team, initialized using firstIndex and secondIndex as their agent

    index numbers.  isRed is True if the red team is being created, and
    will be False if the blue team is being created.

    As a potentially helpful development aid, this function can take
    additional string-valued keyword arguments ("first" and "second" are
    such arguments in the case of this function), which will come from
    the --redOpts and --blueOpts command-line arguments to capture.py.
    For the nightly contest, however, your team will be created without
    any extra arguments, so you should make sure that the default
    behavior is what you want for the nightly contest.
    """

    # The following line is an example only; feel free to change it.
    return [eval(first)(firstIndex), eval(second)(secondIndex)]


##########
# Agents #
##########

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

        return random.choice(actions)


class MonteCarloOffensiveAgent(CaptureAgent):
    """
    A base class for reflex agents that chooses score-maximizing actions
    """

    def registerInitialState(self, gameState):
        self.start = gameState.getAgentPosition(self.index)
        CaptureAgent.registerInitialState(self, gameState)
        self.food = None
        self.totalFood = len(self.getFood(gameState).asList())
        self.startState = gameState

        foodList = self.getFood(gameState).asList()
        self.chooseFood(foodList)
        self.distancer = distanceCalculator.Distancer(gameState.data.layout)
        self.distancer.getMazeDistances()
        self.escape = 1
        self.defense= 2
        self.offense = 3
        self.status = self.offense
        self.goodFood = self.chooseGoodFood(foodList)
        self.save = False
        self.bound = gameState.data.layout.width / 2
        if gameState.isOnRedTeam(self.index):
            self.bound -= 1
        # print(self.getBlockedDistance(self.startState, self.getCapsules(self.startState)[0]))

    def chooseGoodFood(self, foodList):

        goodFoodList = []
        for food in foodList:
            x,y = food
            gameState = self.startState.deepCopy()
            walls = self.startState.data.layout.walls.deepCopy()
            count = 0
            ways = []

            if walls[x + 1][y] == False:
                count += 1
                ways.append((x + 1, y))
            if walls[x - 1][y] == False:
                count += 1
                ways.append((x - 1, y))
            if walls[x][y + 1] == False:
                count += 1
                ways.append((x, y + 1))
            if walls[x][y - 1] == False:
                count += 1
                ways.append((x, y - 1))
            if count >= 2:
                walls[x][y] = True
                gameState.data.layout.walls = walls
                for w1 in ways:
                    for w2 in ways:
                        if w2 != w1:
                            if self.getBlockedDistance(gameState, w1, w2) < 5000:
                                if food not in goodFoodList:
                                    goodFoodList.append(food)

        return goodFoodList


    def chooseFood(self, foodList):
        max = -100
        min = 1000
        for x, y in foodList:
            if y > max:
                max = y
                topFood = (x, y)
            if y < min:
                min = y
                bottomFood = (x, y)

        global position1
        if position1 == 1:

            position1 = self.start
            if topFood[1] - position1[1] > position1[1] - bottomFood[1]:
                self.food = bottomFood
            else:
                self.food = topFood
            global foods
            foods[self.index] = self.food
        else:

            if topFood[1] - position1[1] > position1[1] - bottomFood[1]:
                self.food = topFood
            else:
                self.food = bottomFood
            position1 = 1


    def getDistanceToHome(self, gameState, selfPosition):
            openList = util.Queue()
            openList.push(selfPosition)
            cost = {selfPosition: 0}
            closedList = [selfPosition]
            i = 0
            while True:
                i += 1
                if openList.isEmpty():
                    return 10000
                s = openList.pop()
                x, y = s
                if gameState.isOnRedTeam(self.index):
                    if x <= self.bound:
                        return cost[s]
                else:
                    if x <= self.bound:
                        return  cost[s]
                walls = gameState.data.layout.walls
                x, y = s
                successors = []
                if walls[x + 1][y] == False:
                    successors.append((x + 1, y))
                if walls[x - 1][y] == False:
                    successors.append((x - 1, y))
                if walls[x][y + 1] == False:
                    successors.append((x, y + 1))
                if walls[x][y - 1] == False:
                    successors.append((x, y - 1))

                for successor in successors:
                    if successor not in closedList:
                        openList.push(successor)
                        closedList.append(successor)
                        cost[successor] = cost[s] + 1

    def chooseAction(self, gameState):
        """
        Picks among the actions with the highest Q(s,a).
        """
        start = time.time()
        self.state = gameState
        self.walls = gameState.data.layout.walls
        self.position = gameState.getAgentPosition(self.index)
        self.reward = self.getReward(gameState)
        foodLeft = len(self.getFood(gameState).asList())
        if self.food not in self.getFood(gameState).asList():
            if foodLeft > 2:
                self.nearestFood(self.getFood(gameState).asList())
            else:
                self.food = self.start

        if (foodLeft <= 2 or gameState.data.timeleft < 100) and gameState.getAgentState(self.index).isPacman:
            self.status = self.escape
            self.reward = {}
            self.reward[self.start] = 10000


        if self.reward.__len__() != 0:
            gameState.data.layout.walls = self.walls

            root = Node(gameState, self.reward, gameState.getAgentPosition(self.index), self.index, self)
            act = self.MCTSearch(root,5)
            self.save = False
            end = time.time()
            self.food = None
            return act

        self.status = self.offense

        # if self.getPreviousObservation() != None and self.status == self.defense:
        #
        #         lastState = self.getPreviousObservation()
        #
        #         lastFoodList = self.getFoodYouAreDefending(lastState).asList()
        #         currentFoodList = self.getFoodYouAreDefending(gameState).asList()
        #
        #         lastTimer = self.getPreviousObservation().getAgentState(self.index).scaredTimer
        #         currentTimer = gameState.getAgentState(self.index).scaredTimer
        #         if lastState.getAgentState(self.index).isPacman and not gameState.getAgentState(self.index).isPacman:
        #             if len(lastFoodList) > len(currentFoodList):
        #                 for food in lastFoodList:
        #                     if food not in currentFoodList:
        #                         foodEaten = food
        #
        #                 self.food = foodEaten
        #
        #             if lastTimer == 0 and currentTimer > 0:
        #                 self.nearestFood(self.getFood(gameState).asList())

        # else:
        #         if self.food not in self.getFood(gameState).asList():
        #             self.nearestFood(self.getFood(gameState).asList())


        gameState.data.layout.walls = self.walls
        actions = gameState.getLegalActions(self.index)
        if foodLeft <= 2 and not gameState.getAgentState(self.index).isPacman:
            return random.choice(gameState.getLegalActions(self.index))
        values = [-self.foodHeuristic(self.getSuccessor(gameState, a), self.food) for a in actions]
        if len(values) == 0:
            print("ffff")
            return "Stop"
        maxValue = max(values)

        bestActions = [a for a, v in zip(actions, values) if v == maxValue]
        end = time.time()
        # print("eva: " + str(end - start))

        return random.choice(bestActions)

    def calculateNewDistance(self,gameState, opponent):
        oppoPosition = gameState.getAgentPosition(opponent)
        distances = self.distancer._distances

    def getBlockedDistance(self, gameState, selfPosition, targetPosition):
        openList = util.Queue()
        openList.push(selfPosition)
        cost = {selfPosition: 0}
        closedList = [selfPosition]
        i = 0
        while True:
            i += 1
            if openList.isEmpty():
                return 10000
            s = openList.pop()
            if s == targetPosition:
                return cost[s]
            walls = gameState.data.layout.walls
            x, y = s
            successors = []
            if walls[x + 1][y] == False:
                successors.append((x + 1, y))
            if walls[x - 1][y] == False:
                successors.append((x - 1, y))
            if walls[x][y + 1] == False:
                successors.append((x, y + 1))
            if walls[x][y - 1] == False:
                successors.append((x, y - 1))

            for successor in successors:
                if successor not in closedList:
                    openList.push(successor)
                    closedList.append(successor)
                    cost[successor] = cost[s] + 1
    def nearestPosition(self, List):
        min = 1000
        what = None
        for food in List:
            dis = self.getMazeDistance(self.position, food)
            if dis < min:
                min =dis
                what = food

        return what

    def getReward(self, gameState):
        minDistance = 10000
        reward = {}
        foodList = []
        for food in self.getFood(gameState).asList():
            if self.getMazeDistance(food, self.position) <= 5:
                foodList.append(food)
        if len(foodList) > 0:
            reward[self.nearestPosition(foodList)] = 1
        # for capsule in self.getCapsules(gameState):
        #     if (self.getMazeDistance(gameState.getAgentPosition(self.index), capsule)) <= 5:
        #         if not self.escape:
        #             reward[capsule] = 0.1
        #         else:
        #             reward[capsule] = 2
        self.status = self.offense
        peerIndex = (self.index + 2) % 4
        peerPosition = gameState.getAgentPosition(peerIndex)
        for opponent in self.getOpponents(gameState):
            if gameState.getAgentPosition(opponent) != None:
                myState = gameState.getAgentState(self.index)
                myPosition = gameState.getAgentPosition(self.index)
                opponentPosition = gameState.getAgentPosition(opponent)
                opponentState = gameState.getAgentState(opponent)
                if myState.isPacman and  opponentState.isPacman:
                    self.status = self.offense
                    continue
                elif  myState.isPacman and not opponentState.isPacman:

                    if opponentState.scaredTimer == 0:
                        self.setWalls(gameState, opponentPosition, 1)
                        if self.getMazeDistance(myPosition, opponentPosition) <= 3:
                            self.status = self.escape
                            reward[opponentPosition] = -self.totalFood - 10

                        elif self.getMazeDistance(peerPosition, opponentPosition) <= 3:
                            self.status = self.offense
                            self.save = True
                        else:
                            self.status = self.offense
                    elif opponentState.scaredTimer <= 5:
                        if self.getMazeDistance(myPosition, opponentPosition) <= 4:
                            reward[opponentPosition] = self.totalFood - 10
                        self.status = self.offense
                elif not myState.isPacman and opponentState.isPacman:
                    if myState.scaredTimer == 0:
                        if self.getMazeDistance(myPosition, opponentPosition) <= 4:
                            opponentGameState = gameState.deepCopy()
                            walls = gameState.data.layout.walls.deepCopy()
                            self.setWalls(opponentGameState, myPosition, 2)
                            bestPosition = self.bestDefensePosition(opponentGameState, opponent, opponentGameState.getInitialAgentPosition(opponent))
                            reward[bestPosition] = self.totalFood + 10 - self.getFoodYouAreDefending(gameState).asList().__len__()
                            self.status = self.defense
                        else:
                            self.status = self.offense
                    else:
                        if self.getMazeDistance(myPosition, opponentPosition) <= 4:
                            self.setWalls(gameState, opponentPosition, 1)
                            # bestPosition =self.bestDefensePosition(opponentGameState, opponent, gameState.getInitialAgentPosition(opponent))
                            reward[opponentPosition] = -self.totalFood - 10 - self.getFoodYouAreDefending(gameState).asList().__len__()
                            self.status = self.offense

                elif not myState.isPacman and not opponentState.isPacman:
                    if myState.scaredTimer > 0:
                        if self.getMazeDistance(myPosition, opponentPosition) < 3:
                            reward[opponentPosition] = -self.totalFood - 10
                            self.setWalls(gameState, opponentPosition, 1)
                            self.status = self.offense
                    elif opponentState.scaredTimer > 0:
                        self.status = self.offense
                        continue
                    else:
                        if self.getMazeDistance(myPosition, opponentPosition) <= 2:
                            reward[opponentPosition] = -self.totalFood - 10
                            self.setWalls(gameState, opponentPosition, 1)
                            self.status = self.offense
                        else:
                            self.status = self.offense
        return reward

    def bestDefensePosition(self, gameState,opponent,  initialPosition):
        successorPositions = []
        bestPosition = None
        for action in gameState.getLegalActions(opponent):
            successorPositions.append(gameState.generateSuccessor(opponent, action).getAgentPosition(opponent))
        if len(successorPositions) == 0:
            bestPosition = gameState.getAgentPosition(opponent)
        else:

            minDis = 10001
            for successorPosition in successorPositions:
                dis = self.getBlockedDistance(gameState, successorPosition, initialPosition)
                if self.getBlockedDistance(gameState, successorPosition, initialPosition) < minDis:
                    minDis = dis
                    bestPosition = successorPosition
            print(bestPosition)
        return bestPosition

    def setWalls(self, gameState, opponentPosition, number):
        x,y = opponentPosition
        gameState.data.layout.walls[x][y] = True
        gameState.data.layout.walls[x + 1][y] = True
        gameState.data.layout.walls[x - 1][y] = True
        gameState.data.layout.walls[x][y + 1] = True
        gameState.data.layout.walls[x][y - 1] = True
        if number == 1:
            self.walls = gameState.data.layout.walls
    def foodHeuristic(self, gameState, food):

        fdis = self.getMazeDistance(gameState.getAgentPosition(self.index), food)
        return fdis

    def nearestFood(self, foodList):
        min = 1000

        peerIndex = (self.index + 2) % 4
        peerPosition = self.state.getAgentPosition(peerIndex)
        for food in foodList:
            myDistance = self.getMazeDistance(self.position, food)
            peerDistance = self.getMazeDistance(peerPosition, food)
            if myDistance < min:
                if myDistance < peerDistance:
                    self.food = food
                    min = self.getMazeDistance(self.position, food)
        if self.food == None:
            min = 1000
            for food in foodList:
                myDistance = self.getMazeDistance(self.position, food)
                if myDistance < min:
                        self.food = food
                        min = self.getMazeDistance(self.position, food)

    def getSuccessor(self, gameState, action):
        """
        Finds the next successor which is a grid position (location tuple).
        """
        successor = gameState.generateSuccessor(self.index, action)
        pos = successor.getAgentPosition(self.index)

        if pos != util.nearestPoint(pos):
            # Only half a grid position was covered
            return successor.generateSuccessor(self.index, action)
        return successor

    # def evaluate(self, gameState, reward, value, fromPosition, visitedToday, visitedTimes):
    #
    #     # Monte Carlo
    #     position = gameState.getAgentPosition(self.index)
    #     if position in visitedTimes:
    #         visitedTimes[position] += 1
    #     if position not in value.keys():
    #         value[position] = 0
    #         visitedTimes[position] = 1
    #     if position not in visitedToday:
    #       visitedToday.append(position)
    #     if self.getMazeDistance(position, fromPosition) <= 5:
    #       if position in reward.keys():
    #         value[position] = reward[position]
    #         return (value, reward[position] * 0.6, visitedToday, visitedTimes)
    #       successors = []
    #       actions = gameState.getLegalActions(self.index)
    #       # actions.remove('Stop')
    #       random.shuffle(actions)
    #       for action in actions:
    #           successor = self.getSuccessor(gameState, action)
    #           successors.append(successor)
    #           if successor.getAgentPosition(self.index) not in visitedToday:
    #               visitedToday.append(successor.getAgentPosition(self.index))
    #
    #               successorPosition = successor.getAgentPosition(self.index)
    #
    #
    #           #expansion
    #               if successorPosition not in value.keys():
    #                   # if successorPosition not in visited:
    #                   #     visited[successorPosition] = 0
    #                   v, r, t, times = self.evaluate(successor, reward, value, fromPosition, visitedToday, visitedTimes)
    #                   value = v
    #                   value[position] += r
    #                   visitedTimes = times
    #                   return (value, r * 0.6, t, visitedTimes)
    #
    #       values = [value[successor.getAgentPosition(self.index)] for successor in successors]
    #       positions = [successor.getAgentPosition(self.index) for successor in successors]
    #
    #       for v in values:
    #           values[values.index(v)] -= visitedTimes[positions[values.index(v)]]
    #       print(successors)
    #       print(position)
    #       print(values)
    #       # if values.__len__() > 0:
    #       maxValue = max(values)
    #       best = [(s, v) for s, v in zip(successors, values) if v == maxValue]
    #       best = best[0]
    #       v, r, t, times =  self.evaluate(best[0], reward, value, fromPosition, visitedToday, visitedTimes)
    #       value = v
    #       value[position] += r
    #       visitedTimes = times
    #       return (value, r * 0.6, t, visitedTimes)
    #     return (value, 0, visitedToday, visitedTimes)
    #
    #     # return visited,0
    #
    #     # FoodHeuristic
    #
    #     # reward = self.getReward(gameState)
    #     # position = gameState.getAgentPosition(self.index)
    #     #
    #     # successor = self.getSuccessor(gameState, action)
    #     # successorPosition = successor.getAgentPosition(self.index)
    #     # vHere = 0
    #     # for r in reward:
    #     #     dis = self.getMazeDistance(successorPosition, r)
    #     #     vHere += math.pow(0.9, dis) * reward[r]
    #     #
    #     # return vHere

    # Computes a linear combination of features and feature weights

    # def getReward(self, gameState):
    #     reward = {}
    #     minDistance = 10000
    #     for food in self.getFood(gameState).asList():
    #         fdis = self.getMazeDistance(gameState.getAgentPosition(self.index), food)
    #         if fdis < minDistance:
    #             minDistance = fdis
    #         if fdis <= 5:
    #           reward[food] = 100
    #     for capsule in self.getCapsules(gameState):
    #         if (self.getMazeDistance(gameState.getAgentPosition(self.index), capsule)) <= 5:
    #             reward[capsule] = 300
    #
    #     count = 0
    #     for opponent in self.getOpponents(gameState):
    #         if gameState.getAgentPosition(opponent) != None:
    #             count += 1
    #             if gameState.getAgentState(opponent).isPacman & (not gameState.getAgentState(self.index).isPacman):
    #                 reward[gameState.getAgentPosition(opponent)] = 1000
    #             if (not gameState.getAgentState(opponent).isPacman) & gameState.getAgentState(self.index).isPacman:
    #                 reward[gameState.getAgentPosition(opponent)] = -1000
    #     return reward
    #
    # def getFeatures(self, gameState, action):
    #   """
    #   Returns a counter of features for the state
    #   """
    #   features = util.Counter()
    #   successor = self.getSuccessor(gameState, action)
    #   features['successorScore'] = self.getScore(successor)
    #   return features
    #
    # def getWeights(self, gameState, action):
    #   """
    #   Normally, weights do not depend on the gamestate.  They can be either
    #   a counter or a dictionary.
    #   """
    #   return {'successorScore': 1.0}

    def MCTSearch(self, root, times):
        time = 0

        while time < times:
            # Seletions
            node = root
            time += 1
            expand = 0
            # Simulation
            while expand <= 25:
                expand += 1
                # Expansion
                if not node.fullyExpanded():
                    child = node.getChild()
                    node = child
                else:
                    if node.selectBestChild() != None:
                        node = node.selectBestChild()
                # Backpropagation
                # print(time)
                # print(node.state.getAgentPosition(self.index))
                if node.getReward() != 0 | expand == 25:
                    node.visit()
                    while node.parent != None:
                        node.backPropagation()
                        node = node.parent
                    continue
        if len(root.state.getLegalActions(self.index)) == 0:
            print("tttttt")
            return "Stop"

        return root.getChildAction(root.selectValueChild())


    def distanceToCapsule(self,gameState, position, capsuleList):
        mindis = 1000
        for capsule in capsuleList:
            d = self.getBlockedDistance(gameState, position, capsule)
            if d < mindis:
                mindis = d
            print(d)

        return d


class Node():

    def __init__(self, gameState, reward, position, index, captureAgent, parent=None):
        self.captureAgent = captureAgent
        self.position = position
        self.state = gameState
        self.visitedTimes = 0
        self.value = 0
        self.rewardList = reward
        self.reward = 0
        self.heuristic = 0
        self.index = index
        self.children = []
        self.legalActions = []
        self.mctValue = 9999
        self.parent = parent
        self.childrenPosition = []
        self.legalActions = gameState.getLegalActions(index)
        random.shuffle(self.legalActions)
        self.nways = len(self.legalActions)
        # self.legalActions.remove('Stop')
        self.totalFood = 20
        self.foodCarrying = 0
        self.isPacman = self.state.getAgentState(self.index).isPacman

    def visit(self):
        self.visitedTimes += 1

    def heuristicToReward(self):
        h = 0
        peerIndex = (self.captureAgent.index + 2) % 4
        peerPosition = self.state.getAgentPosition(peerIndex)
        if self.captureAgent.status == self.captureAgent.escape:
            chosenList = self.captureAgent.getCapsules(self.state)
            for food in self.captureAgent.getFood(self.state).asList():
                if food in self.captureAgent.goodFood:
                    chosenList.append(food)
            if len(chosenList) > 0 and (not self.captureAgent.start in self.rewardList.keys()) or self.captureAgent.save == True :
                h = -len(chosenList) + math.pow(0.9, self.captureAgent.getBlockedDistance(self.state, self.position, self.captureAgent.nearestPosition(chosenList)))
            else:
                h = math.pow(0.9,(self.captureAgent.getBlockedDistance(self.state, self.position, self.captureAgent.start)))
            # if len(self.captureAgent.getCapsules(self.state)) > 0 and self.captureAgent.start not in self.rewardList.keys():
            #     i = 0
            #     for capsule in self.captureAgent.getCapsules(self.state):
            #         distocap = self.captureAgent.getBlockedDistance(self.state,self.position, capsule)
            #         if distocap < 5000:
            #             h += -distocap
            #             i += 1
            #     if i == 0:
            #         h = -100 * self.captureAgent.getBlockedDistance(self.state,self.position, self.captureAgent.start)
            #     for food in self.captureAgent.getFood(self.state):
            #         if food in self.captureAgent.goodFood:
            #             h += -self.captureAgent.getBlockedDistance(self.state, self.position, food)
            # else:
            #     h = math.pow(0.9, (self.captureAgent.getBlockedDistance(self.state,self.position, self.captureAgent.start)))
            #     for food in self.captureAgent.getFood(self.state):
            #         if food in self.captureAgent.goodFood:
            #             h += -self.captureAgent.getBlockedDistance(self.state, self.position, food)
        elif self.captureAgent.status == self.captureAgent.defense:
            # h += 1 + math.pow(0.9, self.captureAgent.getMazeDistance(self.captureAgent.food, self.state.getAgentPosition(self.index)))
            for rewardPosition in self.rewardList.keys():
                h += self.rewardList[rewardPosition] * math.pow(0.3, self.captureAgent.getMazeDistance(rewardPosition,
                                                                                        self.position))
        elif self.captureAgent.status == self.captureAgent.offense:
            if self.captureAgent.save:
                if len(self.captureAgent.getCapsules(self.state)) > 0:
                    peerDis = self.captureAgent.distanceToCapsule(self.state, peerPosition, self.captureAgent.getCapsules(self.state))
                    if peerDis > 5000:
                        h = - 300 * len(self.captureAgent.getCapsules(self.state)) - self.captureAgent.distanceToCapsule(self.state, self.position, self.captureAgent.getCapsules(self.state))
                        print("dis")
                        print(h)
                        return h
            for rewardPosition in self.rewardList.keys():
                h += -len(self.captureAgent.getFood(self.state).asList()) + self.rewardList[rewardPosition] * math.pow(0.9, self.captureAgent.getMazeDistance(rewardPosition,
                                                                                        self.position))
                # h = -len(self.captureAgent.getFood(self.state).asList()) + math.pow(0.9, self.captureAgent.getMazeDistance(self.position, self.captureAgent.food))



        # for rewardPosition in self.rewardList.keys():
        #     h += self.rewardList[rewardPosition] * math.pow(0.9, self.captureAgent.getMazeDistance(rewardPosition,
        #                                                                                            self.position)) * 0.5
        #     if self.rewardList[rewardPosition] < -5:
        #         opponents.append(rewardPosition)
        # if self.captureAgent.escape:
        #     if self.captureAgent.start in self.rewardList.keys():
        #         return math.pow(0.9, self.captureAgent.getMazeDistance(self.captureAgent.start, self.state.getAgentPosition(self.index)))
        #     if len(self.captureAgent.getCapsules(self.state)) > 0:
        #         for capsule in self.captureAgent.getCapsules(self.state):
        #             h += -0.1* self.captureAgent.getMazeDistance(capsule, self.state.getAgentPosition(self.index)) + math.pow(0.9, self.captureAgent.getMazeDistance(self.captureAgent.start, self.state.getAgentPosition(self.index)))
        #         for o in opponents:
        #             h += -self.captureAgent.getMazeDistance(o, self.state.getAgentPosition(self.index))
        #     else:
        #         h = math.pow(0.9, self.captureAgent.getMazeDistance(self.captureAgent.start, self.state.getAgentPosition(self.index)))
        return h

    def getChildrenPosition(self):
        self.childrenPosition = []
        for child in self.children:
            self.childrenPosition.append(child.position)

    def getReward(self):
        if self.position in self.rewardList.keys():
            self.reward = self.rewardList[self.position]
            self.value = self.reward
        return self.reward

    def getChild(self):
        self.getChildrenPosition()
        for action in self.legalActions:
            nextState = self.state.generateSuccessor(self.index, action)
            child = Node(nextState, self.rewardList, nextState.getAgentPosition(self.index), self.index,
                         self.captureAgent, self)
            if child.position not in self.childrenPosition:
                self.children.append(child)
                break
        return child

    def fullyExpanded(self):
        if self.legalActions.__len__() == self.children.__len__():
            return True
        return False

    def updateValue(self, reward):
        self.value += reward
        self.reward = reward

    def backPropagation(self):
        self.parent.updateValue(self.reward * 0.9)
        self.parent.visit()

    def getChildAction(self, child):
        return self.legalActions[self.children.index(child)]

    def selectBestChild(self):
        # for child in self.children:
        #         child.mctValue = child.value + math.sqrt(2 * math.log(child.visitedTimes)/float(child.visitedTimes))
        # print(self.children.__len__())
        # for child in self.children:
        #     print(child.heuristicToReward())
        values = [(child.value) for child in self.children]
        if len(values) == 0:
            return None

        maxValue = max(values)

        bestChild = random.choice([child for child, v in zip(self.children, values) if v == maxValue])

        return bestChild

    def selectValueChild(self):
        values = [(child.value * 0.0000001 + child.heuristicToReward() + self.nways * 0.0000000001) for child in self.children]
        # for child in self.children:
        #    print(child.value)
        for child in self.children:
            if child.position == self.position:
                me = child
        if len(values) == 0:
            return None
        maxValue = max(values)
        # print(values)

        bestChild = random.choice([child for child, v in zip(self.children, values) if v == maxValue])

        return bestChild