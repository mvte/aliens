from game.agents.bot import Bot
from game.ship import Node
import game.agents.probability_engines.twoCrewmate as tc
import game.agents.probability_engines.oneCrewmate as oc
import game.agents.probability_engines.twoAlien as ta
import random
import heapq

'''
Bot 8 is Bot 5, except that the probabilities of where the aliens are account for the fact that there are two of them.
We take the probability map that Bot 7 uses, but we collapse it into a 2D map with each cell i holding the probability:
    P(A1 = i or A2 = j | data)
'''
class Bot8(Bot):
    alienPbbMap = None
    crewmatePbbMap = None
    explored = None
    time = None
    notTransitioned = True
    
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
        self.whichBot = "bot8"
        self.time = 0
        self.pos = pos
        self.k = k
        self.a = a

        self.explored = [[False for i in range(ship.dim)] for j in range(ship.dim)]
        self.ape = ta.TwoAlien(ship, k, pos, a)
        self.cpe = tc.TwoCrewmate(ship, k, pos, a)
    

    # the bot should've received beeps or sensor alerts prior to calling this
    def computeNextStep(self, ship):
        self.time += 1

        if self.foundCrewmate and self.notTransitioned:
            self.notTransitioned = False
            collapsedMap = self.cpe.collapseMap(self.pos)
            self.cpe = oc.OneCrewmate(ship, self.k, self.pos, self.a, collapsedMap)

        # update crewmate probabilities
        self.cpe.updateCrewmatePbbMap(self)
        
        # update alien probabilities
        self.ape.updateAlienPbbMap(self)
        self.alienPbbMap = self.ape.getUtilityMap()

        # update explored map
        x, y = self.pos
        self.explored[x][y] = True

        # set utility map
        self.crewmateUtility = self.cpe.getUtilityMap()

        # move to the adjacent cell with the highest utility
        path = self._localSearch(ship)
        if len(path) > 1:
            self.pos = path[1]

        # reset received beeps and sensor alerts
        self.receivedBeep = False
        self.receivedSensor = False
        return self.pos


    def _utility(self, pos):
        x, y = pos
        expWeight = self.expPenalty if self.explored[x][y] else self.unexpReward
        return self.crw * self.crewmateUtility[x][y] + self.aln * self.alienPbbMap[x][y] + expWeight

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
        

                    