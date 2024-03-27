from game.game import Game, State
from visual import Visual
import sys
import json
import datetime

def main():
    timestart = datetime.datetime.now()

    config = None
    with open("config.json", "r") as f:
        config = json.load(f)
    game = Game(config)

    visual = None
    if len(sys.argv) > 1 and sys.argv[1] == "visualize":
        visual = Visual(game)

    while True:
        game.update()
        
        if visual:
            visual.update()

        if game.state == State.DONE:
            break
    
    print("time elapsed", datetime.datetime.now() - timestart)
    print("game over")


if __name__ == "__main__":
    main()