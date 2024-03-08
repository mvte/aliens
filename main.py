from game.game import Game, State
import sys

def main():
    game = Game({
        "dim": 35,
        "bot": "bot",
    })

    while True:
        game.update()

        if game.state == State.DONE:
            break
    
    print("game over")


if __name__ == "__main__":
    main()