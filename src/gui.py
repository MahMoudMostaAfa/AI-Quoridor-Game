"""
Quoridor Game - Modern GUI using Pygame
Implements a beautiful, responsive interface with animations.
Refactored with modular architecture for clean separation of concerns.
"""

import pygame
import sys
import math
from typing import Tuple, Optional, List

from .constants import (
    COLORS, SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    CELL_SIZE, WALL_THICKNESS, BOARD_SIZE,
    FONT_SIZE_TITLE, FONT_SIZE_LARGE, FONT_SIZE_MEDIUM, FONT_SIZE_SMALL, FONT_SIZE_TINY,
    PANEL_WIDTH, PANEL_HEIGHT, PANEL_BORDER_RADIUS,
    GameMode, ScreenState
)
from .game_logic import QuoridorGame, Player, Wall, WallOrientation
from .ai import QuoridorAI, DifficultyLevel
from .ui_components import ModernButton, GlassPanel, ProgressBar, Tooltip
from .board_renderer import BoardRenderer
from .screens import ScreenManager, GameOverOverlay


class GameGUI:
    """
    Main GUI class for the Quoridor game.
    Uses modular components for clean architecture and maintainability.
    """
    
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Quoridor - Strategic Board Game")
        
        # Display setup
        self.windowed_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
        self.is_fullscreen = False
        self.screen = pygame.display.set_mode(self.windowed_size)
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT
        self.clock = pygame.time.Clock()
        
        # Initialize fonts
        self.fonts = {
            'title': pygame.font.Font(None, FONT_SIZE_TITLE),
            'large': pygame.font.Font(None, FONT_SIZE_LARGE),
            'medium': pygame.font.Font(None, FONT_SIZE_MEDIUM),
            'small': pygame.font.Font(None, FONT_SIZE_SMALL),
            'tiny': pygame.font.Font(None, FONT_SIZE_TINY),
        }
        
        # Calculate board position (centered with panels on sides)
        board_total_size = BOARD_SIZE * CELL_SIZE + (BOARD_SIZE - 1) * WALL_THICKNESS
        self.board_offset_x = (SCREEN_WIDTH - board_total_size) // 2 + 50
        self.board_offset_y = (SCREEN_HEIGHT - board_total_size) // 2 + 20
        
        # Initialize screen manager for menu/transitions
        self.screen_manager = ScreenManager()
        self.screen_manager.set_callbacks(
            on_start_game=self._on_start_game,
            on_quit=self._quit_game
        )
        
        # Initialize board renderer
        self.board_renderer = BoardRenderer(self.board_offset_x, self.board_offset_y)
        
        # Game state
        self.game = QuoridorGame()
        self.ai: Optional[QuoridorAI] = None
        self.game_mode: Optional[GameMode] = None
        
        # UI state
        self.current_screen = ScreenState.MENU
        self.wall_placement_mode = False
        self.wall_orientation = WallOrientation.HORIZONTAL
        self.wall_preview: Optional[Wall] = None
        self.valid_moves: List[Tuple[int, int]] = []
        
        # Animation state
        self.animation_time = 0.0
        self.ai_thinking = False
        self.ai_think_timer = 0.0
        
        # Game over overlay
        self.game_over_overlay: Optional[GameOverOverlay] = None
        
        # Tooltip
        self.tooltip = Tooltip(self.fonts['tiny'])
        
        # Create UI components
        self._create_game_ui()
    
    def _create_game_ui(self):
        """Create in-game UI components"""
        # Right side buttons (positioned relative to screen width)
        btn_x = self.screen_width - 160
        btn_width = 140
        btn_height = 45
        
        self.game_buttons = [
            ModernButton(btn_x, 20, btn_width, btn_height, "Menu",
                        self.fonts['small'], self._return_to_menu, style="secondary"),
            ModernButton(btn_x, 75, btn_width, btn_height, "Restart",
                        self.fonts['small'], self._restart_game, style="secondary"),
            ModernButton(btn_x, 130, btn_width, btn_height, "Place Wall",
                        self.fonts['small'], self._toggle_wall_mode, style="primary"),
            ModernButton(btn_x, 185, btn_width, btn_height, 
                        "Windowed" if self.is_fullscreen else "Fullscreen",
                        self.fonts['small'], self._toggle_fullscreen, style="secondary"),
        ]
        
        # Player panels - position vertically centered
        panel_x = 20
        panel_center_y = self.screen_height // 2
        panel_spacing = 20
        
        # Player 1 panel above center, Player 2 below center
        p1_panel_y = panel_center_y - PANEL_HEIGHT - panel_spacing // 2
        p2_panel_y = panel_center_y + panel_spacing // 2
        
        self.player1_panel = GlassPanel(panel_x, p1_panel_y, PANEL_WIDTH, PANEL_HEIGHT,
                                        PANEL_BORDER_RADIUS)
        self.player2_panel = GlassPanel(panel_x, p2_panel_y, PANEL_WIDTH, PANEL_HEIGHT,
                                        PANEL_BORDER_RADIUS)
        
        # Wall progress bars (positioned relative to panels)
        self.player1_walls_bar = ProgressBar(panel_x + 20, p1_panel_y + 160, 
                                             PANEL_WIDTH - 40, 8, 10, COLORS.WALL_PLACED)
        self.player2_walls_bar = ProgressBar(panel_x + 20, p2_panel_y + 160, 
                                             PANEL_WIDTH - 40, 8, 10, COLORS.WALL_PLACED)
        
        # Store panel positions for drawing
        self.p1_panel_y = p1_panel_y
        self.p2_panel_y = p2_panel_y
    
    def _on_start_game(self, mode: GameMode):
        """Callback when game starts from menu"""
        self.game_mode = mode
        self.game.reset()
        self.current_screen = ScreenState.GAME
        self.valid_moves = self.game.get_valid_moves()
        self.wall_placement_mode = False
        self.game_over_overlay = None
        
        # Setup AI if needed
        if mode == GameMode.PVE_EASY:
            self.ai = QuoridorAI(Player.PLAYER2, "easy")
        elif mode == GameMode.PVE_MEDIUM:
            self.ai = QuoridorAI(Player.PLAYER2, "medium")
        elif mode == GameMode.PVE_HARD:
            self.ai = QuoridorAI(Player.PLAYER2, "hard")
        else:
            self.ai = None
    
    def _return_to_menu(self):
        """Return to main menu"""
        self.current_screen = ScreenState.MENU
        self.screen_manager.return_to_menu()
        self.game.reset()
        self.game_over_overlay = None
    
    def _restart_game(self):
        """Restart current game"""
        if self.game_mode:
            self._on_start_game(self.game_mode)
    
    def _toggle_wall_mode(self):
        """Toggle wall placement mode"""
        if self.game.state.get_current_player_walls() > 0:
            self.wall_placement_mode = not self.wall_placement_mode
            self.wall_orientation = WallOrientation.HORIZONTAL
            self.wall_preview = None
            
            # Update button text
            self.game_buttons[2].text = "Cancel Wall" if self.wall_placement_mode else "Place Wall"
    
    def _quit_game(self):
        """Quit the application"""
        pygame.quit()
        sys.exit()
    
    def _toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode"""
        self.is_fullscreen = not self.is_fullscreen
        
        if self.is_fullscreen:
            # Switch to fullscreen first, then get the actual dimensions
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            # Now get the actual fullscreen resolution
            self.screen_width = self.screen.get_width()
            self.screen_height = self.screen.get_height()
        else:
            # Return to windowed mode
            self.screen_width = SCREEN_WIDTH
            self.screen_height = SCREEN_HEIGHT
            self.screen = pygame.display.set_mode(self.windowed_size)
        
        # Recalculate board position for new screen size
        self._recalculate_layout()
        
        # Update screen manager for menu
        self.screen_manager.update_screen_size(self.screen_width, self.screen_height)
    
    def _recalculate_layout(self):
        """Recalculate UI positions based on current screen size"""
        # Recalculate board position (centered in screen)
        board_total_size = BOARD_SIZE * CELL_SIZE + (BOARD_SIZE - 1) * WALL_THICKNESS
        
        # Leave room for left panel and right buttons
        left_margin = PANEL_WIDTH + 40   # Left panel area
        right_margin = 180               # Right buttons area
        
        # Calculate available space and center the board within it
        available_width = self.screen_width - left_margin - right_margin
        
        self.board_offset_x = left_margin + (available_width - board_total_size) // 2
        self.board_offset_y = (self.screen_height - board_total_size) // 2
        
        # Update board renderer position
        self.board_renderer.offset_x = self.board_offset_x
        self.board_renderer.offset_y = self.board_offset_y
        
        # Recreate game UI with new positions
        self._create_game_ui()
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            self.animation_time += dt
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    self._handle_event(event)
            
            # Update
            self._update(dt)
            
            # Draw
            self._draw()
            
            pygame.display.flip()
        
        pygame.quit()
    
    def _handle_event(self, event: pygame.event.Event):
        """Handle pygame events based on current screen"""
        # Global key handlers (work on any screen)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                self._toggle_fullscreen()
                return
            elif event.key == pygame.K_ESCAPE and self.is_fullscreen:
                self._toggle_fullscreen()
                return
        
        if self.current_screen == ScreenState.MENU:
            self.screen_manager.handle_event(event)
        
        elif self.current_screen == ScreenState.GAME:
            # Handle game over overlay first
            if self.game_over_overlay:
                if self.game_over_overlay.handle_event(event):
                    return
            
            # Handle button events
            for button in self.game_buttons:
                if button.handle_event(event):
                    return
            
            # Don't handle game input if game is over or AI is thinking
            if self.game.state.game_over or self.ai_thinking:
                return
            
            # Don't handle input during AI turn
            if self._is_ai_turn():
                return
            
            self._handle_game_event(event)
    
    def _handle_game_event(self, event: pygame.event.Event):
        """Handle game-specific events"""
        if event.type == pygame.MOUSEMOTION:
            self._handle_mouse_motion(event.pos)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                self._handle_left_click(event.pos)
            elif event.button == 3:  # Right click - rotate wall
                if self.wall_placement_mode:
                    self._rotate_wall()
        
        elif event.type == pygame.KEYDOWN:
            self._handle_key_press(event.key)
    
    def _handle_mouse_motion(self, pos: Tuple[int, int]):
        """Handle mouse movement"""
        # Update board renderer hover state
        cell = self.board_renderer.get_cell_at_pos(pos)
        self.board_renderer.set_hovered_cell(cell)
        
        # Update wall preview
        if self.wall_placement_mode:
            wall_pos = self.board_renderer.get_wall_at_pos(pos)
            if wall_pos:
                row, col = wall_pos
                self.wall_preview = Wall(row, col, self.wall_orientation)
            else:
                self.wall_preview = None
        
        # Update button hover states
        for button in self.game_buttons:
            button.hovered = button.rect.collidepoint(pos)
    
    def _handle_left_click(self, pos: Tuple[int, int]):
        """Handle left mouse click"""
        if self.wall_placement_mode:
            # Try to place wall
            if self.wall_preview and self.game.can_place_wall(self.wall_preview):
                self.game.place_wall(self.wall_preview)
                self.wall_placement_mode = False
                self.wall_preview = None
                self.game_buttons[2].text = "Place Wall"
                self.valid_moves = self.game.get_valid_moves()
                self._check_game_over()
        else:
            # Try to move player
            cell = self.board_renderer.get_cell_at_pos(pos)
            if cell and cell in self.valid_moves:
                self.game.move_player(cell)
                self.valid_moves = self.game.get_valid_moves()
                self._check_game_over()
    
    def _handle_key_press(self, key: int):
        """Handle keyboard input"""
        if key == pygame.K_w:
            self._toggle_wall_mode()
        elif key == pygame.K_r:
            if self.wall_placement_mode:
                self._rotate_wall()
        elif key == pygame.K_ESCAPE:
            if self.wall_placement_mode:
                self.wall_placement_mode = False
                self.wall_preview = None
                self.game_buttons[2].text = "Place Wall"
    
    def _rotate_wall(self):
        """Rotate wall orientation"""
        if self.wall_orientation == WallOrientation.HORIZONTAL:
            self.wall_orientation = WallOrientation.VERTICAL
        else:
            self.wall_orientation = WallOrientation.HORIZONTAL
        
        # Update preview
        if self.wall_preview:
            self.wall_preview = Wall(self.wall_preview.row, self.wall_preview.col,
                                     self.wall_orientation)
    
    def _is_ai_turn(self) -> bool:
        """Check if it's the AI's turn"""
        return (self.ai is not None and 
                self.game.state.current_player == Player.PLAYER2 and
                not self.game.state.game_over)
    
    def _check_game_over(self):
        """Check if game is over and create overlay"""
        if self.game.state.game_over and self.game_over_overlay is None:
            winner = self.game.state.winner
            
            if self.ai is not None:
                winner_text = "You Win" if winner == Player.PLAYER1 else "AI Wins"
            else:
                winner_text = "Player 1" if winner == Player.PLAYER1 else "Player 2"
            
            winner_color = COLORS.PLAYER1_PRIMARY if winner == Player.PLAYER1 else COLORS.PLAYER2_PRIMARY
            
            self.game_over_overlay = GameOverOverlay(
                self.fonts, winner_text, winner_color,
                self._return_to_menu, self._restart_game,
                self.screen_width, self.screen_height
            )
    
    def _update(self, dt: float):
        """Update game state and animations"""
        if self.current_screen == ScreenState.MENU:
            self.screen_manager.update(dt)
        
        elif self.current_screen == ScreenState.GAME:
            # Update board renderer
            self.board_renderer.update(dt, 
                                       self.game.state.player1_pos,
                                       self.game.state.player2_pos)
            
            # Update UI components
            for button in self.game_buttons:
                button.update(dt)
            
            self.player1_panel.update(dt)
            self.player2_panel.update(dt)
            
            # Update wall bars
            self.player1_walls_bar.set_value(self.game.state.player1_walls)
            self.player2_walls_bar.set_value(self.game.state.player2_walls)
            self.player1_walls_bar.update(dt)
            self.player2_walls_bar.update(dt)
            
            # Update panel highlights
            is_p1_turn = self.game.state.current_player == Player.PLAYER1
            self.player1_panel.set_highlight(is_p1_turn, COLORS.PLAYER1_PRIMARY)
            self.player2_panel.set_highlight(not is_p1_turn, COLORS.PLAYER2_PRIMARY)
            
            # Update game over overlay
            if self.game_over_overlay:
                self.game_over_overlay.update(dt)
            
            # Update tooltip
            self.tooltip.update(dt)
            
            # Handle AI turn
            if self._is_ai_turn() and not self.ai_thinking:
                self.ai_thinking = True
                self.ai_think_timer = 0.4  # Small delay for visual feedback
            
            if self.ai_thinking:
                self.ai_think_timer -= dt
                if self.ai_think_timer <= 0:
                    self._execute_ai_move()
                    self.ai_thinking = False
    
    def _execute_ai_move(self):
        """Execute AI move"""
        if not self.ai or self.game.state.game_over:
            return
        
        move_type, move_data = self.ai.get_best_move(self.game)
        
        if move_type == "move":
            self.game.move_player(move_data)
        else:
            self.game.place_wall(move_data)
        
        self.valid_moves = self.game.get_valid_moves()
        self._check_game_over()
    
    def _draw(self):
        """Draw the current screen"""
        if self.current_screen == ScreenState.MENU:
            self.screen_manager.draw(self.screen)
        
        elif self.current_screen == ScreenState.GAME:
            self._draw_game()
    
    def _draw_game(self):
        """Draw the game screen"""
        # Draw gradient background
        self._draw_background()
        
        # Draw board
        self.board_renderer.draw_board(self.screen)
        self.board_renderer.draw_walls(self.screen, self.game.state.walls)
        
        # Draw valid moves (only when not placing wall and not AI turn)
        if not self.wall_placement_mode and not self._is_ai_turn():
            self.board_renderer.draw_valid_moves(self.screen, self.valid_moves, 
                                                  self.game.state.current_player)
        
        # Draw wall preview
        if self.wall_placement_mode and self.wall_preview:
            is_valid = self.game.can_place_wall(self.wall_preview)
            self.board_renderer.draw_wall_preview(self.screen, self.wall_preview, is_valid)
        
        # Draw pawns
        self.board_renderer.draw_pawns(self.screen, self.game.state.current_player)
        
        # Draw UI
        self._draw_ui()
        
        # Draw game over overlay
        if self.game_over_overlay:
            self.game_over_overlay.draw(self.screen)
        
        # Draw tooltip
        self.tooltip.draw(self.screen)
    
    def _draw_background(self):
        """Draw gradient background"""
        for y in range(self.screen_height):
            progress = y / self.screen_height
            color = tuple(
                int(COLORS.BG_PRIMARY[i] + (COLORS.BG_SECONDARY[i] - COLORS.BG_PRIMARY[i]) * progress * 0.5)
                for i in range(3)
            )
            pygame.draw.line(self.screen, color, (0, y), (self.screen_width, y))
    
    def _draw_ui(self):
        """Draw all UI elements"""
        # Draw buttons
        for button in self.game_buttons:
            button.draw(self.screen)
        
        # Draw player panels
        self._draw_player_panel(1)
        self._draw_player_panel(2)
        
        # Draw turn indicator
        self._draw_turn_indicator()
        
        # Draw wall mode indicator
        if self.wall_placement_mode:
            self._draw_wall_mode_indicator()
    
    def _draw_player_panel(self, player_num: int):
        """Draw player info panel"""
        is_player1 = player_num == 1
        panel = self.player1_panel if is_player1 else self.player2_panel
        walls_bar = self.player1_walls_bar if is_player1 else self.player2_walls_bar
        
        color = COLORS.PLAYER1_PRIMARY if is_player1 else COLORS.PLAYER2_PRIMARY
        walls = self.game.state.player1_walls if is_player1 else self.game.state.player2_walls
        is_current = (self.game.state.current_player == Player.PLAYER1) == is_player1
        
        # Draw panel background
        panel.draw(self.screen)
        
        # Get panel position
        x = panel.rect.x
        y = panel.rect.y
        width = panel.rect.width
        
        # Draw player label
        if is_player1:
            label = "Player 1"
        else:
            if self.ai:
                difficulty = "Easy" if self.game_mode == GameMode.PVE_EASY else \
                            "Medium" if self.game_mode == GameMode.PVE_MEDIUM else "Hard"
                label = f"AI ({difficulty})"
            else:
                label = "Player 2"
        
        label_surface = self.fonts['medium'].render(label, True, color)
        label_rect = label_surface.get_rect(center=(x + width // 2, y + 35))
        self.screen.blit(label_surface, label_rect)
        
        # Draw pawn icon
        pawn_y = y + 90
        self._draw_pawn_icon(x + width // 2, pawn_y, color, 25, is_current)
        
        # Draw walls remaining text
        walls_text = f"Walls: {walls}"
        walls_surface = self.fonts['small'].render(walls_text, True, COLORS.TEXT_PRIMARY)
        walls_rect = walls_surface.get_rect(center=(x + width // 2, y + 140))
        self.screen.blit(walls_surface, walls_rect)
        
        # Draw wall progress bar
        walls_bar.draw(self.screen)
        
        # Draw thinking indicator for AI
        if not is_player1 and self.ai_thinking:
            thinking_text = "Thinking..."
            thinking_surface = self.fonts['tiny'].render(thinking_text, True, COLORS.ACCENT_CYAN)
            thinking_rect = thinking_surface.get_rect(center=(x + width // 2, y + 185))
            self.screen.blit(thinking_surface, thinking_rect)
    
    def _draw_pawn_icon(self, x: int, y: int, color: Tuple[int, int, int], 
                        radius: int, glow: bool):
        """Draw a pawn icon"""
        if glow:
            # Animated glow
            pulse = (math.sin(self.animation_time * 3) + 1) / 2
            for i in range(3, 0, -1):
                glow_radius = radius + i * 4 + int(pulse * 2)
                glow_alpha = int((30 - i * 8) * (0.8 + pulse * 0.2))
                glow_surface = pygame.Surface((glow_radius * 2 + 10, glow_radius * 2 + 10), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (*color, max(0, glow_alpha)),
                                 (glow_radius + 5, glow_radius + 5), glow_radius)
                self.screen.blit(glow_surface, (x - glow_radius - 5, y - glow_radius - 5))
        
        # Shadow
        pygame.draw.circle(self.screen, (0, 0, 0, 40), (x + 2, y + 2), radius)
        
        # Main pawn
        pygame.draw.circle(self.screen, color, (x, y), radius)
        
        # Highlight
        highlight_radius = radius // 3
        pygame.draw.circle(self.screen, (255, 255, 255),
                          (x - radius // 4, y - radius // 4), highlight_radius)
    
    def _draw_turn_indicator(self):
        """Draw current turn indicator"""
        is_p1 = self.game.state.current_player == Player.PLAYER1
        
        if self.ai_thinking:
            text = "AI is thinking..."
            color = COLORS.ACCENT_CYAN
        elif is_p1:
            text = "Player 1's Turn"
            color = COLORS.PLAYER1_PRIMARY
        else:
            if self.ai:
                text = "AI's Turn"
            else:
                text = "Player 2's Turn"
            color = COLORS.PLAYER2_PRIMARY
        
        # Draw with shadow
        shadow_surface = self.fonts['medium'].render(text, True, (0, 0, 0))
        text_surface = self.fonts['medium'].render(text, True, color)
        
        text_rect = text_surface.get_rect(center=(self.screen_width // 2, 40))
        self.screen.blit(shadow_surface, (text_rect.x + 2, text_rect.y + 2))
        self.screen.blit(text_surface, text_rect)
    
    def _draw_wall_mode_indicator(self):
        """Draw wall placement mode indicator"""
        # Mode text
        orientation = "Horizontal" if self.wall_orientation == WallOrientation.HORIZONTAL else "Vertical"
        mode_text = f"Wall Mode: {orientation}"
        mode_surface = self.fonts['small'].render(mode_text, True, COLORS.WALL_PLACED)
        mode_rect = mode_surface.get_rect(center=(self.screen_width // 2, 70))
        self.screen.blit(mode_surface, mode_rect)
        
        # Help text
        help_text = "Right-click to rotate • ESC to cancel • F11 for fullscreen"
        help_surface = self.fonts['tiny'].render(help_text, True, COLORS.TEXT_MUTED)
        help_rect = help_surface.get_rect(center=(self.screen_width // 2, self.screen_height - 30))
        self.screen.blit(help_surface, help_rect)
        
        # Draw wall orientation preview
        preview_x = self.screen_width // 2
        preview_y = self.screen_height - 70
        
        if self.wall_orientation == WallOrientation.HORIZONTAL:
            pygame.draw.rect(self.screen, COLORS.WALL_PLACED,
                           (preview_x - 40, preview_y - 4, 80, 8), border_radius=4)
        else:
            pygame.draw.rect(self.screen, COLORS.WALL_PLACED,
                           (preview_x - 4, preview_y - 40, 8, 80), border_radius=4)
