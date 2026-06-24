from __future__ import annotations

from enum import Enum

class Player(Enum):
    WHITE, BLACK = range(2)
        
    def __str__(self) -> str:
        match self:
            case Player.WHITE:
                return "WHITE"
            case Player.BLACK:
                return "BLACK"
    
class State(Enum):
    IN_PROGRESS, WHITE_WIN, BLACK_WIN, DRAW = range(4)

    def __bool__(self):
        return self == State.IN_PROGRESS

    def __str__(self) -> str:
        match self:
            case State.IN_PROGRESS:
                return "In Progress"
            case State.WHITE_WIN:
                return "WHITE wins!"
            case State.BLACK_WIN:
                return "BLACK wins!"
            case State.DRAW:
                return "Draw..."

class GameException(Exception):
    """Game errors"""

class Game:
    """Super-class for two player games."""

    def move(self, move_str: str):
        pass

    def lose_turn(self):
        pass

    def resign(self):
        raise GameException()
        
    def is_over(self) -> bool:
        return False

    def copy(self) -> Game:
        pass

    def print(self):
        pass
