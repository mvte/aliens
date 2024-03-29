import numpy as np
import random
from game.ship import Node

class OneCrewmate:
    def __init__(self, ship, k, pos, a, map=None):
        self.k = k
        self.a = a
        self.ship = ship
        self.dim = ship.dim

        board = np.array(ship.board)
        self.validMask = board == Node.OPEN

        if map is not None:
            self.crewmatePbbMap = map
            return
        
        # create pbb map if one is not given
        numOpen = np.sum(self.validMask)

        x, y = pos
        pbbMap = np.full((ship.dim, ship.dim), np.nan)
        pbbMap[self.validMask] = 1/numOpen
        pbbMap[x, y] = 0

        self.crewmatePbbMap = pbbMap

    # Blf_t+1(i) = P(C = i | S_t) = P(S_t | C = i) * Blf_t(i)
    def updateCrewmatePbbMap(self, bot):
        # we necessarily have perfect knowledge of where we are
        x, y = bot.pos
        self.crewmatePbbMap[x, y] = 0

        # compute probabilities
        dist_matrix = self.calcDistanceMatrix(x, y)
        p = self.pbbBeepGivenCrewmateInCell(dist_matrix) if bot.receivedBeep else (1 - self.pbbBeepGivenCrewmateInCell(dist_matrix))
        self.crewmatePbbMap *= p

        # normalize
        self.crewmatePbbMap /= np.nansum(self.crewmatePbbMap)
        
    # for global search bots, gives a target to move towards
    def getTarget(self, botPos):
        maxIndices = np.argwhere(self.crewmatePbbMap == np.nanmax(self.crewmatePbbMap))

        selected = random.choice(maxIndices)
        return tuple(selected)
    
    # for local search bots, gives a utility map
    def getUtilityMap(self):
        return self.crewmatePbbMap

    # computes the distance matrix from a given position
    def calcDistanceMatrix(self, x, y):
        if not hasattr(self, 'distance_matrix') or self.distance_matrix_pos != (x, y):
            i, j = np.indices((self.dim, self.dim))
            self.distance_matrix = np.abs(i - x) + np.abs(j - y)
            self.distance_matrix_pos = (x, y)
        return self.distance_matrix
    

    # P(S | C = i) = exp(-a * (d - 1))
    def pbbBeepGivenCrewmateInCell(self, dist_matrix):
        return np.exp(-self.a * (dist_matrix - 1))