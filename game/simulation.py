from .ship import Ship, Node
from .bot_factory import botFactory
from .agents.crewmate import Crewmate
from .agents.alien import Alien
import math
import random

class Simulation:
    # set of aliens
    aliens = None
    # set of crewmates
    crewmates = None

    ship = None
    bot = None
    config = None
    finished = False
    positions = {}
    whichBot = None

    # state
    currentIteration = 0
    positionsIndex = 0
    time = 0

    # stats
    successes = 0
    failures = 0
    movesToCrewmate = 0
    crewmatesSaved = 0

    def __init__(self, config, ship, positions, whichBot):
        self.config = config
        self.ship = ship
        self.positions = positions
        self.whichBot = whichBot
        self.time = 0
        self.aliens = set()
        self.crewmates = set()

        # place the bot, crewmates, and aliens for first set of iterations
        self._placeBot(whichBot, positions["bot"][0])
        self._placeCrewmates(positions["crewmates"][0])
        self._placeAliens(positions["aliens"][0])
    
    # places the bot in a random open position on the ship
    def _placeBot(self, whichBot, pos):
        bot = botFactory(whichBot, self.ship, self.config["k"], pos, self.config["a"])
        self.bot = bot


    # places crewmates in random position that isn't the bot's position
    def _placeCrewmates(self, crewmatePositions):
        for pos in crewmatePositions:
            self.crewmates.add(Crewmate(pos))
    

    # places aliens in random position that isn't within the bot's sensor range
    def _placeAliens(self, alienPositions):
        for pos in alienPositions:
            self.aliens.add(Alien(pos))


    def _getManhattanDistance(self, pos1, pos2):
        x1, y1 = pos1
        x2, y2 = pos2
        return abs(x1 - x2) + abs(y1 - y2)


    def step(self):
        if self.finished:
            return
        
        # simulate beep
        for crew in self.crewmates:
            dist = self._getManhattanDistance(self.bot.pos, crew.pos)
            a = self.config["a"]
            p = math.exp(-a * (dist - 1))
            if random.random() < p:
                self.bot.receivedBeep = True

        # simulate sensor
        for alien in self.aliens:
            if self.bot.isWithinSensorRange(alien.pos):
                self.bot.receivedSensor = True

        # update the bot
        botX, botY = self.bot.computeNextStep(self.ship)
        
        # determine if the bot is on an alien
        for alien in self.aliens:
            if alien.pos == self.bot.pos:
                self.endRun(False)
                return

        # determine if the bot has found all the crewmates
        toRemove = set()
        for crewmate in self.crewmates:
            if crewmate.pos == self.bot.pos:
                toRemove.add(crewmate)
                self.crewmatesSaved += 1
        self.crewmates -= toRemove
        if not self.crewmates:
            self.endRun(True)
            return
    
        # advance the aliens
        randomizedAliens = list(self.aliens)
        random.shuffle(randomizedAliens)
        for alien in randomizedAliens:
            newX, newY = alien.computeNextStep(self.ship)
        
        # determine if the bot is on an alien
        for alien in self.aliens:
            if alien.pos == self.bot.pos:
                self.endRun(False)
                return
        
        self.time += 1
    

    def endRun(self, success):
        # update stats
        if success:
            self.successes += 1
            self.movesToCrewmate += self.time
        else:
            self.failures += 1
        
        # move to the next iteration
        self.currentIteration += 1

        # reset time
        self.time = 0

        # if we've reached the end of the iterations, move to the next set of positions
        if self.currentIteration == self.config["iterations"]:
            self.currentIteration = 0
            self.positionsIndex += 1
        
        # if we've reached the end of the positions, end the simulation
        if self.positionsIndex == self.config["positions"]:
            self.endSimulation()
            return
        
        # reset the bot, crewmates, and aliens
        self.aliens = set()
        self.crewmates = set()
        self.bot = None
        self._placeBot(self.whichBot, self.positions["bot"][self.positionsIndex])
        self._placeCrewmates(self.positions["crewmates"][self.positionsIndex])
        self._placeAliens(self.positions["aliens"][self.positionsIndex])


    def endSimulation(self):
        self.finished = True
        print("\nsimulation has ended")
        print(self.bot.whichBot)
        print("successes: ", self.successes)
        print("failures: ", self.failures)
        print("moves to crewmate: ", self.movesToCrewmate)
        print("crewmates saved: ", self.crewmatesSaved)
        
