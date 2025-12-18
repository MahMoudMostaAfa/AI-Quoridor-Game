"""
Quoridor Game - Constants and Configuration
Central location for all game constants, colors, and configuration values.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Tuple


# =============================================================================
# GAME CONSTANTS
# =============================================================================

BOARD_SIZE = 9
WALLS_PER_PLAYER = 10
PLAYER1_START = (8, 4)  # Bottom center
PLAYER2_START = (0, 4)  # Top center
PLAYER1_GOAL_ROW = 0
PLAYER2_GOAL_ROW = 8


# =============================================================================
# DISPLAY SETTINGS
# =============================================================================

SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 800
FPS = 60
FULLSCREEN = False  # Default to windowed mode

# Board dimensions
CELL_SIZE = 65
WALL_THICKNESS = 10
BOARD_PADDING = 20

# Animation settings
ANIMATION_SPEED = 4.0
HOVER_TRANSITION_SPEED = 8.0
PAWN_MOVE_SPEED = 12.0


# =============================================================================
# COLOR PALETTE - Modern Glassmorphism Theme
# =============================================================================

@dataclass(frozen=True)
class ColorScheme:
    """Modern color scheme with glassmorphism effects"""
    
    # Backgrounds
    BG_PRIMARY: Tuple[int, int, int] = (15, 15, 25)
    BG_SECONDARY: Tuple[int, int, int] = (25, 28, 40)
    BG_TERTIARY: Tuple[int, int, int] = (35, 40, 55)
    
    # Glass effect colors
    GLASS_BG: Tuple[int, int, int, int] = (255, 255, 255, 8)
    GLASS_BORDER: Tuple[int, int, int, int] = (255, 255, 255, 20)
    GLASS_HIGHLIGHT: Tuple[int, int, int, int] = (255, 255, 255, 40)
    
    # Board colors
    BOARD_BG: Tuple[int, int, int] = (30, 35, 50)
    CELL_LIGHT: Tuple[int, int, int] = (50, 55, 75)
    CELL_DARK: Tuple[int, int, int] = (40, 45, 65)
    CELL_HOVER: Tuple[int, int, int] = (70, 75, 100)
    CELL_VALID_MOVE: Tuple[int, int, int] = (46, 204, 113)
    
    # Player colors
    PLAYER1_PRIMARY: Tuple[int, int, int] = (52, 152, 219)  # Blue
    PLAYER1_SECONDARY: Tuple[int, int, int] = (41, 128, 185)
    PLAYER1_GLOW: Tuple[int, int, int] = (100, 180, 255)
    
    PLAYER2_PRIMARY: Tuple[int, int, int] = (231, 76, 60)   # Red
    PLAYER2_SECONDARY: Tuple[int, int, int] = (192, 57, 43)
    PLAYER2_GLOW: Tuple[int, int, int] = (255, 120, 100)
    
    # Wall colors
    WALL_SLOT: Tuple[int, int, int] = (35, 40, 55)
    WALL_PLACED: Tuple[int, int, int] = (241, 196, 15)      # Gold
    WALL_PREVIEW_VALID: Tuple[int, int, int] = (46, 204, 113)
    WALL_PREVIEW_INVALID: Tuple[int, int, int] = (231, 76, 60)
    
    # UI colors
    TEXT_PRIMARY: Tuple[int, int, int] = (255, 255, 255)
    TEXT_SECONDARY: Tuple[int, int, int] = (160, 165, 180)
    TEXT_MUTED: Tuple[int, int, int] = (100, 105, 120)
    
    # Button colors
    BTN_PRIMARY: Tuple[int, int, int] = (52, 152, 219)
    BTN_PRIMARY_HOVER: Tuple[int, int, int] = (41, 128, 185)
    BTN_SECONDARY: Tuple[int, int, int] = (45, 50, 70)
    BTN_SECONDARY_HOVER: Tuple[int, int, int] = (60, 65, 90)
    BTN_DANGER: Tuple[int, int, int] = (231, 76, 60)
    BTN_SUCCESS: Tuple[int, int, int] = (46, 204, 113)
    
    # Accent colors
    ACCENT_GOLD: Tuple[int, int, int] = (241, 196, 15)
    ACCENT_PURPLE: Tuple[int, int, int] = (155, 89, 182)
    ACCENT_CYAN: Tuple[int, int, int] = (26, 188, 156)
    
    # Shadows
    SHADOW_COLOR: Tuple[int, int, int, int] = (0, 0, 0, 80)


# Global color instance
COLORS = ColorScheme()


# =============================================================================
# FONT SETTINGS
# =============================================================================

FONT_SIZE_TITLE = 86
FONT_SIZE_LARGE = 48
FONT_SIZE_MEDIUM = 28
FONT_SIZE_SMALL = 20
FONT_SIZE_TINY = 16


# =============================================================================
# UI DIMENSIONS
# =============================================================================

BUTTON_HEIGHT = 55
BUTTON_WIDTH = 280
BUTTON_SPACING = 15
BUTTON_BORDER_RADIUS = 12

PANEL_WIDTH = 200
PANEL_HEIGHT = 220
PANEL_BORDER_RADIUS = 15

CARD_BORDER_RADIUS = 20


# =============================================================================
# GAME MODES
# =============================================================================

class GameMode(Enum):
    """Available game modes"""
    PVP = "pvp"
    PVE_EASY = "pve_easy"
    PVE_MEDIUM = "pve_medium"
    PVE_HARD = "pve_hard"


# =============================================================================
# SCREEN STATES
# =============================================================================

class ScreenState(Enum):
    """Application screen states"""
    MENU = "menu"
    GAME = "game"
    PAUSE = "pause"
    GAME_OVER = "game_over"
    SETTINGS = "settings"
