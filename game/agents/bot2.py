from game.agents.bot import Bot
from game.ship import Node
import random
import heapq

'''
Bot 2 uses a utilitarian approach towards finding the crewmate. That is, at any point, the bot will move to the cell within some 
local search depth that has the highest utility. The utility of a cell is defined as the sum of the following:
1. The probability that the crewmate is in the cell multiplied by the crewmate utility
2. The probability that the alien is in the cell multiplied by the alien utility
3. A penalty for cells that have been explored
4. A reward for cells that have not been explored
'''
class Bot2(Bot):
    alienPbbMap = None
    crewmatePbbMap = None
    explored = None
    time = None

    # crewmate utility
    crw = 10
    # alien utility
    aln = -5
    # explored cell penalty
    expPenalty = -1
    # unexplored cell reward
    unexpReward = 1
    # local search depth
    depth = 7

    def __init__(self, ship, k, pos, a):
        self.whichBot = "bot2"
        self.time = 0
        self.pos = pos
        self.k = k
        self.a = a
        self.alienPbbMap = self._initializeAlienPbbMap(ship)
        self.crewmatePbbMap = self._initializeCrewPbbMap(ship)
        self.explored = [[False for i in range(ship.dim)] for j in range(ship.dim)]


    def _initializeCrewPbbMap(self, ship):
        pbbMap = [[0 for i in range(ship.dim)] for j in range(ship.dim)]
        numOpen = 0
        for i in range(ship.dim):
            for j in range(ship.dim):
                # the bot does not know where the aliens are, so we consider it open
                open = ship.board[i][j] == Node.OPEN
                if open and (i, j) != self.pos:
                    numOpen += 1
        
        for i in range(ship.dim):
            for j in range(ship.dim):
                open = ship.board[i][j] == Node.OPEN
                if open and (i, j) != self.pos:
                    pbbMap[i][j] = 1 / numOpen
                else:
                    pbbMap[i][j] = float("nan")
                    
        return pbbMap
    
    def _initializeAlienPbbMap(self, ship):
        pbbMap = [[0 for i in range(ship.dim)] for j in range(ship.dim)]
        numOpen = 0
        for i in range(ship.dim):
            for j in range(ship.dim):
                if ship.board[i][j] == Node.OPEN and (i, j) != self.pos and not self.isWithinSensorRange((i, j)):
                    numOpen += 1
        
        for i in range(ship.dim):
            for j in range(ship.dim):
                if ship.board[i][j] == Node.OPEN and (i, j) != self.pos and not self.isWithinSensorRange((i, j)):
                    pbbMap[i][j] = 1 / numOpen
                elif ship.board[i][j] == Node.CLOSED:
                    pbbMap[i][j] = float("nan")
                else:
                    pbbMap[i][j] = 0
                    
        return pbbMap
    

    # the bot should've received beeps or sensor alerts prior to calling this
    # 
    def computeNextStep(self, ship):
        self.time += 1

        # update crewmate probabilities
        self._updateCrewmatePbbMap(ship)
        
        # update alien probabilities
        self._updateAlienPbbMap(ship)

        # update explored map
        x, y = self.pos
        self.explored[x][y] = True

        # move to the adjacent cell with the highest utility
        path = self._localSearch(ship)
        if len(path) > 1:
            self.pos = path[1]

        # reset received beeps and sensor alerts
        self.receivedBeep = False
        self.receivedSensor = False
        return self.pos
        

    # dr cowan only has three tricks
    # defition of conditional probability
    # marginalization
    # conditional refactoring
    def _updateCrewmatePbbMap(self, ship):
        # want to compute the P(crewmate is in cell i | beep in cell j) for each i
        # i.e. our belief of where the crewmate is given that we heard a beep in cell j
        # blf_t+1(i) = P(S_t+1 | C_t+1 = i) * Blf_t(i)
        # then divide by sum of all blf_t+1(i) to normalize
        # we necessarily have perfect knowledge of the cell we are in
        q = []
        x, y = self.pos
        self.crewmatePbbMap[x][y] = 0

        sum = 0
        for i in range(ship.dim):
            for j in range(ship.dim):
                open = ship.board[i][j] == Node.OPEN
                if open and (i, j) != self.pos:
                    p = self.pbbBeepGivenCrewmateInCell(i,j) if self.receivedBeep else (1 - self.pbbBeepGivenCrewmateInCell(i, j))
                    blf = p * self.crewmatePbbMap[i][j]
                    self.crewmatePbbMap[i][j] = blf
                    sum += blf
                    heapq.heappush(q, (-blf, (i, j)))
        
        # normalize
        for i in range(ship.dim):
            for j in range(ship.dim):
                if ship.board[i][j] != Node.CLOSED:
                    self.crewmatePbbMap[i][j] /= sum


    def _updateAlienPbbMap(self, ship):
        # want to compute the P(alien is in cell i | sensors go off in cell j) for each i
        # since the alien moves, we want P(alien in cell i !now!)
        newPbbMap = [[0 for i in range(ship.dim)] for j in range(ship.dim)]
        sum = 0
        for i in range(ship.dim):
            for j in range(ship.dim):
                # we skip closed cells
                if ship.board[i][j] == Node.CLOSED:
                    newPbbMap[i][j] = float("nan")
                    continue
                # if the cell is out of sensor range but the sensor went off, then the alien cannot be there
                if self.receivedSensor and not self.isWithinSensorRange((i, j)):
                    continue
                # if the cell is within sensor range but the sensor didn't go off, then the alien cannot be there
                if not self.receivedSensor and self.isWithinSensorRange((i, j)):
                    continue
                
                # the alien can only be in this cell if the alien was in a neighboring cell
                # so we calculate the pbb of the alien in this cell based off the pbb of the alien in the neighboring cells
                # blf_t+1(i) = ∑_i' (Blf_t(i') * P(A_t+1 = i | A_t = i')
                blf = 0
                for nb in ship.getValidMoves((i, j)):
                    x, y = nb
                    numNeighbors = len(ship.getValidMoves(nb))
                    if numNeighbors == 0:
                        numNeighbors = 1
                    blf += self.alienPbbMap[x][y] / numNeighbors
                sum += blf
                newPbbMap[i][j] = blf

        # normalize
        for i in range(ship.dim):
            for j in range(ship.dim):
                if ship.board[i][j] != Node.CLOSED:
                    newPbbMap[i][j] /= sum
        self.alienPbbMap = newPbbMap


    def _utility(self, pos):
        x, y = pos
        expWeight = self.expPenalty if self.explored[x][y] else self.unexpReward
        return self.crw * self.crewmatePbbMap[x][y] + self.aln * self.alienPbbMap[x][y] + expWeight

    # select cell with the highest utility within our search space, breaking ties at random, and return the path to that cell
    def _localSearch(self, ship):
        # compute utility of cells the bot can move to 
        utils = []
        q = []
        prev = {}

        # bfs to compute utility of each cell within given depth
        for i in range(self.depth):
            if i == 0:
                q.append(self.pos)
                prev[self.pos] = None
                continue
            
            newQ = []
            while q:
                curr = q.pop(0)
                heapq.heappush(utils, (-self._utility(curr), curr))
                for nb in ship.getValidMoves(curr):
                    nx, ny = nb
                    if (nx, ny) in prev:
                        continue
                    prev[(nx, ny)] = curr
                    newQ.append((nx, ny))
            q = newQ
        
        # break ties at random
        mx, pos = heapq.heappop(utils)
        selected = [pos]
        while utils and mx == utils[0][0]:
            _, pos = heapq.heappop(utils)
            selected.append(pos)
        target = random.choice(selected)

        # return path to selected cell with highest utility
        path = []
        while target:
            path.append(target)
            target = prev[target]
        path.reverse()
        return path
        

                    