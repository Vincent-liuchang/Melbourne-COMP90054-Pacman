import util
from captureAgents import CaptureAgent
import random

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
        self.setup(gameState)

    '''
    Your initialization code goes here, if you need any.
    '''
    def setup(self, gameState):
        self.myPosition = self.start
        self.cost = self.getMazeDistance(self.myPosition,self.start)
        self.foodLeft = len(self.getFood(gameState).asList())
        self.time = 0
        self.spotEnemy = False
        self.targetFood = random.choice(self.getFood(gameState).asList())

    def update(self, gameState):
        self.myPosition = gameState.getAgentPosition(self.index)
        self.cost = self.getMazeDistance(self.myPosition,self.start)
        self.time += 1
        self.foodLeft = len(self.getFood(gameState).asList())

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

    def getAllSuccessors(self, gameState):
        actions = gameState.getLegalActions(self.index)
        successors = []
        for action in actions:
            successors.append((self.getSuccessor(gameState, action),action))
        return successors

    def chooseAction(self, gameState):
        self.update(gameState)
        if self.spotEnemy:
            action = self.flee_action(gameState)
        else:
            action = self.eat_action(gameState)
        if self.foodLeft <= 2:
            action = self.chooseActionHome(gameState)
        return action

    def flee_action(self, gameState):
        return self.waStarSearch(gameState, self.foodHeuristic, self.targetFood)
    def eat_action(self, gameState):
        self.changeTargetFood(gameState)
        print(self.targetFood)
        return self.waStarSearch(gameState, self.foodHeuristic(gameState), self.targetFood)

    def changeTargetFood(self, gameState):
        if not self.getFood(gameState).asList() == []:
            while self.targetFood not in self.getFood(gameState).asList():
                self.targetFood = self.getNearstFood(gameState)


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

    # def final(self, gameState):

    def getHomeDistance(self, gameState):
        my_position = gameState.getAgentPosition(self.index)
        return self.getMazeDistance(my_position, self.start) + 1

    def getNearstFood(self, gameState):
        food_list = self.getFood(gameState).asList()
        food_distance = [9999]
        for x, y in food_list:
            food = tuple((x, y))
            food_distance.append(self.getMazeDistance(food, self.myPosition))
        return food_list[food_distance.index(min(food_distance))]

    def getAllFoodDistance(self, gameState):
        food_list = self.getFood(gameState).asList()
        food_distance = [9999]
        for x, y in food_list:
            food = tuple((x, y))
            food_distance.append(self.getMazeDistance(food, self.myPosition))
        return food_distance

    def getCapsuleDistance(self, gameState):
        ca_list = self.getCapsules(gameState)
        ca_distance = [9999]
        if ca_list != []:
            ca_distance = []
            for x, y in ca_list:
                ca = tuple((x, y))
                ca_distance.append(self.getMazeDistance(ca, self.myPosition))
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
                enermy_distance.append(9999)
        return enermy_distance

    def goBack(self, gamestate, successor):
        if abs(successor.getAgentState(self.index).numCarrying - successor.getAgentState(self.index).numCarrying) > 0 \
                and not successor.getAgentPosition(self.index) == successor.getInitialAgentPosition(self.index):
            return True
        return False

    def beEaten(self, gamestate, successor):
        if successor.getAgentPosition(self.index) == successor.getInitialAgentPosition(self.index) \
                and abs(self.getHomeDistance(gamestate)- self.getHomeDistance(successor)) > 1:
            return True
        return False

    def waStarSearch(self, gamestate, heuritic, goal):
        w = 2
        current_node = (gamestate, [], 0, w * heuritic)
        # (state, action, g(n), f(n))
        open_list = util.PriorityQueue()
        visited_list = {current_node[0]: current_node}

        while not current_node[0].getAgentPosition(self.index) == goal:
            successors = self.getAllSuccessors(current_node[0])
            for successor in successors:
                open_list.push((successor[0], current_node[1] + [successor[1]], current_node[2] + 1,
                                current_node[2] + 1 + w * heuritic),
                               current_node[2] + 1 + w * max(self.getAllFoodDistance(gamestate)))
            current_node = open_list.pop()
            while current_node[0] in visited_list:
                if current_node[2] < visited_list[current_node[0]][2]:
                    break
                current_node = open_list.pop()
            visited_list[current_node[0]] = current_node

        result = current_node[1]
        print(result)
        return result[0]


    def foodHeuristic(self, gameState):
        return max(self.getAllFoodDistance(gameState))




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

# "food": sum(self.getAllFoodDistance(successor))/(100*self.totalFoodNumber),
#                     "foodCarry": successor.getAgentState(self.index).numCarrying/self.totalFoodNumber,
#                     "foodLeft": len(self.getFood(successor).asList())/self.totalFoodNumber,
#                     "distanceHome": self.getHomeDistance(successor)/100,
#                     "capsule": min(self.getCapsuleDistance(successor))/100,
#                     "ghost": min(self.getEnemyPacmanDistance(successor))/100,