import curses
import sys
from typing import Dict, List
import time
from random import randint, shuffle, choice
from copy import deepcopy


class Game:
    def __init__(self):
        # Global ship ID counter to uniquely identify each ship
        self.ship_id_counter = 0

        # Create player and computer boards
        self.p1 = Board('Player', self)
        self.p2 = Board('Computer', self)

        # Player manually places ships, computer auto-places
        self.p1.place_initial_boats()
        self.p2.auto_place_ships()

        # Attack controllers for each side
        self.p1_atk = Attack(player=self.p1, opp=self.p2)
        self.p2_atk = Attack(player=self.p2, opp=self.p1)

        # Turn order list; will be shuffled so start player is random
        self.moves = [self.move, self.auto_move]

    def main_loop(self):
        # Randomize who starts (player or computer)
        shuffle(self.moves)

        # Main game loop
        while True:
            for func in self.moves:
                # Execute one turn (player move or computer move)
                func()

                # Check for winner after each move
                winner = self.get_winner()
                if winner is not None:
                    print(f"{winner} wins!")
                    return  # Exit the game loop cleanly

    def move(self):
        # Human player object
        obj = self.p1

        # Let player choose a target and resolve the shot
        self.p1_atk.pick_target()

        # After shooting, place any ships that were earned
        ships_to_place = obj.to_place.copy()
        obj.to_place.clear()

        for pending in ships_to_place:
            # Only place a ship if there is at least one legal placement
            if obj.is_possible(pending):
                obj.place_boat(pending)
            else:
                # Re-queue ships that currently cannot be placed
                obj.to_place.append(pending)

    def auto_move(self):
        # Computer player object
        obj = self.p2

        # AI chooses a target and resolves the shot
        shot = self.p2_atk.auto_pick_target()

        # If the shot hit the player, show an animation
        if shot in self.p1.hit_coors:
            curses.wrapper(lambda stdscr: self.p2_atk.animate_computer_hit(stdscr, shot))

        # After shooting, place any ships the computer earned
        ships_to_place = obj.to_place.copy()
        obj.to_place.clear()

        for pending in ships_to_place:
            if obj.is_possible(pending):
                obj.auto_place(pending)
            else:
                obj.to_place.append(pending)
    
    def new_ship_id(self):
        # Generate a new unique ship ID
        self.ship_id_counter += 1
        return self.ship_id_counter - 1

    def get_winner(self):
        """
        Decide if the game has a winner.

        Returns:
            'Player', 'Computer', a tie message, or None if game continues.
        """
        p1_alive = self.p1.has_live_ships()
        p2_alive = self.p2.has_live_ships()

        # Normal win by sinking all ships
        if p1_alive and not p2_alive:
            return 'Player'
        if p2_alive and not p1_alive:
            return 'Computer'

        # Check remaining guesses (each board has 100 cells)
        p1_has_guesses_left = len(self.p1_atk.guesses) < 100
        p2_has_guesses_left = len(self.p2_atk.guesses) < 100

        # If both sides are out of guesses, compare remaining ship scores
        if not p1_has_guesses_left and not p2_has_guesses_left:
            p1_score = self.p1.score()
            p2_score = self.p2.score()
            if p1_score > p2_score:
                return 'Player'
            elif p2_score > p1_score:
                return 'Computer'
            else:
                # Perfect tie on remaining ship points
                return r"It's a tie!!! ;) No one"

        # If only one side is out of guesses, still decide by score
        if not p1_has_guesses_left and p2_has_guesses_left:
            p1_score = self.p1.score()
            p2_score = self.p2.score()
            return 'Player' if p1_score > p2_score else 'Computer' if p2_score > p1_score else None

        if not p2_has_guesses_left and p1_has_guesses_left:
            p1_score = self.p1.score()
            p2_score = self.p2.score()
            return 'Player' if p1_score > p2_score else 'Computer' if p2_score > p1_score else None

        # No winner yet
        return None


class Board:
    def __init__(self, name, game):
        self.name = name          # 'Player' or 'Computer'
        self.game = game          # Reference back to Game

        # Ships waiting to be placed (sizes)
        self.to_place: list[int] = []

        # Coordinates that have been hit on this board
        self.hit_coors: list[list[int]] = []

        # All coordinates occupied by ships
        self.taken_coor: list[list[int]] = []

        # Coordinates that were guessed and found to be empty (misses)
        self.blocked_coors: list[list[int]] = []

        # 10x10 grid storing ship sizes or 0 for empty
        self.board = [[0 for i in range(10)] for i in range(10)]

        # Per-ship tracking structures
        self.hit_coors_byID: dict[int, list[list[int]]] = {}  # Hits per ship ID
        self.typebyID: dict[int, int] = {}                    # Ship size per ID
        self.unhit_coors: dict[int, list[list[int]]] = {}     # Unhit cells per ship ID

    def score(self) -> int:
        """
        Score is the sum of sizes of all ships that still exist on this board.
        Example: one size-5 and one size-3 ship -> score 8.
        """
        return sum(self.typebyID.values())

    def place_initial_boats(self):
        # Player places ships of size 2,3,4,5 interactively
        for i in range(2, 6):
            PlaceBoat(i, self).position_boat()
    
    def place_boat(self, boat):
        # Place one new boat of given size interactively
        PlaceBoat(boat, self).position_boat()
    
    def auto_place_ships(self):
        # Computer auto-places ships of size 2,3,4,5
        for i in range(2, 6):
            PlaceBoat(i, self).auto_place()
    
    def auto_place(self, boat_size):
        # Get all legal placements for a ship of this size
        placements = self.all_legal_placements(boat_size)

        # If there are no placements, defer this ship
        if not placements:
            self.to_place.append(boat_size)
            return

        # Randomly choose one legal placement
        coords = choice(placements)

        # Register a new ship ID
        ship_id = self.game.new_ship_id()

        # Initialize tracking structures for this ship
        self.unhit_coors[ship_id] = []
        self.typebyID[ship_id] = boat_size
        self.hit_coors_byID[ship_id] = []

        # Mark cells on the board and in tracking lists
        for y, x in coords:
            self.board[y][x] = boat_size
            self.taken_coor.append([y, x])
            self.unhit_coors[ship_id].append([y, x])
    
    def has_live_ships(self) -> bool:
        """Return True if this board still has any ship cells unhit."""
        return len(self.unhit_coors) > 0
    
    def all_legal_placements(self, boat_size: int) -> List[List[List[int]]]:
        """
        Compute all legal placements of a ship of given size, given the current board state.
        Each placement is a list of [y, x] coordinates for that ship.
        """
        placements: List[List[List[int]]] = []
        possible_angles = [0, 90, 180, 270]

        for y in range(10):
            for x in range(10):
                for angle in possible_angles:
                    coords: List[List[int]] = []

                    # Build candidate coordinates depending on angle
                    if angle == 90:      # vertical down
                        for i in range(boat_size):
                            coords.append([y + i, x])
                    elif angle == 180:   # horizontal left
                        for i in range(boat_size):
                            coords.append([y, x - i])
                    elif angle == 270:   # vertical up
                        for i in range(boat_size):
                            coords.append([y - i, x])
                    else:                # 0, horizontal right
                        for i in range(boat_size):
                            coords.append([y, x + i])

                    # Validate all coordinates for this placement
                    legal = True
                    for cy, cx in coords:
                        # Must be on the board
                        if not (0 <= cy < 10 and 0 <= cx < 10):
                            legal = False
                            break
                        # Must not overlap existing ships or blocked cells
                        if [cy, cx] in self.taken_coor:
                            legal = False
                            break
                        if [cy, cx] in self.blocked_coors:
                            legal = False
                            break

                    if legal:
                        placements.append(coords)

        return placements

    def is_possible(self, boat_size: int) -> bool:
        """
        Return True if there exists at least one valid placement
        for a ship of this size on the current board.
        """
        possible_angles = [0, 90, 180, 270]
        
        for y in range(10): 
            for x in range(10):
                for angle in possible_angles:
                    boat_coordinates = []
                    
                    # Generate candidate coordinates for this angle
                    if angle == 90:  # down
                        for i in range(boat_size):
                            boat_coordinates.append([y + i, x])
                    elif angle == 180:  # left
                        for i in range(boat_size):
                            boat_coordinates.append([y, x - i])
                    elif angle == 270:  # up
                        for i in range(boat_size):
                            boat_coordinates.append([y - i, x])
                    else:  # 0, right
                        for i in range(boat_size):
                            boat_coordinates.append([y, x + i])
                    
                    is_valid_placement = True
                    
                    # Check bounds and collisions for this placement
                    for coord in boat_coordinates:
                        coord_y, coord_x = coord[0], coord[1]
                        
                        # On-board check
                        if coord_y < 0 or coord_y > 9:
                            is_valid_placement = False
                            break 
                        if coord_x < 0 or coord_x > 9:
                            is_valid_placement = False
                            break
                        
                        # Cannot overlap ships or blocked cells
                        if coord in self.taken_coor:
                            is_valid_placement = False
                            break 
                        if coord in self.blocked_coors:
                            is_valid_placement = False
                            break  
                    
                    if is_valid_placement:
                        return True
        
        # No valid placement found anywhere
        return False


class Attack:
    def __init__(self, player, opp):
        # All guesses made by this attacker (hits and misses)
        self.guesses: list[list[int]] = []
        # Missed shots
        self.misses: list[list[int]] = []
        # Successful hits (current ship cells)
        self.hits: list[list[int]] = []

        # Legacy board (not used for rendering anymore, but kept)
        self.board = [[0 for i in range(10)] for i in range(10)]
        self.visual_board = [["-" for i in range(10)] for i in range(10)]

        # Defender object and owner of this Attack
        self.obj = opp
        self.player = player

        # AI mode for the computer: "hunt" random / parity, "target" focused
        self.mode = "hunt"
        self.target_stack: list[list[int]] = []  # Cells to prioritize in target mode

        # Cursor position for interactive targeting
        self.cursor = [0, 0]  # [y, x]

    def smallest_alive_ship(self) -> int:
        """
        Return size of smallest ship still alive on opponent board.
        Used to adjust parity strategy.
        """
        if not self.obj.typebyID:
            return 2
        return min(self.obj.typebyID.values())

    def pick_hunt_shot(self) -> list[int]:
        """
        Choose a random guess using a parity pattern based on the smallest ship.
        """
        smallest = self.smallest_alive_ship()
        candidates = []

        for y in range(10):
            for x in range(10):
                if [y, x] in self.guesses:
                    continue
                # Generalized parity filter to skip some cells
                if (y + x) % smallest != 0:
                    continue
                candidates.append([y, x])

        # Fallback: if parity leaves no cells, guess any unguessed cell
        if not candidates:
            for y in range(10):
                for x in range(10):
                    if [y, x] not in self.guesses:
                        candidates.append([y, x])
        return choice(candidates)

    def add_neighbors(self, coor: list[int]):
        """
        After a hit, add orthogonal neighbors as higher-priority targets.
        """
        y, x = coor
        for dy, dx in [(-1,0),(1,0),(0,-1),(0,1)]:
            ny, nx = y + dy, x + dx
            cand = [ny, nx]
            if 0 <= ny < 10 and 0 <= nx < 10 and cand not in self.guesses and cand not in self.target_stack:
                self.target_stack.append(cand)

    def view_own_ships(self, stdscr):
        """
        Show the player's own ships with color coding.

        - Red   = hit ship cells
        - Cyan  = unhit ship cells
        - Yellow X = opponent misses
        - '-'   = empty water

        Closes automatically after 5 seconds or when 'v' is pressed.
        """
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)   # default
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)     # hit ship
        curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)    # ship (unhit)
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # miss X

        DEFAULT_COLOR = curses.color_pair(1)
        HIT_COLOR = curses.color_pair(2)
        SHIP_COLOR = curses.color_pair(3)
        MISS_COLOR = curses.color_pair(4)

        curses.noecho()
        curses.cbreak()
        stdscr.nodelay(True)  # Non-blocking getch for countdown

        start = time.time()
        duration = 5  # seconds to keep view open

        while True:
            remaining = max(0, duration - int(time.time() - start))
            stdscr.clear()
            header = f"{self.player.name}'s ships | {remaining}s left (press 'v' to go back)"
            stdscr.addstr(0, 0, header)

            max_y, max_x = stdscr.getmaxyx()

            # Draw player's board with same styling as placement view
            for y, row in enumerate(self.player.board):
                for x, cell in enumerate(row):
                    draw_y = y + 1
                    draw_x = x * 4
                    if draw_y < 0 or draw_y >= max_y:
                        continue
                    if draw_x < 0 or draw_x + 1 > max_x:
                        continue

                    coord = [y, x]
                    ch = '-'
                    attr = DEFAULT_COLOR

                    # Opponent miss on you
                    if coord in self.player.blocked_coors:
                        ch = 'X'
                        attr = MISS_COLOR
                    # Hit on your ship
                    elif coord in self.player.hit_coors:
                        ch = str(cell) if cell != 0 else 'H'
                        attr = HIT_COLOR
                    # Your existing ships (unhit)
                    elif cell != 0:
                        ch = str(cell)
                        attr = SHIP_COLOR
                    # Empty water
                    else:
                        ch = '-'
                        attr = DEFAULT_COLOR

                    stdscr.addstr(draw_y, draw_x, ch, attr)

            stdscr.refresh()

            # Allow user to exit early with 'v'
            key = stdscr.getch()
            if key == ord('v'):
                stdscr.nodelay(False)
                return

            # Auto-exit after duration
            if time.time() - start >= duration:
                stdscr.nodelay(False)
                return

            time.sleep(0.05)

    def animate_computer_hit(self, stdscr, target):
        """
        Animate the computer's shot on a blank grid.

        - No ships or hit/miss info shown.
        - Only a '*' moving from (0,0) to the target.
        """
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)   # default
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK) # animation marker

        DEFAULT_COLOR = curses.color_pair(1)
        MARKER_COLOR = curses.color_pair(5) | curses.A_BOLD

        ty, tx = target  # Target coordinate

        # Build a simple path from (0,0) to (ty,tx)
        path = []
        y, x = 0, 0
        while y != ty or x != tx:
            path.append((y, x))
            if y < ty:
                y += 1
            elif x < tx:
                x += 1
            elif x < tx:
                x += 1
        path.append((ty, tx))

        for step_y, step_x in path:
            stdscr.clear()
            stdscr.addstr(0, 0, "Computer is firing...")

            max_y, max_x = stdscr.getmaxyx()

            # Draw a blank 10x10 grid
            for gy in range(10):
                for gx in range(10):
                    draw_y = gy + 1
                    draw_x = gx * 4
                    if draw_y < 0 or draw_y >= max_y:
                        continue
                    if draw_x < 0 or draw_x + 1 > max_x:
                        continue
                    stdscr.addstr(draw_y, draw_x, '-', DEFAULT_COLOR)

            # Draw animated marker for the projectile
            marker_draw_y = step_y + 1
            marker_draw_x = step_x * 4
            if 0 <= marker_draw_y < max_y and 0 <= marker_draw_x < max_x:
                stdscr.addstr(marker_draw_y, marker_draw_x, '*', MARKER_COLOR)

            stdscr.refresh()
            time.sleep(0.2)

        # Pause briefly on impact
        time.sleep(0.8)

    def shoot(self, shot):
        """
        Resolve a single shot against the opponent board.
        """
        obj = self.obj
        self.guesses.append(shot)

        if shot in obj.taken_coor:
            # Hit a ship
            self.hits.append(shot)
            self.onhit(shot)
            obj.hit_coors.append(shot)
            self.visual_board[shot[0]][shot[1]] = '!'
        else:
            # Missed; mark blocked on defender and miss for attacker
            obj.blocked_coors.append(shot)
            self.misses.append(shot)
            self.visual_board[shot[0]][shot[1]] = 'X'

    def onhit(self, coor):
        """
        Handle bookkeeping when a shot hits a ship cell:
        - Update per-ship hit/unhit lists.
        - Detect when a ship is fully sunk.
        - Award ship to attacker and allow re-placement.
        """
        obj = self.obj
        boatsbyID = obj.unhit_coors
        visual_board = self.visual_board

        sunk_ids = []

        # Find which ship this coord belongs to and update its lists
        for ID, cells in boatsbyID.items():
            if coor in cells:
                # Record hit once per ship ID
                if coor not in obj.hit_coors_byID[ID]:
                    obj.hit_coors_byID[ID].append(coor)

                # Remove all occurrences of this coord from unhit list
                obj.unhit_coors[ID] = [c for c in obj.unhit_coors[ID] if c != coor]

                # Unique coordinates still unhit for this ship
                remaining_unique = set(tuple(c) for c in obj.unhit_coors[ID])

                # If nothing remains, ship is sunk
                if not remaining_unique:
                    sunk_ids.append(ID)
                break  # Coord belongs to only one ship

        # For computer AI: switch to target mode when a hit occurs
        if self.player.name == "Computer":
            self.mode = "target"
            self.add_neighbors(coor)

        # Handle all sunk ships
        for ID in sunk_ids:
            print(f"{self.player.name} sank a size {obj.typebyID[ID]} ship!")
            # Award a ship of same size to attacker for re-placement
            self.player.to_place.append(obj.typebyID[ID])

            # All coords that belonged to this ship
            ship_cells = obj.hit_coors_byID[ID].copy()

            for hit in ship_cells:
                # Clear attacker visual board for re-guessing
                visual_board[hit[0]][hit[1]] = "-"

                # Remove this coord from defender occupancy
                obj.taken_coor = [c for c in obj.taken_coor if c != hit]

                # Remove from attacker history so cell can be used again
                if hit in self.hits:
                    self.hits.remove(hit)
                if hit in self.guesses:
                    self.guesses.remove(hit)

            # Cleanup ship bookkeeping
            del obj.unhit_coors[ID]
            del obj.typebyID[ID]
            del obj.hit_coors_byID[ID]

        # Computer-specific cleanup after all ships of a target are sunk
        if self.player.name == "Computer":
            # If no ships remain unhit, reset AI mode and clear stack
            if not self.obj.unhit_coors:
                self.mode = "hunt"
                self.target_stack.clear()

    def pick_target(self):
        """
        Interactive targeting for the human player using curses.
        """
        header = 'Pick a coordinate to attack - (v) to view ships'
        while True:
            # Use curses UI to get a coordinate
            choosen_coor = curses.wrapper(lambda stdscr: self.get_coor(stdscr, header))

            # Never re-guess known misses
            if choosen_coor in self.misses:
                continue

            # Do not re-guess hits that still correspond to live ship cells
            if choosen_coor in self.hits and choosen_coor in self.obj.taken_coor:
                continue

            # Accept this coordinate
            break

        self.shoot(choosen_coor)

    def auto_pick_target(self):
        """
        AI targeting logic for the computer.

        - Uses target mode when a ship was recently hit.
        - Uses hunt mode (parity search) otherwise.
        """
        # Set mode based on whether we have queued target cells
        if self.target_stack:
            self.mode = "target"
        else:
            self.mode = "hunt"

        if self.mode == "target":
            # Depth-first style: pop from end of stack
            shot = self.target_stack.pop()
            # If already guessed, fall back to hunt mode
            if shot in self.guesses:
                return self.auto_pick_target()
        else:
            shot = self.pick_hunt_shot()

        self.shoot(shot)
        return shot
            
    def get_coor(self, stdscr, header):
        """
        Curses UI for choosing a target coordinate with arrow keys.

        Returns:
            [row, col] coordinate on the opponent's board.
        """
        curses.curs_set(0)
        curses.start_color()
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(True)

        # Color pairs for different cell states
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)   # default
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)     # miss / invalid
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)   # valid new guess
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)    # hit
        DEFAULT = curses.color_pair(1)
        MISS = curses.color_pair(2)
        VALID = curses.color_pair(3)
        HIT = curses.color_pair(4)

        # Start cursor from last used position
        y, x = self.cursor

        while True:
            stdscr.clear()
            if header:
                stdscr.addstr(0, 0, header)

            max_y, max_x = stdscr.getmaxyx()

            # Draw 10x10 attack grid
            for i in range(10):
                for j in range(10):
                    draw_y = i + 1
                    draw_x = j * 4
                    if draw_y < 0 or draw_y >= max_y:
                        continue
                    if draw_x < 0 or draw_x + 1 > max_x:
                        continue

                    coord = [i, j]

                    # Derive symbol from hits/misses
                    if coord in self.misses:
                        ch = 'X'
                        attr = MISS
                    elif coord in self.hits:
                        ch = '!'
                        attr = HIT
                    else:
                        ch = '-'
                        attr = DEFAULT

                    # Cursor highlighting and validity feedback
                    if i == y and j == x:
                        if coord in self.misses:
                            # Known miss — red highlight
                            attr = MISS | curses.A_REVERSE
                        elif coord in self.hits and coord in self.obj.taken_coor:
                            # Hit that is still a live ship cell — cyan highlight
                            attr = HIT | curses.A_REVERSE
                        else:
                            # Either a sunk ship cell or a fresh cell — green highlight
                            attr = VALID | curses.A_REVERSE

                    stdscr.addstr(draw_y, draw_x, ch, attr)

            key = stdscr.getch()

            # Move cursor with arrow keys
            if key == curses.KEY_UP:
                y = max(0, y - 1)
            elif key == curses.KEY_DOWN:
                y = min(9, y + 1)
            elif key == curses.KEY_LEFT:
                x = max(0, x - 1)
            elif key == curses.KEY_RIGHT:
                x = min(9, x + 1)
            elif key == ord('v'):
                # Temporarily view own ships
                self.view_own_ships(stdscr)
                continue
            elif key == ord('\n'):
                # Confirm selection on Enter
                self.cursor = [y, x]
                return [y, x]


class PlaceBoat:
    def __init__(self, ship: int, obj):
        # List of ship segments (value is ship size)
        self.ship = [ship for i in range(ship)]
        self.obj = obj

        # Snapshot of board when starting placement
        self.board = deepcopy(obj.board)
        # Working copy used for rendering the moving ship
        self.working_board = deepcopy(self.board)

        # Start in the middle-ish
        x = 4
        y = 4

        # Dictionary representation of ship coordinates relative to reference
        self.coor = {y + i: x for i in range(ship)}
        # Rotation pivot
        self.reference_coor = (y, x)
        # Start vertical (90 degrees)
        self.angle = 90

    def update_ship(self):
        """
        Recalculate self.coor based on current angle and reference coordinate.
        """
        ship = self.ship[0]
        y, x = self.reference_coor  # Point of rotation
        
        if self.angle == 90:
            self.coor = {y + i: x for i in range(ship)}
        elif self.angle == 180:
            self.coor = {y: [x - i for i in range(ship)]}
        elif self.angle == 270:
            self.coor = {y - i: x for i in range(ship)}
        else:  # 0 degrees
            self.coor = {y: [x + i for i in range(ship)]}

    def reset_position(self):
        """
        Reset ship candidate position to default center column.
        """
        self.coor = {4 + i: 4 for i in range(self.ship[0])}

    def flatten_coor(self):
        """
        Flatten internal coordinate dict into a 1D list of ints for min/max checks.
        """
        flat_list = []
        for k in self.coor.keys():
            if isinstance(k, list):
                flat_list.extend(k)
            else:
                flat_list.append(k)
        for v in self.coor.values():
            if isinstance(v, list):
                flat_list.extend(v)
            else: 
                flat_list.append(v)
        
        return flat_list

    def valid_position(self):
        """
        Set self.legal to True if current candidate position is fully on board
        and does not collide with taken or blocked coordinates.
        """
        array = self.flatten_coor()
        if max(array) > 9:
            self.legal = False
        elif min(array) < 0: 
            self.legal = False
        else:
            self.legal = True

        a2 = self.concatenate_coor()
        for coor in a2:
            if coor in self.obj.taken_coor:  
                self.legal = False
                return
            if coor in self.obj.blocked_coors:
                self.legal = False
                return

    def place_ship(self, ship_id=None):
        """
        Commit the current candidate ship position onto the real board.
        """
        if ship_id is None:
            ship_id = self.obj.game.new_ship_id()
        
        ship_coords = []

        # Copy coordinates into board and tracking structures
        for y, x in self.concatenate_coor():
            self.obj.board[y][x] = self.ship[0]
            self.obj.taken_coor.append([y, x])
            ship_coords.append([y, x])

        self.obj.unhit_coors[ship_id] = ship_coords.copy()
        self.obj.typebyID[ship_id] = self.ship[0]
        self.obj.hit_coors_byID[ship_id] = []
    
    def auto_place(self):
        """
        Automatically place this ship in a random legal position.
        """
        while True:
            # Randomly choose a reference coordinate
            self.reference_coor = (randint(0,9), randint(0, 9))
            self.update_ship()
            self.valid_position()
            if self.legal:
                self.place_ship()
                return

    def check_offscreen(self):
        """
        Check if any part of candidate ship is off the board.
        """
        for key in self.coor.keys():
            if key < 0 or key > 9:
                return True
        for value in self.coor.values():
            lo, hi = (value, value) if isinstance(value, int) else (min(value), max(value))
            if lo < 0 or hi > 9:
                return True

        return False

    def update_board(self):
        """
        Refresh working_board with the candidate ship overlaid on top.
        """
        self.working_board = deepcopy(self.board)
        for Ys in self.coor.keys():
            Ys = [Ys] if isinstance(Ys, int) else Ys
            for y in Ys:
                if 0 > y or y > 9:
                    continue
                for Xs in self.coor.values():
                    Xs = [Xs] if isinstance(Xs, int) else Xs
                    for x in list(Xs):
                        if 0 > x or x > 9:
                            continue
                        self.working_board[y][x] = self.ship[0]
    
    def concatenate_coor(self):
        """
        Convert internal coordinate representation into a list of [y, x] pairs.
        """
        coor = self.coor
        output = []
        for Ys in coor.keys():
            Ys = [Ys] if isinstance(Ys, int) else Ys
            for y in Ys:
                for Xs in coor.values():
                    Xs = [Xs] if isinstance(Xs, int) else Xs
                    for x in Xs:
                        output.append([y, x])
        return output

    def position_boat(self):
        """
        Start curses UI to position this boat manually.

        Returns:
            None (ship is placed directly onto the board when confirmed).
        """
        header = 'Place the boat (R to rotate):\n\n'
        return curses.wrapper(lambda stdscr: self.get_position(stdscr, header))

    def get_position(self, stdscr, header):
        """
        Curses loop for moving and rotating the current ship until
        the user confirms a legal position with Enter.
        """
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)   # default
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)     # hit ship
        curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)    # ship (unhit)
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # miss X

        DEFAULT_COLOR = curses.color_pair(1)
        HIT_COLOR = curses.color_pair(2)
        SHIP_COLOR = curses.color_pair(3)
        MISS_COLOR = curses.color_pair(4)

        curses.noecho()
        curses.cbreak()
        stdscr.keypad(True)  # Enable arrow keys

        while True:
            stdscr.clear()
            if header:
                stdscr.addstr(0, 0, header)

            # Validate and update candidate position
            self.valid_position()
            self.check_offscreen()
            self.update_board()

            Ccoor = self.concatenate_coor()
            max_y, max_x = stdscr.getmaxyx()  # Terminal bounds

            for y, row in enumerate(self.working_board):
                for x, cell in enumerate(row):
                    draw_y = y + 1
                    draw_x = x * 4

                    if draw_y < 0 or draw_y >= max_y:
                        continue
                    if draw_x < 0 or draw_x + 1 > max_x:
                        continue

                    coord = [y, x]
                    ch = '-'
                    attr = DEFAULT_COLOR

                    # Opponent miss on you
                    if coord in self.obj.blocked_coors:
                        ch = 'X'
                        attr = MISS_COLOR

                    # Hit on your ship
                    elif coord in self.obj.hit_coors:
                        ch = str(self.board[y][x]) if self.board[y][x] != 0 else 'H'
                        attr = HIT_COLOR

                    # Existing ships (unhit)
                    elif self.board[y][x] != 0:
                        ch = str(self.board[y][x])
                        attr = SHIP_COLOR

                    # Empty cell
                    else:
                        ch = '-'
                        attr = DEFAULT_COLOR

                    # Highlight current candidate ship cells
                    if coord in Ccoor:
                        attr = SHIP_COLOR if self.legal else HIT_COLOR

                    stdscr.addstr(draw_y, draw_x, ch, attr)

            key = stdscr.getch()
            y, x = self.reference_coor

            # Move reference coordinate with arrow keys
            if key == curses.KEY_UP:
                y = max(0, y - 1)
            elif key == curses.KEY_DOWN:
                y = min(len(self.board) - 1, y + 1)
            elif key == curses.KEY_LEFT:
                x = max(0, x - 1)
            elif key == curses.KEY_RIGHT:
                x = min(len(self.board[y]) - 1, x + 1)
            elif key == ord('r'):
                # Rotate 90 degrees clockwise
                self.angle = (self.angle + 90) % 360
            elif key == ord('\n') and self.legal:
                # Confirm placement when in a legal position
                self.place_ship()
                return

            # Update reference and recompute candidate ship
            self.reference_coor = (y, x)
            self.update_ship()
            self.update_board()


def main():
    # Create a Game instance and start the main loop
    game = Game()
    game.main_loop()


if __name__ == "__main__":
    main()
