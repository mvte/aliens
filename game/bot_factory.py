from game.agents.bot1 import Bot1
from game.agents.bot2 import Bot2
from game.agents.bot3 import Bot3

def botFactory(which, ship, k, pos, a):
    match which:
        case 1:
            return Bot1(ship, k, pos, a)
        case 2:
            return Bot2(ship, k, pos, a)
        case 3:
            return Bot3(ship, k, pos, a)
        case _:
            return None