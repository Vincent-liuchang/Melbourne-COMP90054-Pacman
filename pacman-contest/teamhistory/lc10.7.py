# myTeam.py
# ----------

from captureAgents import CaptureAgent
import random, time, util
from game import Directions, Actions
import game
from util import nearestPoint

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
							 first = 'SmartOffense', second = 'SmartOffense'):
	"""
	This function should return a list of two agents that will form the
	team, initialized using firstIndex and secondIndex as their agent
	index numbers.
	"""
	return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########


class SmartOffense(CaptureAgent):
	"""
	The offensive agent uses q-learing to learn an optimal offensive policy 
	over hundreds of games/training sessions. The policy changes this agent's 
	focus to offensive features such as collecting pellets/capsules, avoiding ghosts, 
	maximizing scores via eating pellets etc.
	"""

	def registerInitialState(self, gameState):
		CaptureAgent.registerInitialState(self, gameState)
		self.init = gameState.getAgentState(self.index).getPosition()
		self.epsilon = 0.0#exploration prob
		self.alpha = 0.1 #learning rate
		self.discountRate = 0.8
		self.dangeFood = []
		self.mode = 1
		self.weights1 = {'closest-food': 2.35219445732408, 'bias': 2.579502234147277, 'closest-capsule': 2.473714473123398}
		self.weights2 = {'closest-food': 1.02910769618005556, 'bias': -6.112936837778204, 'closest-ghosts': -10.11587156566253, 'closest-capsule': 1.257363246901937, 'num-of-walls': -10.4903928122119086, 'time-of-scared-ghosts': 1.6265815562445105, 'reverse': -2.732599631268455}
		self.weights3 = {'bias': -0.1619191782335229, 'closest-ghosts': -18.645334316865307, 'num-of-walls': -10.45335435502801, 'distance-back-to-home': 2.0996715469522775, 'time-of-scared-ghosts': 0.7966612961334337, 'reverse': -2.732599631268455,'closest-capsule': 4.523232232232323}										
		self.weights4 = {'bias': 6.802602309336149, 'distance-back-to-home': 12.7541385540534}
		self.finish = False
		self.myAgents = CaptureAgent.getTeam(self, gameState)
		self.opAgents = CaptureAgent.getOpponents(self, gameState)
		self.myFoods = CaptureAgent.getFood(self, gameState).asList()
		self.opFoods = CaptureAgent.getFoodYouAreDefending(self, gameState).asList()
		self.lostFoods = []
		self.gamescore = 0

		self.midWidth = gameState.data.layout.width / 2
		self.height = gameState.data.layout.height
		self.width = gameState.data.layout.width
		self.midHeight = gameState.data.layout.height / 2
	
	def chooseAction(self,gameState):
		if self.mode ==1:
			self.updateLostFood(gameState)
			return self.chooseOfAction(gameState)
			
		else:
			print("mode22222222")
			return self.chooseDeAction(gameState)

	
	#------------------------------- mode2: defensive -------------------------------
	def getDeSuccessor(self, gameState, action):
		successor = gameState.generateSuccessor(self.index, action)
		pos = successor.getAgentState(self.index).getPosition()
		if pos != nearestPoint(pos):
			# Only half a grid position was covered
			return successor.generateSuccessor(self.index, action)
		else:
			return successor
	def nullHeuristic(self, state, problem=None):
		return 0
	def aStarSearch(self, problem, gameState, heuristic=nullHeuristic):
		"""Search the node that has the lowest combined cost and heuristic first."""
		from util import PriorityQueue
		start_state = problem.getStartState()
		fringe = PriorityQueue()
		h = heuristic(start_state, gameState)
		g = 0
		f = g + h
		start_node = (start_state, [], g)
		fringe.push(start_node, f)
		explored = []
		while not fringe.isEmpty():
			current_node = fringe.pop()
			state = current_node[0]
			path = current_node[1]
			current_cost = current_node[2]
			if state not in explored:
				explored.append(state)
				if problem.isGoalState(state):
					return path
				successors = problem.getSuccessors(state)
				for successor in successors:
					current_path = list(path)
					successor_state = successor[0]
					move = successor[1]
					g = successor[2] + current_cost
					h = heuristic(successor_state, gameState)
					if successor_state not in explored:
						current_path.append(move)
						f = g + h
						successor_node = (successor_state, current_path, g)
						fringe.push(successor_node, f)
						
		return []
	def GeneralHeuristic(self, state, gameState):
		heuristic = 0
		if self.getNearestGhostDistance(gameState) != None:
			enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
			# pacmans = [a for a in enemies if a.isPacman]
			ghosts = [a for a in enemies if not a.isPacman and a.scaredTimer < 2 and a.getPosition() != None]
			if ghosts != None and len(ghosts) > 0:
				ghostpositions = [ghost.getPosition() for ghost in ghosts]
				# pacmanPositions = [pacman.getPosition() for pacman in pacmans]
				ghostDists = [self.getMazeDistance(state, ghostposition) for ghostposition in ghostpositions]
				ghostDist = min(ghostDists)
				if ghostDist < 2:
					# print ghostDist
					heuristic = pow((5 - ghostDist), 5)
		return heuristic

	def distToHome(self, gameState):
		''''
		return the distance to nearest boudndary
		'''
		myState = gameState.getAgentState(self.index)
		myPosition = myState.getPosition()

		if self.red:
			i = self.midWidth - 1
		else:
			i = self.midWidth + 1
		boudaries = [(i, j) for j in range(self.height)]
		validPositions = []
		for i in boudaries:
			if not gameState.hasWall(int(i[0]), int(i[1])):
				validPositions.append(i)
		dist = 9999
		for validPosition in validPositions:
			tempDist = self.getMazeDistance(validPosition, myPosition)
			if tempDist < dist:
				dist = tempDist
				temp = validPosition
		return dist
	
	def getNearestGhostDistance(self, gameState):
		''''
		return the distance of the nearest ghost
		'''
		myPosition = gameState.getAgentState(self.index).getPosition()
		enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
		ghosts = [a for a in enemies if not a.isPacman and a.getPosition() != None]
		if len(ghosts) > 0:
			dists = [self.getMazeDistance(myPosition, a.getPosition()) for a in ghosts]
			return min(dists)
		else:
			return None


	# Returns a counter of features for the state
	def getDeFeatures(self, gameState, action):
		features = util.Counter()
		successor = self.getSuccessor(gameState, action)
		myState = successor.getAgentState(self.index)
		myPos = myState.getPosition()
		features['dead'] = 0

		# Computes whether we're on defense (1) or offense (0)
		features['onDefense'] = 1
		if myState.isPacman: features['onDefense'] = 0

		# Computes distance to invaders we can see
		enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
		invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
		features['numInvaders'] = len(invaders)
		if len(invaders) > 0 and gameState.getAgentState(self.index).scaredTimer > 0:
			dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
			features['invaderDistance'] = -1 / min(dists)

		if action == Directions.STOP: features['stop'] = 1
		rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
		if action == rev: features['reverse'] = 1
		features['DistToBoundary'] = - self.distToHome(successor)
		return features

		if gameState.isOnRedTeam(self.index):
			if successor.getAgentState(self.index) == (1, 1):
				features['dead'] = 1
		else:
			if successor.getAgentState(self.index) == (self.height - 1, self.width - 1):
				features['dead'] = 1

		return features
	def updateLostFood(self,gameState):
		currentFood = self.getFoodYouAreDefending(gameState).asList()		
		if len(self.opFoods) > len(currentFood):
			for each in self.opFoods:
				if each not in currentFood:
					self.opFoods.remove(each)
					self.lostFoods.append(each)
		if len(self.opFoods) < len(currentFood):
			for each in currentFood:
				if each not in self.opFoods:
					self.opFoods.append(each)
			self.lostFoods.clear()
		currentScore = gameState.getScore()
		if self.red:
			if currentScore< self.gamescore:
				self.lostFoods.clear()
		else:
			if currentScore> self.gamescore:
				self.lostFoods.clear()
		self.gamescore = gameState.getScore()
		

	# Returns a dictionary of features for the state
	def getDeWeights(self, gameState, action):
		return {'invaderDistance': 1000, 'onDefense': 200, 'stop': -100, 'reverse': -2, 'DistToBoundary': 1,'dead': -10000}

	# Computes a linear combination of features and feature weights
	def evaluate(self, gameState, action):
		features = self.getDeFeatures(gameState, action)
		weights = self.getDeWeights(gameState, action)
		return features * weights

	# Choose the best action for the current agent to take
	def chooseDeAction(self, gameState):

		actions = gameState.getLegalActions(self.index)
		values = [self.evaluate(gameState, a) for a in actions]
		enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]

		knowninvaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
		if len(knowninvaders) == 0 and len(self.lostFoods)>0 and gameState.getAgentState(
				self.index).scaredTimer < 5:
			min = 9999
			minAct = None
			for each in actions:
				nextState = self.getSuccessor(gameState,each)
				pos = nextState.getAgentPosition(self.index)
				dis = self.getMazeDistance(pos,self.lostFoods[-1])
				if min > dis:
					min = dis
					minAct = each
			return minAct
		# chase the invader only the distance is Known and ghost not scared
		if len(knowninvaders) > 0 and gameState.getAgentState(self.index).scaredTimer <5:
			problem = SearchInvaders(gameState, self, self.index)
			
			return self.aStarSearch(problem, gameState, self.GeneralHeuristic)[0]

		maxValue = max(values)
		bestActions = [a for a, v in zip(actions, values) if v == maxValue]
		return random.choice(bestActions)

	#------------------------------- mode1: offensive -------------------------------

	"""
	Iterate through all features (closest food, bias, ghost dist),
	multiply each of the features' value to the feature's weight,
	and return the sum of all these values to get the q-value.
	"""
	def getQValue(self, gameState, action):
		features = self.getFeatures(gameState, action)
		return(features * self.weights)

	"""
	Iterate through all q-values that we get from all
	possible actions, and return the highest q-value
	"""
	def getValue(self, gameState):
		qVals = []
		legalActions = gameState.getLegalActions(self.index)
		legalActions.remove(Directions.STOP)
		if len(legalActions) == 0:
			return 0.0
		else:
			for action in legalActions:
				qVals.append(self.getQValue(gameState, action))
			return max(qVals)

	"""
	Iterate through all q-values that we get from all
	possible actions, and return the action associated
	with the highest q-value.
	"""
	def getPolicy(self, gameState):
		values = []
		legalActions = gameState.getLegalActions(self.index)
		legalActions.remove(Directions.STOP)
		if len(legalActions) == 0:
			return None
		else:
			for action in legalActions:
				
				# self.updateWeights(gameState, action)
				values.append((self.getQValue(gameState, action), action))
		return max(values)[1]

	def getSafePolicy(self,gameState):
		values = []
		legalActions = gameState.getLegalActions(self.index)
		legalActions.remove(Directions.STOP)
		if len(legalActions) == 0:
			return None
		else:
			opAgents = self.getOpponents(gameState)
			dis = gameState.getAgentDistances()
			min = 100000
			pos = []
			scared = 0
			for op in opAgents:
				if not gameState.getAgentState(op).scaredTimer ==None:
					if gameState.getAgentState(op).scaredTimer>=0:
						scared = gameState.getAgentState(op).scaredTimer
				if min>dis[op]:
					min = dis[op]
				if not gameState.getAgentPosition(op) == None and not gameState.getAgentState(op).isPacman:
					pos.append(gameState.getAgentPosition(op) )
			# print(min)
			# if scared<10:		
				
			for action in legalActions:
				# print(self.getDeathRound(gameState,action),self.getDeathRoad(gameState,action))
				if len(pos)>0:
					distance = 100000
					for oppos in pos:
						if distance>self.getMazeDistance(gameState.getAgentPosition(self.index),oppos) :
							distance =self.getMazeDistance(gameState.getAgentPosition(self.index),oppos) 
					if distance > max(self.getDeathRound(gameState,action),self.getDeathRoad(gameState,action))*2 or scared>15 :
						
						values.append((self.getQValue(gameState, action), action))
					else:
						if max(self.getDeathRound(gameState,action),self.getDeathRoad(gameState,action))>9:
							food = self.getDeathFood(gameState,action)
							for each in food:
								if each[1]>5:
									self.dangeFood.append(each[0])
						nextState= self.getSuccessor(gameState,action)
						if not len(self.getFood(gameState).asList()) ==len(self.getFood(nextState).asList()):
							# self.updateWeights(gameState, action)
							values.append((self.getQValue(gameState, action), action))
				elif min<10 and scared<10:
					print("dangerous!!!!!!")	
					if max(self.getDeathRound(gameState,action),self.getDeathRoad(gameState,action))<3:
						# self.updateWeights(gameState, action)
						values.append((self.getQValue(gameState, action), action))
					else:
						if(self.getDeathRoad(gameState,action)>=8):
							food = self.getDeathFood(gameState,action)
							for each in food:
								if each[1]>5:
									self.dangeFood.append(each[0])
						nextState= self.getSuccessor(gameState,action)
						if not len(self.getFood(gameState).asList()) ==len(self.getFood(nextState).asList()):
							# self.updateWeights(gameState, action)
							values.append((self.getQValue(gameState, action), action))
				elif min<12 and scared<10:
					print("dangerous!!!!!!")	
					if max(self.getDeathRound(gameState,action),self.getDeathRoad(gameState,action))<5:
						# self.updateWeights(gameState, action)
						values.append((self.getQValue(gameState, action), action))
					else:
						if(self.getDeathRoad(gameState,action)>=8):
							food = self.getDeathFood(gameState,action)
							for each in food:
								if each[1]>6:
									self.dangeFood.append(each[0])
						nextState= self.getSuccessor(gameState,action)
						if not len(self.getFood(gameState).asList()) ==len(self.getFood(nextState).asList()):
							# self.updateWeights(gameState, action)
							values.append((self.getQValue(gameState, action), action))
				else:
					# self.updateWeights(gameState, action)
					if max(self.getDeathRound(gameState,action),self.getDeathRoad(gameState,action))<10 :
						# self.updateWeights(gameState, action)
						values.append((self.getQValue(gameState, action), action))
					else:
						if(self.getDeathRoad(gameState,action)>=10):
							food = self.getDeathFood(gameState,action)
							for each in food:
								if each[1]>6:
									self.dangeFood.append(each[0])
						nextState= self.getSuccessor(gameState,action)
						if not len(self.getFood(gameState).asList()) ==len(self.getFood(nextState).asList()):
							self.updateWeights(gameState, action)
					values.append((self.getQValue(gameState, action), action))				
		if len(values)>0:				
			return max(values)[1]
		else:
			return "Directions.STOP"		
	
	def chooseOfAction(self, gameState):
		# Pick Action
		ghost=[]
		ghostIndex = 0
		opAgents = CaptureAgent.getOpponents(self,gameState)
		currentPos = gameState.getAgentPosition(self.index)
		# Get ghost locations and states if observable
		if opAgents:
			for opponent in opAgents:
				opPos = gameState.getAgentPosition(opponent)
				opIsPacman = gameState.getAgentState(opponent).isPacman
				
				if opPos and not opIsPacman: 
					dis = abs(currentPos[0]-opPos[0])+abs(currentPos[1]-opPos[1])
					if dis<=6:
						ghost.append(opPos)
						ghostIndex = opponent
		if   len(self.getFood(gameState).asList())>2:
			
			if len(ghost) ==0 :
				if gameState.getAgentState(self.index).numCarrying>1 and  gameState.data.timeleft<200:
					self.weights =self.weights4
				else:
					self.weights = self.weights1

			else:

				if min([self.getMazeDistance(gameState.getAgentPosition(self.index),a) for a in ghost])>6:
					self.weights = self.weights1

				else:
					if gameState.getAgentState(ghostIndex).scaredTimer<10:
						if gameState.data.timeleft<200 :
							if gameState.getAgentState(self.index).numCarrying>2:
								self.weights = self.weights3
								print("33333333333333333333")
							else:
								self.weights = self.weights2
								print("2222222222222222222222")
						else:
							if gameState.getAgentState(self.index).numCarrying>10:
								if self.red:
									middle = int((gameState.data.layout.width - 2)/2 )
								else:
									middle = int((gameState.data.layout.width - 2)/2 + 1)
								if abs(gameState.getAgentPosition(self.index)[0]-middle) < middle/2:
									self.weights = self.weights3
									print("33333333333333333333")
								else :
									self.weights = self.weights2
									print("2222222222222222222222")
							else:
								self.weights = self.weights2
								print("2222222222222222222222")
					else :
						self.weights = self.weights1

		else :
			if len(ghost) ==0:
				self.weights = self.weights4
				print("44444444444444444444")
			else:
				if gameState.getAgentState(ghostIndex).scaredTimer<10:
					self.weights = self.weights3
					print("33333333333333333333")
				else: 
					self.weights = self.weights4
					print("44444444444444444444")
		legalActions = gameState.getLegalActions(self.index)
		legalActions.remove(Directions.STOP)
		
		action = None

		if len(legalActions) != 0:
			prob = util.flipCoin(self.epsilon)
			if prob:
				action = random.choice(legalActions)

			else:
				if self.weights ==self.weights1:
					action = self.getSafePolicy(gameState)
			
				else:
					action = self.getPolicy(gameState)

		if self.weights == self.weights2 or self.weights == self.weights3:

			walls = self.getFeatures(gameState,action)["num-of-walls"]
			distance = self.getFeatures(gameState,action)["closest-ghosts"]
			print(self.index,walls*100,distance*100)
		if not gameState.getAgentState(self.index).isPacman:
			if self.red:
				if gameState.getScore()>5 and self.finish:
					self.mode =2 
			else:
				if gameState.getScore()<-5 and self.finish:
					self.mode = 2
		return action
	
	
	#------------------------------ Features And Weights --------------------------------
	def reverseDirection(self,action):
		if action == Directions.NORTH:
			return Directions.SOUTH
		if action == Directions.SOUTH:
			return Directions.NORTH
		if action == Directions.EAST:
			return Directions.WEST
		if action == Directions.WEST: 
			return Directions.EAST
		return action
	
	def WhetherCapsule(self,gameState,action):

		nextState = self.getSuccessor(gameState,action)
		legalActions = nextState.getLegalActions(self.index)
		legalActions.remove(Directions.STOP)
		if(self.reverseDirection(action) in legalActions):
			legalActions.remove(self.reverseDirection(action))
		
		if len(legalActions) ==0:
			return False
		elif not len(self.getCapsules(gameState)) ==len(self.getCapsules(nextState)):
			return True
		else :
			next = self.WhetherCapsule(nextState,legalActions[0])
			return next
	def getDeathRound(self,gameState,action):
		walls = gameState.getWalls()
		pos = gameState.getAgentPosition(self.index)
		explored = []
		explored.append(pos)
		states = util.Queue()
		stateTuple = (gameState,action)
		states.push(stateTuple)
		length = 0
		
		while not states.isEmpty():
			# print("start a new round")
			if(length>10):
				return 0
			else :
				gameState, action = states.pop()
				nextState = self.getSuccessor(gameState,action)
				if nextState.getAgentPosition(self.index) not in walls and nextState.getAgentPosition(self.index) not in explored:
					explored.append(nextState.getAgentPosition(self.index))
					length +=1
					actions = nextState.getLegalActions(self.index)
					# print(action,self.reverseDirection(action))
					actions.remove(Directions.STOP)
					if self.reverseDirection(action) in actions:
						actions.remove(self.reverseDirection(action))
					# print(len(actions),"Action length!!!!!!!")
					if(len(actions)>0):
						for each in actions:
							nextTuple = (nextState,each)
							states.push(nextTuple)
					# print(len(states.list),"states length!!!!!!!")
				else :
					continue
		
		return length
		
	def getDeathRoad(self,gameState,action):
		nextState = self.getSuccessor(gameState,action)
		legalActions = nextState.getLegalActions(self.index)
		legalActions.remove(Directions.STOP)
		
		if(self.reverseDirection(action) in legalActions):
			legalActions.remove(self.reverseDirection(action))
		if len(legalActions)==0:
			return 1
		elif len(legalActions)>=2:
			return 0
		else :
			next = self.getDeathRoad(nextState,legalActions[0])
			if next ==0:
				return 0
			else: 
				return next+1
	def getDeathFood(self,gameState,action):
		foodList = self.getFood(gameState).asList()
		nextState = self.getSuccessor(gameState,action)
		legalActions = nextState.getLegalActions(self.index)
		legalActions.remove(Directions.STOP)
		Food = []
		if(self.reverseDirection(action) in legalActions):
			legalActions.remove(self.reverseDirection(action))
		
		if len(legalActions) ==0:
			return Food
		else :
			next = self.getDeathFood(nextState,legalActions[0])

			if not len(next) ==0:
				next[:] = [(a,b+1) for (a,b) in next]
			if nextState.getAgentPosition(self.index) in foodList:
				next.append((nextState.getAgentPosition(self.index),0))
		return next


	def getFirstFeatures(self, gameState, action):
		nextState = self.getSuccessor(gameState, action)
			
		food = self.getFood(gameState)
		nextfood = self.getFood(nextState)
		walls = gameState.getWalls()

		self.ghosts = []
		
		features = util.Counter()
		
		features["bias"] = 1.0
		op = self.getOpponents(gameState)
		scared = [gameState.getAgentState(ops).scaredTimer for ops in op]
		minScare = min(scared)
		if minScare< 10:
			eat = 1
		else:
			eat = -1
		if eat>0:
			if(len(self.getCapsules(nextState))>1):
				if len(self.getCapsules(gameState))==len(self.getCapsules(nextState))+1:
					features['closest-capsule']=2.0
				else:
					minCap = 10000
					for each in self.getCapsules(nextState):
						if minCap > self.getMazeDistance(nextState.getAgentPosition(self.index),each):
							minCap = self.getMazeDistance(nextState.getAgentPosition(self.index),each)
					features['closest-capsule'] = 1.0/minCap
			elif(len(self.getCapsules(nextState))==1): 
				if len(self.getCapsules(gameState))==2:
					features['closest-capsule']=2.0
				else:
					features['closest-capsule'] = 1.0/self.getMazeDistance(nextState.getAgentPosition(self.index),self.getCapsules(gameState)[0])*eat
			else: 
				if(len(self.getCapsules(gameState))>0):
					features['closest-capsule']=2.0
				else :
					features['closest-capsule']=0.0
		else:
			features['closest-capsule']=0.0
		# Closest food
		# if len()
		if self.index ==self.getTeam(gameState)[0]:
			dist = self.halfUpperClosestFood(nextState.getAgentPosition(self.index), nextfood, walls,nextState)
			if len(food.asList()) == len(nextfood.asList() ) and not dist ==0:
				# make the distance a number less than one otherwise the update
				# will diverge wildly
				features["closest-food"] = 1.0/float(dist)
				# print("The distance is",dist)
			else : 
				features["closest-food"] = 2
		else:
			dist = self.halfLowerClosestFood(nextState.getAgentPosition(self.index), nextfood, walls,nextState)
			if len(food.asList()) == len(nextfood.asList() ) and not dist ==0:
				# make the distance a number less than one otherwise the update
				# will diverge wildly
				features["closest-food"] = 1.0/float(dist)
				# print("The distance is",dist)
			else : 
				features["closest-food"] = 2
		
		features.divideAll(100)
		return features

	def getSecondFeatures(self, gameState, action):
		nextState = self.getSuccessor(gameState, action)
		
		food = self.getFood(gameState)
		nextfood = self.getFood(nextState)
		walls = gameState.getWalls()
		ghost=[]
		self.ghosts = []
		opAgents = CaptureAgent.getOpponents(self,nextState)
		# Get ghost locations and states if observable
		if opAgents:
			for opponent in opAgents:
				opPos = nextState.getAgentPosition(opponent)
				opIsPacman = nextState.getAgentState(opponent).isPacman
				if opPos and not opIsPacman: 
					currentPos = gameState.getAgentPosition(self.index)
					nopPos = gameState.getAgentPosition(opponent)
					dis = abs(currentPos[0]-nopPos[0])+abs(currentPos[1]-nopPos[1])
					if dis<= 5:
						ghost.append(opPos)
						ghost.append(opponent)
						self.ghosts.append(ghost)
		
		# Initialize features
		features = util.Counter()
		reverse = self.reverseDirection(action)
		if reverse == gameState.getAgentState(self.index).configuration.direction:
			features["reverse"]=1
			# print("reverse")
		else:
			features["reverse"]=0
			# print("notreverse")
		features["bias"] = 1.0
		legalActions = nextState.getLegalActions(self.index)
		legalActions.remove(Directions.STOP)
		features['num-of-walls'] = max(self.getDeathRoad(gameState,action),self.getDeathRound(gameState,action))
		if(self.getDeathRoad(gameState,action)>=8):
			deathfood = self.getDeathFood(gameState,action)
			for each in deathfood:
				if each[1]>5:
					self.dangeFood.append(each[0])
		# compute the location of pacman after he takes the action
		
		
		if len(self.ghosts)==0:
			# print("0000000000000000000000000")
			features['time-of-scared-ghosts']=0
			features['closest-ghosts']=0
			self.scareTimer = 0
		else:
			features['time-of-scared-ghosts'] = min(nextState.getAgentState(opponent).scaredTimer for opponent in opAgents)

			if(min(nextState.getAgentState(opponent).scaredTimer for opponent in opAgents)>10):
				self.scareTimer = 1
				features['time-of-scared-ghosts']=1

			else:
				features['time-of-scared-ghosts']=0

				self.scareTimer = 0
			# print("next",nextState.getAgentState(self.ghosts[0][1]).getPosition()[0],"   inital",nextState.getInitialAgentPosition(self.ghosts[0][1])[0])	
		
			if len(self.ghosts)==1:
				ghostIndex = self.ghosts[0][1]
				pos = gameState.getAgentState(ghostIndex).getPosition()
				nextpos = nextState.getAgentState(ghostIndex).getPosition()
				posDis = self.getMazeDistance(gameState.getAgentState(self.index).getPosition(),pos)
				nextDis = self.getMazeDistance(nextState.getAgentState(self.index).getPosition(),nextpos)
				if abs(posDis-nextDis)>5:
					# print("!!!!!!!!!!!!!!!!!!!!!!!!!!")
					features['closest-ghosts'] = 2 
					# print("222222222222222222222")
				else :
					# print("333333333333333333")
					
					features['closest-ghosts'] = 1.0/self.getMazeDistance(nextState.getAgentPosition(self.index),self.ghosts[0][0])
			else:
				ghostIndex1 = self.ghosts[0][1]
				pos1 = gameState.getAgentState(ghostIndex1).getPosition()
				nextpos1 = nextState.getAgentState(ghostIndex1).getPosition()
				ghostIndex2 = self.ghosts[1][1]
				pos2 = gameState.getAgentState(ghostIndex2).getPosition()
				nextpos2 = nextState.getAgentState(ghostIndex2).getPosition()
				posDis1 = self.getMazeDistance(gameState.getAgentState(self.index).getPosition(),pos1)
				nextDis1 = self.getMazeDistance(nextState.getAgentState(self.index).getPosition(),nextpos1)
				posDis2 = self.getMazeDistance(gameState.getAgentState(self.index).getPosition(),pos2)
				nextDis2 = self.getMazeDistance(nextState.getAgentState(self.index).getPosition(),nextpos2)
				if abs(posDis1-nextDis1)>5 or abs(posDis2-nextDis2)>5:
					# print("!!!!!!!!!!!!!!!!!!!!!!!!!!")
					features['closest-ghosts'] = 2 
					# print("222222222222222222222")
				else :
					# print("333333333333333333")
					if posDis1==posDis2:
						features['closest-ghosts'] = 1.0/(nextDis1+nextDis2)*2
					else:
						features['closest-ghosts'] = 1.0/min(nextDis1,nextDis2)

		if(len(self.getCapsules(nextState))>1):
			if len(self.getCapsules(gameState))==len(self.getCapsules(nextState))+1:
				features['closest-capsule']=2.0
			else:
				minCap = 10000
				for each in self.getCapsules(nextState):
					if minCap > self.getMazeDistance(nextState.getAgentPosition(self.index),each):
						minCap = self.getMazeDistance(nextState.getAgentPosition(self.index),each)
				features['closest-capsule'] = 1.0/minCap
		elif(len(self.getCapsules(nextState))==1): 
			if len(self.getCapsules(gameState))==2:
				features['closest-capsule']=2.0
			else:
				features['closest-capsule'] = 1.0/self.getMazeDistance(nextState.getAgentPosition(self.index),self.getCapsules(gameState)[0])
		else: 
			if(len(self.getCapsules(gameState))>0):
				features['closest-capsule']=2.0
			else :
				features['closest-capsule']=0.0
		# Closest food
		# if len()
		if self.index ==self.getTeam(gameState)[0]:
			dist = self.halfUpperClosestFood(nextState.getAgentPosition(self.index), nextfood, walls,nextState)
			if len(food.asList()) == len(nextfood.asList() ) and not dist ==0:
				# make the distance a number less than one otherwise the update
				# will diverge wildly
				features["closest-food"] = 1.0/float(dist)
				# print("The distance is",dist)
			else : 
				features["closest-food"] = 2
		else:
			dist = self.halfLowerClosestFood(nextState.getAgentPosition(self.index), nextfood, walls,nextState)
			if len(food.asList()) == len(nextfood.asList() ) and not dist ==0:
				# make the distance a number less than one otherwise the update
				# will diverge wildly
				features["closest-food"] = 1.0/float(dist)
				# print("The distance is",dist)
			else : 
				features["closest-food"] = 2
		
		
		features.divideAll(100)
		return features
	
	def getThirdFeatures(self, gameState, action):
		nextState = self.getSuccessor(gameState, action)
			

		ghost=[]
		self.ghosts = []
		opAgents = CaptureAgent.getOpponents(self,nextState)
		# Get ghost locations and states if observable
		if opAgents:
			for opponent in opAgents:
				opPos = nextState.getAgentPosition(opponent)
				opIsPacman = nextState.getAgentState(opponent).isPacman
				if opPos and not opIsPacman: 
					currentPos = gameState.getAgentPosition(self.index)
					nopPos = gameState.getAgentPosition(opponent)
					dis = abs(currentPos[0]-nopPos[0])+abs(currentPos[1]-nopPos[1])
					if dis<= 5:
						ghost.append(opPos)
						ghost.append(opponent)
						self.ghosts.append(ghost)
					
		# Initialize features
		features = util.Counter()
		reverse = self.reverseDirection(action)
		if reverse == gameState.getAgentState(self.index).configuration.direction:
			features["reverse"]=1
			# print("reverse")
		else:
			features["reverse"]=0
			# print("notreverse")
		# features['num-of-carry']  = nextState.getAgentState(self.index).numCarrying
		if self.red:
			self.middle = int((gameState.data.layout.width - 2)/2 )
		else:
			self.middle = int((gameState.data.layout.width - 2)/2 + 1)
		self.boundary = []
		for i in range(1, gameState.data.layout.height - 1):
			if not gameState.hasWall(self.middle, i):
				self.boundary.append((self.middle, i))
		if gameState.getAgentState(self.index):
			
			distance_to_boundary = 10000
			for each in self.boundary:
				distance = self.getMazeDistance(nextState.getAgentPosition(self.index),each)
				if distance<distance_to_boundary:
					distance_to_boundary = distance
			if distance_to_boundary ==0:
				features['distance-back-to-home']=2
			else :
				features['distance-back-to-home'] = 1.0/distance_to_boundary
		else : 
			features['distance-back-to-home'] = 0

		# Bias
		features["bias"] = 1.0
		legalActions = nextState.getLegalActions(self.index)
		legalActions.remove(Directions.STOP)
		features['num-of-walls'] = max(self.getDeathRoad(gameState,action),self.getDeathRound(gameState,action))
		# compute the location of pacman after he takes the action
		if(self.getDeathRoad(gameState,action)>=8):
			food = self.getDeathFood(gameState,action)
			for each in food:
				if each[1]>5:
					self.dangeFood.append(each[0])
		

		if(len(self.getCapsules(nextState))>1):
			if len(self.getCapsules(gameState))==len(self.getCapsules(nextState))+1:
				features['closest-capsule']=2.0
			else:
				minCap = 10000
				for each in self.getCapsules(nextState):
					if minCap > self.getMazeDistance(nextState.getAgentPosition(self.index),each):
						minCap = self.getMazeDistance(nextState.getAgentPosition(self.index),each)
				features['closest-capsule'] = 1.0/minCap
		elif(len(self.getCapsules(nextState))==1): 
			if len(self.getCapsules(gameState))==2:
				features['closest-capsule']=2.0
			else:
				features['closest-capsule'] = 1.0/self.getMazeDistance(nextState.getAgentPosition(self.index),self.getCapsules(gameState)[0])
		else: 
			if(len(self.getCapsules(gameState))>0):
				features['closest-capsule']=2.0
			else :
				features['closest-capsule']=0.0

		if len(self.ghosts)==0:
			features['time-of-scared-ghosts']=0
			features['closest-ghosts']=0
			self.scareTimer = 0
		else:
			features['time-of-scared-ghosts'] = min(nextState.getAgentState(opponent).scaredTimer for opponent in opAgents)

			if(min(nextState.getAgentState(opponent).scaredTimer for opponent in opAgents)>10):
				self.scareTimer = 1
				features['time-of-scared-ghosts']=1

			else:
				features['time-of-scared-ghosts']=0

				self.scareTimer = 0
			if len(self.ghosts)==1:
				ghostIndex = self.ghosts[0][1]
				pos = gameState.getAgentState(ghostIndex).getPosition()
				nextpos = nextState.getAgentState(ghostIndex).getPosition()
				posDis = self.getMazeDistance(gameState.getAgentState(self.index).getPosition(),pos)
				nextDis = self.getMazeDistance(nextState.getAgentState(self.index).getPosition(),nextpos)
				if abs(posDis-nextDis)>5:
					# print("!!!!!!!!!!!!!!!!!!!!!!!!!!")
					features['closest-ghosts'] = 2 
					# print("222222222222222222222")
				else :
					# print("333333333333333333")
					
					features['closest-ghosts'] = 1.0/self.getMazeDistance(nextState.getAgentPosition(self.index),self.ghosts[0][0])
			else:
				ghostIndex1 = self.ghosts[0][1]
				pos1 = gameState.getAgentState(ghostIndex1).getPosition()
				nextpos1 = nextState.getAgentState(ghostIndex1).getPosition()
				ghostIndex2 = self.ghosts[1][1]
				pos2 = gameState.getAgentState(ghostIndex2).getPosition()
				nextpos2 = nextState.getAgentState(ghostIndex2).getPosition()
				posDis1 = self.getMazeDistance(gameState.getAgentState(self.index).getPosition(),pos1)
				nextDis1 = self.getMazeDistance(nextState.getAgentState(self.index).getPosition(),nextpos1)
				posDis2 = self.getMazeDistance(gameState.getAgentState(self.index).getPosition(),pos2)
				nextDis2 = self.getMazeDistance(nextState.getAgentState(self.index).getPosition(),nextpos2)
				if abs(posDis1-nextDis1)>5 or abs(posDis2-nextDis2)>5:
					# print("!!!!!!!!!!!!!!!!!!!!!!!!!!")
					features['closest-ghosts'] = 2 
					# print("222222222222222222222")
				else :
					# print("333333333333333333")	
					if posDis1==posDis2:
						features['closest-ghosts'] = 1.0/(nextDis1+nextDis2)*2
					else:
						features['closest-ghosts'] = 1.0/min(nextDis1,nextDis2)
		
		features.divideAll(100)
		return features

	def getFourthFeatures(self, gameState, action):
		nextState = self.getSuccessor(gameState, action)
				
		# Initialize features
		features = util.Counter()
		# features['num-of-carry']  = nextState.getAgentState(self.index).numCarrying
		if self.red:
			self.middle = int((gameState.data.layout.width - 2)/2 )
		else:
			self.middle = int((gameState.data.layout.width - 2)/2 + 1)
		self.boundary = []
		for i in range(1, gameState.data.layout.height - 1):
			if not gameState.hasWall(self.middle, i):
				self.boundary.append((self.middle, i))
		if gameState.getAgentState(self.index):
			
			distance_to_boundary = 10000
			for each in self.boundary:
				distance = self.getMazeDistance(nextState.getAgentPosition(self.index),each)
				if distance<distance_to_boundary:
					distance_to_boundary = distance
			if distance_to_boundary ==0:
				features['distance-back-to-home']=2
			else :
				features['distance-back-to-home'] = 1.0/distance_to_boundary
		else : 
			features['distance-back-to-home'] = 0
		
		# Bias
		features["bias"] = 1.0		
		features.divideAll(100)
		return features	
	# Define features to use. NEEDS WORK	
	def getFeatures(self, gameState, action):
		# Extract the grid of food and wall locations
		if self.weights == self.weights1:
			return self.getFirstFeatures(gameState, action)
		elif self.weights == self.weights2:
			return self.getSecondFeatures(gameState, action)
		elif self.weights == self.weights3:
			return self.getThirdFeatures(gameState, action)
		else:
			return self.getFourthFeatures(gameState, action)
			

	"""
	Iterate through all features and for each feature, update
	its weight values using the following formula:
	w(i) = w(i) + alpha((reward + discount*value(nextState)) - Q(s,a)) * f(i)(s,a)
	"""

	def getRewards(self,gameState,nextState):
		
		if self.weights == self.weights2:
			# print("length!!!!!!!!",len(self.ghosts))
			reward = 0
			if(nextState.getAgentState(self.index).getPosition() in self.getFood(gameState).asList()):
				print("Eating a food!!!")
				reward +=2

			if len(self.ghosts)>0:
				ghostPosition = self.ghosts[0][0]
				ghostIndex = self.ghosts[0][1]
				if self.scareTimer == 0:
					if self.getMazeDistance(nextState.getAgentState(self.index).getPosition(),ghostPosition)<=1 or nextState.getAgentState(self.index).getPosition()[0]==self.init[0]:

						reward +=-3
						
						
						print("Being eaten")
				else :
					print(self.scareTimer,"!!!!!!!!!!")
					pos = gameState.getAgentState(ghostIndex).getPosition()
					nextpos = nextState.getAgentState(ghostIndex).getPosition()
					posDis = self.getMazeDistance(gameState.getAgentState(self.index).getPosition(),pos)
					nextDis = self.getMazeDistance(nextState.getAgentState(self.index).getPosition(),nextpos)
					print(posDis,nextDis)
					if self.getMazeDistance(nextState.getAgentState(self.index).getPosition(),ghostPosition)<=1 or abs(posDis-nextDis)>5:
						
						print("Eating others")
						reward +=3
			# print(nextState.getAgentState(self.index).getPosition(),self.getCapsules(gameState)[0])
			if len(self.getCapsules(gameState)):
				if (nextState.getAgentState(self.index).getPosition() == self.getCapsules(gameState)[0]) :
					print("Eating a capsule!!!")
					reward+=3
			# print(reward,"\n")
			return reward
		elif self.weights==self.weights1:
			reward = 0
			if(nextState.getAgentState(self.index).getPosition() in self.getFood(gameState).asList()):
				print("Eating a food!!!")
				reward +=2

			
			if len(self.getCapsules(gameState)):
				if (nextState.getAgentState(self.index).getPosition() == self.getCapsules(gameState)[0]) :
					print("Eating a capsule!!!")
					reward+=3
			# print(reward,"\n")
			return reward
		elif self.weights ==self.weights3:
			reward = 0
		
			if abs(nextState.getScore() - gameState.getScore())>0:
				reward += 2
				print("Score ",reward, " Points!!!" )
			if len(self.ghosts)>0:
				ghostPosition = self.ghosts[0][0]
				ghostIndex = self.ghosts[0][1]
				
				print("scareTimer!!!!!",self.scareTimer)
				if self.scareTimer == 0:
					if self.getMazeDistance(nextState.getAgentState(self.index).getPosition(),ghostPosition)<=1 or nextState.getAgentState(self.index).getPosition()==self.init:

						reward +=-3
						
						
						print("Being eaten")
				else :
					pos = gameState.getAgentState(ghostIndex).getPosition()
					nextpos = nextState.getAgentState(ghostIndex).getPosition()
					posDis = self.getMazeDistance(gameState.getAgentState(self.index).getPosition(),pos)
					nextDis = self.getMazeDistance(nextState.getAgentState(self.index).getPosition(),nextpos)

					if self.getMazeDistance(nextState.getAgentState(self.index).getPosition(),ghostPosition)<=2 or abs(posDis-nextDis)>5:
						
						print("Eating others")
						reward +=3
			return reward
		else:
			reward = 0
		
			if abs(nextState.getScore() - gameState.getScore())>0:
				reward +=abs(nextState.getScore() - gameState.getScore())
				print("Score ",reward, " Points!!!" )
			return reward
	def updateWeights(self, gameState, action):
		features = self.getFeatures(gameState, action)
		nextState = self.getSuccessor(gameState, action)

		reward = self.getRewards(gameState,nextState)

		for feature in features:
			correction = (reward + self.discountRate*self.getValue(nextState)) - self.getQValue(gameState, action)
			self.weights[feature] = self.weights[feature] + self.alpha*correction * features[feature]
	
	#-------------------------------- Helper Functions ----------------------------------

	# Finds the next successor which is a grid position (location tuple).
	def getSuccessor(self, gameState, action):
		successor = gameState.generateSuccessor(self.index, action)

		return successor

	def closestFood(self, pos, food, walls):
		foodList = food.asList()
		min = 100000
		for each in foodList:
			# print(pos,each)
			if each not in self.dangeFood:
				distance = self.getMazeDistance(pos,each)

				if distance<min:
					min = distance
		return min
	def halfUpperClosestFood(self, pos, food, walls,gameState):
		foodList = food.asList()
		left = 9999
		right = 9999
		for each in foodList:
			# print(pos,each)

			if(each[1]>=int(gameState.data.layout.height/2)) and each not in self.dangeFood:
				distance = self.getMazeDistance(pos,each)
				if self.red:
					if each[0]>self.width*0.7:
						if right>distance:
							right = distance
					if each[0]<self.width*0.8:
						if left>distance:
							left= distance
				else:
					if each[0]<self.width*0.3:
						if right>distance:
							right = distance
					if each[0]>self.width*0.2:
						if left>distance:
							left= distance

		if min(left,right) == 9999:
			self.finish = True
			team = self.getTeam(gameState)
			if team[0] == self.index:
				return self.getMazeDistance(pos,self.furthestFood(gameState.getAgentPosition(team[1]),food,walls,gameState))
			else:
				return self.getMazeDistance(pos,self.furthestFood(gameState.getAgentPosition(team[0]),food,walls,gameState))
			# return self.closestFood(pos,food,walls)
		elif left==9999:
		
			return right
		elif right==9999:
			return left
		else:
			if min(left,right)<10:
				return min(left,right)
			else:
				return left
	def halfLowerClosestFood(self, pos, food, walls,gameState):
		foodList = food.asList()
		left = 9999
		right = 9999
		for each in foodList:
			# print(pos,each)
			if(each[1]<int(gameState.data.layout.height/2)) and each not in self.dangeFood:
				distance = self.getMazeDistance(pos,each)
				if self.red:
					if each[0]>self.width*0.7:
						if right>distance:
							right = distance
					if each[0]<self.width*0.8:
						if left>distance:
							left= distance
				else:
					if each[0]<self.width*0.3:
						if right>distance:
							right = distance
					if each[0]>self.width*0.2:
						if left>distance:
							left= distance
		if min ==9999:
			self.finish = True
			team = self.getTeam(gameState)
			if team[0] == self.index:
				return self.getMazeDistance(pos,self.furthestFood(gameState.getAgentPosition(team[1]),food,walls,gameState))
			else:
				return self.getMazeDistance(pos,self.furthestFood(gameState.getAgentPosition(team[0]),food,walls,gameState))
			# return self.closestFood(pos,food,walls)
		elif left==9999:
		
			return right
		elif right==9999:
			return left
		else:
			if min(left,right)<10:
				return min(left,right)
			else:
				return left
	def furthestFood(self, pos, food, walls,gameState):
		foodList = food.asList()
		max = 0
		if self.weights == self.weights2:
			op = self.getOpponents(gameState)
			pos2 = [gameState.getAgentPosition(each) for each in op if not gameState.getAgentPosition(each)==None]
			dis = 1000000
			for each in pos2:
				if dis> self.getMazeDistance(pos,each):
					dis = self.getMazeDistance(pos,each)
					oppos = each

			if dis>=2:
				return  oppos
			else:
				return (int(gameState.data.layout.width/2),int(gameState.data.layout.height/2))
	
		for each in foodList:
			# print(pos,each)
			if each not in self.dangeFood:
				distance = self.getMazeDistance(pos,each)
				
				if distance>max:
					pos = each
					max = distance
		return pos

class PositionSearchProblem:
    """
    It is the ancestor class for all the search problem class.
    A search problem defines the state space, start state, goal test, successor
    function and cost function.  This search problem can be used to find paths
    to a particular point.
    """

    def __init__(self, gameState, agent, agentIndex=0, costFn=lambda x: 1):
        self.walls = gameState.getWalls()
        self.costFn = costFn
        self.startState = gameState.getAgentState(agentIndex).getPosition()
        # For display purposes
        self._visited, self._visitedlist, self._expanded = {}, [], 0  # DO NOT CHANGE

    def getStartState(self):
        return self.startState

    def isGoalState(self, state):

        util.raiseNotDefined()

    def getSuccessors(self, state):
        successors = []
        for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            x, y = state
            dx, dy = Actions.directionToVector(action)
            nextx, nexty = int(x + dx), int(y + dy)
            if not self.walls[nextx][nexty]:
                nextState = (nextx, nexty)
                cost = self.costFn(nextState)
                successors.append((nextState, action, cost))

        # Bookkeeping for display purposes
        self._expanded += 1  # DO NOT CHANGE
        if state not in self._visited:
            self._visited[state] = True
            self._visitedlist.append(state)

        return successors

    def getCostOfActions(self, actions):
        if actions == None: return 999999
        x, y = self.getStartState()
        cost = 0
        for action in actions:
            # Check figure out the next state and see whether its' legal
            dx, dy = Actions.directionToVector(action)
            x, y = int(x + dx), int(y + dy)
            if self.walls[x][y]: return 999999
            cost += self.costFn((x, y))
        return cost


class SearchInvaders(PositionSearchProblem):
    """
    Used to search capsule
    """

    def __init__(self, gameState, agent, agentIndex=0):
        # Store the food for later reference
        self.food = agent.getFood(gameState)
        self.capsule = agent.getCapsules(gameState)
        # Store info for the PositionSearchProblem (no need to change this)
        self.startState = gameState.getAgentState(agentIndex).getPosition()
        self.walls = gameState.getWalls()
        # self.lastEatenFood = agent.lostFoods[-1]
        self.costFn = lambda x: 1
        self._visited, self._visitedlist, self._expanded = {}, [], 0  # DO NOT CHANGE
        self.enemies = [gameState.getAgentState(agentIndex) for agentIndex in agent.getOpponents(gameState)]
        self.invaders = [a for a in self.enemies if a.isPacman and a.getPosition != None]
        if len(self.invaders) > 0:
            self.invadersPosition = [invader.getPosition() for invader in self.invaders]
        else:
            self.invadersPosition = None

    def isGoalState(self, state):
        # # the goal state is the location of invader
        return state in self.invadersPosition