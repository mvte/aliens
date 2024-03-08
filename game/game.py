from enum import Enum

class Game:
    config = None
    state = None
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
    

    def change_state(self, new_state):
        self.state = new_state


    def _handle_initializing(self):
        print("initializing")
        print(self.config)
        self.state = State.READY

    def _handle_ready(self):
        print("ready")
        self.state = State.DONE



class State(Enum):
    INITIALIZING  = 1
    READY = 2
    RUNNING = 3
    DONE = 4