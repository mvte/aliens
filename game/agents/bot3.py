from game.agents.bot import Bot
from game.ship import Node
import game.agents.probability_engines.oneCrewmate as oc
import game.agents.probability_engines.oneAlien as oa
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
    time = None

    def __init__(self, ship, k, pos, a):
        self.whichBot = "bot3"
        self.time = 0
        self.pos = pos
        self.k = k
        self.a = a
        
        self.ape = oa.OneAlien(ship, k, pos, a)
        self.cpe = oc.OneCrewmate(ship, k, pos, a)
    

    # the bot should've received beeps or sensor alerts prior to calling this
    def computeNextStep(self, ship):
        self.time += 1

        # update crewmate probabilities
        self.cpe.updateCrewmatePbbMap(self)
        
        # update alien probabilities
        self.ape.updateAlienPbbMap(self)

        # TODO: a* to the most likely crewmate position, avoiding cells where the alien is known not to be (0% probability)
        target = self.cpe.getTarget(self.pos)
        next = self._aStar(ship, self.pos, target)
        if next and len(next) > 0:
            self.pos = next[1]

        # reset received beeps and sensor alerts
        self.receivedBeep = False
        self.receivedSensor = False
        return self.pos


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
                if firstStep and self.ape.alienPbbMap[vx][vy] > 0:
                    continue
                # all other steps should be to cells under some probability of containing the alien
                elif not firstStep and self.ape.alienPbbMap[vx][vy] > 0.1:
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




                    




                



    


    