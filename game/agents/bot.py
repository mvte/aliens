import math
import heapq
import numpy as np

class Bot:
    pos = None
    receivedSensor = False
    receivedBeep = False
    whichBot = None
    k = None
    a = None

    pbbLookup = {}

    # determines if an alien is within a 2k+1 x 2k+1 square of the bot
    def isWithinSensorRange(self, alienPos):
        k = self.k
        botX, botY = self.pos
        alienX, alienY = alienPos

        return abs(botX - alienX) <= k and abs(botY - alienY) <= k
    
    # returns a mask of the same shape as the board where each cell is true if the corresponding cell is within the sensor range of the bot
    def sensorRangeMask(self, dim):
        k = self.k
        botPos = np.array(self.pos)

        # Create a grid of positions
        grid = np.indices((dim, dim)).reshape(2, -1).T

        # Compute the absolute difference between botPos and each position in the grid
        diff = np.abs(grid - botPos)

        # Check if each position in the grid is within sensor range
        return np.logical_and(diff[:, 0] <= k, diff[:, 1] <= k).reshape(dim, dim)
    
    
    # determines the probability that we receive a beep given that the crewmate is in the cell (i, j)
    def pbbBeepGivenCrewmateInCell(self, i, j):
        if ((self.pos), (i, j)) in self.pbbLookup:
            return self.pbbLookup[(self.pos), (i, j)]
        a = self.a
        x, y = self.pos
        dist = abs(x - i) + abs(y - j)

        self.pbbLookup[(self.pos), (i,j)] = math.exp(-a * (dist - 1))
        return self.pbbLookup[(self.pos), (i,j)]
    
    # returns an array of probabilities of receiving the beep given that the crewmate is in each cell
    def pbbBeepGivenMask(self, mask):
        i, j = np.where(mask)
        p = np.zeros(mask.shape)

        for x, y in zip(i, j):
            p[x, y] = self.pbbBeepGivenCrewmateInCell(x, y)
        
        return p



