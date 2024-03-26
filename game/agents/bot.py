import math
import heapq

class Bot:
    pos = None
    receivedSensor = False
    receivedBeep = False
    k = None
    a = None

    # determines if an alien is within a 2k+1 x 2k+1 square of the bot
    def isWithinSensorRange(self, alienPos):
        k = self.k
        botX, botY = self.pos
        alienX, alienY = alienPos

        return abs(botX - alienX) <= k and abs(botY - alienY) <= k

    # determines the probability that we receive a beep given that the crewmate is in the cell (i, j)
    def pbbBeepGivenCrewmateInCell(self, i, j):
        a = self.a
        x, y = self.pos
        dist = abs(x - i) + abs(y - j)

        return math.exp(-a * (dist - 1))
        

