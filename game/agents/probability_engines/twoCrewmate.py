import numpy as np
import random
from game.ship import Node

class TwoCrewmate:
    k = None
    a = None
    crewmatePbbMap = None
    validMask = None


    def __init__(self, ship, k, pos, a):
        self.k = k
        self.a = a
        x, y = pos

        # create a 2d boolean mask where each cell is true if the corresponding cell is open
        board = np.array(ship.board)
        self.validMask = (board.reshape(ship.dim, ship.dim, 1, 1) == Node.OPEN) & (board.reshape(1, 1, ship.dim, ship.dim) == Node.OPEN)

        # count the number of valid positions
        numOpen = np.sum(self.validMask)

        # initialize the pbb map
        pbbMap = np.full((ship.dim, ship.dim, ship.dim, ship.dim), np.nan)
        # the pbbmap is symmetric
        pbbMap[self.validMask] = 2/numOpen
        pbbMap[x, y, :, :] = 0
        pbbMap[:, :, x, y] = 0

        self.crewmatePbbMap = pbbMap


    def updateCrewmatePbbMap(self, bot):
        # our new formula for Blf_t+1(i,j) = P(S_t+1 | C1 = i and C2 = j) * Blf(i, j) 
        # then normalization
        # we necessarily have perfect knowledge of the cell we are in
        x, y = bot.pos
        self.crewmatePbbMap[x, y, :, :] = 0
        self.crewmatePbbMap[:, :, x, y] = 0

        # compute
        p = self.pbbBeepGiven4dMask(bot, self.validMask) if bot.receivedBeep else (1 - self.pbbBeepGiven4dMask(bot, self.validMask))
        self.crewmatePbbMap *= p

        # normalize
        self.crewmatePbbMap /= np.nansum(self.crewmatePbbMap)


    # for global search bots, gives a target to move towards (the closest to the given pos)
    def getTarget(self, pos):
        maxIndices = np.argwhere(self.crewmatePbbMap == np.nanmax(self.crewmatePbbMap))
        selected = random.choice(maxIndices)

        target1 = (selected[0], selected[1])
        target2 = (selected[2], selected[3])
        target = target1 if self._h(pos, target1) < self._h(pos, target2) else target2

        return target
        

    # manhattan distance
    def _h(self, u, v):
        return abs(u[0] - v[0]) + abs(u[1] - v[1])


    # for local search bots, collapses the 4d map into a 2d map where P(C1 = i or C2 = i | data)
    def getUtilityMap(self):
        # law of total probability: P(C1 = i or C2 = i) = P(C1 = i) + P(C2 = i) - P(C1 = i and C2 = i)
        # marginalization: P(C1 = i) = ∑_j P(C1 = i and C2 = j) and P(C2 = i) = ∑_j P(C1 = j and C2 = i)
        # fact: C1 and C2 cannot be in the same cell, so P(C1 = i and C2 = i) = 0

        # calculate P(C1 = i | data) for all i
        p_c1 = np.nansum(self.crewmatePbbMap, axis=(2, 3))
        
        # calculate P(C2 = i | data) for all i
        p_c2 = np.nansum(self.crewmatePbbMap, axis=(0, 1))
        
        # calculate P(C1 = i or C2 = i | data) for all i
        p_c1_or_c2 = p_c1 + p_c2 
        
        return p_c1_or_c2


    def pbbBeepGiven4dMask(self, bot, mask):
        x, y = bot.pos
        dist_matrix = self.calcDistanceMatrix(x, y)
        p = self.pbbBeepGivenCrewmateInCell4d(dist_matrix)

        return np.where(mask, p, np.nan)
    

    # calculate the distance matrix from the bot to each cell
    def calcDistanceMatrix(self, x, y):
        if not hasattr(self, 'distanceMatrix') or self.distanceMatrixPos != (x, y):
            i, j = np.indices((self.crewmatePbbMap.shape[0], self.crewmatePbbMap.shape[1]))
            self.distanceMatrix = np.abs(i - x) + np.abs(j - y)
            self.distanceMatrixPos = (x, y)
        return self.distanceMatrix
    
    # returns a 4d map of the probability of a beep given that a crewmate is in a cell, given a distance matrix of the bot to each cell
    # where p[i,j,k,l] = P(beep | C1 = (i,j), C2 = (k,l)) = 1 - (1 - exp(-a * (d - 1))) * (1 - exp(-a * (d' - 1)))
    # where d is the distance from the bot to C1 and d' is the distance from the bot to C2
    def pbbBeepGivenCrewmateInCell4d(self, distMatrix):
        a = self.a

        dist = distMatrix.reshape(distMatrix.shape[0], distMatrix.shape[1], 1, 1)
        distPrime = distMatrix.reshape(1, 1, distMatrix.shape[0], distMatrix.shape[1])

        p = 1 - (1 - np.exp(-a * (dist - 1))) * (1 - np.exp(-a * (distPrime - 1)))
        return p
    

    # collapses the 4d map into a 2d map given that a crewmate has been found
    def collapseMap(self, crewPos):
        # we know that the crewmate is in the cell crewPos
        # P(C1 = i | data, C2 = crewPos) = P(C1 = i and C2 = crewPos | data) / P(C2 = crewPos | data)
        x, y = crewPos

        # get the 2d mask for the cell
        twoDimMask = self.validMask[x, y, :, :]
        collapsed = self.crewmatePbbMap[x, y, :, :]

        # normalize
        normalizer = np.sum(collapsed[twoDimMask])
        collapsed[twoDimMask] /= normalizer
        
        return collapsed