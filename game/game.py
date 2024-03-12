from enum import Enum
from .ship import Ship, Node

class Game:
    config = None
    state = None
    ship = None
    def __init__(self, config):
        self.config = config
        self.state = State.INITIALIZING
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
        self.ship = Ship(self.config["dim"])
        self.state = State.READY


    def _handle_ready(self):
        print("ready")
        self.state = State.DONE



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