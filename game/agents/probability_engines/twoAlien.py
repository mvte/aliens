import numpy as np
import random
from game.ship import Node
import time
from numba import njit

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

        self.precompute(ship)
            
    # precomputes a bunch of things for the probability map
    def precompute(self, ship):
        # precompute the number of valid moves for each cell
        twoDimMask = np.array(ship.board) == Node.OPEN
        self.twoDimMask = twoDimMask
        self.numNeighbors = np.full((self.dim, self.dim), 0)
        for i in range(self.dim):
            for j in range(self.dim):
                if not twoDimMask[i, j]:
                    continue
                self.numNeighbors[i, j] = len(self.ship.getValidMoves((i, j)))
        self.numNeighbors[~twoDimMask] = -1

        # precompute shifted neighbors
        self.shiftedNeighbors = {}
        for dir in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            self.shiftedNeighbors[dir] = np.roll(self.numNeighbors, dir, axis=(0, 1))

        # mask over the edges
        self.shiftedNeighbors[(0, 1)][:, 0] = -1
        self.shiftedNeighbors[(0, -1)][:, -1] = -1
        self.shiftedNeighbors[(1, 0)][0, :] = -1
        self.shiftedNeighbors[(-1, 0)][-1, :] = -1

        # precompute their products
        self.shiftedNbProducts = {}
        for dir1 in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            for dir2 in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                self.shiftedNbProducts[(dir1, dir2)] = self.shiftedNeighbors[dir1][:, :, np.newaxis, np.newaxis] * self.shiftedNeighbors[dir2][np.newaxis, np.newaxis, :, :]

        # precompute padding for the blf map
        self.padSizesLeft = {
            (0, 1): ((0, 0), (1, 0), (0, 0), (0, 0)),
            (0, -1): ((0, 0), (0, 1), (0, 0), (0, 0)),
            (1, 0): ((1, 0), (0, 0), (0, 0), (0, 0)),
            (-1, 0): ((0, 1), (0, 0), (0, 0), (0, 0)),
        }

        self.padSizesRight = {
            (0, 1): ((0, 0), (0, 0), (0, 0), (1, 0)),
            (0, -1): ((0, 0), (0, 0), (0, 0), (0, 1)),
            (1, 0): ((0, 0), (0, 0), (1, 0), (0, 0)),
            (-1, 0): ((0, 0), (0, 0), (0, 1), (0, 0)),
        }


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
                # pad the array with zeros
                paddedBlf = np.pad(self.alienPbbMap, self.padSizesLeft[dir1], mode='constant', constant_values=0)
                paddedBlf = np.pad(paddedBlf, self.padSizesRight[dir2], mode='constant', constant_values=0)

                # slice the array to shift it
                if dir1 == (0, 1):
                    shiftedBlf = paddedBlf[:, :-1, :, :]
                elif dir1 == (0, -1):
                    shiftedBlf = paddedBlf[:, 1:, :, :]
                elif dir1 == (1, 0):
                    shiftedBlf = paddedBlf[:-1, :, :, :]
                elif dir1 == (-1, 0):
                    shiftedBlf = paddedBlf[1:, :, :, :]

                if dir2 == (0, 1):
                    shiftedBlf = shiftedBlf[:, :, :, :-1]
                elif dir2 == (0, -1):
                    shiftedBlf = shiftedBlf[:, :, :, 1:]
                elif dir2 == (1, 0):
                    shiftedBlf = shiftedBlf[:, :, :-1, :]
                elif dir2 == (-1, 0):
                    shiftedBlf = shiftedBlf[:, :, 1:, :]

                shiftedBlf = np.nan_to_num(shiftedBlf)
                newBlf = newBlf + shiftedBlf / self.shiftedNbProducts[(dir1, dir2)]

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

        p_a1_or_a2[~self.twoDimMask] = np.nan

        return p_a1_or_a2
    

    
