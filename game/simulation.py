from .ship import Ship, Node
from .bot_factory import botFactory
from .agents.crewmate import Crewmate
from .agents.alien import Alien
import math
import random

class Simulation:
    # set of aliens
    aliens = set()
    # set of crewmates
    crewmates = set()

    ship = None
    bot = None
    config = None
    finished = False

    # step limiter
    steps = 0
    MAX_STEPS = 1000

    # stats
    successes = 0
    failures = 0

    def __init__(self, config):
        self.config = config
        self.ship = Ship(config["dim"])
        
        # place bot
        self._placeBot(config["bot"])

        # place crewmates
        self._placeCrewmates(config["crewmates"])

        # place aliens
        self._placeAliens(config["aliens"])

    
    # places the bot in a random open position on the ship
    def _placeBot(self, whichBot):
        x, y = random.randint(0, self.config["dim"] - 1), random.randint(0, self.config["dim"] - 1)
        while self.ship.board[x][y] == Node.CLOSED:
            x, y = random.randint(0, self.config["dim"] - 1), random.randint(0, self.config["dim"] - 1)

        bot = botFactory(whichBot, self.ship, self.config["k"], (x, y), self.config["a"])
        self.bot = bot


    # places crewmates in random position that isn't the bot's position
    def _placeCrewmates(self, numCrewmates):
        for i in range(numCrewmates):
            x, y = random.randint(0, self.config["dim"] - 1), random.randint(0, self.config["dim"] - 1)
            while self.ship.board[x][y] == Node.CLOSED or self.bot.pos == (x, y):
                x, y = random.randint(0, self.config["dim"] - 1), random.randint(0, self.config["dim"] - 1)

            self.crewmates.add(Crewmate((x, y)))
    

    # places aliens in random position that isn't within the bot's sensor range
    def _placeAliens(self, numAliens):
        botPos = self.bot.pos

        for i in range(numAliens):
            x, y = random.randint(0, self.config["dim"] - 1), random.randint(0, self.config["dim"] - 1)
            while self.ship.board[x][y] == Node.CLOSED or self.bot.isWithinSensorRange((x, y)):
                x, y = random.randint(0, self.config["dim"] - 1), random.randint(0, self.config["dim"] - 1)

            self.aliens.add(Alien((x, y)))
            self.ship.board[x][y] = Node.ALIEN


    def _getManhattanDistance(self, pos1, pos2):
        x1, y1 = pos1
        x2, y2 = pos2
        return abs(x1 - x2) + abs(y1 - y2)

    # TODO: implement the simulation logic
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
                self.bot.alienDetected = True

        # update the bot
        botX, botY = self.bot.computeNextStep(self.ship)
        
        # determine if the bot is on an alien
        if self.ship.board[botX][botY] == Node.ALIEN:
            self.endRun(False)
            return

        # determine if the bot has found all the crewmates
        for crewmate in self.crewmates:
            if crewmate.pos == self.bot.pos:
                self.crewmates.remove(crewmate)
        if not self.crewmates:
            self.endRun(True)
            return
    
        # advance the aliens
        randomizedAliens = list(self.aliens)
        random.shuffle(randomizedAliens)
        for alien in randomizedAliens:
            oldX, oldY = alien.pos
            newX, newY = alien.computeNextStep(self.ship)
            self.ship.board[oldX][oldY] = Node.OPEN
            self.ship.board[newX][newY] = Node.ALIEN
        
        # determine if the bot is on an alien
        if self.ship.board[botX][botY] == Node.ALIEN:
            self.endRun(False)
            return
        
        self.steps += 1


    def endRun(self, success):
        self.finished = True
        if success:
            print("bot has found all crewmates")
        else:
            print("bot has been caught by an alien")
        
