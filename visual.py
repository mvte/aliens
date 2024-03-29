import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from game.ship import Node
from game.game import State


'''
displays the game state
'''
class Visual:
    oneCrewmateLogic = ["bot1", "bot2", "bot3", "bot6"]
    twoCrewmateLogic = ["bot4", "bot5"]

    oneAlienLogic = ["bot1", "bot2", "bot3", "bot4", "bot5", "bot6"]
    
    
    onlyOneGraph = False

    def __init__(self, game):
        if not self.onlyOneGraph:
            self.fig, self.ax = plt.subplots(ncols = 3)
        else:   
            self.fig, self.ax = plt.subplots(ncols = 1)
        self.game = game


    def update(self):
        if self.game.state != State.RUNNING:
            return

        if not self.onlyOneGraph:
            ax = self.ax[0]
            self.ax[1].clear()
            self.ax[2].clear()
        else:
            ax = self.ax
        ax.clear()

        remapped = self._remap(self.game.sims[0].ship.board)

        sim = sns.heatmap(
            remapped, 
            ax=ax, 
            vmax=5,
            cbar=False, 
            square=True, 
            xticklabels=False,
            yticklabels=False,
        )

        if not self.onlyOneGraph:
            if hasattr(self.game.sims[0].bot, "cpe"):
                if self.game.sims[0].bot.whichBot in self.oneCrewmateLogic:
                    crewmatePbbMap = self.game.sims[0].bot.cpe.crewmatePbbMap
                else:
                    crewmatePbbMap = self.game.sims[0].bot.cpe.getUtilityMap()
                
                if self.game.sims[0].bot.whichBot in self.oneAlienLogic:
                    alienPbbMap = self.game.sims[0].bot.ape.alienPbbMap
                else:
                    # todo
                    alienPbbMap = self.game.sims[0].bot.ape.alienPbbMap
            else:
                crewmatePbbMap = self.game.sims[0].bot.crewmatePbbMap
                alienPbbMap = self.game.sims[0].bot.alienPbbMap

            crewPbb = sns.heatmap(
                crewmatePbbMap,
                ax=self.ax[1], 
                cmap = "rocket_r",
                cbar=False,
                square=True, 
                xticklabels=False,
                yticklabels=False,
            )
            alienPbb = sns.heatmap(
                alienPbbMap,
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

    
