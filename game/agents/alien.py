import random

class Alien:
    pos = None


    def __init__(self, pos): 
        self.pos = pos


    # returns the next step the alien is going to take (randomly chosen from the 4 possible directions)
    def computeNextStep(self, ship):
        validMoves = ship.getValidAlienMoves(self.pos)
        if len(validMoves) == 0:
            return self.pos
        newPos = random.choice(validMoves)
        self.pos = newPos
        return newPos

