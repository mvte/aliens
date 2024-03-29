import numpy as np
import random
from game.ship import Node

class TwoAlien:
    def __init__(self, ship, k, pos, a):
        self.k = k
        self.a = a
        self.ship = ship
        self.dim = ship.dim

        # initialize the valid mask
        board = np.array(ship.board)
        validMask = (board.reshape(ship.dim, ship.dim, 1, 1) == Node.OPEN) & (board.reshape(1, 1, ship.dim, ship.dim) == Node.OPEN)
        self.validMask = validMask

        # initialize the pbb map
        pbbMap = np.full((ship.dim, ship.dim, ship.dim, ship.dim), np.nan)
        # the aliens are not within the sensor range
        outSensorMask = (~self.sensorMask(pos)) & validMask
        inSensorMask = self.sensorMask(pos) & validMask
        numOpen = np.nansum(outSensorMask)
        pbbMap[outSensorMask] = 1/numOpen
        pbbMap[inSensorMask] = 0

        self.alienPbbMap = pbbMap

        # precompute the number of valid moves for each cell
        twoDimMask = np.array(ship.board) == Node.OPEN
        self.numNeighbors = np.full((self.dim, self.dim), 0)
        for i in range(self.dim):
            for j in range(self.dim):
                if not twoDimMask[i, j]:
                    continue
                self.numNeighbors[i, j] = len(self.ship.getValidMoves((i, j)))
        self.numNeighbors[~twoDimMask] = -1


    # 4 dimensional sensor mask
    def sensorMask(self, botPos):
        botX, botY = botPos
        x, y = np.indices((self.dim, self.dim))
        sensorMask2d = ((np.abs(x - botX) < self.k) & (np.abs(y - botY) < self.k))

        sensorMask = sensorMask2d.reshape(self.dim, self.dim, 1, 1) | sensorMask2d.reshape(1, 1, self.dim, self.dim)

        return sensorMask
    
    
    # update the probability map
    def updateAlienPbbMap(self, bot):
        newBlf = np.zeros((self.dim, self.dim, self.dim, self.dim))

        dirs = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for dir1 in dirs:
            for dir2 in dirs:
                # shift both belief neighbor naps in the same direction for each alien
                shiftedBlf = np.roll(self.alienPbbMap, dir1, axis=(0, 1))
                shiftedBlf = np.roll(shiftedBlf, dir2, axis=(2, 3))
                shiftedBlf = np.nan_to_num(shiftedBlf, nan=0)
                shiftedNb1 = np.roll(self.numNeighbors, dir1, axis=(0, 1))
                shiftedNb2 = np.roll(self.numNeighbors, dir2, axis=(0, 1))

                # mask the rolled over edges for alien 1
                if dir1 == (0, 1):
                    shiftedBlf[:, 0, :, ] = 0
                    shiftedNb1[:, 0] = -1
                elif dir1 == (0, -1):
                    shiftedBlf[:, -1, :, ] = 0
                    shiftedNb1[:, -1] = -1
                elif dir1 == (1, 0):
                    shiftedBlf[0, :, :, ] = 0
                    shiftedNb1[0, :] = -1
                elif dir1 == (-1, 0):
                    shiftedBlf[-1, :, :, ] = 0
                    shiftedNb1[-1, :] = -1
                
                # mask the rolled over edges for alien 2
                if dir2 == (0, 1):
                    shiftedBlf[:, :, :, 0] = 0
                    shiftedNb2[:, 0] = -1
                elif dir2 == (0, -1):
                    shiftedBlf[:, :, :, -1] = 0
                    shiftedNb2[:, -1] = -1
                elif dir2 == (1, 0):
                    shiftedBlf[:, :, 0, :] = 0
                    shiftedNb2[0, :] = -1
                elif dir2 == (-1, 0):
                    shiftedBlf[:, :, -1, :] = 0
                    shiftedNb2[-1, :] = -1
                
                newBlf = newBlf + shiftedBlf / (shiftedNb1[:, :, np.newaxis, np.newaxis] * shiftedNb2[np.newaxis, np.newaxis, :, :])

        # apply the valid mask
        newBlf[~self.validMask] = np.nan

        # apply the sensor mask if the sensor did not go off
        if not bot.receivedSensor:
            sensorMask = self.sensorMask(bot.pos) & self.validMask
            newBlf[sensorMask] = 0
        
        # normalize
        newBlf /= np.nansum(newBlf)

        self.alienPbbMap = newBlf
    

    # collapse into a 2d utility map for local search bots
    # P(A1 = i or A2 = i | data)
    def getUtilityMap(self):
        p_a1 = np.nansum(self.alienPbbMap, axis=(2, 3))
        p_a2 = np.nansum(self.alienPbbMap, axis=(0, 1))
        p_a1_or_a2 = p_a1 + p_a2

        twoDimValidMask = np.array(self.ship.board) == Node.OPEN
        p_a1_or_a2[~twoDimValidMask] = np.nan

        return p_a1_or_a2
    


    
