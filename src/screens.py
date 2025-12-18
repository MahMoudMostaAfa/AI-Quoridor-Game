"""
Quoridor Game - Screen Manager Module
Handles different game screens (menu, game, game over) with transitions.
"""

import pygame
from typing import Optional, Callable
from abc import ABC, abstractmethod

from .constants import (
    COLORS, SCREEN_WIDTH, SCREEN_HEIGHT,
    FONT_SIZE_TITLE, FONT_SIZE_LARGE, FONT_SIZE_MEDIUM, FONT_SIZE_SMALL,
    BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_SPACING,
    ScreenState, GameMode
)
from .ui_components import ModernButton, GlassPanel, AnimatedText


class Screen(ABC):
    """Base class for all screens"""
    
    def __init__(self, screen_manager: 'ScreenManager'):
        self.manager = screen_manager
        self.components = []
        self._fade_alpha = 0.0
        self._transitioning = False
    
    @abstractmethod
    def setup(self):
        """Initialize screen components"""
        pass
    
    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events, return True if consumed"""
        pass
    
    @abstractmethod
    def update(self, dt: float):
        """Update screen state"""
        pass
    
    @abstractmethod
    def draw(self, surface: pygame.Surface):
        """Draw the screen"""
        pass


class MenuScreen(Screen):
    """Main menu screen"""
    
    def setup(self):
        self.fonts = self.manager.fonts
        self.screen_width = self.manager.screen_width
        self.screen_height = self.manager.screen_height
        center_x = self.screen_width // 2
        start_y = 320
        
        # Create buttons
        self.buttons = [
            ModernButton(
                center_x - BUTTON_WIDTH // 2, start_y,
                BUTTON_WIDTH, BUTTON_HEIGHT,
                "Player vs Player", self.fonts['medium'],
                lambda: self.manager.start_game(GameMode.PVP),
                style="primary"
            ),
            ModernButton(
                center_x - BUTTON_WIDTH // 2, start_y + BUTTON_HEIGHT + BUTTON_SPACING,
                BUTTON_WIDTH, BUTTON_HEIGHT,
                "vs AI - Easy", self.fonts['medium'],
                lambda: self.manager.start_game(GameMode.PVE_EASY),
                style="secondary"
            ),
            ModernButton(
                center_x - BUTTON_WIDTH // 2, start_y + (BUTTON_HEIGHT + BUTTON_SPACING) * 2,
                BUTTON_WIDTH, BUTTON_HEIGHT,
                "vs AI - Medium", self.fonts['medium'],
                lambda: self.manager.start_game(GameMode.PVE_MEDIUM),
                style="secondary"
            ),
            ModernButton(
                center_x - BUTTON_WIDTH // 2, start_y + (BUTTON_HEIGHT + BUTTON_SPACING) * 3,
                BUTTON_WIDTH, BUTTON_HEIGHT,
                "vs AI - Hard", self.fonts['medium'],
                lambda: self.manager.start_game(GameMode.PVE_HARD),
                style="secondary"
            ),
            ModernButton(
                center_x - BUTTON_WIDTH // 2, start_y + (BUTTON_HEIGHT + BUTTON_SPACING) * 4 + 20,
                BUTTON_WIDTH, BUTTON_HEIGHT,
                "Quit Game", self.fonts['medium'],
                self.manager.quit_game,
                style="danger"
            ),
        ]
        
        # Title animation
        self.title_y = 130
        self.subtitle_y = 210
        self._time = 0.0
        
        # Load larger font for epic title
        self.title_font = pygame.font.Font(None, 96)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        for button in self.buttons:
            if button.handle_event(event):
                return True
        return False
    
    def update(self, dt: float):
        self._time += dt
        for button in self.buttons:
            button.update(dt)
    
    def draw(self, surface: pygame.Surface):
        # Draw background gradient
        self._draw_gradient_bg(surface)
        
        # Draw decorative elements
        self._draw_decorations(surface)
        
        # Draw epic title with glow and gradient effect
        self._draw_epic_title(surface)
        
        # Draw subtitle
        subtitle_text = "Strategic Board Game"
        subtitle_surface = self.fonts['medium'].render(subtitle_text, True, COLORS.TEXT_SECONDARY)
        subtitle_rect = subtitle_surface.get_rect(center=(self.screen_width // 2, self.subtitle_y))
        surface.blit(subtitle_surface, subtitle_rect)
        
        # Draw version badge
        version_text = "v1.0"
        version_surface = self.fonts['small'].render(version_text, True, COLORS.TEXT_MUTED)
        surface.blit(version_surface, (self.screen_width - 50, self.screen_height - 30))
        
        # Draw fullscreen hint
        fullscreen_hint = "Press F11 for fullscreen"
        hint_surface = self.fonts['small'].render(fullscreen_hint, True, COLORS.TEXT_MUTED)
        surface.blit(hint_surface, (15, self.screen_height - 30))
        
        # Draw buttons
        for button in self.buttons:
            button.draw(surface)
        
        # Draw instructions
        self._draw_instructions(surface)
    
    def _draw_gradient_bg(self, surface: pygame.Surface):
        """Draw gradient background"""
        for y in range(self.screen_height):
            progress = y / self.screen_height
            color = tuple(
                int(COLORS.BG_PRIMARY[i] + (COLORS.BG_SECONDARY[i] - COLORS.BG_PRIMARY[i]) * progress)
                for i in range(3)
            )
            pygame.draw.line(surface, color, (0, y), (self.screen_width, y))
    
    def _draw_decorations(self, surface: pygame.Surface):
        """Draw decorative game pieces"""
        import math
        
        # Animated floating pawns
        offset = math.sin(self._time * 2) * 10
        
        # Left pawn
        self._draw_decorative_pawn(surface, 150, 140 + offset, COLORS.PLAYER1_PRIMARY, 30)
        
        # Right pawn
        self._draw_decorative_pawn(surface, self.screen_width - 150, 140 - offset, COLORS.PLAYER2_PRIMARY, 30)
        
        # Draw some decorative walls
        wall_y = 230
        wall_width = 80
        wall_height = 8
        
        pygame.draw.rect(surface, COLORS.WALL_PLACED,
                        (self.screen_width // 2 - wall_width - 20, wall_y, wall_width, wall_height),
                        border_radius=4)
        pygame.draw.rect(surface, COLORS.WALL_PLACED,
                        (self.screen_width // 2 + 20, wall_y, wall_width, wall_height),
                        border_radius=4)
    
    def _draw_decorative_pawn(self, surface: pygame.Surface, x: int, y: int,
                              color: tuple, radius: int):
        """Draw a decorative pawn"""
        # Glow
        for i in range(3, 0, -1):
            glow_surface = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*color, 20),
                             (radius * 2, radius * 2), radius + i * 8)
            surface.blit(glow_surface, (x - radius * 2, y - radius * 2))
        
        # Shadow
        pygame.draw.circle(surface, (0, 0, 0, 50), (x + 3, y + 3), radius)
        
        # Pawn
        pygame.draw.circle(surface, color, (x, y), radius)
        
        # Highlight
        pygame.draw.circle(surface, (255, 255, 255), (x - radius // 4, y - radius // 4), radius // 3)
    
    def _draw_epic_title(self, surface: pygame.Surface):
        """Draw an epic animated title with glow effects"""
        import math
        
        title_text = "QUORIDOR"
        center_x = self.screen_width // 2
        
        # Animated glow intensity
        pulse = (math.sin(self._time * 2) + 1) / 2
        
        # Draw outer glow layers (multiple passes for soft glow)
        glow_colors = [
            (*COLORS.PLAYER1_PRIMARY, int(30 * pulse)),
            (*COLORS.ACCENT_GOLD, int(50 * pulse)),
            (*COLORS.PLAYER1_GLOW, int(40 * pulse)),
        ]
        
        for i, glow_color in enumerate(glow_colors):
            glow_offset = (3 - i) * 4
            glow_surface = pygame.Surface((600, 120), pygame.SRCALPHA)
            glow_text = self.title_font.render(title_text, True, glow_color)
            glow_rect = glow_text.get_rect(center=(300, 60))
            glow_surface.blit(glow_text, glow_rect)
            
            # Blur effect by drawing multiple times with offset
            for ox in range(-glow_offset, glow_offset + 1, 2):
                for oy in range(-glow_offset, glow_offset + 1, 2):
                    surface.blit(glow_surface, (center_x - 300 + ox, self.title_y - 60 + oy))
        
        # Draw shadow
        shadow_surface = self.title_font.render(title_text, True, (0, 0, 0))
        shadow_rect = shadow_surface.get_rect(center=(center_x + 4, self.title_y + 4))
        surface.blit(shadow_surface, shadow_rect)
        
        # Draw main title with gradient effect (simulate with multiple colored layers)
        # Gold/white gradient
        main_color = (
            int(255 - 20 * pulse),
            int(215 + 40 * pulse),
            int(100 + 50 * pulse)
        )
        title_surface = self.title_font.render(title_text, True, main_color)
        title_rect = title_surface.get_rect(center=(center_x, self.title_y))
        surface.blit(title_surface, title_rect)
        
        # Draw highlight on top edge of letters
        highlight_color = (255, 255, 255)
        highlight_surface = self.title_font.render(title_text, True, highlight_color)
        highlight_surface.set_alpha(int(80 + 40 * pulse))
        surface.blit(highlight_surface, (title_rect.x, title_rect.y - 2))
        
        # Draw sparkle effects around title
        self._draw_sparkles(surface, center_x, self.title_y, pulse)
    
    def _draw_sparkles(self, surface: pygame.Surface, center_x: int, center_y: int, pulse: float):
        """Draw animated sparkle effects"""
        import math
        
        sparkle_positions = [
            (-180, -30), (180, -30), (-220, 10), (220, 10),
            (-150, 30), (150, 30), (0, -45)
        ]
        
        for i, (ox, oy) in enumerate(sparkle_positions):
            # Each sparkle has its own phase
            phase = self._time * 3 + i * 0.8
            sparkle_alpha = int((math.sin(phase) + 1) / 2 * 200)
            sparkle_size = int(2 + (math.sin(phase) + 1) * 2)
            
            if sparkle_alpha > 50:
                x = center_x + ox
                y = center_y + oy
                
                # Draw sparkle (small cross/star shape)
                sparkle_surface = pygame.Surface((20, 20), pygame.SRCALPHA)
                color = (*COLORS.ACCENT_GOLD, sparkle_alpha)
                
                # Cross shape
                pygame.draw.line(sparkle_surface, color, (10, 10 - sparkle_size), (10, 10 + sparkle_size), 2)
                pygame.draw.line(sparkle_surface, color, (10 - sparkle_size, 10), (10 + sparkle_size, 10), 2)
                
                # Diagonal lines for star effect
                diag_size = sparkle_size // 2
                pygame.draw.line(sparkle_surface, color, (10 - diag_size, 10 - diag_size), (10 + diag_size, 10 + diag_size), 1)
                pygame.draw.line(sparkle_surface, color, (10 + diag_size, 10 - diag_size), (10 - diag_size, 10 + diag_size), 1)
                
                surface.blit(sparkle_surface, (x - 10, y - 10))
    
    def _draw_instructions(self, surface: pygame.Surface):
        """Draw control instructions"""
        instructions = [
            "Controls: Click to move • W for walls • Right-click to rotate • F11 for fullscreen"
        ]
        
        y = self.screen_height - 60
        for text in instructions:
            text_surface = self.fonts['small'].render(text, True, COLORS.TEXT_MUTED)
            text_rect = text_surface.get_rect(center=(self.screen_width // 2, y))
            surface.blit(text_surface, text_rect)
            y += 25


class GameOverOverlay:
    """Game over overlay that appears on top of the game"""
    
    def __init__(self, fonts: dict, winner: str, winner_color: tuple,
                 on_menu: Callable, on_restart: Callable,
                 screen_width: int = SCREEN_WIDTH, screen_height: int = SCREEN_HEIGHT):
        self.fonts = fonts
        self.winner = winner
        self.winner_color = winner_color
        self.on_menu = on_menu
        self.on_restart = on_restart
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self._fade = 0.0
        self._time = 0.0
        
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        
        self.buttons = [
            ModernButton(
                center_x - 140, center_y + 80,
                130, 50, "Menu", fonts['medium'],
                on_menu, style="secondary"
            ),
            ModernButton(
                center_x + 10, center_y + 80,
                130, 50, "Rematch", fonts['medium'],
                on_restart, style="primary"
            ),
        ]
    
    def update(self, dt: float):
        self._fade = min(1.0, self._fade + dt * 3)
        self._time += dt
        for button in self.buttons:
            button.update(dt)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if self._fade < 0.5:
            return False
        
        for button in self.buttons:
            if button.handle_event(event):
                return True
        return False
    
    def draw(self, surface: pygame.Surface):
        # Draw semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, int(180 * self._fade)))
        surface.blit(overlay, (0, 0))
        
        if self._fade < 0.3:
            return
        
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        
        # Draw winner announcement with glow
        import math
        pulse = (math.sin(self._time * 3) + 1) / 2
        
        # Glow effect
        glow_color = (*self.winner_color, int(100 * pulse * self._fade))
        glow_surface = pygame.Surface((400, 100), pygame.SRCALPHA)
        pygame.draw.ellipse(glow_surface, glow_color, (0, 0, 400, 100))
        surface.blit(glow_surface, (center_x - 200, center_y - 80))
        
        # Winner text
        win_text = f"{self.winner} Wins!"
        text_surface = self.fonts['large'].render(win_text, True, COLORS.ACCENT_GOLD)
        text_surface.set_alpha(int(255 * self._fade))
        text_rect = text_surface.get_rect(center=(center_x, center_y - 40))
        surface.blit(text_surface, text_rect)
        
        # Subtitle
        subtitle = "Congratulations!"
        subtitle_surface = self.fonts['medium'].render(subtitle, True, COLORS.TEXT_SECONDARY)
        subtitle_surface.set_alpha(int(255 * self._fade))
        subtitle_rect = subtitle_surface.get_rect(center=(center_x, center_y + 10))
        surface.blit(subtitle_surface, subtitle_rect)
        
        # Draw buttons
        if self._fade > 0.5:
            for button in self.buttons:
                button.draw(surface)


class ScreenManager:
    """Manages game screens and transitions"""
    
    def __init__(self, screen_width: int = SCREEN_WIDTH, screen_height: int = SCREEN_HEIGHT):
        pygame.font.init()
        
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.fonts = {
            'title': pygame.font.Font(None, FONT_SIZE_TITLE),
            'large': pygame.font.Font(None, FONT_SIZE_LARGE),
            'medium': pygame.font.Font(None, FONT_SIZE_MEDIUM),
            'small': pygame.font.Font(None, FONT_SIZE_SMALL),
        }
        
        self.current_state = ScreenState.MENU
        self.screens = {}
        self.game_mode: Optional[GameMode] = None
        
        # Callbacks
        self.on_start_game: Optional[Callable] = None
        self.on_quit: Optional[Callable] = None
        
        self._setup_screens()
    
    def _setup_screens(self):
        """Initialize all screens"""
        self.screens[ScreenState.MENU] = MenuScreen(self)
        self.screens[ScreenState.MENU].setup()
    
    def update_screen_size(self, width: int, height: int):
        """Update screen dimensions and recreate screens"""
        self.screen_width = width
        self.screen_height = height
        # Recreate menu screen with new dimensions
        self._setup_screens()
    
    def set_callbacks(self, on_start_game: Callable, on_quit: Callable):
        """Set callback functions"""
        self.on_start_game = on_start_game
        self.on_quit = on_quit
    
    def start_game(self, mode: GameMode):
        """Transition to game screen"""
        self.game_mode = mode
        self.current_state = ScreenState.GAME
        if self.on_start_game:
            self.on_start_game(mode)
    
    def return_to_menu(self):
        """Return to main menu"""
        self.current_state = ScreenState.MENU
    
    def quit_game(self):
        """Quit the application"""
        if self.on_quit:
            self.on_quit()
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events for current screen"""
        if self.current_state in self.screens:
            return self.screens[self.current_state].handle_event(event)
        return False
    
    def update(self, dt: float):
        """Update current screen"""
        if self.current_state in self.screens:
            self.screens[self.current_state].update(dt)
    
    def draw(self, surface: pygame.Surface):
        """Draw current screen"""
        if self.current_state in self.screens:
            self.screens[self.current_state].draw(surface)
