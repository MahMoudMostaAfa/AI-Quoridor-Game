"""
Quoridor Game - UI Components Module
Reusable UI components with modern styling and animations.
"""

import pygame
import math
from typing import Tuple, Optional, Callable, List
from .constants import COLORS, BUTTON_BORDER_RADIUS, ANIMATION_SPEED


class UIComponent:
    """Base class for all UI components"""
    
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.visible = True
        self.enabled = True
        self._hover_progress = 0.0
        self._click_progress = 0.0
    
    def update(self, dt: float):
        """Update component animations"""
        pass
    
    def draw(self, screen: pygame.Surface):
        """Draw the component"""
        pass
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events, return True if consumed"""
        return False


class ModernButton(UIComponent):
    """Modern button with hover animations and glass effect"""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str,
                 font: pygame.font.Font, callback: Optional[Callable] = None,
                 style: str = "primary", icon: Optional[str] = None):
        super().__init__(x, y, width, height)
        self.text = text
        self.font = font
        self.callback = callback
        self.style = style
        self.icon = icon
        self.hovered = False
        self.pressed = False
        self._hover_anim = 0.0
        self._press_anim = 0.0
    
    def update(self, dt: float):
        # Smooth hover animation
        target_hover = 1.0 if self.hovered else 0.0
        self._hover_anim += (target_hover - self._hover_anim) * min(1.0, dt * 12)
        
        # Press animation decay
        if self._press_anim > 0:
            self._press_anim = max(0, self._press_anim - dt * 8)
    
    def draw(self, screen: pygame.Surface):
        if not self.visible:
            return
        
        # Calculate animated properties
        scale = 1.0 + self._hover_anim * 0.02 - self._press_anim * 0.05
        
        # Get colors based on style
        if self.style == "primary":
            base_color = COLORS.BTN_PRIMARY
            hover_color = COLORS.BTN_PRIMARY_HOVER
        elif self.style == "danger":
            base_color = COLORS.BTN_DANGER
            hover_color = (200, 60, 50)
        elif self.style == "success":
            base_color = COLORS.BTN_SUCCESS
            hover_color = (36, 180, 100)
        else:  # secondary
            base_color = COLORS.BTN_SECONDARY
            hover_color = COLORS.BTN_SECONDARY_HOVER
        
        # Interpolate colors
        color = self._lerp_color(base_color, hover_color, self._hover_anim)
        
        # Calculate scaled rect
        scaled_width = int(self.rect.width * scale)
        scaled_height = int(self.rect.height * scale)
        scaled_x = self.rect.centerx - scaled_width // 2
        scaled_y = self.rect.centery - scaled_height // 2
        scaled_rect = pygame.Rect(scaled_x, scaled_y, scaled_width, scaled_height)
        
        # Draw shadow
        shadow_rect = scaled_rect.copy()
        shadow_rect.y += 4
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 40), 
                        (0, 0, shadow_rect.width, shadow_rect.height),
                        border_radius=BUTTON_BORDER_RADIUS)
        screen.blit(shadow_surface, shadow_rect.topleft)
        
        # Draw main button
        pygame.draw.rect(screen, color, scaled_rect, border_radius=BUTTON_BORDER_RADIUS)
        
        # Draw border/glow on hover
        if self._hover_anim > 0.1:
            border_alpha = int(100 * self._hover_anim)
            border_surface = pygame.Surface((scaled_rect.width + 4, scaled_rect.height + 4), pygame.SRCALPHA)
            pygame.draw.rect(border_surface, (*COLORS.TEXT_PRIMARY, border_alpha),
                           (0, 0, scaled_rect.width + 4, scaled_rect.height + 4),
                           width=2, border_radius=BUTTON_BORDER_RADIUS + 2)
            screen.blit(border_surface, (scaled_rect.x - 2, scaled_rect.y - 2))
        
        # Draw text
        text_color = COLORS.TEXT_PRIMARY if self.enabled else COLORS.TEXT_MUTED
        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=scaled_rect.center)
        screen.blit(text_surface, text_rect)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible or not self.enabled:
            return False
        
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
                self._press_anim = 1.0
                return True
        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.pressed and self.rect.collidepoint(event.pos):
                self.pressed = False
                if self.callback:
                    self.callback()
                return True
            self.pressed = False
        
        return False
    
    def _lerp_color(self, c1: Tuple, c2: Tuple, t: float) -> Tuple[int, int, int]:
        """Linear interpolation between two colors"""
        return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


class GlassPanel(UIComponent):
    """Modern glass-morphism panel"""
    
    def __init__(self, x: int, y: int, width: int, height: int,
                 border_radius: int = 15, highlight: bool = False,
                 highlight_color: Optional[Tuple[int, int, int]] = None):
        super().__init__(x, y, width, height)
        self.border_radius = border_radius
        self.highlight = highlight
        self.highlight_color = highlight_color
        self._glow_anim = 0.0
    
    def set_highlight(self, active: bool, color: Optional[Tuple[int, int, int]] = None):
        self.highlight = active
        if color:
            self.highlight_color = color
    
    def update(self, dt: float):
        target = 1.0 if self.highlight else 0.0
        self._glow_anim += (target - self._glow_anim) * min(1.0, dt * 8)
    
    def draw(self, screen: pygame.Surface):
        if not self.visible:
            return
        
        # Create glass surface
        glass_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        
        # Draw background
        pygame.draw.rect(glass_surface, (*COLORS.BG_SECONDARY, 220),
                        (0, 0, self.rect.width, self.rect.height),
                        border_radius=self.border_radius)
        
        # Draw highlight glow if active
        if self._glow_anim > 0.1 and self.highlight_color:
            glow_alpha = int(50 * self._glow_anim)
            pygame.draw.rect(glass_surface, (*self.highlight_color, glow_alpha),
                           (0, 0, self.rect.width, self.rect.height),
                           border_radius=self.border_radius)
        
        # Draw border
        border_color = self.highlight_color if self.highlight and self.highlight_color else COLORS.TEXT_MUTED
        border_alpha = int(100 + 155 * self._glow_anim) if self.highlight else 60
        pygame.draw.rect(glass_surface, (*border_color[:3], border_alpha),
                        (0, 0, self.rect.width, self.rect.height),
                        width=2, border_radius=self.border_radius)
        
        # Draw top highlight line for glass effect
        highlight_rect = pygame.Rect(10, 2, self.rect.width - 20, 1)
        pygame.draw.rect(glass_surface, (255, 255, 255, 30), highlight_rect,
                        border_radius=1)
        
        screen.blit(glass_surface, self.rect.topleft)


class AnimatedText:
    """Text with animation capabilities"""
    
    def __init__(self, text: str, font: pygame.font.Font, color: Tuple[int, int, int],
                 x: int, y: int, anchor: str = "center"):
        self.text = text
        self.font = font
        self.color = color
        self.x = x
        self.y = y
        self.anchor = anchor
        self._pulse_time = 0.0
        self.pulse = False
        self.visible = True
    
    def update(self, dt: float):
        if self.pulse:
            self._pulse_time += dt * ANIMATION_SPEED
    
    def draw(self, screen: pygame.Surface):
        if not self.visible:
            return
        
        # Calculate pulse effect
        if self.pulse:
            scale = 1.0 + math.sin(self._pulse_time) * 0.05
            alpha = int(200 + 55 * math.sin(self._pulse_time))
        else:
            scale = 1.0
            alpha = 255
        
        # Render text
        text_surface = self.font.render(self.text, True, self.color)
        
        # Apply alpha
        text_surface.set_alpha(alpha)
        
        # Scale if needed
        if scale != 1.0:
            new_size = (int(text_surface.get_width() * scale),
                       int(text_surface.get_height() * scale))
            text_surface = pygame.transform.smoothscale(text_surface, new_size)
        
        # Position based on anchor
        text_rect = text_surface.get_rect()
        if self.anchor == "center":
            text_rect.center = (self.x, self.y)
        elif self.anchor == "topleft":
            text_rect.topleft = (self.x, self.y)
        elif self.anchor == "topright":
            text_rect.topright = (self.x, self.y)
        
        screen.blit(text_surface, text_rect)


class ProgressBar(UIComponent):
    """Animated progress bar for showing wall counts etc."""
    
    def __init__(self, x: int, y: int, width: int, height: int,
                 max_value: int, color: Tuple[int, int, int]):
        super().__init__(x, y, width, height)
        self.max_value = max_value
        self.value = max_value
        self.color = color
        self._display_value = float(max_value)
    
    def set_value(self, value: int):
        self.value = max(0, min(value, self.max_value))
    
    def update(self, dt: float):
        # Smooth value transition
        self._display_value += (self.value - self._display_value) * min(1.0, dt * 8)
    
    def draw(self, screen: pygame.Surface):
        if not self.visible:
            return
        
        segment_width = (self.rect.width - (self.max_value - 1) * 3) // self.max_value
        
        for i in range(self.max_value):
            segment_x = self.rect.x + i * (segment_width + 3)
            segment_rect = pygame.Rect(segment_x, self.rect.y, segment_width, self.rect.height)
            
            if i < self._display_value:
                # Filled segment
                fill_amount = min(1.0, self._display_value - i)
                fill_color = self.color
                
                if fill_amount < 1.0:
                    # Partially filled (animating)
                    fill_color = tuple(int(c * fill_amount + COLORS.WALL_SLOT[j] * (1 - fill_amount)) 
                                      for j, c in enumerate(self.color))
                
                pygame.draw.rect(screen, fill_color, segment_rect, border_radius=2)
            else:
                # Empty segment
                pygame.draw.rect(screen, COLORS.WALL_SLOT, segment_rect, border_radius=2)


class Tooltip:
    """Tooltip that follows the mouse"""
    
    def __init__(self, font: pygame.font.Font):
        self.font = font
        self.text = ""
        self.visible = False
        self.x = 0
        self.y = 0
        self._fade = 0.0
    
    def show(self, text: str, x: int, y: int):
        self.text = text
        self.x = x + 15
        self.y = y + 15
        self.visible = True
    
    def hide(self):
        self.visible = False
    
    def update(self, dt: float):
        target = 1.0 if self.visible else 0.0
        self._fade += (target - self._fade) * min(1.0, dt * 12)
    
    def draw(self, screen: pygame.Surface):
        if self._fade < 0.05:
            return
        
        text_surface = self.font.render(self.text, True, COLORS.TEXT_PRIMARY)
        padding = 8
        
        bg_rect = pygame.Rect(self.x, self.y,
                             text_surface.get_width() + padding * 2,
                             text_surface.get_height() + padding * 2)
        
        # Keep on screen
        if bg_rect.right > screen.get_width():
            bg_rect.right = screen.get_width() - 5
        if bg_rect.bottom > screen.get_height():
            bg_rect.bottom = screen.get_height() - 5
        
        # Draw background
        alpha = int(220 * self._fade)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surface, (*COLORS.BG_TERTIARY, alpha),
                        (0, 0, bg_rect.width, bg_rect.height),
                        border_radius=6)
        pygame.draw.rect(bg_surface, (*COLORS.TEXT_MUTED, alpha),
                        (0, 0, bg_rect.width, bg_rect.height),
                        width=1, border_radius=6)
        
        screen.blit(bg_surface, bg_rect.topleft)
        
        # Draw text
        text_surface.set_alpha(int(255 * self._fade))
        screen.blit(text_surface, (bg_rect.x + padding, bg_rect.y + padding))
