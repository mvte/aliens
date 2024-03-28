from game.agents.bot import Bot
from game.ship import Node
import random
import heapq

'''
Bot 3 is just Bot 1 applied in this new setting, but when the first crew member is found, they are
teleported away, and the updates continue until the second crewmember is found. This can be implemented by
simply keeping the same current probabilities of where a crew member is, though updated appropriately after
the found crewmember is teleported away

this means we don't have to change anything for bot 3
'''
class Bot3(Bot):
    alienPbbMap = None
    crewmatePbbMap = None
    time = None

    def __init__(self, ship, k, pos, a):
        self.whichBot = "bot3"
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
                open = ship.board[i][j] == Node.OPEN
                if open and (i, j) != self.pos:
                    numOpen += 1
        
        for i in range(ship.dim):
            for j in range(ship.dim):
                open = ship.board[i][j] == Node.OPEN
                if open and (i, j) != self.pos:
                    pbbMap[i][j] = 1 / numOpen
                else:
                    pbbMap[i][j] = float("nan")
                    
        return pbbMap
    
    def _initializeAlienPbbMap(self, ship):
        pbbMap = [[0 for i in range(ship.dim)] for j in range(ship.dim)]
        numOpen = 0
        for i in range(ship.dim):
            for j in range(ship.dim):
                if ship.board[i][j] == Node.OPEN and (i, j) != self.pos and not self.isWithinSensorRange((i, j)):
                    numOpen += 1
        
        for i in range(ship.dim):
            for j in range(ship.dim):
                if ship.board[i][j] == Node.OPEN and (i, j) != self.pos and not self.isWithinSensorRange((i, j)):
                    pbbMap[i][j] = 1 / numOpen
                elif ship.board[i][j] == Node.CLOSED:
                    pbbMap[i][j] = float("nan")
                else:
                    pbbMap[i][j] = 0
                    
        return pbbMap
    

    # the bot should've received beeps or sensor alerts prior to calling this
    # 
    def computeNextStep(self, ship):
        self.time += 1

        # update crewmate probabilities
        target = self._updateCrewmatePbbMap(ship)
        
        # update alien probabilities
        self._updateAlienPbbMap(ship)

        # TODO: a* to the most likely crewmate position, avoiding cells where the alien is known not to be (0% probability)
        next = self._aStar(ship, self.pos, target)
        if next and len(next) > 0:
            self.pos = next[1]

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
        q = []
        x, y = self.pos
        self.crewmatePbbMap[x][y] = 0

        sum = 0
        for i in range(ship.dim):
            for j in range(ship.dim):
                open = ship.board[i][j] == Node.OPEN
                if open and (i, j) != self.pos:
                    p = self.pbbBeepGivenCrewmateInCell(i,j) if self.receivedBeep else (1 - self.pbbBeepGivenCrewmateInCell(i, j))
                    blf = p * self.crewmatePbbMap[i][j]
                    self.crewmatePbbMap[i][j] = blf
                    sum += blf
                    heapq.heappush(q, (-blf, (i, j)))
        
        for i in range(ship.dim):
            for j in range(ship.dim):
                if ship.board[i][j] != Node.CLOSED:
                    self.crewmatePbbMap[i][j] /= sum
        
        selected = []
        blf, pos = heapq.heappop(q)
        selected.append(pos)
        while q and blf == q[0][0]:
            _, pos = heapq.heappop(q)
            selected.append(pos)

        return random.choice(selected)


    def _updateAlienPbbMap(self, ship):
        # want to compute the P(alien is in cell i | sensors go off in cell j) for each i
        # since the alien moves, we want P(alien in cell i !now!)
        newPbbMap = [[0 for i in range(ship.dim)] for j in range(ship.dim)]
        sum = 0
        for i in range(ship.dim):
            for j in range(ship.dim):
                # we skip closed cells
                if ship.board[i][j] == Node.CLOSED:
                    newPbbMap[i][j] = float("nan")
                    continue
                # if the cell is out of sensor range but the sensor went off, then the alien cannot be there
                if self.receivedSensor and not self.isWithinSensorRange((i, j)):
                    continue
                # if the cell is within sensor range but the sensor didn't go off, then the alien cannot be there
                if not self.receivedSensor and self.isWithinSensorRange((i, j)):
                    continue
                
                # the alien can only be in this cell if the alien was in a neighboring cell
                # so we calculate the pbb of the alien in this cell based off the pbb of the alien in the neighboring cells
                # blf_t+1(i) = ∑_i' (Blf_t(i') * P(A_t+1 = i | A_t = i')
                blf = 0
                for nb in ship.getValidMoves((i, j)):
                    x, y = nb
                    numNeighbors = len(ship.getValidMoves(nb))
                    if numNeighbors == 0:
                        numNeighbors = 1
                    blf += self.alienPbbMap[x][y] / numNeighbors
                sum += blf
                newPbbMap[i][j] = blf

        # normalize
        for i in range(ship.dim):
            for j in range(ship.dim):
                if ship.board[i][j] != Node.CLOSED:
                    newPbbMap[i][j] /= sum
        self.alienPbbMap = newPbbMap

    # a* search given ship, bot position, and target position
    def _aStar(self, ship, s, g):
        fringe = []
        heapq.heappush(fringe, (0, s))
        dist = {s: 0}
        prev = {s: s}
        firstStep = True

        while fringe:
            _, u = heapq.heappop(fringe)
            if u == g:
                break

            for v in ship.getValidMoves(u):
                vx, vy = v
                # at the very least, our first step should be to a cell that definitely does not contain the alien
                if firstStep and self.alienPbbMap[vx][vy] > 0:
                    continue
                # all other steps should be to cells under some probability of containing the alien
                elif not firstStep and self.alienPbbMap[vx][vy] > 0.1:
                    continue

                alt = dist[u] + 1
                if v not in dist or alt < dist[v]:
                    dist[v] = alt
                    prev[v] = u
                    heapq.heappush(fringe, (alt + self._h(v, g), v))

                firstStep = False
        
        if g not in prev:
            return None

        path = []
        u = g
        while u != s:
            path.append(u)
            u = prev[u]
        path.append(s)
        path.reverse()

        return path

    # manhattan distance
    def _h(self, u, v):
        return abs(u[0] - v[0]) + abs(u[1] - v[1])




                    




                



    


    