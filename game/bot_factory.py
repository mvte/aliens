from game.agents.bot1 import Bot1

def botFactory(which, ship):
    match which:
        case 1:
            return Bot1(ship)
        case _:
            return None