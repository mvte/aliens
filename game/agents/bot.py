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

    foundCrewmate = False
    pbbLookup = {}

    # determines if an alien is within a 2k+1 x 2k+1 square of the bot
    def isWithinSensorRange(self, alienPos):
        k = self.k
        botX, botY = self.pos
        alienX, alienY = alienPos

        return abs(botX - alienX) < k and abs(botY - alienY) < k
    
     # determines the probability that we receive a beep given that the crewmate is in the cell (i, j)
    def pbbBeepGivenCrewmateInCell(self, i, j):
        if ((self.pos), (i, j)) in self.pbbLookup:
            return self.pbbLookup[(self.pos), (i, j)]
        a = self.a
        x, y = self.pos
        dist = abs(x - i) + abs(y - j)

        self.pbbLookup[(self.pos), (i,j)] = math.exp(-a * (dist - 1))
        return self.pbbLookup[(self.pos), (i,j)]

    



