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
from game import Directions
import game

#################
# Team creation #
#################
position1 = 1


def createTeam(firstIndex, secondIndex, isRed,
               first='MonteCarloOffensiveAgent', second='MonteCarloDefensiveAgent'):
    """
    This function should return a list of two agents that will form the
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
    value = {}

    def registerInitialState(self, gameState):
        self.escape = False
        self.start = gameState.getAgentPosition(self.index)
        CaptureAgent.registerInitialState(self, gameState)
        self.food = None
        self.totalFood = len(self.getFood(gameState).asList())

        foodList = self.getFood(gameState).asList()
        self.chooseFood(foodList)


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
        else:
            if topFood[1] - position1[1] > position1[1] - bottomFood[1]:
                self.food = topFood
            else:
                self.food = bottomFood


    def chooseAction(self, gameState):
        """
        Picks among the actions with the highest Q(s,a).
        """
        self.walls = gameState.data.layout.walls
        self.defense = False
        self.reward = self.getReward(gameState)
        if self.food == None or self.getMazeDistance(self.food, gameState.getAgentPosition(self.index)) == 0:
            if len(self.getFood(gameState).asList()) > 0:
                self.chooseFood(self.getFood(gameState).asList())
            else:
                self.food = self.start
        foodLeft = len(self.getFood(gameState).asList())
        if foodLeft <= 2:
            self.escape = True
            self.reward[self.start] = 1000

        if self.reward.__len__() != 0 and not self.defense:
            gameState.data.layout.walls = self.walls
            root = Node(gameState, self.reward, gameState.getAgentPosition(self.index), self.index, self)
            self.food = None
            global position1
            position1 = 1
            # print(self.getPreviousObservation().getAgentPosition(self.index))
            return self.MCTSearch(root, 10)

        self.escape = False

        if gameState.getAgentState(self.index).scaredTimer == 0:
            if self.getPreviousObservation() != None:

                lastState = self.getPreviousObservation()

                lastFoodList = self.getFoodYouAreDefending(lastState).asList()
                currentFoodList = self.getFoodYouAreDefending(gameState).asList()

                lastTimer = self.getPreviousObservation().getAgentState(self.index).scaredTimer
                currentTimer = gameState.getAgentState(self.index).scaredTimer

                if len(lastFoodList) > len(currentFoodList):
                    for food in lastFoodList:
                        if food not in currentFoodList:
                            foodEaten = food

                    self.food = foodEaten

                if lastTimer == 0 and currentTimer > 0:
                    self.food = self.food = random.choice(self.getFood(gameState).asList())
            else:
                self.food = random.choice(self.getFood(gameState).asList())
        gameState.data.layout.walls = self.walls
        actions = gameState.getLegalActions(self.index)
        values = [-self.foodHeuristic(self.getSuccessor(gameState, a), self.food) for a in actions]
        if len(values) == 0:
            return "Stop"
        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]
        print(self.food)

        return random.choice(bestActions)

    def getReward(self, gameState):
        disOpponent = 0
        minDistance = 10000
        reward = {}
        for food in self.getFood(gameState).asList():
            fdis = self.getMazeDistance(gameState.getAgentPosition(self.index), food)
            if fdis < minDistance:
                minDistance = fdis
            if fdis <= 5:
                reward[food] = 1
        for capsule in self.getCapsules(gameState):
            if (self.getMazeDistance(gameState.getAgentPosition(self.index), capsule)) <= 5:
                reward[capsule] =  self.totalFood + 10 - self.getFoodYouAreDefending(
                        gameState).asList().__len__()

        for opponent in self.getOpponents(gameState):
            if gameState.getAgentPosition(opponent) != None:
                if (gameState.getAgentState(opponent).isPacman & (
                        not gameState.getAgentState(self.index).isPacman)) and self.getMazeDistance(
                    gameState.getAgentPosition(opponent),
                    gameState.getAgentPosition(self.index)) <= 5 and not gameState.getAgentState(
                    self.index).scaredTimer > 0:
                    reward[gameState.getAgentPosition(opponent)] = self.totalFood + 10 - self.getFoodYouAreDefending(
                        gameState).asList().__len__()
                    # x, y = gameState.getAgentPosition(self.index)
                    # gameState.data.layout.walls[x][y] = True
                    # self.walls = gameState.data.layout.walls
                    continue

                if (gameState.getAgentState(opponent).scaredTimer > 5 & gameState.getAgentState(self.index).isPacman):
                    continue
                elif ((not gameState.getAgentState(opponent).isPacman)) or ((
                        gameState.getAgentState(self.index).scaredTimer > 0 and not gameState.getAgentState(
                    self.index).isPacman)):

                    if self.getMazeDistance(gameState.getAgentPosition(opponent),
                                            gameState.getAgentPosition(self.index)) <= 5:
                        reward[gameState.getAgentPosition(opponent)] = -self.totalFood -10 + self.getFoodYouAreDefending(
                        gameState).asList().__len__()
                        if not gameState.getAgentState(self.index).isPacman:
                            self.defense = True
                        if (gameState.getAgentState(self.index).scaredTimer > 0 and not gameState.getAgentState(
                                self.index).isPacman):
                            continue
                        self.escape = True
                    x, y = gameState.getAgentPosition(opponent)

                    gameState.data.layout.walls[x][y] = True
                    gameState.data.layout.walls[x + 1][y] = True
                    gameState.data.layout.walls[x - 1][y] = True
                    gameState.data.layout.walls[x][y + 1] = True
                    gameState.data.layout.walls[x][y - 1] = True
                    self.walls = gameState.data.layout.walls

                # elif gameState.getAgentState(opponent).isPacman & gameState.getAgentState(self.index).isPacman:
                #     reward[gameState.getAgentPosition(opponent)] = self.totalFood - self.getFoodYouAreDefending(gameState).asList().__len__()
        return reward

    def foodHeuristic(self, gameState, food):
        fdis = self.getMazeDistance(gameState.getAgentPosition(self.index), food)

        return fdis

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
            return "Stop"
        return root.getChildAction(root.selectValueChild())


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
        # self.legalActions.remove('Stop')
        self.totalFood = 20
        self.foodCarrying = 0
        self.isPacman = self.state.getAgentState(self.index).isPacman

    def visit(self):
        self.visitedTimes += 1

    def heuristicToReward(self):
        h = 0
        for rewardPosition in self.rewardList.keys():
            h += self.rewardList[rewardPosition] * math.pow(0.9, self.captureAgent.getMazeDistance(rewardPosition,
                                                                                                   self.position)) * 0.5
        if self.captureAgent.escape:
            h = -self.captureAgent.getMazeDistance(self.captureAgent.start, self.state.getAgentPosition(self.index))
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

        values = [(child.value + child.heuristicToReward()) for child in self.children]

        for child in self.children:
            if child.position == self.position:
                me = child
        if len(values) == 0:
            return None

        maxValue = max(values)

        bestChild = random.choice([child for child, v in zip(self.children, values) if v == maxValue])

        return bestChild

    def selectValueChild(self):
        values = [(child.value + child.heuristicToReward()) for child in self.children]
        # for child in self.children:
        # print(child.value)
        for child in self.children:
            if child.position == self.position:
                me = child
        if len(values) == 0:
            return None
        maxValue = max(values)

        bestChild = random.choice([child for child, v in zip(self.children, values) if v == maxValue])

        return bestChild


class MonteCarloDefensiveAgent(MonteCarloOffensiveAgent):

    # def foodHeuristic(self, gameState, food):
    #      fdis = self.getMazeDistance(food, gameState.getAgentPosition(self.index))
    #      # if gameState.getAgentPosition(self.index) in self.getFoodYouAreDefending(gameState).asList() or food == None:
    #
    #
    #      return fdis

    def getReward(self, gameState):
        minDistance = 10000
        reward = {}
        for food in self.getFood(gameState).asList():
            fdis = self.getMazeDistance(gameState.getAgentPosition(self.index), food)
            if fdis < minDistance:
                minDistance = fdis
            if fdis <= 5:
                reward[food] = 1
        for capsule in self.getCapsules(gameState):
            if (self.getMazeDistance(gameState.getAgentPosition(self.index), capsule)) <= 5:
                reward[capsule] =  self.totalFood + 10 - self.getFoodYouAreDefending(
                        gameState).asList().__len__()

        for opponent in self.getOpponents(gameState):
            if gameState.getAgentPosition(opponent) != None:
                if (gameState.getAgentState(opponent).isPacman & (
                        not gameState.getAgentState(self.index).isPacman)) and self.getMazeDistance(
                    gameState.getAgentPosition(opponent),
                    gameState.getAgentPosition(self.index)) <= 5 and (not gameState.getAgentState(
                    self.index).scaredTimer > 0):
                    reward[gameState.getAgentPosition(opponent)] = self.totalFood + 10 - self.getFoodYouAreDefending(
                        gameState).asList().__len__()
                    continue

                if (gameState.getAgentState(opponent).scaredTimer > 5 & gameState.getAgentState(self.index).isPacman):
                    continue
                elif (not gameState.getAgentState(opponent).isPacman) or ((
                        gameState.getAgentState(self.index).scaredTimer > 0 and not gameState.getAgentState(
                    self.index).isPacman)):

                    if self.getMazeDistance(gameState.getAgentPosition(opponent),
                                            gameState.getAgentPosition(self.index)) <= 5:
                        if not gameState.getAgentState(self.index).isPacman:
                            self.defense = True

                        reward[gameState.getAgentPosition(opponent)] = -self.totalFood - 10 + self.getFoodYouAreDefending(
                        gameState).asList().__len__()
                        if (gameState.getAgentState(self.index).scaredTimer > 0 and not gameState.getAgentState(
                                self.index).isPacman):
                            continue
                        self.escape = True
                    x, y = gameState.getAgentPosition(opponent)

                    gameState.data.layout.walls[x][y] = True
                    gameState.data.layout.walls[x + 1][y] = True
                    gameState.data.layout.walls[x - 1][y] = True
                    gameState.data.layout.walls[x][y + 1] = True
                    gameState.data.layout.walls[x][y - 1] = True
                    self.walls = gameState.data.layout.walls

                # elif gameState.getAgentState(opponent).isPacman & gameState.getAgentState(self.index).isPacman:
                #     reward[gameState.getAgentPosition(opponent)] = self.totalFood - self.getFoodYouAreDefending(
                #         gameState).asList().__len__()
        return reward

    def chooseAction(self, gameState):
        """
        Picks among the actions with the highest Q(s,a).
        """
        self.walls = gameState.data.layout.walls
        actions = gameState.getLegalActions(self.index)

        self.defense = False
        self.reward = self.getReward(gameState)
        if self.food == None or self.getMazeDistance(self.food, gameState.getAgentPosition(self.index)) == 0:
                if len(self.getFood(gameState).asList()) > 0:
                    self.chooseFood(self.getFood(gameState).asList())
                else:
                    self.food = self.start
        foodLeft = len(self.getFood(gameState).asList())
        if foodLeft <= 2:
            self.escape = True
            self.reward[self.start] = 1000

        if self.reward.__len__() != 0 and not self.defense:

            gameState.data.layout.walls = self.walls
            root = Node(gameState, self.reward, gameState.getAgentPosition(self.index), self.index, self)
            # print(self.getPreviousObservation().getAgentPosition(self.index))
            self.food = None
            global position1
            position1 = 1
            return self.MCTSearch(root, 10)
        self.escape = False

        if gameState.getAgentState(self.index).scaredTimer == 0:
            if self.getPreviousObservation() != None:

                lastState = self.getPreviousObservation()

                lastFoodList = self.getFoodYouAreDefending(lastState).asList()
                currentFoodList = self.getFoodYouAreDefending(gameState).asList()

                lastTimer = self.getPreviousObservation().getAgentState(self.index).scaredTimer
                currentTimer = gameState.getAgentState(self.index).scaredTimer

                if len(lastFoodList) > len(currentFoodList):
                    for food in lastFoodList:
                        if food not in currentFoodList:
                            foodEaten = food

                    self.food = foodEaten

                if lastTimer == 0 and currentTimer > 0:
                    self.food = self.food = random.choice(self.getFood(gameState).asList())
            else:
                self.food = random.choice(self.getFood(gameState).asList())
        gameState.data.layout.walls = self.walls
        actions = gameState.getLegalActions(self.index)
        values = [-self.foodHeuristic(self.getSuccessor(gameState, a), self.food) for a in actions]
        if len(values) == 0:
            return "Stop"
        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]
        print(self.food)

        return random.choice(bestActions)