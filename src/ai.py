"""
Quoridor Game - AI Module
Implements AI opponent using Minimax algorithm with Alpha-Beta pruning.
"""

import random
from typing import List, Tuple, Optional
from .game_logic import QuoridorGame, GameState, Player, Wall, WallOrientation


class QuoridorAI:
    """
    AI player for Quoridor using Minimax with Alpha-Beta pruning.
    Includes multiple difficulty levels and strategic evaluation.
    """
    
    def __init__(self, player: Player, difficulty: str = "medium"):
        """
        Initialize AI player.
        
        Args:
            player: Which player the AI controls
            difficulty: AI difficulty level - "easy", "medium", or "hard"
        """
        self.player = player
        self.difficulty = difficulty
        self.max_depth = self._get_depth_for_difficulty(difficulty)
        
        # Weights for evaluation function
        self.weights = {
            'path_difference': 10.0,
            'wall_advantage': 2.0,
            'center_control': 1.0,
            'wall_blocking': 3.0
        }
    
    def _get_depth_for_difficulty(self, difficulty: str) -> int:
        """Get search depth based on difficulty"""
        depths = {
            "easy": 1,
            "medium": 2,
            "hard": 3
        }
        return depths.get(difficulty, 2)
    
    def get_best_move(self, game: QuoridorGame) -> Tuple[str, any]:
        """
        Get the best move for the AI player.
        
        Returns:
            Tuple of (move_type, move_data) where:
            - move_type is "move" or "wall"
            - move_data is position tuple or Wall object
        """
        if self.difficulty == "easy":
            return self._get_easy_move(game)
        else:
            return self._get_minimax_move(game)
    
    def _get_easy_move(self, game: QuoridorGame) -> Tuple[str, any]:
        """Get a simple move for easy difficulty - mostly random with some strategy"""
        valid_moves = game.get_valid_moves()
        
        # 70% chance to make a strategic move
        if random.random() < 0.7:
            # Find move that gets closest to goal
            best_move = None
            best_distance = float('inf')
            goal_row = 0 if self.player == Player.PLAYER1 else game.state.board_size - 1
            
            for move in valid_moves:
                dist = abs(move[0] - goal_row)
                if dist < best_distance:
                    best_distance = dist
                    best_move = move
            
            if best_move:
                return ("move", best_move)
        
        # Random move or wall
        if random.random() < 0.8 or game.state.get_current_player_walls() == 0:
            return ("move", random.choice(valid_moves))
        else:
            valid_walls = game.get_all_valid_walls()
            if valid_walls:
                # Limit wall choices for performance
                sample_size = min(10, len(valid_walls))
                return ("wall", random.choice(random.sample(valid_walls, sample_size)))
            return ("move", random.choice(valid_moves))
    
    def _get_minimax_move(self, game: QuoridorGame) -> Tuple[str, any]:
        """Get best move using Minimax with Alpha-Beta pruning"""
        best_score = float('-inf')
        best_move = None
        alpha = float('-inf')
        beta = float('inf')
        
        # Get all possible actions
        moves = game.get_valid_moves()
        walls = self._get_strategic_walls(game) if game.state.get_current_player_walls() > 0 else []
        
        # Evaluate all moves
        for move in moves:
            game_copy = QuoridorGame()
            game_copy.state = game.state.copy()
            game_copy.move_player(move)
            
            score = self._minimax(game_copy, self.max_depth - 1, alpha, beta, False)
            
            if score > best_score:
                best_score = score
                best_move = ("move", move)
            
            alpha = max(alpha, score)
        
        # Evaluate wall placements
        for wall in walls:
            game_copy = QuoridorGame()
            game_copy.state = game.state.copy()
            
            if game_copy.can_place_wall(wall):
                game_copy.place_wall(wall)
                score = self._minimax(game_copy, self.max_depth - 1, alpha, beta, False)
                
                if score > best_score:
                    best_score = score
                    best_move = ("wall", wall)
                
                alpha = max(alpha, score)
        
        # Fallback to first valid move
        if best_move is None:
            best_move = ("move", moves[0])
        
        return best_move
    
    def _minimax(self, game: QuoridorGame, depth: int, alpha: float, beta: float, 
                 is_maximizing: bool) -> float:
        """Minimax algorithm with alpha-beta pruning"""
        # Terminal conditions
        if game.state.game_over:
            if game.state.winner == self.player:
                return 1000 + depth  # Win sooner is better
            else:
                return -1000 - depth  # Lose later is better
        
        if depth == 0:
            return self._evaluate(game)
        
        if is_maximizing:
            max_eval = float('-inf')
            
            for move in game.get_valid_moves():
                game_copy = QuoridorGame()
                game_copy.state = game.state.copy()
                game_copy.move_player(move)
                
                eval_score = self._minimax(game_copy, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                
                if beta <= alpha:
                    break
            
            return max_eval
        else:
            min_eval = float('inf')
            
            for move in game.get_valid_moves():
                game_copy = QuoridorGame()
                game_copy.state = game.state.copy()
                game_copy.move_player(move)
                
                eval_score = self._minimax(game_copy, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                
                if beta <= alpha:
                    break
            
            return min_eval
    
    def _evaluate(self, game: QuoridorGame) -> float:
        """
        Evaluate the game state for the AI player.
        Higher scores are better for the AI.
        """
        state = game.state
        
        # Path length difference (shorter is better for AI)
        ai_path = game.get_shortest_path_length(
            state.player1_pos if self.player == Player.PLAYER1 else state.player2_pos,
            self.player
        )
        opponent_path = game.get_shortest_path_length(
            state.player2_pos if self.player == Player.PLAYER1 else state.player1_pos,
            Player.PLAYER2 if self.player == Player.PLAYER1 else Player.PLAYER1
        )
        
        path_score = (opponent_path - ai_path) * self.weights['path_difference']
        
        # Wall advantage
        ai_walls = state.player1_walls if self.player == Player.PLAYER1 else state.player2_walls
        opponent_walls = state.player2_walls if self.player == Player.PLAYER1 else state.player1_walls
        wall_score = (ai_walls - opponent_walls) * self.weights['wall_advantage']
        
        # Center control bonus
        ai_pos = state.player1_pos if self.player == Player.PLAYER1 else state.player2_pos
        center = state.board_size // 2
        center_dist = abs(ai_pos[1] - center)
        center_score = (center - center_dist) * self.weights['center_control']
        
        # Progress towards goal
        if self.player == Player.PLAYER1:
            progress = (8 - ai_pos[0]) * 2  # Player 1 wants to reach row 0
        else:
            progress = ai_pos[0] * 2  # Player 2 wants to reach row 8
        
        return path_score + wall_score + center_score + progress
    
    def _get_strategic_walls(self, game: QuoridorGame) -> List[Wall]:
        """
        Get a filtered list of strategic wall placements.
        Instead of checking all 128 possible walls, focus on positions
        that are likely to be beneficial.
        """
        strategic_walls = []
        state = game.state
        
        # Get opponent position
        opponent_pos = state.player2_pos if self.player == Player.PLAYER1 else state.player1_pos
        op_row, op_col = opponent_pos
        
        # Focus on walls near opponent's position and along their path
        for dr in range(-2, 3):
            for dc in range(-2, 3):
                row = op_row + dr
                col = op_col + dc
                
                if 0 <= row < state.board_size - 1 and 0 <= col < state.board_size - 1:
                    # Try both orientations
                    for orientation in WallOrientation:
                        wall = Wall(row, col, orientation)
                        if game.can_place_wall(wall):
                            strategic_walls.append(wall)
        
        # Limit total walls considered for performance
        if len(strategic_walls) > 20:
            strategic_walls = random.sample(strategic_walls, 20)
        
        return strategic_walls


class DifficultyLevel:
    """Enum-like class for difficulty levels"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    
    @staticmethod
    def all_levels() -> List[str]:
        return ["easy", "medium", "hard"]
    
    @staticmethod
    def display_name(level: str) -> str:
        names = {
            "easy": "Easy",
            "medium": "Medium", 
            "hard": "Hard"
        }
        return names.get(level, "Medium")
