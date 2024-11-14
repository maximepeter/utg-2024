from typing import List, NamedTuple, Dict, Optional, Literal, cast, get_args
import sys
import math
import heapq

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

def log(*message: str):
    print(*message, file=sys.stderr)


ProteinType = Literal['A', 'B', 'C', 'D']
DirectionType = Literal['N', 'E', 'S', 'W']
OrganType = Literal['ROOT', 'BASIC', 'HARVESTER']
WALL: str = 'WALL'

width: int
height: int
width, height = [int(i) for i in input().split()]


class Pos(NamedTuple):
    x: int
    y: int


class Organ(NamedTuple):
    id: int
    owner: int
    parent_id: int
    root_id: int
    pos: Pos
    organ_type: OrganType
    dir: DirectionType


class Protein(NamedTuple):
    pos: Pos
    protein_type: ProteinType


WALL_WEIGHT = 100
PROTEIN_WEIGHT = 100
EMPTY_WEIGHT = 1
ENEMY_WEIGHT = 100

class Cell(NamedTuple):
    pos: Pos
    isWall: bool = False
    protein: Optional[ProteinType] = None
    organ: Optional[Organ] = None
    weight: int


class Grid:
    cells: List[Cell] = []

    def __init__(self) -> None:
        self.reset()
    
    def reset(self) -> None:
        self.cells = []
        for y in range(height):
            for x in range(width):
                self.cells.append(Cell(Pos(x, y), weight=EMPTY_WEIGHT))

    def get_cell(self, pos: Pos) -> Optional[Cell]:
        if width > pos.x >= 0 and height > pos.y >= 0:
            return self.cells[pos.x + width * pos.y]
        return None
    
    def set_cell(self, pos: Pos, cell: Cell) -> None:
        self.cells[pos.x + width * pos.y] = cell


class Game:
    grid: Grid
    my_proteins: Dict[ProteinType, int]
    opp_proteins: Dict[ProteinType, int]
    my_organs: List[Organ]
    opp_organs: List[Organ]
    free_proteins = List[Protein]
    organ_map: Dict[int, Organ]

    def __init__(self) -> None:
        self.grid = Grid()
        self.reset()

    def reset(self) -> None:
        self.my_proteins = {}
        self.opp_proteins = {}
        self.grid.reset()
        self.my_organs = []
        self.opp_organs = []
        self.free_proteins = []
        self.organ_map = {}


game: Game = Game()

# game loop
while True:
    game.reset()

    entity_count: int = int(input())
    for i in range(entity_count):
        inputs: List[str] = input().split()
        x: int = int(inputs[0])
        y: int = int(inputs[1])
        pos: Pos = Pos(x, y)
        _type: str = inputs[2]
        owner: int = int(inputs[3])
        organ_id: int = int(inputs[4])
        organ_dir: DirectionType = cast(DirectionType, inputs[5])
        organ_parent_id: int = int(inputs[6])
        organ_root_id: int = int(inputs[7])

        cell: Optional[Cell] = None
        organ: Optional[Organ] = None

        if _type == WALL:
            cell = Cell(pos, True, weight=WALL_WEIGHT)
        elif _type in get_args(ProteinType):
            cell = Cell(pos, False, cast(ProteinType, _type), weight=PROTEIN_WEIGHT)
            protein = Protein(pos, _type)
            game.free_proteins.append(protein)
        else:
            organ = Organ(organ_id, owner, organ_parent_id, organ_root_id, pos, cast(OrganType, _type), organ_dir)
            cell = Cell(pos, False, None, organ, weight=ENEMY_WEIGHT)
            if owner == 1:
                game.my_organs.append(organ)
            else:
                game.opp_organs.append(organ)
            game.organ_map[organ_id] = organ
        
        if cell != None:
            game.grid.set_cell(pos, cell)

    my_proteins: List[int] = [int(i) for i in input().split()]
    opp_proteins: List[int] = [int(i) for i in input().split()]

    game.my_proteins = { 'A': my_proteins[0], 'B': my_proteins[1], 'C': my_proteins[2], 'D': my_proteins[3] }
    game.opp_proteins = { 'A': opp_proteins[0], 'B': opp_proteins[1], 'C': opp_proteins[2], 'D': opp_proteins[3] }

    required_actions_count: int = int(input())

    for i in range(required_actions_count):

        # Write an action using print
        # To debug: print("Debug messages...", file=sys.stderr, flush=True)
        my_last_organ = game.my_organs[-1]
        my_last_organ_id = my_last_organ.id

        opp_last_organ = game.opp_organs[-1]
        opp_pos = opp_last_organ.pos
        opp_x, opp_y = opp_pos.x, opp_pos.y

        print(f"GROW {my_last_organ_id} {opp_x} {opp_y} BASIC")


# HARVERSTING STRAT:
    # p = get closest protein
    # go NEXT TO p
    # harvest p (get direction)
    # get closest : *enemy* or *protein* (strategy)
    # EXCLUDE PROTEINS FROM PATH

# -----------------------------------

# TO TEST
# Returns the List[Pos] of the shortest path. Empty if it's unreachable.
def dijkstra_shortest_path(grid: Grid, start_x, start_y, goal_x, goal_y) -> List[Pos]:
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    min_heap = [(0, start_x, start_y)]  # (cost, x, y)
    min_cost = {(start_x, start_y): 0}
    predecessor = {(start_x, start_y): None}  # To track the path

    while min_heap:
        current_cost, x, y = heapq.heappop(min_heap)
        
        # If we reach the goal, reconstruct the path
        if x == goal_x and y == goal_y:
            path = []
            while (x, y) is not None:
                path.append(Pos(x, y))
                x, y = predecessor[(x, y)]
            return path[::-1]  # Reverse the path to go from start to goal
        
        # Explore neighbors
        for dx, dy in directions:
            nx, ny = x + dx, y + dy # neighbor
            if 0 <= nx < height and 0 <= ny < width:
                new_cost = current_cost + grid.get_cell(Pos(nx, ny)).weight
                neighbor = (nx, ny)
                
                # Only add to heap if we found a cheaper way to get to (nx, ny)
                if neighbor not in min_cost or new_cost < min_cost[neighbor]:
                    min_cost[neighbor] = new_cost
                    predecessor[neighbor] = (x, y)
                    heapq.heappush(min_heap, (new_cost, nx, ny))

    # If there's no path to the goal, return None or an empty list
    return []
