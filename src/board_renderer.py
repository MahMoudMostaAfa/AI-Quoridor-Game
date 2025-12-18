"""
Quoridor Game - Board Renderer Module
Handles all board rendering with modern visuals and animations.
"""

import pygame
import math
from typing import Tuple, Optional, List, Set
from .constants import (
    COLORS, CELL_SIZE, WALL_THICKNESS, BOARD_SIZE,
    ANIMATION_SPEED, CARD_BORDER_RADIUS
)
from .game_logic import Wall, WallOrientation, Player


class BoardRenderer:
    """Handles rendering of the game board with modern effects"""
    
    def __init__(self, offset_x: int, offset_y: int):
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.cell_size = CELL_SIZE
        self.wall_thickness = WALL_THICKNESS
        self.board_size = BOARD_SIZE
        
        # Animation state
        self.animation_time = 0.0
        self.hovered_cell: Optional[Tuple[int, int]] = None
        self.hover_progress: dict = {}  # Cell -> hover progress
        
        # Pawn animation
        self.pawn_positions = {
            Player.PLAYER1: None,
            Player.PLAYER2: None
        }
        self.pawn_targets = {
            Player.PLAYER1: None,
            Player.PLAYER2: None
        }
        
        # Calculate board dimensions
        self.board_width = self.board_size * self.cell_size + (self.board_size - 1) * self.wall_thickness
        self.board_height = self.board_width
    
    def update(self, dt: float, player1_pos: Tuple[int, int], player2_pos: Tuple[int, int]):
        """Update animations"""
        self.animation_time += dt
        
        # Update hover animations
        for cell in list(self.hover_progress.keys()):
            target = 1.0 if cell == self.hovered_cell else 0.0
            self.hover_progress[cell] += (target - self.hover_progress[cell]) * min(1.0, dt * 10)
            if self.hover_progress[cell] < 0.01 and target == 0:
                del self.hover_progress[cell]
        
        if self.hovered_cell and self.hovered_cell not in self.hover_progress:
            self.hover_progress[self.hovered_cell] = 0.0
        
        # Update pawn positions (smooth movement)
        for player, pos in [(Player.PLAYER1, player1_pos), (Player.PLAYER2, player2_pos)]:
            target_screen = self._cell_to_screen_center(pos)
            
            if self.pawn_positions[player] is None:
                self.pawn_positions[player] = target_screen
            else:
                current = self.pawn_positions[player]
                dx = target_screen[0] - current[0]
                dy = target_screen[1] - current[1]
                speed = min(1.0, dt * 12)
                self.pawn_positions[player] = (
                    current[0] + dx * speed,
                    current[1] + dy * speed
                )
    
    def set_hovered_cell(self, cell: Optional[Tuple[int, int]]):
        """Set the currently hovered cell"""
        self.hovered_cell = cell
    
    def draw_board(self, screen: pygame.Surface):
        """Draw the game board background and cells"""
        # Draw board container with shadow
        container_rect = pygame.Rect(
            self.offset_x - 15,
            self.offset_y - 15,
            self.board_width + 30,
            self.board_height + 30
        )
        
        # Shadow
        shadow_surface = pygame.Surface((container_rect.width + 20, container_rect.height + 20), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 50),
                        (10, 10, container_rect.width, container_rect.height),
                        border_radius=CARD_BORDER_RADIUS + 5)
        screen.blit(shadow_surface, (container_rect.x - 10, container_rect.y - 10))
        
        # Main container
        pygame.draw.rect(screen, COLORS.BOARD_BG, container_rect, border_radius=CARD_BORDER_RADIUS)
        pygame.draw.rect(screen, COLORS.TEXT_MUTED, container_rect, width=1, border_radius=CARD_BORDER_RADIUS)
        
        # Draw cells
        for row in range(self.board_size):
            for col in range(self.board_size):
                self._draw_cell(screen, row, col)
        
        # Draw wall slots
        self._draw_wall_slots(screen)
    
    def _draw_cell(self, screen: pygame.Surface, row: int, col: int):
        """Draw a single cell"""
        x, y = self._cell_to_screen(row, col)
        
        # Determine base color
        is_goal_p1 = row == 0
        is_goal_p2 = row == self.board_size - 1
        
        if (row + col) % 2 == 0:
            base_color = COLORS.CELL_LIGHT
        else:
            base_color = COLORS.CELL_DARK
        
        # Apply hover effect
        hover_amount = self.hover_progress.get((row, col), 0.0)
        if hover_amount > 0:
            color = self._lerp_color(base_color, COLORS.CELL_HOVER, hover_amount)
        else:
            color = base_color
        
        # Draw cell
        cell_rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
        pygame.draw.rect(screen, color, cell_rect, border_radius=6)
        
        # Draw goal highlighting
        if is_goal_p1:
            self._draw_goal_highlight(screen, x, y, COLORS.PLAYER1_PRIMARY)
        elif is_goal_p2:
            self._draw_goal_highlight(screen, x, y, COLORS.PLAYER2_PRIMARY)
    
    def _draw_goal_highlight(self, screen: pygame.Surface, x: int, y: int, color: Tuple[int, int, int]):
        """Draw goal row highlight"""
        highlight_surface = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
        
        # Gradient effect
        for i in range(self.cell_size // 2):
            alpha = int(30 * (1 - i / (self.cell_size // 2)))
            pygame.draw.rect(highlight_surface, (*color, alpha),
                           (i, i, self.cell_size - 2*i, self.cell_size - 2*i),
                           border_radius=max(1, 6 - i))
        
        screen.blit(highlight_surface, (x, y))
    
    def _draw_wall_slots(self, screen: pygame.Surface):
        """Draw wall placement slots"""
        for row in range(self.board_size - 1):
            for col in range(self.board_size - 1):
                # Intersection point
                ix = self.offset_x + (col + 1) * self.cell_size + col * self.wall_thickness
                iy = self.offset_y + (row + 1) * self.cell_size + row * self.wall_thickness
                
                pygame.draw.rect(screen, COLORS.WALL_SLOT,
                               (ix, iy, self.wall_thickness, self.wall_thickness),
                               border_radius=2)
    
    def draw_walls(self, screen: pygame.Surface, walls: Set[Wall]):
        """Draw placed walls"""
        for wall in walls:
            self._draw_wall(screen, wall, COLORS.WALL_PLACED)
    
    def draw_wall_preview(self, screen: pygame.Surface, wall: Optional[Wall], is_valid: bool):
        """Draw wall placement preview"""
        if wall is None:
            return
        
        color = COLORS.WALL_PREVIEW_VALID if is_valid else COLORS.WALL_PREVIEW_INVALID
        self._draw_wall(screen, wall, color, alpha=180)
    
    def _draw_wall(self, screen: pygame.Surface, wall: Wall, color: Tuple[int, int, int], alpha: int = 255):
        """Draw a single wall"""
        row, col = wall.row, wall.col
        
        # Calculate intersection center
        ix = self.offset_x + (col + 1) * self.cell_size + col * self.wall_thickness + self.wall_thickness // 2
        iy = self.offset_y + (row + 1) * self.cell_size + row * self.wall_thickness + self.wall_thickness // 2
        
        if wall.orientation == WallOrientation.HORIZONTAL:
            x = ix - self.cell_size - self.wall_thickness
            y = iy - self.wall_thickness // 2
            width = 2 * self.cell_size + self.wall_thickness
            height = self.wall_thickness
        else:
            x = ix - self.wall_thickness // 2
            y = iy - self.cell_size - self.wall_thickness
            width = self.wall_thickness
            height = 2 * self.cell_size + self.wall_thickness
        
        if alpha < 255:
            wall_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.rect(wall_surface, (*color, alpha),
                           (0, 0, width, height), border_radius=4)
            screen.blit(wall_surface, (x, y))
        else:
            # Draw shadow
            shadow_surface = pygame.Surface((width + 4, height + 4), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surface, (0, 0, 0, 40),
                           (2, 2, width, height), border_radius=4)
            screen.blit(shadow_surface, (x - 2, y - 2))
            
            # Draw wall
            pygame.draw.rect(screen, color, (x, y, width, height), border_radius=4)
            
            # Draw highlight
            if wall.orientation == WallOrientation.HORIZONTAL:
                pygame.draw.line(screen, (255, 255, 255, 80),
                               (x + 4, y + 2), (x + width - 4, y + 2), 1)
            else:
                pygame.draw.line(screen, (255, 255, 255, 80),
                               (x + 2, y + 4), (x + 2, y + height - 4), 1)
    
    def draw_valid_moves(self, screen: pygame.Surface, valid_moves: List[Tuple[int, int]], 
                          current_player: Player):
        """Draw indicators for valid moves using player's color"""
        # Get player color and create lighter version
        if current_player == Player.PLAYER1:
            base_color = COLORS.PLAYER1_PRIMARY
        else:
            base_color = COLORS.PLAYER2_PRIMARY
        
        # Create a lighter version of the color
        light_color = (
            min(255, base_color[0] + 60),
            min(255, base_color[1] + 60),
            min(255, base_color[2] + 60)
        )
        
        for row, col in valid_moves:
            x, y = self._cell_to_screen(row, col)
            center_x = x + self.cell_size // 2
            center_y = y + self.cell_size // 2
            
            # Pulsing animation
            pulse = (math.sin(self.animation_time * ANIMATION_SPEED) + 1) / 2
            radius = int(10 + pulse * 4)
            alpha = int(80 + pulse * 50)  # Lower opacity (80-130 range)
            
            # Draw glow
            glow_surface = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
            for i in range(3):
                glow_radius = radius + (3 - i) * 4
                glow_alpha = alpha // (i + 2)
                pygame.draw.circle(glow_surface, (*light_color, glow_alpha),
                                 (self.cell_size // 2, self.cell_size // 2), glow_radius)
            
            # Draw main indicator
            pygame.draw.circle(glow_surface, (*light_color, alpha),
                             (self.cell_size // 2, self.cell_size // 2), radius)
            
            screen.blit(glow_surface, (x, y))
    
    def draw_pawns(self, screen: pygame.Surface, current_player: Player):
        """Draw player pawns with glow effect for current player"""
        for player in [Player.PLAYER1, Player.PLAYER2]:
            pos = self.pawn_positions[player]
            if pos is None:
                continue
            
            x, y = pos
            is_current = player == current_player
            
            if player == Player.PLAYER1:
                color = COLORS.PLAYER1_PRIMARY
                glow_color = COLORS.PLAYER1_GLOW
            else:
                color = COLORS.PLAYER2_PRIMARY
                glow_color = COLORS.PLAYER2_GLOW
            
            self._draw_pawn(screen, int(x), int(y), color, glow_color, 24, is_current)
    
    def _draw_pawn(self, screen: pygame.Surface, x: int, y: int,
                   color: Tuple[int, int, int], glow_color: Tuple[int, int, int],
                   radius: int, glow: bool):
        """Draw a player pawn"""
        # Draw glow effect for current player
        if glow:
            pulse = (math.sin(self.animation_time * 3) + 1) / 2
            for i in range(4, 0, -1):
                glow_radius = radius + i * 5 + int(pulse * 3)
                glow_alpha = int((40 - i * 8) * (0.7 + pulse * 0.3))
                glow_surface = pygame.Surface((glow_radius * 2 + 10, glow_radius * 2 + 10), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (*glow_color, max(0, glow_alpha)),
                                 (glow_radius + 5, glow_radius + 5), glow_radius)
                screen.blit(glow_surface, (x - glow_radius - 5, y - glow_radius - 5))
        
        # Draw shadow
        shadow_surface = pygame.Surface((radius * 2 + 10, radius * 2 + 10), pygame.SRCALPHA)
        pygame.draw.circle(shadow_surface, (0, 0, 0, 40),
                         (radius + 7, radius + 7), radius)
        screen.blit(shadow_surface, (x - radius - 5, y - radius - 3))
        
        # Draw main pawn
        pygame.draw.circle(screen, color, (x, y), radius)
        
        # Draw gradient/highlight
        highlight_radius = radius // 3
        highlight_x = x - radius // 4
        highlight_y = y - radius // 4
        pygame.draw.circle(screen, (255, 255, 255), (highlight_x, highlight_y), highlight_radius)
        
        # Draw rim
        pygame.draw.circle(screen, self._darken_color(color, 0.8), (x, y), radius, 2)
    
    def get_cell_at_pos(self, pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Get board cell at screen position"""
        x, y = pos
        
        for row in range(self.board_size):
            for col in range(self.board_size):
                cell_x, cell_y = self._cell_to_screen(row, col)
                if (cell_x <= x < cell_x + self.cell_size and
                    cell_y <= y < cell_y + self.cell_size):
                    return (row, col)
        
        return None
    
    def get_wall_at_pos(self, pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Get wall intersection at screen position"""
        x, y = pos
        
        for row in range(self.board_size - 1):
            for col in range(self.board_size - 1):
                # Calculate intersection center
                ix = self.offset_x + (col + 1) * self.cell_size + col * self.wall_thickness + self.wall_thickness // 2
                iy = self.offset_y + (row + 1) * self.cell_size + row * self.wall_thickness + self.wall_thickness // 2
                
                # Check distance from intersection
                dist = math.sqrt((x - ix) ** 2 + (y - iy) ** 2)
                if dist < self.cell_size * 0.8:
                    return (row, col)
        
        return None
    
    def _cell_to_screen(self, row: int, col: int) -> Tuple[int, int]:
        """Convert cell coordinates to screen position"""
        x = self.offset_x + col * (self.cell_size + self.wall_thickness)
        y = self.offset_y + row * (self.cell_size + self.wall_thickness)
        return (x, y)
    
    def _cell_to_screen_center(self, pos: Tuple[int, int]) -> Tuple[int, int]:
        """Convert cell coordinates to screen center position"""
        row, col = pos
        x, y = self._cell_to_screen(row, col)
        return (x + self.cell_size // 2, y + self.cell_size // 2)
    
    def _lerp_color(self, c1: Tuple, c2: Tuple, t: float) -> Tuple[int, int, int]:
        """Linear interpolation between colors"""
        return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
    
    def _darken_color(self, color: Tuple, factor: float) -> Tuple[int, int, int]:
        """Darken a color by a factor"""
        return tuple(int(c * factor) for c in color)
