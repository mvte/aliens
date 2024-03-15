from game.agents.bot import Bot
from game.ship import Node

'''
At the start, the bot knows that the alien is equally likely to be in any open cell outside the bot’s
detection square, and the crew member is equally likely to be in any cell other than the bot’s initial cell. At
every point in time, update what is known about the crew member and the alien based on the data received
(How? ). (Note: the bot necessarily has perfect knowledge of the cell that it is currently in.) Note, when the
alien has the opportunity to move, the bot’s knowledge of the alien should be updated accordingly (How? ).
The bot should proceed by moving toward the cell most likely to contain the crew member (breaking ties at
random), sticking (when possible) to cells that definitely do not contain the alien. If necessary, the bot should
flee towards cells where the alien is known not to be.
'''
class Bot1(Bot):
    alienPbbMap = None
    crewmatePbbMap = None
    steps = None

    def __init__(self, ship):
        self.alienPbbMap = self._initializePbbMap(ship)
        self.crewmatePbbMap = self._initializePbbMap(ship)
        self.steps = 0
        self.pos = (0, 0)


    def _initializePbbMap(self, ship):
        pbbMap = {}
        numOpen = 0
        for i in range(ship.dim):
            for j in range(ship.dim):
                if ship.board[i][j] == Node.OPEN:
                    numOpen += 1
        
        for i in range(ship.dim):
            for j in range(ship.dim):
                if ship.board[i][j] == Node.OPEN:
                    pbbMap[(i, j)] = 1 / numOpen
                else:
                    pbbMap[(i, j)] = 0
                    
        return pbbMap
    

    # the bot should've received beeps or sensor alerts prior to calling this
    def computeNextStep(self, ship):
        self.steps += 1

        # update crewmate probabilities
        self._updateCrewmatePbbMap(ship)
        
        # update alien probabilities
        self._updateAlienPbbMap(ship)

        # TODO: a* to the most likely crewmate position, avoiding cells where the alien is known not to be (0% probability)

        return self.pos
        

    def _updateCrewmatePbbMap(self, ship):
        pass


    def _updateAlienPbbMap(self, ship):
        pass


    


    