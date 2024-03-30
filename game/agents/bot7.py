from game.agents.bot import Bot
from game.ship import Node
import heapq
import game.agents.probability_engines.twoAlien as ta
import game.agents.probability_engines.twoCrewmate as tc
import game.agents.probability_engines.oneCrewmate as oc
import time

'''
Bot 7 is Bot 1, with correct modeling and updates for the fact that there are now two aliens and two
crew members
'''
class Bot7(Bot):
    alienPbbMap = None
    cpe = None
    beepPbbMap = None
    time = None
    validMask = None
    notTransitioned = True

    def __init__(self, ship, k, pos, a):
        self.whichBot = "bot7"
        self.time = 0
        self.pos = pos
        self.k = k
        self.a = a

        self.ape = ta.TwoAlien(ship, k, pos, a)
        self.cpe = tc.TwoCrewmate(ship, k, pos, a)
    

    # the bot should've received beeps or sensor alerts prior to calling this
    def computeNextStep(self, ship):
        self.time += 1

        if self.foundCrewmate and self.notTransitioned:
            self.notTransitioned = False
            collapsedMap = self.cpe.collapseMap(self.pos)
            self.cpe = oc.OneCrewmate(ship, self.k, self.pos, self.a, collapsedMap)

        # update crewmate probabilities
        self.cpe.updateCrewmatePbbMap(self)
        
        # update alien probabilities
        self.ape.updateAlienPbbMap(self)
        self.alienPbbMap = self.ape.getUtilityMap()

        # select the closest target
        target = self.cpe.getTarget(self.pos)

        # move towards the target
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
