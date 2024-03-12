import random
from enum import Enum

'''
a ship is a boolean grid of size dim x dim
if a node is True, then that node is open and crewmates/aliens/bots can move into it
if a node is False, then that node is closed and these^ cannot move into it
'''
class Ship:
    board = None

    def __init__(self, dim):
        print("creating ship")
        tempBoard = generate_ship(dim)
        for i in range(dim):
            for j in range(dim):
                if tempBoard[i][j]:
                    tempBoard[i][j] = Node.OPEN
                else:
                    tempBoard[i][j] = Node.CLOSED
        
        self.board = tempBoard
    
    def get_ship(self):
        return self.board
    

class Node(Enum):
    OPEN = 1
    CLOSED = 2
    ALIEN = 3
    CREWMATE = 4
    BOT = 5

'''
1. Choose a square at random
2. Iterate:
    a. Identify all currently blocked cells that have exactly one neighbor
    b. Open one of those cells at random
    c. Repeat until no more cells can be opened
3. Identify all cells that are 'dead ends' - open cells with one neighbor
4. For approximately half these cells, pick one of their closed neighbors and open it
'''
def generate_ship(dim):
    # create a local random so it's threadsafe
    localRandom = random.Random()
    dirs = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    # create a dim x dim grid of False
    ship = [[False for i in range(dim)] for j in range(dim)]
    # choose a square at random to open
    startX = localRandom.randint(0, dim - 1)
    startY = localRandom.randint(0, dim - 1)
    ship[startX][startY] = True

    openNodes = [(startX, startY)]
    while True:
        # identify blocked cells that have neighbors
        blockedNodes = []
        for node in openNodes:
            x, y = node
            for dir in dirs:
                dx, dy = dir
                if x + dx < 0 or x + dx >= dim or y + dy < 0 or y + dy >= dim:
                    continue
                if not ship[x + dx][y + dy]:
                    blockedNodes.append((x + dx, y + dy))
                
        # of those blocked cells, find the ones with exactly one open neighbor
        singleNeighborNodes = []
        for node in blockedNodes:
            x, y = node
            neighbors = 0
            for dir in dirs:
                dx, dy = dir
                if x + dx < 0 or x + dx >= dim or y + dy < 0 or y + dy >= dim:
                    continue
                if ship[x + dx][y + dy]:
                    neighbors += 1
            if neighbors == 1:
                singleNeighborNodes.append(node)
        
        # if there are no single neighbor nodes, then we're done
        if not singleNeighborNodes:
            break
            
        # open one of the single neighbor nodes at random
        node = localRandom.choice(singleNeighborNodes)
        x, y = node
        ship[x][y] = True
        openNodes.append(node)

    # identify dead ends - open cells with one open neighbor
    deadEnds = []
    for node in openNodes:
        x, y = node
        neighbors = 0
        for dir in dirs:
            dx, dy = dir
            if x + dx < 0 or x + dx >= dim or y + dy < 0 or y + dy >= dim:
                continue
            if ship[x + dx][y + dy]:
                neighbors += 1
        if neighbors == 1:
            deadEnds.append(node)

    # for approximately half the dead ends, pick one of their closed neighbors and open it
    for node in deadEnds:
        if localRandom.random() < 0.5:
            continue
        x, y = node
        neighbors = []
        for dir in dirs:
            dx, dy = dir
            if x + dx < 0 or x + dx >= dim or y + dy < 0 or y + dy >= dim:
                continue
            if not ship[x + dx][y + dy]:
                neighbors.append((x + dx, y + dy))
        if neighbors:
            neighbor = localRandom.choice(neighbors)
            x, y = neighbor
            ship[x][y] = True
            openNodes.append(neighbor)
    
    return ship


def generate_ships_parallel(dim, num_ships):
    pass