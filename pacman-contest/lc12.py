# myTeam.py
# ----------

from captureAgents import CaptureAgent
import random, time, util
from game import Directions, Actions
import game
from util import nearestPoint
import copy

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
		self.weights1 = {'closest-food': 2.35219445732408, 'bias': 2.579502234147277, 'closest-capsule': 2.3714473123398,"team":-0.1}
		self.weights2 = {'closest-food': 1.02910769618005556, 'bias': -6.112936837778204, 'closest-ghosts': -10.11587156566253, 'closest-capsule': 3.257363246901937, 'num-of-walls': -10.4903928122119086, 'time-of-scared-ghosts': 1.6265815562445105, 'reverse': -2.732599631268455}
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
		self.entrylist = self.getEntry(gameState)
		self.entry = random.choice(self.entrylist)
		self.noMove=[(1,1),0]
		scanmap = ScanMap(gameState, self)
		foodList = scanmap.getFoodList(gameState)
		self.safeFoods = scanmap.getSafeFoods(foodList)  # a list of tuple contains safe food location
		self.dangerFoods = scanmap.getDangerFoods(self.safeFoods)
		# (self.dangerFoods)

	
	def chooseAction(self,gameState):
		team = self.getTeam(gameState)
		if self.index == team[0]:
			self.mode = 1
		else:
			self.mode = 2
		if self.mode ==1:
			self.updateLostFood(gameState)
			return self.chooseOfAction(gameState)
			
		else:
			# ("mode22222222")
			# (self.chooseDeAction(gameState))
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
					#  ghostDist
					heuristic = pow((5 - ghostDist), 5)
		return heuristic
	def boundaryPosition(self, gameState):
		''''
		return a list of positions of boundary
		'''
		myState = gameState.getAgentState(self.index)
		myPosition = myState.getPosition()
		boundaries = []
		if self.red:
			i = self.midWidth - 1
		else:
			i = self.midWidth + 1
		boudaries = [(i, j) for j in range(self.height)]
		validPositions = []
		for i in boudaries:
			if not gameState.hasWall(int(i[0]), int(i[1])):
				validPositions.append(i)
		return validPositions
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
		self.updateLostFood(gameState)
		actions = gameState.getLegalActions(self.index)
		values = [self.evaluate(gameState, a) for a in actions]
		enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
		selfPos = gameState.getAgentPosition(self.index)
		invaders = [a for a in enemies if a.isPacman]
		knowninvaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
		enemiesPos = [a.getPosition() for a in enemies if a.getPosition() != None]
		
		
		if len(invaders)<1 or gameState.getAgentState(self.index).isPacman:
			return self.chooseOfAction(gameState)
		
		# chase the invader only the distance is Known and ghost not scared
		if len(knowninvaders) > 0 and gameState.getAgentState(self.index).scaredTimer<=2:
			problem = SearchInvaders(gameState, self, self.index)
			
			return self.aStarSearch(problem, gameState, self.GeneralHeuristic)[0]
		if len(knowninvaders) == 0 and len(self.lostFoods)>0 :
			mindis = 9999
			minAct = None
			for each in actions:
				nextState = self.getSuccessor(gameState,each)
				pos = nextState.getAgentPosition(self.index)
				dis = self.getMazeDistance(pos,self.lostFoods[-1])
				if mindis > dis:
					mindis = dis
					minAct = each
			return minAct
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
				if max(self.getDeathRoad(gameState,action),self.getDeathRound(gameState,action))>0 and self.whetherCapsule(gameState,action):
					return action
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
			ghost = 0
			for op in opAgents:
				if not gameState.getAgentState(op).isPacman:
					ghost+=1
				if not gameState.getAgentState(op).scaredTimer ==None:
					if gameState.getAgentState(op).scaredTimer>=0:
						scared = gameState.getAgentState(op).scaredTimer
				if min>dis[op]:
					min = dis[op]
				if not gameState.getAgentPosition(op) == None and not gameState.getAgentState(op).isPacman:
					pos.append(gameState.getAgentPosition(op) )
			# (min)
			# if scared<10:		
				
			for action in legalActions:
				# # (self.getDeathRound(gameState,action),self.getDeathRoad(gameState,action))
				# if  ghost ==0:
				# 	values.append((self.getQValue(gameState, action), action))
				# elif len(pos)>1 or (ghost==0 and len(pos)==1):
				# 	values.append((self.getQValue(gameState, action), action))
				# elif len(pos)>0:

				# 	distance = 100000
				# 	for oppos in pos:
				# 		if distance>self.getMazeDistance(gameState.getAgentPosition(self.index),oppos) :
				# 			distance =self.getMazeDistance(gameState.getAgentPosition(self.index),oppos) 
				# 	(action)
				# 	if distance > max(self.getDeathRound(gameState,action),self.getDeathRoad(gameState,action))*2 or scared>15 :
						
				# 		values.append((self.getQValue(gameState, action), action))
				# 	else:
				# 		if self.getDeathRoad(gameState,action)>10:
				# 			food = self.getDeathFood(gameState,action)
				# 			for each in food:
				# 				if each[1]>5:
				# 					self.dangeFood.append(each[0])
								
				# 		nextState= self.getSuccessor(gameState,action)
				# 		if not len(self.getFood(gameState).asList()) ==len(self.getFood(nextState).asList()) :
				# 			# self.updateWeights(gameState, action)
				# 			values.append((self.getQValue(gameState, action), action))
				# else:
				# 	if min<10 :
				# 		if  scared<10:
				# 			# ("dangerous!!!!!!")
				# 			if max(self.getDeathRound(gameState,action),self.getDeathRoad(gameState,action))<=2:
				# 				# self.updateWeights(gameState, action)
				# 				values.append((self.getQValue(gameState, action), action))
				# 			else:
				# 				if(self.getDeathRoad(gameState,action)>=8):
				# 					food = self.getDeathFood(gameState,action)
				# 					for each in food:
				# 						if each[1]>5:
				# 							self.dangeFood.append(each[0])
				# 				nextState= self.getSuccessor(gameState,action)
				# 				if not len(self.getFood(gameState).asList()) ==len(self.getFood(nextState).asList()) :
				# 					# self.updateWeights(gameState, action)
				# 					values.append((self.getQValue(gameState, action), action))
				# 				if self.whetherCapsule(gameState,action):
				# 					values.append((self.getQValue(gameState, action), action)) 
				# 		else:
				# 			values.append((self.getQValue(gameState, action), action))
					
				# 	else:
						
						values.append((self.getQValue(gameState, action), action))
				
		if len(values)>0:				
			return max(values)[1]
		else:
			return "Stop"		
	
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
				# opIsPacman = gameState.getAgentState(opponent).isPacman
				
				if opPos : 
					dis = abs(currentPos[0]-opPos[0])+abs(currentPos[1]-opPos[1])
					if dis<=6:
						ghost.append(opPos)
						ghostIndex = opponent
		team = self.getTeam(gameState)
		if self.index == team[1]:
			enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
		
			invaders = [a for a in enemies if a.isPacman]

			if len(invaders)<1:
				if   len(self.getFood(gameState).asList())>2:
			
					if len(ghost) ==0 :
						if gameState.getAgentState(self.index).numCarrying>1 and  gameState.data.timeleft<200:
							self.weights =self.weights4
							("444444444444444444444")
						else:
							self.weights = self.weights1
							("111111111111111111111")
					else:

						if min([self.getMazeDistance(gameState.getAgentPosition(self.index),a) for a in ghost])>8:
							self.weights = self.weights1
							("111111111111111111111")
						else:
							if gameState.getAgentState(ghostIndex).scaredTimer<10:
								if gameState.data.timeleft<200 :
									if gameState.getAgentState(self.index).numCarrying>1:
										self.weights = self.weights3
										("33333333333333333333")
									else:
										self.weights = self.weights2
										("2222222222222222222222")
								else:
									if gameState.getAgentState(self.index).numCarrying>2:
										
										self.weights = self.weights3
										("33333333333333333333")
										

									else:
										self.weights = self.weights2
										("2222222222222222222222")
							else :
								self.weights = self.weights1
								("111111111111111111111")

				else :
					if len(ghost) ==0:
						self.weights = self.weights4
						("44444444444444444444")
					else:
						if gameState.getAgentState(ghostIndex).scaredTimer<10:
							self.weights = self.weights3
							("33333333333333333333")
						else: 
							self.weights = self.weights4
							("44444444444444444444")
			else:
				if len(ghost) ==0 or  (gameState.getAgentState(ghostIndex).scaredTimer>10 and len(ghost) >0):
					self.weights =self.weights4
					("444444444444444444444")
				else: 
					self.weights = self.weights3
					("33333333333333333333")
		
		else:
			if   len(self.getFood(gameState).asList())>2:
				
				if len(ghost) ==0 :
					if gameState.getAgentState(self.index).numCarrying>1 and  gameState.data.timeleft<200:
						self.weights =self.weights4
						("444444444444444444444")
					else:
						self.weights = self.weights1
						("111111111111111111111")
				else:

					if min([self.getMazeDistance(gameState.getAgentPosition(self.index),a) for a in ghost])>8:
						self.weights = self.weights1
						("111111111111111111111")
					else:
						if gameState.getAgentState(ghostIndex).scaredTimer<10:
							if gameState.data.timeleft<200 :
								if gameState.getAgentState(self.index).numCarrying>1:
									self.weights = self.weights3
									("33333333333333333333")
								else:
									self.weights = self.weights2
									("2222222222222222222222")
							else:
								if gameState.getAgentState(self.index).numCarrying>2:
									
									self.weights = self.weights3
									("33333333333333333333")
									

								else:
									self.weights = self.weights2
									("2222222222222222222222")
						else :
							self.weights = self.weights1
							("111111111111111111111")

			else :
				if len(ghost) ==0:
					self.weights = self.weights4
					("44444444444444444444")
				else:
					if gameState.getAgentState(ghostIndex).scaredTimer<10:
						self.weights = self.weights3
						("33333333333333333333")
					else: 
						self.weights = self.weights4
						("44444444444444444444")
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

		if self.getMazeDistance( gameState.getAgentPosition(self.index),self.noMove[0])<3:
			self.noMove[1] +=1
		else:
			self.noMove[0] = gameState.getAgentPosition(self.index)
			self.noMove[1]= 0
		
		if self.noMove[1]>10:
			return random.choice(legalActions)
		
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
	
	def whetherCapsule(self,gameState,action):

		capsules = gameState.getCapsules()
		# (capsules)
		walls = gameState.getWalls().asList()
		
		pos = gameState.getAgentPosition(self.index)
		explored = []
		explored.append(pos)
		states = util.Queue()
		stateTuple = (gameState,action)
		states.push(stateTuple)
		length = 0
		
		while not states.isEmpty():
			# ("start a new round")
			if(length>25):
				return False
			else :
				gameState, action = states.pop()
				nextState = self.getSuccessor(gameState,action)
				if nextState.getAgentPosition(self.index) not in walls and nextState.getAgentPosition(self.index) not in explored:
					if nextState.getAgentPosition(self.index) in capsules:
						# ("Yes!!!!!!!!!!!!!!!!!!!!!!!!!:")
						return True
					explored.append(nextState.getAgentPosition(self.index))
					length +=1
					actions = nextState.getLegalActions(self.index)
					# (action,self.reverseDirection(action))
					actions.remove(Directions.STOP)
					
					
					# (len(actions),"Action length!!!!!!!")
					if(len(actions)>0):
						for each in actions:
							nextTuple = (nextState,each)
							states.push(nextTuple)
					# (len(states.list),"states length!!!!!!!")
				else :
					continue
		
		return False
	def getDeathRound(self,gameState,action):
		walls = gameState.getWalls().asList()
		
		pos = gameState.getAgentPosition(self.index)
		explored = []
		explored.append(pos)
		states = util.Queue()
		stateTuple = (gameState,action)
		states.push(stateTuple)
		length = 0
		
		while not states.isEmpty():
			# ("start a new round")
			if(length>25):
				return 0
			else :
				gameState, action = states.pop()
				nextState = self.getSuccessor(gameState,action)
				if nextState.getAgentPosition(self.index) not in walls and nextState.getAgentPosition(self.index) not in explored:
					explored.append(nextState.getAgentPosition(self.index))
					length +=1
					actions = nextState.getLegalActions(self.index)
					# (action,self.reverseDirection(action))
					actions.remove(Directions.STOP)
					
					
					# (len(actions),"Action length!!!!!!!")
					if(len(actions)>0):
						for each in actions:
							nextTuple = (nextState,each)
							states.push(nextTuple)
					# (len(states.list),"states length!!!!!!!")
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
		opAgents = self.getOpponents(gameState)
		scared = 0
		ghost = 0

		for op1 in opAgents:
			if not gameState.getAgentState(op1).isPacman:
				ghost+=1
		scared = [gameState.getAgentState(ops).scaredTimer for ops in op]
		minScare = min(scared)
		# (self.whetherClosestCapsule(gameState))
		if minScare<5:
			eat = 1
		else:
			eat = -1
		if gameState.getAgentState(self.index).isPacman and  ghost ==0:
			features['closest-capsule']=0.0
		else:
			
			if eat>0 :
				
		
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
		dist = self.closestFood(nextState.getAgentPosition(self.index), nextfood, walls,gameState)
		if len(food.asList()) == len(nextfood.asList() ) and not dist ==0:
			# make the distance a number less than one otherwise the update
			# will diverge wildly
			features["closest-food"] = 1.0/float(dist)
			# ("The distance is",dist)
		else : 
			features["closest-food"] = 2
	
		team = self.getTeam(gameState)
		teamdis = self.getMazeDistance(nextState.getAgentPosition(team[0]),nextState.getAgentPosition(team[1]))
		if gameState.data.timeleft<1050:
			if teamdis == 0:
				features["team"] = 2
			else: 
				features["team"] = 1/teamdis
		features.divideAll(100)
		return features

	def getSecondFeatures(self, gameState, action):
		
		nextState = self.getSuccessor(gameState, action)
		self.entry = random.choice(self.entrylist)
		food = self.getFood(gameState)
		nextfood = self.getFood(nextState)
		walls = gameState.getWalls()
		
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
						ghost=[]
						ghost.append(opPos)
						ghost.append(opponent)
						self.ghosts.append(ghost)
		
		# Initialize features
		features = util.Counter()
		reverse = self.reverseDirection(action)
		if reverse == gameState.getAgentState(self.index).configuration.direction:
			features["reverse"]=1
			# ("reverse")
		else:
			features["reverse"]=0
			# ("notreverse")
		features["bias"] = 1.0
		legalActions = nextState.getLegalActions(self.index)
		legalActions.remove(Directions.STOP)
		features['num-of-walls'] = max(self.getDeathRoad(gameState,action),self.getDeathRound(gameState,action))
		# if(self.getDeathRoad(gameState,action)>=8):
		# 	deathfood = self.getDeathFood(gameState,action)
		# 	for each in deathfood:
		# 		if each[1]>5:
		# 			self.dangeFood.append(each[0])
		# compute the location of pacman after he takes the action
		
		
		if len(self.ghosts)==0:
			# ("0000000000000000000000000")
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
			# ("next",nextState.getAgentState(self.ghosts[0][1]).getPosition()[0],"   inital",nextState.getInitialAgentPosition(self.ghosts[0][1])[0])
		
			if len(self.ghosts)==1:
				ghostIndex = self.ghosts[0][1]
				pos = gameState.getAgentState(ghostIndex).getPosition()
				nextpos = nextState.getAgentState(ghostIndex).getPosition()
				posDis = self.getMazeDistance(gameState.getAgentState(self.index).getPosition(),pos)
				nextDis = self.getMazeDistance(nextState.getAgentState(self.index).getPosition(),nextpos)
				if abs(posDis-nextDis)>5:
					# ("!!!!!!!!!!!!!!!!!!!!!!!!!!")
					features['closest-ghosts'] = 2 
					# ("222222222222222222222")
				else :
					# ("333333333333333333")
					
					features['closest-ghosts'] = 1.0/nextDis

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
					# ("!!!!!!!!!!!!!!!!!!!!!!!!!!")
					features['closest-ghosts'] = 2 
					# ("222222222222222222222")
				else :
					# ("333333333333333333")
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
		
		dist = self.closestFood(nextState.getAgentPosition(self.index), nextfood, walls,gameState)
		if len(food.asList()) == len(nextfood.asList() ) and not dist ==0:
			# make the distance a number less than one otherwise the update
			# will diverge wildly
			features["closest-food"] = 1.0/float(dist)
			# ("The distance is",dist)
		else : 
			features["closest-food"] = 2
	
		
		features.divideAll(100)
		return features
	
	def getThirdFeatures(self, gameState, action):
		nextState = self.getSuccessor(gameState, action)		
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
						ghost=[]
						ghost.append(opPos)
						ghost.append(opponent)
						self.ghosts.append(ghost)
					
		# Initialize features
		features = util.Counter()
		reverse = self.reverseDirection(action)
		if reverse == gameState.getAgentState(self.index).configuration.direction:
			features["reverse"]=1
			# ("reverse")
		else:
			features["reverse"]=0
			# ("notreverse")
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
					# ("!!!!!!!!!!!!!!!!!!!!!!!!!!")
					features['closest-ghosts'] = 2 
					# ("222222222222222222222")
				else :
					# ("333333333333333333")
					
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
					# ("!!!!!!!!!!!!!!!!!!!!!!!!!!")
					features['closest-ghosts'] = 2 
					# ("222222222222222222222")
				else :
					# ("333333333333333333")
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
			# ("length!!!!!!!!",len(self.ghosts))
			reward = 0
			if(nextState.getAgentState(self.index).getPosition() in self.getFood(gameState).asList()):
				("Eating a food!!!")
				reward +=2

			if len(self.ghosts)>0:
				ghostPosition = self.ghosts[0][0]
				ghostIndex = self.ghosts[0][1]
				if self.scareTimer == 0:
					if self.getMazeDistance(nextState.getAgentState(self.index).getPosition(),ghostPosition)<=1 or nextState.getAgentState(self.index).getPosition()[0]==self.init[0]:

						reward +=-3
						
						
						("Being eaten")
				else :
					(self.scareTimer,"!!!!!!!!!!")
					pos = gameState.getAgentState(ghostIndex).getPosition()
					nextpos = nextState.getAgentState(ghostIndex).getPosition()
					posDis = self.getMazeDistance(gameState.getAgentState(self.index).getPosition(),pos)
					nextDis = self.getMazeDistance(nextState.getAgentState(self.index).getPosition(),nextpos)
					(posDis,nextDis)
					if self.getMazeDistance(nextState.getAgentState(self.index).getPosition(),ghostPosition)<=1 or abs(posDis-nextDis)>5:
						
						("Eating others")
						reward +=3
			# (nextState.getAgentState(self.index).getPosition(),self.getCapsules(gameState)[0])
			if len(self.getCapsules(gameState)):
				if (nextState.getAgentState(self.index).getPosition() == self.getCapsules(gameState)[0]) :
					("Eating a capsule!!!")
					reward+=3
			# (reward,"\n")
			return reward
		elif self.weights==self.weights1:
			reward = 0
			if(nextState.getAgentState(self.index).getPosition() in self.getFood(gameState).asList()):
				("Eating a food!!!")
				reward +=2

			
			if len(self.getCapsules(gameState)):
				if (nextState.getAgentState(self.index).getPosition() == self.getCapsules(gameState)[0]) :
					("Eating a capsule!!!")
					reward+=3
			# (reward,"\n")
			return reward
		elif self.weights ==self.weights3:
			reward = 0
		
			if abs(nextState.getScore() - gameState.getScore())>0:
				reward += 2
				("Score ",reward, " Points!!!" )
			if len(self.ghosts)>0:
				ghostPosition = self.ghosts[0][0]
				ghostIndex = self.ghosts[0][1]
				
				("scareTimer!!!!!",self.scareTimer)
				if self.scareTimer == 0:
					if self.getMazeDistance(nextState.getAgentState(self.index).getPosition(),ghostPosition)<=1 or nextState.getAgentState(self.index).getPosition()==self.init:

						reward +=-3
						
						
						("Being eaten")
				else :
					pos = gameState.getAgentState(ghostIndex).getPosition()
					nextpos = nextState.getAgentState(ghostIndex).getPosition()
					posDis = self.getMazeDistance(gameState.getAgentState(self.index).getPosition(),pos)
					nextDis = self.getMazeDistance(nextState.getAgentState(self.index).getPosition(),nextpos)

					if self.getMazeDistance(nextState.getAgentState(self.index).getPosition(),ghostPosition)<=2 or abs(posDis-nextDis)>5:
						
						("Eating others")
						reward +=3
			return reward
		else:
			reward = 0
		
			if abs(nextState.getScore() - gameState.getScore())>0:
				reward +=abs(nextState.getScore() - gameState.getScore())
				("Score ",reward, " Points!!!" )
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

	def closestFood(self, pos, food, walls,gameState):
		
		if self.red:
			entry = int(self.width/2)+1
		else:
			entry = int(self.width/2)-2
		if self.weights == self.weights2 and pos[0]< entry and gameState.getAgentState(self.index).numCarrying==0:
			return self.getMazeDistance(pos,self.entry)
		if self.weights ==self.weights2:
			return self.closestSafeFood(pos, food, walls,gameState)
		foodList = food.asList()
		min=9999
		for each in foodList:
			# (pos,each)
			if each not in self.dangeFood:
				distance = self.getMazeDistance(pos,each)

				if distance<min:
					min = distance
		return min
	def closestSafeFood(self, pos, food, walls,gameState):
		

		foodList = food.asList()
		min=9999
		for each in foodList:
			# (pos,each)
			if each not in self.dangeFood and each not in self.dangerFoods:

				distance = self.getMazeDistance(pos,each)

				if distance<min:
					min = distance
		return min
	
	def getEntry(self,gameState):
		if self.red:
			entry = int(self.width/2)+1
		else:
			entry = int(self.width/2)-2
		available = []
		for i in range(1,self.height):
			if (entry,i) not in gameState.getWalls().asList():
				pos = (entry,i)
				available.append(pos)
		# (available)
		for each in available:
			if self.red:
				
				if self.getOpenEntry(each,"right",gameState,available)>0:
					available.remove(each)
			else:
				(self.getOpenEntry(each,"left",gameState,available))
				if self.getOpenEntry(each,"left",gameState,available)>0:
					available.remove(each)
		# (available)
		return available
	
	def getOpenEntry(self,pos,action,gameState,available):
		walls = gameState.getWalls().asList()
		explored = []
		explored.append(pos)
		states = util.Queue()
		stateTuple = (pos,action)
		states.push(stateTuple)
		length = 1
		
		while not states.isEmpty():
			# ("start a new round")
			if(length>15):
				return 0
			else :
				pos, action = states.pop()
				nextPos = self.getNextPos(pos,action)
				
				if nextPos not in walls and nextPos not in explored and nextPos not in available:
					explored.append(nextPos)
					length +=1
					if self.red:
						ignore=[]
						
						ignore.append("left")
						if not self.getRevAction(action)=="left":
							ignore.append(self.getRevAction(action))
						actions = self.getNextActions(nextPos,ignore)
						# (actions)
					else: 
						ignore=[]
						
						ignore.append("right")
						if not "right" == self.getRevAction(action):
							ignore.append(self.getRevAction(action))
						actions = self.getNextActions(nextPos,ignore)

					if(len(actions)>0):
						for each in actions:
							nextTuple = (nextPos,each)
							states.push(nextTuple)
					# (len(states.list),"states length!!!!!!!")
				else :
					continue
		
		return length
	def getRevAction(self,action):
		if action=="right":
			return "left"
		elif action =="left":
			return "right"
		elif action == "top":
			return"bottom"
		else:
			return "top"
	def getNextActions(self,pos,action):
		actions = ["left","right","top","bottom"]
		# (action)
		for each in action:
			actions.remove(each)
		return actions

	def getNextPos(self,pos,action):
		if action=="right":
			return (pos[0]+1,pos[1])
		elif action =="left":
			return (pos[0]-1,pos[1])
		elif action == "top":
			return (pos[0],pos[1]+1)
		else:
			return (pos[0],pos[1]-1)


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
class ScanMap:
	"""
	A Class Below is used for scanning the map to find
	Safe food and dangerousfood
	Note: Safe food is the food whitin the position can has
	at least two ways home
	"""

	def __init__(self, gameState, agent):
		"Stores information from the gameState.  You don't need to change this."
		# Store the food for later reference
		self.food = agent.getFood(gameState).asList()
		# Store info for the PositionSearchProblem (no need to change this)
		self.walls = gameState.getWalls()
		self.homeBoundary = agent.boundaryPosition(gameState)
		self.height = gameState.data.layout.height
		self.width = gameState.data.layout.width

	def getFoodList(self, gameState):
		foods = []
		for food in self.food:
			food_fringes = []
			food_valid_fringes = []
			count = 0
			food_fringes.append((food[0] + 1, food[1]))
			food_fringes.append((food[0] - 1, food[1]))
			food_fringes.append((food[0], food[1] + 1))
			food_fringes.append((food[0], food[1] - 1))
			for food_fringe in food_fringes:
				if not gameState.hasWall(food_fringe[0], food_fringe[1]):
					count = count + 1
					food_valid_fringes.append(food_fringe)
			if count > 1:
				foods.append((food, food_valid_fringes))
		return foods

	def getSafeFoods(self, foods):
		safe_foods = []
		for food in foods:
			count = self.getNumOfValidActions(food)
			if count > 1:
				safe_foods.append(food[0])
		return safe_foods

	def getDangerFoods(self, safe_foods):
		danger_foods = []
		for food in self.food:
			if food not in safe_foods:
				danger_foods.append(food)
		return danger_foods

	def getSuccessors(self, state):
		successors = []
		for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
			x, y = state
			dx, dy = Actions.directionToVector(action)
			nextx, nexty = int(x + dx), int(y + dy)
			if not self.walls[nextx][nexty]:
				nextState = (nextx, nexty)
				successors.append((nextState, action))
		return successors

	def isGoalState(self, state):
		return state in self.homeBoundary

	def getNumOfValidActions(self, foods):
		food = foods[0]
		food_fringes = foods[1]
		visited = []
		visited.append(food)
		count = 0
		for food_fringe in food_fringes:
			closed = copy.deepcopy(visited)
			if self.BFS(food_fringe, closed):
				count = count + 1
		return count

	def BFS(self, food_fringe, closed):
		from util import Queue

		fringe = Queue()
		fringe.push((food_fringe, []))
		while not fringe.isEmpty():
			state, actions = fringe.pop()
			closed.append(state)
			if self.isGoalState(state):
				return True
			for successor, direction in self.getSuccessors(state):
				if successor not in closed:
					closed.append(successor)
					fringe.push((successor, actions + [direction]))
