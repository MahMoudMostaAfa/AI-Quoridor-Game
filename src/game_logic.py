"""
Quoridor Game - Game State and Logic
Handles the core game mechanics including board state, moves, wall placement, and win conditions.
"""

from typing import List, Tuple, Set, Optional
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import copy


class Player(Enum):
    """Enum for player identification"""
    PLAYER1 = 1  # Bottom player (starts at row 8)
    PLAYER2 = 2  # Top player (starts at row 0)


class WallOrientation(Enum):
    """Enum for wall orientation"""
    HORIZONTAL = "H"
    VERTICAL = "V"


@dataclass
class Wall:
    """Represents a wall on the board"""
    row: int
    col: int
    orientation: WallOrientation
    
    def __hash__(self):
        return hash((self.row, self.col, self.orientation))
    
    def __eq__(self, other):
        if not isinstance(other, Wall):
            return False
        return self.row == other.row and self.col == other.col and self.orientation == other.orientation


@dataclass
class GameState:
    """
    Represents the complete state of a Quoridor game.
    Board is 9x9, positions are (row, col) tuples.
    Walls are placed between cells.
    """
    board_size: int = 9
    player1_pos: Tuple[int, int] = (8, 4)  # Bottom center
    player2_pos: Tuple[int, int] = (0, 4)  # Top center
    player1_walls: int = 10
    player2_walls: int = 10
    walls: Set[Wall] = field(default_factory=set)
    current_player: Player = Player.PLAYER1
    game_over: bool = False
    winner: Optional[Player] = None
    
    def copy(self) -> 'GameState':
        """Create a deep copy of the game state"""
        new_state = GameState(
            board_size=self.board_size,
            player1_pos=self.player1_pos,
            player2_pos=self.player2_pos,
            player1_walls=self.player1_walls,
            player2_walls=self.player2_walls,
            walls=self.walls.copy(),
            current_player=self.current_player,
            game_over=self.game_over,
            winner=self.winner
        )
        return new_state
    
    def get_current_player_pos(self) -> Tuple[int, int]:
        """Get position of current player"""
        return self.player1_pos if self.current_player == Player.PLAYER1 else self.player2_pos
    
    def get_opponent_pos(self) -> Tuple[int, int]:
        """Get position of opponent player"""
        return self.player2_pos if self.current_player == Player.PLAYER1 else self.player1_pos
    
    def get_current_player_walls(self) -> int:
        """Get remaining walls for current player"""
        return self.player1_walls if self.current_player == Player.PLAYER1 else self.player2_walls


class QuoridorGame:
    """
    Main game logic class for Quoridor.
    Handles move validation, wall placement, pathfinding, and win conditions.
    """
    
    def __init__(self):
        self.state = GameState()
        self.move_history: List[Tuple] = []
    
    def reset(self):
        """Reset the game to initial state"""
        self.state = GameState()
        self.move_history = []
    
    def is_valid_position(self, row: int, col: int) -> bool:
        """Check if position is within board bounds"""
        return 0 <= row < self.state.board_size and 0 <= col < self.state.board_size
    
    def is_wall_between(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> bool:
        """Check if there's a wall between two adjacent positions"""
        r1, c1 = pos1
        r2, c2 = pos2
        
        # Moving vertically (up or down)
        if c1 == c2:
            if r2 < r1:  # Moving up
                wall_row = r1 - 1
                # Check for horizontal wall at this position
                for wall in self.state.walls:
                    if wall.orientation == WallOrientation.HORIZONTAL:
                        if wall.row == wall_row and (wall.col == c1 or wall.col == c1 - 1):
                            return True
            else:  # Moving down
                wall_row = r1
                for wall in self.state.walls:
                    if wall.orientation == WallOrientation.HORIZONTAL:
                        if wall.row == wall_row and (wall.col == c1 or wall.col == c1 - 1):
                            return True
        
        # Moving horizontally (left or right)
        if r1 == r2:
            if c2 < c1:  # Moving left
                wall_col = c1 - 1
                for wall in self.state.walls:
                    if wall.orientation == WallOrientation.VERTICAL:
                        if wall.col == wall_col and (wall.row == r1 or wall.row == r1 - 1):
                            return True
            else:  # Moving right
                wall_col = c1
                for wall in self.state.walls:
                    if wall.orientation == WallOrientation.VERTICAL:
                        if wall.col == wall_col and (wall.row == r1 or wall.row == r1 - 1):
                            return True
        
        return False
    
    def get_valid_moves(self, player: Optional[Player] = None) -> List[Tuple[int, int]]:
        """Get all valid moves for a player"""
        if player is None:
            player = self.state.current_player
        
        if player == Player.PLAYER1:
            current_pos = self.state.player1_pos
            opponent_pos = self.state.player2_pos
        else:
            current_pos = self.state.player2_pos
            opponent_pos = self.state.player1_pos
        
        valid_moves = []
        row, col = current_pos
        
        # Basic moves: up, down, left, right
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            
            if not self.is_valid_position(new_row, new_col):
                continue
            
            if self.is_wall_between(current_pos, (new_row, new_col)):
                continue
            
            # Check if opponent is in the way
            if (new_row, new_col) == opponent_pos:
                # Try to jump over opponent
                jump_row, jump_col = new_row + dr, new_col + dc
                
                if self.is_valid_position(jump_row, jump_col) and \
                   not self.is_wall_between(opponent_pos, (jump_row, jump_col)):
                    valid_moves.append((jump_row, jump_col))
                else:
                    # Diagonal moves if jump is blocked
                    if dr == 0:  # Moving horizontally, try vertical diagonals
                        for ddr in [-1, 1]:
                            diag_row, diag_col = new_row + ddr, new_col
                            if self.is_valid_position(diag_row, diag_col) and \
                               not self.is_wall_between(opponent_pos, (diag_row, diag_col)):
                                valid_moves.append((diag_row, diag_col))
                    else:  # Moving vertically, try horizontal diagonals
                        for ddc in [-1, 1]:
                            diag_row, diag_col = new_row, new_col + ddc
                            if self.is_valid_position(diag_row, diag_col) and \
                               not self.is_wall_between(opponent_pos, (diag_row, diag_col)):
                                valid_moves.append((diag_row, diag_col))
            else:
                valid_moves.append((new_row, new_col))
        
        return valid_moves
    
    def can_place_wall(self, wall: Wall) -> bool:
        """Check if a wall can be placed at the given position"""
        # Check if player has walls remaining
        if self.state.get_current_player_walls() <= 0:
            return False
        
        # Check if wall position is valid
        if wall.orientation == WallOrientation.HORIZONTAL:
            if not (0 <= wall.row < self.state.board_size - 1 and 
                    0 <= wall.col < self.state.board_size - 1):
                return False
        else:
            if not (0 <= wall.row < self.state.board_size - 1 and 
                    0 <= wall.col < self.state.board_size - 1):
                return False
        
        # Check if wall overlaps with existing walls
        if wall in self.state.walls:
            return False
        
        # Check for crossing walls
        for existing_wall in self.state.walls:
            if self._walls_overlap(wall, existing_wall):
                return False
        
        # Check if wall blocks all paths (must leave at least one path for each player)
        test_state = self.state.copy()
        test_state.walls.add(wall)
        
        # Save current state and temporarily use test state
        original_state = self.state
        self.state = test_state
        
        p1_has_path = self._has_path_to_goal(self.state.player1_pos, Player.PLAYER1)
        p2_has_path = self._has_path_to_goal(self.state.player2_pos, Player.PLAYER2)
        
        # Restore original state
        self.state = original_state
        
        return p1_has_path and p2_has_path

    def _walls_overlap(self, wall1: Wall, wall2: Wall) -> bool:
        """Check if two walls overlap or cross"""
        # Same position and orientation
        if wall1.row == wall2.row and wall1.col == wall2.col:
            return True
        
        # Same orientation - check if they overlap
        if wall1.orientation == wall2.orientation:
            if wall1.orientation == WallOrientation.HORIZONTAL:
                if wall1.row == wall2.row:
                    return abs(wall1.col - wall2.col) <= 1
            else:
                if wall1.col == wall2.col:
                    return abs(wall1.row - wall2.row) <= 1
        else:
            # Different orientation - check if they cross
            if wall1.orientation == WallOrientation.HORIZONTAL:
                h_wall, v_wall = wall1, wall2
            else:
                h_wall, v_wall = wall2, wall1
            
            # Check if they cross at the center
            if h_wall.row == v_wall.row and h_wall.col == v_wall.col:
                return True
        
        return False
    
    def _has_path_to_goal(self, start: Tuple[int, int], player: Player) -> bool:
        """Check if there's a path from start to the goal row using BFS"""
        goal_row = 0 if player == Player.PLAYER1 else self.state.board_size - 1
        
        visited = set()
        queue = deque([start])
        visited.add(start)
        
        while queue:
            current = queue.popleft()
            row, col = current
            
            if row == goal_row:
                return True
            
            # Check all four directions
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                new_row, new_col = row + dr, col + dc
                
                if not self.is_valid_position(new_row, new_col):
                    continue
                
                if (new_row, new_col) in visited:
                    continue
                
                if self.is_wall_between(current, (new_row, new_col)):
                    continue
                
                visited.add((new_row, new_col))
                queue.append((new_row, new_col))
        
        return False
    
    def get_shortest_path_length(self, start: Tuple[int, int], player: Player) -> int:
        """Get the length of shortest path to goal row using BFS"""
        goal_row = 0 if player == Player.PLAYER1 else self.state.board_size - 1
        
        visited = set()
        queue = deque([(start, 0)])
        visited.add(start)
        
        while queue:
            current, dist = queue.popleft()
            row, col = current
            
            if row == goal_row:
                return dist
            
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                new_row, new_col = row + dr, col + dc
                
                if not self.is_valid_position(new_row, new_col):
                    continue
                
                if (new_row, new_col) in visited:
                    continue
                
                if self.is_wall_between(current, (new_row, new_col)):
                    continue
                
                visited.add((new_row, new_col))
                queue.append(((new_row, new_col), dist + 1))
        
        return float('inf')
    
    def move_player(self, new_pos: Tuple[int, int]) -> bool:
        """Move current player to new position"""
        if new_pos not in self.get_valid_moves():
            return False
        
        if self.state.current_player == Player.PLAYER1:
            old_pos = self.state.player1_pos
            self.state.player1_pos = new_pos
        else:
            old_pos = self.state.player2_pos
            self.state.player2_pos = new_pos
        
        self.move_history.append(('move', self.state.current_player, old_pos, new_pos))
        self._check_win()
        self._switch_player()
        
        return True
    
    def place_wall(self, wall: Wall) -> bool:
        """Place a wall on the board"""
        if not self.can_place_wall(wall):
            return False
        
        self.state.walls.add(wall)
        
        if self.state.current_player == Player.PLAYER1:
            self.state.player1_walls -= 1
        else:
            self.state.player2_walls -= 1
        
        self.move_history.append(('wall', self.state.current_player, wall))
        self._switch_player()
        
        return True
    
    def _check_win(self):
        """Check if current player has won"""
        if self.state.player1_pos[0] == 0:
            self.state.game_over = True
            self.state.winner = Player.PLAYER1
        elif self.state.player2_pos[0] == self.state.board_size - 1:
            self.state.game_over = True
            self.state.winner = Player.PLAYER2
    
    def _switch_player(self):
        """Switch to the other player"""
        if self.state.current_player == Player.PLAYER1:
            self.state.current_player = Player.PLAYER2
        else:
            self.state.current_player = Player.PLAYER1
    
    def get_all_valid_walls(self) -> List[Wall]:
        """Get all valid wall placements for current player"""
        valid_walls = []
        
        if self.state.get_current_player_walls() <= 0:
            return valid_walls
        
        for row in range(self.state.board_size - 1):
            for col in range(self.state.board_size - 1):
                for orientation in WallOrientation:
                    wall = Wall(row, col, orientation)
                    if self.can_place_wall(wall):
                        valid_walls.append(wall)
        
        return valid_walls
    
    def undo_move(self) -> bool:
        """Undo the last move"""
        if not self.move_history:
            return False
        
        last_move = self.move_history.pop()
        
        if last_move[0] == 'move':
            _, player, old_pos, new_pos = last_move
            if player == Player.PLAYER1:
                self.state.player1_pos = old_pos
            else:
                self.state.player2_pos = old_pos
        else:  # wall
            _, player, wall = last_move
            self.state.walls.remove(wall)
            if player == Player.PLAYER1:
                self.state.player1_walls += 1
            else:
                self.state.player2_walls += 1
        
        self._switch_player()
        self.state.game_over = False
        self.state.winner = None
        
        return True
