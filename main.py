#!/usr/bin/env python3
"""
Quoridor Game - Main Entry Point
A modern implementation of the classic Quoridor board game.

Run this file to start the game.

Project Structure:
    src/
    ├── __init__.py         - Package initialization
    ├── constants.py        - Game constants, colors, settings
    ├── game_logic.py       - Core game mechanics
    ├── ai.py               - AI opponent (Minimax + Alpha-Beta)
    ├── ui_components.py    - Reusable UI components
    ├── board_renderer.py   - Board rendering with animations
    ├── screens.py          - Screen management (menu, game over)
    └── gui.py              - Main GUI orchestration
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.gui import GameGUI


def main():
    """Main function to start the game"""
    print()
    print("╔═══════════════════════════════════════════╗")
    print("║           QUORIDOR - Board Game           ║")
    print("╠═══════════════════════════════════════════╣")
    print("║  Controls:                                ║")
    print("║  • Click cells to move your pawn          ║")
    print("║  • Press 'W' or button to place walls     ║")
    print("║  • Right-click to rotate wall             ║")
    print("║  • ESC to cancel wall placement           ║")
    print("╚═══════════════════════════════════════════╝")
    print()
    
    game = GameGUI()
    game.run()


if __name__ == "__main__":
    main()
