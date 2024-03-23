from game.agents.bot import Bot
from game.ship import Node

'''
This bot computes the probability of alien being in each cell and the probability of crewmate being in each cell, but also
the utility of each cell. Then, as opposed to A* search to the most likely crewmate position, moves to the cell with the
highest utility. The 

U(cell) = 
'''
class Bot2(Bot):
    alienPbbMap = None
    crewmatePbbMap = None
    utilityMap = None
    time = None

    def __init__(self, ship, k):
        self.alienPbbMap = self._initializeAlienPbbMap(ship)
        self.crewmatePbbMap = self._initializeCrewPbbMap(ship)
        self.utilityMap = self._initializeUtilityMap(ship)
        self.pos = (0, 0)
        self.k = k
    
    def _initializeCrewPbbMap(self, ship):
        pbbMap = {}
        numOpen = 0
        for i in range(ship.dim):
            for j in range(ship.dim):
                if ship.board[i][j] == Node.OPEN and (i, j) != self.pos:
                    numOpen += 1
        
        for i in range(ship.dim):
            for j in range(ship.dim):
                if ship.board[i][j] == Node.OPEN and (i, j) != self.pos:
                    pbbMap[(i, j)] = 1 / numOpen
                else:
                    pbbMap[(i, j)] = 0
                    
        return pbbMap
    
    def _initializeAlienPbbMap(self, ship):
        pbbMap = {}
        numOpen = 0
        for i in range(ship.dim):
            for j in range(ship.dim):
                if ship.board[i][j] == Node.OPEN and (i, j) != self.pos and not self.isWithinSensorRange((i, j)):
                    numOpen += 1
        
        for i in range(ship.dim):
            for j in range(ship.dim):
                if ship.board[i][j] == Node.OPEN and (i, j) != self.pos and not self.isWithinSensorRange((i, j)):
                    pbbMap[(i, j)] = 1 / numOpen
                else:
                    pbbMap[(i, j)] = 0
                    
        return pbbMap
    

    def _initializeUtilityMap(self, ship):
        pass