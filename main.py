from typing import List, NamedTuple, Dict, Optional, Literal, cast, get_args
import sys
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
PROTEIN_WEIGHT = 1
EMPTY_WEIGHT = 1
ORGAN_WEIGHT = 100
MAX_WEIGHT = 1000


class Cell(NamedTuple):
    pos: Pos
    isWall: bool = False
    protein: Optional[ProteinType] = None
    organ: Optional[Organ] = None
    weight: int = EMPTY_WEIGHT


class Grid:
    cells: List[Cell] = []

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.cells = []
        for y in range(height):
            for x in range(width):
                self.cells.append(Cell(Pos(x, y)))

    def get_cell(self, pos: Pos) -> Optional[Cell]:
        if width > pos.x >= 0 and height > pos.y >= 0:
            return self.cells[pos.x + width * pos.y]
        return None

    def set_cell(self, pos: Pos, cell: Cell) -> None:
        self.cells[pos.x + width * pos.y] = cell

    # Returns the List[Pos] of the shortest path. Empty if it's unreachable.
    def dijkstra_shortest_path(self, start_x, start_y, goal_x, goal_y):
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        min_heap = [(0, start_x, start_y)]  # (cost, x, y)
        min_cost_dict = {(start_x, start_y): 0}
        predecessors_dict = {(start_x, start_y): (start_x, start_y)}  # To track the path

        while min_heap:
            current_cost, x, y = heapq.heappop(min_heap)

            # If we reach the goal, reconstruct the path
            if x == goal_x and y == goal_y:
                path = []
                while (x, y) != (start_x, start_y):
                    path.append(Pos(x, y))
                    x, y = predecessors_dict[(x, y)]
                return (current_cost, path[::-1])  # Reverse the path to go from start to goal

            # Explore neighbors
            for dx, dy in directions:
                nx, ny = x + dx, y + dy  # neighbor
                if 0 <= nx < width and 0 <= ny < height:
                    new_cost = current_cost + self.get_cell(Pos(nx, ny)).weight
                    neighbor = (nx, ny)

                    # Only add to heap if we found a cheaper way to get to (nx, ny)
                    if neighbor not in min_cost_dict or new_cost < min_cost_dict[neighbor]:
                        min_cost_dict[neighbor] = new_cost
                        predecessors_dict[neighbor] = (x, y)
                        heapq.heappush(min_heap, (new_cost, nx, ny))

        # If there's no path to the goal, return None or an empty list
        return (MAX_WEIGHT, [])


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

# UTILITY FUNCTIONS --------------------------

def next_to(x1, y1, x2, y2):
    if x2 == x1 and y2 == y1 - 1:
        return 'N'  # North
    elif x2 == x1 and y2 == y1 + 1:
        return 'S'  # South
    elif x2 == x1 + 1 and y2 == y1:
        return 'E'  # East
    elif x2 == x1 - 1 and y2 == y1:
        return 'W'  # West
    else:
        return None  # Not adjacent or not a cardinal direction
    
def grow_random_basic():
    for cell in game.grid.cells:
        if not cell.isWall and not cell.protein and not cell.organ in game.opp_organs and not cell.organ in game.my_organs:
            empty_cell_x, empty_cell_y = cell.pos.x, cell.pos.y
            min_cost = MAX_WEIGHT
            origin = game.my_organs[0]
            for organ in game.my_organs:
                (cost, _) = game.grid.dijkstra_shortest_path(organ.pos.x, organ.pos.y, empty_cell_x, empty_cell_y)
                if cost < min_cost:
                    min_cost = cost
                    origin = organ
            print(f"GROW {origin.id} {empty_cell_x} {empty_cell_y} BASIC")
            break


def get_protein_list(protein_string: str, free_proteins: List[Protein]) -> List[Protein]:
    protein_list = []
    for protein in free_proteins:
        if protein.protein_type == protein_string:
            protein_list.append(protein)
    return protein_list

def harvest_closest_protein(protein_string: str):
    if game.free_proteins:
        target_protein_list = get_protein_list(protein_string, game.free_proteins)
        if target_protein_list:
            root_farmer_organs = []
            for organ in game.my_organs:
                if organ.root_id == 1:
                    root_farmer_organs.append(organ)
            start_organ, closest_target_protein_empty_space, closest_target_protein_pos = get_closest_protein_empty_space(root_farmer_organs, target_protein_list)
            start_organ_x, start_organ_y = start_organ.pos.x, start_organ.pos.y
            start_organ_id = start_organ.id
            closest_target_protein_empty_space_x, closest_target_protein_empty_space_y = closest_target_protein_empty_space.x, closest_target_protein_empty_space.y
            print(f"Start Organ x,y = {start_organ_x},{start_organ_y}", file=sys.stderr, flush=True)
            print(f"Harvester Cell x,y = {closest_target_protein_empty_space.x},{closest_target_protein_empty_space.y}", file=sys.stderr, flush=True)
            print(f"Target Protein x,y = {closest_target_protein_pos.x},{closest_target_protein_pos.y}", file=sys.stderr, flush=True)
            direction_to_harvester = next_to(start_organ_x, start_organ_y, closest_target_protein_empty_space_x, closest_target_protein_empty_space_y)
            print(f"Direction to Harvester = {direction_to_harvester}", file=sys.stderr, flush=True)
            if direction_to_harvester:
                direction_to_protein = next_to(closest_target_protein_empty_space_x, closest_target_protein_empty_space_y, closest_target_protein_pos.x, closest_target_protein_pos.y)
                print(f"Direction to Protein = {direction_to_protein}", file=sys.stderr, flush=True)
                print(f"GROW {start_organ_id } {closest_target_protein_empty_space_x} {closest_target_protein_empty_space_y} HARVESTER {direction_to_protein}")
                return root_farmer_counter + 1
            else:
                print(f"GROW {start_organ_id} {closest_target_protein_empty_space_x} {closest_target_protein_empty_space_y} BASIC")
                return root_farmer_counter
        else:
            grow_random_basic()
            return root_farmer_counter + 1
    else:
        grow_random_basic()
        return root_farmer_counter + 1

main_counter = 0
root_farmer_counter = 0
root_killer_counter = 0
# UTILITY FUNCTIONS --------------------------

# Returns (Organ, Pos)
def get_closest_protein_empty_space(my_organs: List[Organ], target_protein_list: List[Protein]):
    min_cost = MAX_WEIGHT
    origin_organ = my_organs[0]
    destination_harvest_pos = target_protein_list[0]
    destination_protein = target_protein_list[0]
    for organ in my_organs:
        # filter protein list to get only possible spaces
        possible_dest = get_good_protein_neighbors(target_protein_list, game.grid)
        for protein, neighbor in possible_dest:
            (cost, path) = game.grid.dijkstra_shortest_path(organ.pos.x, organ.pos.y, neighbor.x, neighbor.y)
            if cost < min_cost:
                min_cost = cost
                origin_organ = organ
                destination_harvest_pos = path[-1]  # last element is the neighbor of possible_prot
                destination_protein = protein
    return origin_organ, destination_harvest_pos, destination_protein

# Returns the list of possible neighbors of all proteins (proteins itself not included)
def get_good_protein_neighbors(target_protein_list: List[Protein], grid: Grid) -> List[tuple[Protein, Pos]]:
    useful = []  # protein, neighbor_pos
    for p in target_protein_list:
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        for dx, dy in directions:
            n = Pos(dx + p.pos.x, dy + p.pos.y)
            c = grid.get_cell(n)
            if (c is not None) and not (c.isWall or c.organ):
                useful.append((p, n))
    return useful

# START ================== Max's functions ==================

# def get_best_sporer_position(organs):
#     ???
#     return x,y

# def get_best_sporer_direction(organ: Organ, grid: Grid):
#     directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
#     best_position = None
#     best_direction = None
#     best_score = max(width-1, height-1)
#     for dx, dy in directions:
#         possible_sporer_pos = Pos(dx + organ.pos.x, dy + organ.pos.y)
#         possible_sporer_cell = grid.get_cell(possible_sporer_pos)
#         if (possible_sporer_cell is not None) and not (possible_sporer_cell.isWall or possible_sporer_cell.organ):

def spawn_harvester(id, harvester_x, harvester_y, direction):
    print(f"GROW {id} {harvester_x} {harvester_y} HARVESTER {direction}")

def spawn_basic(id, basic_x, basic_y):
    print(f"GROW {i} {basic_x} {basic_y} BASIC")

def spawn_sporer(id, sporer_x, sporer_y, direction):
    print(f"GROW {id} {sporer_x} {sporer_y} SPORER {direction}")
# END ================== Max's functions ==================

# ---------------------------------------------

game: Game = Game()
is_sporer = False

# game loop
while True:
    # Initialisation
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
            cell = Cell(pos, False, None, organ, weight=ORGAN_WEIGHT)
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

    # Actions
    for i in range(required_actions_count):
        can_spawn_sporer = (game.my_proteins["B"], game.my_proteins["D"]) == (1,1)
        can_spore = (game.my_proteins["A"], game.my_proteins["B"], game.my_proteins["C"], game.my_proteins["D"]) == (1,1,1,1) and is_sporer
        can_spawn_tentacle = (game.my_proteins["B"], game.my_proteins["C"]) == (1,1)
        need_A = game.my_proteins["A"] < required_actions_count # All roots should be able to grow
        need_B = game.my_proteins["B"] < 2 * required_actions_count # All roots should be able to create a root
        need_C = game.my_proteins["C"] < required_actions_count # All roots should be able to create a tentacle
        need_D = game.my_proteins["D"] < 2 * required_actions_count # All roots should be able to create a root

        if can_spawn_sporer:
            pass
            # sporer_x, sporer_y = get_best_sporer_position(game.my_organs)
            # direction = ???
            # spawn_sporer(i, sporer_x, sporer_y, direction)
            # is_sporer = True
        # elif can_spore:
        #     spore(???)
        # elif can_spawn_tentacle:
        #     # Grow a tentacle as close as possible to the ennemy
        #     # spawn_tentacle(???)
        #     # spawn_position = get_pos_close_to_enemy(game.grid, game.my_organs, game.opp_organs)
        #     # spawn_tentacle(i, spawn_position.pos.x, spawn_position.pos.x, direction)
        #     pass
        elif need_A:
            a_proteins = get_protein_list("A", game.free_proteins)
            origin_organ, destination_harvest_pos, destination_protein = get_closest_protein_empty_space(game.my_organs, a_proteins)
            direction = next_to(origin_organ.pos.x, origin_organ.pos.y, destination_harvest_pos.x, destination_harvest_pos.y)
            if direction:
                spawn_harvester(origin_organ.id, destination_harvest_pos.x, destination_harvest_pos.y, direction)
            else:
                spawn_basic(origin_organ.id, destination_harvest_pos.x, destination_harvest_pos.y)
        elif need_B:
            b_proteins = get_protein_list("B", game.free_proteins)
            origin_organ, destination_harvest_pos, destination_protein = get_closest_protein_empty_space(game.my_organs, b_proteins)
            direction = next_to(origin_organ.pos.x, origin_organ.pos.y, destination_harvest_pos.x, destination_harvest_pos.y)
            if direction:
                spawn_harvester(origin_organ.id, destination_harvest_pos.x, destination_harvest_pos.y, direction)
            else:
                spawn_basic(origin_organ.id, destination_harvest_pos.x, destination_harvest_pos.y)
            pass
        elif need_C:
            c_proteins = get_protein_list("C", game.free_proteins)
            origin_organ, destination_harvest_pos, destination_protein = get_closest_protein_empty_space(game.my_organs, c_proteins)
            direction = next_to(origin_organ.pos.x, origin_organ.pos.y, destination_harvest_pos.x, destination_harvest_pos.y)
            if direction:
                spawn_harvester(origin_organ.id, destination_harvest_pos.x, destination_harvest_pos.y, direction)
            else:
                spawn_basic(origin_organ.id, destination_harvest_pos.x, destination_harvest_pos.y)
            pass
        elif need_D:
            d_proteins = get_protein_list("D", game.free_proteins)
            origin_organ, destination_harvest_pos, destination_protein = get_closest_protein_empty_space(game.my_organs, d_proteins)
            direction = next_to(origin_organ.pos.x, origin_organ.pos.y, destination_harvest_pos.x, destination_harvest_pos.y)
            if direction:
                spawn_harvester(origin_organ.id, destination_harvest_pos.x, destination_harvest_pos.y, direction)
            else:
                spawn_basic(origin_organ.id, destination_harvest_pos.x, destination_harvest_pos.y)
            pass
        else:
            grow_random_basic()