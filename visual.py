import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from game.ship import Node


'''
displays the game state
'''
class Visual:
    def __init__(self, game):
        self.fig, self.ax = plt.subplots(ncols = 2)
        self.game = game


    def update(self):
        self.ax[0].clear()
        self.ax[1].clear()
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

        self.fig.canvas.draw()

        plt.pause(0.0001)
    

    def _remap(self, board):
        lookup = {
            Node.CLOSED: 1,
            Node.OPEN: np.nan,
            Node.ALIEN: 2,
        }

        arr = np.array([[lookup[node] for node in row] for row in board])
        
        botPos = self.game.sims[0].bot.pos
        crewmatePos = []
        for crewmate in self.game.sims[0].crewmates:
            crewmatePos.append(crewmate.pos)

        arr[botPos[0]][botPos[1]] = 3
        for pos in crewmatePos:
            arr[pos[0]][pos[1]] = 4

        return arr

    
