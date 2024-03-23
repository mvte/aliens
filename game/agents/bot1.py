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
    time = None

    def __init__(self, ship, k, pos, a):
        self.time = 0
        self.pos = pos
        self.k = k
        self.a = a
        self.alienPbbMap = self._initializeAlienPbbMap(ship)
        self.crewmatePbbMap = self._initializeCrewPbbMap(ship)


    def _initializeCrewPbbMap(self, ship):
        pbbMap = [[0 for i in range(ship.dim)] for j in range(ship.dim)]
        numOpen = 0
        for i in range(ship.dim):
            for j in range(ship.dim):
                # the bot does not know where the aliens are, so we consider it open
                open = ship.board[i][j] == Node.OPEN or ship.board[i][j] == Node.ALIEN
                if open and (i, j) != self.pos:
                    numOpen += 1
        
        for i in range(ship.dim):
            for j in range(ship.dim):
                open = ship.board[i][j] == Node.OPEN or ship.board[i][j] == Node.ALIEN
                if open and (i, j) != self.pos:
                    pbbMap[i][j] = 1 / numOpen
                else:
                    pbbMap[i][j] = float("nan")
                    
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
    

    # the bot should've received beeps or sensor alerts prior to calling this
    # 
    def computeNextStep(self, ship):
        self.time += 1

        # update crewmate probabilities
        self._updateCrewmatePbbMap(ship)
        
        # update alien probabilities
        self._updateAlienPbbMap(ship)

        # TODO: a* to the most likely crewmate position, avoiding cells where the alien is known not to be (0% probability)

        # reset received beeps and sensor alerts
        self.receivedBeep = False
        self.receivedSensor = False
        return self.pos
        

    # dr cowan only has three tricks
    # defition of conditional probability
    # marginalization
    # conditional refactoring
    def _updateCrewmatePbbMap(self, ship):
        # want to compute the P(crewmate is in cell i | beep in cell j) for each i
        # i.e. our belief of where the crewmate is given that we heard a beep in cell j
        # blf_t+1(i) = P(S_t+1 | C_t+1 = i) * Blf_t(i)
        # then divide by sum of all blf_t+1(i) to normalize

        # we necessarily have perfect knowledge of the cell we are in
        x, y = self.pos
        self.crewmatePbbMap[x][y] = 0

        sum = 0
        for i in range(ship.dim):
            for j in range(ship.dim):
                open = ship.board[i][j] == Node.OPEN or ship.board[i][j] == Node.ALIEN
                if open and (i, j) != self.pos:
                    p = self.pbbBeepGivenCrewmateInCell(i,j) if self.receivedBeep else (1 - self.pbbBeepGivenCrewmateInCell(i, j))
                    blf = p * self.crewmatePbbMap[i][j]
                    self.crewmatePbbMap[i][j] = blf
                    sum += blf
        
        for i in range(ship.dim):
            for j in range(ship.dim):
                if ship.board[i][j] != Node.CLOSED:
                    self.crewmatePbbMap[i][j] /= sum
        


    def _updateAlienPbbMap(self, ship):
        # want to compute the P(alien is in cell i | sensors go off in cell j) for each i
        # since the alien moves, we want P(alien in cell i !now!)
        pass


    


    