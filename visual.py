import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from game.ship import Node
from game.game import State


'''
displays the game state
'''
class Visual:
    def __init__(self, game):
        self.fig, self.ax = plt.subplots(ncols = 3)
        self.game = game


    def update(self):
        if self.game.state != State.RUNNING:
            return

        self.ax[0].clear()
        self.ax[1].clear()
        self.ax[2].clear()
        remapped = self._remap(self.game.sims[0].ship.board)

        sim = sns.heatmap(
            remapped, 
            ax=self.ax[0], 
            vmax=5,
            cbar=False, 
            square=True, 
            xticklabels=False,
            yticklabels=False,
        )
        crewPbb = sns.heatmap(
            self.game.sims[0].bot.crewmatePbbMap,
            ax=self.ax[1], 
            cmap = "rocket_r",
            cbar=False,
            square=True, 
            xticklabels=False,
            yticklabels=False,
        )
        
        alienPbb = sns.heatmap(
            self.game.sims[0].bot.alienPbbMap,
            ax=self.ax[2], 
            cmap = "rocket_r",
            cbar=False,
            square=True, 
            xticklabels=False,
            yticklabels=False,
        )

        self.fig.canvas.draw()

        plt.pause(0.0001)
    

    def _remap(self, board):
        lookup = {
            Node.CLOSED: 1,
            Node.OPEN: np.nan,
        }

        arr = np.array([[lookup[node] for node in row] for row in board])
        
        botPos = self.game.sims[0].bot.pos
        crewmatePos = []
        alienPos = []
        for crewmate in self.game.sims[0].crewmates:
            crewmatePos.append(crewmate.pos)
        for alien in self.game.sims[0].aliens:
            alienPos.append(alien.pos)

        for pos in alienPos:
            arr[pos[0]][pos[1]] = 2
        arr[botPos[0]][botPos[1]] = 3
        for pos in crewmatePos:
            arr[pos[0]][pos[1]] = 4

        return arr

if __name__ == "__main__":
    print("testing")

    
