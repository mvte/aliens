from game.agents.bot import Bot
from game.ship import Node
import random
import heapq
import numpy as np

'''
testing vectorized logic
currently slower than the original implementation, but should be faster for larger maps
'''
class Bot1(Bot):
    alienPbbMap = None
    crewmatePbbMap = None
    time = None

    def __init__(self, ship, k, pos, a):
        self.whichBot = "bot1"
        self.time = 0
        self.pos = pos
        self.k = k
        self.a = a
        self.alienPbbMap = self._initializeAlienPbbMap(ship)
        self.crewmatePbbMap = self._initializeCrewPbbMap(ship)


    def _initializeCrewPbbMap(self, ship):
        board = np.array(ship.board)

        # create a 2d boolean mask where each cell is true if the corresponding cell is open
        mask = board == Node.OPEN

        # exclude the current position as well
        x, y = self.pos
        mask[x, y] = False

        # count the number of valid positions
        numOpen = np.sum(mask)

        # initialize the pbb map
        pbbMap = np.full((ship.dim, ship.dim), np.nan)
        pbbMap[mask] = 1/numOpen

        return pbbMap

    
    def _initializeAlienPbbMap(self, ship):
        board = np.array(ship.board)

        # create a boolean mask where each cell is true if the corresponding cell is open
        mask = (board == Node.OPEN)

        # create a boolean mask where each cell is true if the corresponding cell is outside the sensor range
        sensorMask = np.logical_not(self.sensorRangeMask(ship.dim))

        # count the number of positions outside the sensor range
        numOpen = np.sum(mask)

        # initialize the pbb map
        pbbMap = np.full((ship.dim, ship.dim), np.nan)
        pbbMap[mask] = 0
        pbbMap[sensorMask] = 1/numOpen
                    
        return pbbMap
    

    # the bot should've received beeps or sensor alerts prior to calling this
    def computeNextStep(self, ship):
        self.time += 1

        # update crewmate probabilities
        target = self._updateCrewmatePbbMap(ship)
        
        # update alien probabilities
        self._updateAlienPbbMap(ship)

        # TODO: a* to the most likely crewmate position, avoiding cells where the alien is known not to be (0% probability)
        next = self._aStar(ship, self.pos, target)
        if next and len(next) > 0:
            self.pos = next[1]

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
        self.crewmatePbbMap[self.pos] = 0

        # mask for valid positions
        mask = np.array(ship.board) == Node.OPEN
        x, y = self.pos
        mask[x][y] = False

        # compute the probability for open cells
        p = self.pbbBeepGivenMask(mask) if self.receivedBeep else (1 - self.pbbBeepGivenMask(mask))
        blf = p * self.crewmatePbbMap

        # normalize
        self.crewmatePbbMap = blf / np.sum(blf[mask])

        # select the most likely position, breaking ties at random
        maxIndices = np.argwhere(self.crewmatePbbMap == np.max(np.nan_to_num(self.crewmatePbbMap, nan=-1)))
        selected = random.choice(maxIndices)

        return (selected[0], selected[1])



    def _updateAlienPbbMap(self, ship):
        # mask for valid positions
        board = np.array(ship.board)
        mask = board == Node.OPEN
        x, y = self.pos

        # mask for valid positions
        # if the sensor went off, we know the alien is not outside of the sensor range
        if self.receivedSensor:
            sensorMask = mask & self.sensorRangeMask(ship.dim)
        # if the sensor did not go off, we know the alien is not within the sensor range
        else:
            sensorMask = mask & np.logical_not(self.sensorRangeMask(ship.dim))
    
        # compute the new probability map
        newPbbMap = np.full((ship.dim, ship.dim), np.nan)
        newPbbMap[mask] = 0
        newPbbMap
        for i, j in zip(*np.where(sensorMask)):
            blf = 0
            for nb in ship.getValidMoves((i, j)):
                x, y = nb
                numNeighbors = len(ship.getValidMoves(nb))
                if numNeighbors == 0:
                    numNeighbors = 1
                blf += self.alienPbbMap[x][y] / numNeighbors
            newPbbMap[i][j] = blf

        # normalize
        newPbbMap = newPbbMap / np.sum(newPbbMap[mask])
        self.alienPbbMap = newPbbMap

    # a* search given ship, bot position, and target position
    def _aStar(self, ship, s, g):
        fringe = []
        heapq.heappush(fringe, (0, s))
        dist = {s: 0}
        prev = {s: s}
        firstStep = True

        while fringe:
            _, u = heapq.heappop(fringe)
            if u == g:
                break

            for v in ship.getValidMoves(u):
                vx, vy = v
                # at the very least, our first step should be to a cell that definitely does not contain the alien
                if firstStep and self.alienPbbMap[vx][vy] > 0:
                    continue
                # all other steps should be to cells under some probability of containing the alien
                elif not firstStep and self.alienPbbMap[vx][vy] > 0.1:
                    continue

                alt = dist[u] + 1
                if v not in dist or alt < dist[v]:
                    dist[v] = alt
                    prev[v] = u
                    heapq.heappush(fringe, (alt + self._h(v, g), v))

                firstStep = False
        
        if g not in prev:
            return None

        path = []
        u = g
        while u != s:
            path.append(u)
            u = prev[u]
        path.append(s)
        path.reverse()

        return path

    # manhattan distance
    def _h(self, u, v):
        return abs(u[0] - v[0]) + abs(u[1] - v[1])




                    




                



    


    