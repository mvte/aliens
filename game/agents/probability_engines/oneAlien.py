from game.ship import Node
import numpy as np

class OneAlien:
    # initializes the probability map for the alien
    # everything outside the sensor range is equally likely
    def __init__(self, ship, k, pos, a, map = None, twoAlienCase = False):
        self.k = k
        self.a = a
        self.ship = ship
        self.dim = ship.dim
        
        # if this engine is used for two aliens, then the update logic is a little bit different
        self.twoAlienCase = twoAlienCase

        if map is not None:
            self.alienPbbMap = map
            return

        # create masks for valid and sensor range
        self.validMask = np.array(ship.board) == Node.OPEN
        inSensorMask = self.validMask & self.sensorMask(pos)
        outSensorMask = self.validMask & (~self.sensorMask(pos))

        # initialize the probability map
        self.alienPbbMap = np.full((self.dim, self.dim), np.nan)
        numOpen = np.sum(outSensorMask)
        self.alienPbbMap[outSensorMask] = 1 / numOpen
        self.alienPbbMap[inSensorMask] = 0

        # precompute the number of valid moves for each cell
        self.numNeighbors = np.full((self.dim, self.dim), 0)
        for i in range(self.dim):
            for j in range(self.dim):
                if not self.validMask[i, j]:
                    continue
                self.numNeighbors[i, j] = len(self.ship.getValidMoves((i, j)))
        self.numNeighbors[~self.validMask] = -1


    # creates a 2d mask of the sensor range (true within, false without)
    def sensorMask(self, pos):
        botX, botY = pos
        x, y = np.indices((self.dim, self.dim))
        return ((np.abs(x - botX) < self.k) & (np.abs(y - botY) < self.k))
    
    def updateAlienPbbMap(self, bot):
        # initialize a new probability map = 0
        newBlf = np.zeros((self.dim, self.dim))

        dirs = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for dir in dirs:
            # shift both belief and neighbors map in the same direction
            shiftedBlf = np.nan_to_num(np.roll(self.alienPbbMap, dir, axis=(0, 1)), nan=0)
            shiftedNb = np.roll(self.numNeighbors, dir, axis=(0, 1))

            # mask the rolled over edges
            # shift right
            if dir == (0, 1):
                # set the leftmost column to default values
                shiftedBlf[:, 0] = 0
                shiftedNb[:, 0] = -1
            # shift left
            if dir == (0, -1):
                # set the rightmost column to default values
                shiftedBlf[:, -1] = 0
                shiftedNb[:, -1] = -1
            # shift down
            if dir == (1, 0):
                # set the topmost row to default values
                shiftedBlf[0, :] = 0
                shiftedNb[0, :] = -1
            # shift up
            if dir == (-1, 0):
                shiftedBlf[-1, :] = 0
                shiftedNb[-1, :] = -1

            newBlf += shiftedBlf / shiftedNb

        # apply the validMask
        newBlf[~self.validMask] = np.nan

        # apply the correct sensor mask
        if bot.receivedSensor and not self.twoAlienCase:
            # zero out the probabilities outside the sensor range
            sensorMask = self.validMask & (~self.sensorMask(bot.pos))
            newBlf[sensorMask] = 0
        elif not bot.receivedSensor or self.twoAlienCase:
            # zero out the probabilities inside the sensor range
            sensorMask = self.validMask & self.sensorMask(bot.pos)
            newBlf[sensorMask] = 0

        # normalize
        newBlf /= np.nansum(newBlf)

        self.alienPbbMap = newBlf


    def getMap(self):
        return self.alienPbbMap

    
