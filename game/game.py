from enum import Enum
from .simulation import Simulation
from .ship import Ship, Node
import random
import datetime

'''
Game class

'''
class Game:
    # suite 0 is the test suite
    suiteLookup = {
        0: {
            "bots": [4, 5],
            "crewmates": 2,
            "aliens": 1,
        },
        1: {
            "bots": [1, 2],
            "crewmates": 1,
            "aliens": 1,
        },
        2: {
            "bots": [3, 4, 5],
            "crewmates": 2,
            "aliens": 1,
        },
        3: {
            "bots": [6, 7, 8],
            "crewmates": 2,
            "aliens": 2,
        },
    }

    config = None
    state = None
    suite = None
    sims = []
    ships = []
    filename = None

    currentShip = 0

    symbols = ['|', '/', '-', '\\']
    i = 0


    def __init__(self, config):
        self.config = config
        self.suite = self.suiteLookup[config["suite"]]
        self.state = State.INITIALIZING
        self.i = 0
        pass
        

    def update(self):
        match self.state:
            case State.INITIALIZING:
                self._handle_initializing()
            case State.READY:
                self._handle_ready()
                pass
            case State.RUNNING:
                self._handle_running()
                pass
            case State.TRANSITION:
                self._handle_transition()
                pass
    

    def change_state(self, new_state):
        self.state = new_state


    def _handle_initializing(self):
        print("initializing")
        print(self.config)
        print(self.suite)

        # create file to store results
        self._createFile()

        # generate ship layouts
        ships = []
        for i in range(self.config["layouts"]):
            ships.append(Ship(self.config["dim"]))
        self.ships = ships

        self.prepareSimulations()
        self.state = State.READY

    
    def _createFile(self):    
        # data section
        date = datetime.datetime.now().strftime("%m.%d %H.%M")
        self.filename = f"results/suite{self.config['suite']}/ s{self.config['suite']}k{self.config['k']}a{self.config['a']} - {date}.csv"
        dataHeader = "layout,bot,successes,failures,moves to crewmate,crewmates saved\n"
        with open(self.filename, "w") as f:
            f.write(dataHeader)


    def prepareSimulations(self):
        # generate initial bot, alien, and crewmate positions for the current ship layout
        for i in range(self.config["positions"]):
            positions = self.generatePositions(self.ships[self.currentShip])
        
        self.sims = []
        # create simulations for each bot
        for i in range(len(self.suite["bots"])):
            self.sims.append(Simulation(self.config, self.ships[self.currentShip], positions, self.suite["bots"][i]))


    def _handle_ready(self):
        print("ready")
        self.state = State.RUNNING


    def _handle_running(self):
        self.i = (self.i + 1) % len(self.symbols)
        print(f'\r\033[K{self.symbols[self.i]} running...', flush=True, end='')

        finished = True
        for sim in self.sims:
            sim.step()
            finished = finished and sim.finished
        
        if finished:
            self.state = State.TRANSITION
    

    # transition to the next set of simulations
    def _handle_transition(self):
        print("transitioning to next layout")

        # write the data for the current set of simulations to the file
        # layout, bot, successes, failures, moves to crewmate, crewmates saved
        with open(self.filename, "a") as f:
            for sim in self.sims:
                f.write(f"{self.currentShip},{sim.bot.whichBot},{sim.successes},{sim.failures},{sim.movesToCrewmate},{sim.crewmatesSaved}\n")

        # move to the next ship layout, or end the game if we've reached the end
        self.currentShip += 1
        if self.currentShip >= len(self.ships):
            self.state = State.DONE
            return

        # create new simulations for new layout and positions
        self.prepareSimulations()
        self.state = State.READY
    

    # generates 10 random positions for the bot, crewmates, and aliens for this layout
    # e.g. positions["bot"][0] is the bot's position for the first set of simulations
    def generatePositions(self, ship):
        botPositions = []
        crewmatePositions = []
        alienPositions = []

        for i in range(self.config["positions"]):
            # place bot
            botX, botY = random.randint(0, self.config["dim"] - 1), random.randint(0, self.config["dim"] - 1)
            while ship.board[botX][botY] == Node.CLOSED:
                botX, botY = random.randint(0, self.config["dim"] - 1), random.randint(0, self.config["dim"] - 1)
            botPositions.append((botX, botY))

            # place crewmates
            crew = []
            for i in range(self.suite["crewmates"]):
                crewX, crewY = random.randint(0, self.config["dim"] - 1), random.randint(0, self.config["dim"] - 1)
                while ship.board[crewX][crewY] == Node.CLOSED or (crewX, crewY) == (botX, botY) or (crewX, crewY) in crew:
                    crewX, crewY = random.randint(0, self.config["dim"] - 1), random.randint(0, self.config["dim"] - 1)
                crew.append((crewX, crewY))
            crewmatePositions.append(crew)

            # place aliens
            aliens = []
            for i in range(self.suite["aliens"]):
                alienX, alienY = random.randint(0, self.config["dim"] - 1), random.randint(0, self.config["dim"] - 1)
                while ship.board[alienX][alienY] == Node.CLOSED or (alienX, alienY) in aliens or self.isWithinSensorRange((botX, botY), (alienX, alienY)):
                    alienX, alienY = random.randint(0, self.config["dim"] - 1), random.randint(0, self.config["dim"] - 1)
                aliens.append((alienX, alienY))
            alienPositions.append(aliens)

        return {
            "bot": botPositions,
            "crewmates": crewmatePositions,
            "aliens": alienPositions,
        }


    def isWithinSensorRange(self, botPos, alienPos):
        k = self.config["k"]
        botX, botY = botPos
        alienX, alienY = alienPos

        return abs(botX - alienX) <= k and abs(botY - alienY) <= k

class State(Enum):
    # sets up the game as per the config
    INITIALIZING  = 1
    # ready to start the game
    READY = 2
    # game is running
    RUNNING = 3
    # in the case of certain configurations, the game may need to modify its configuration
    TRANSITION = 4
    # game is done
    DONE = 5