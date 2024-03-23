from game.agents.bot1 import Bot1

def botFactory(which, ship, k, pos, a):
    match which:
        case 1:
            return Bot1(ship, k, pos, a)
        case _:
            return None