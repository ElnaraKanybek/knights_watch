from __future__ import annotations

import math

from game import Game, Player

# for estimating the branching factor. Used to tune the pruning optimizations.
NODE_COUNT = 0
LEAF_COUNT = 0

class Interrupted(Exception):
    """Raised when the minimax algorithm has timed out."""


class BaseDecideMove:
    """Super-class code algorithm to decide best move. Setup for to use the minimax algorithm."""

    def __init__(self, max_depth: int, max_white_score: int = 1, min_black_score: int = -1):
        """max_depth: the number of moves to look ahead for the computer
           max_white_score: the upper limit of the evaluation function for WHITE.
           min_black_score: the lower limit of the evaluation function for BLACK. 
        """
        self.best_move: str = "PASS"
        self.max_white_score: int = max_white_score
        self.min_black_score: int = min_black_score
        self.max_depth: int = max_depth

        self.is_interrupted: bool = False


    def interrupt(self):
        """Stop decide move on the next call to minimax."""
        self.is_interrupted = True

        
    def decide_best_move(self, game: Game):
        """Decide the best move, keeping self.best_move as up to date as possible."""
        raise Exception()  # override in subclass

    
    def evaluate(self, game: Game) -> int:
        """Evaluation the current game. White player is maximizing, Black is minimizing."""
        raise Exception()  # override in subclass

    
    def check_is_over(self, game) -> bool:
        """Check that the game is over. Default is to check the game. Override as needed"""
        return game.is_over()

    
    def moves_from(self, game: Game) -> list[Game]:
        """Get all the possible games from the provided game."""
        raise Exception()  # overwrite in subclass

    
    def minimax(self, game: Game, depth: int = 1, alpha: int = -math.inf, beta: int = math.inf) -> int:
        """Implementation of minimax algorithm with alpha-beta pruning
           - `https://en.wikipedia.org/wiki/Minimax
           - https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning
        """

        #print(f"minimax(game, {depth=}, {alpha=}, {beta=})")
        
        if self.is_interrupted:
            raise Interrupted()

        global NODE_COUNT, LEAF_COUNT

        if self.check_is_over(game) or depth > self.max_depth:
            LEAF_COUNT += 1
            return self.evaluate(game)

        NODE_COUNT += 1

        match game.turn:
            case Player.WHITE: # white is maximizing
                score: int = -math.inf
                for g in self.moves_from(game):
                    score = max(score, self.minimax(g, depth + 1, alpha, beta))
                    if score > beta:
                       return score
                    alpha = max(alpha, score)
                return score
            case Player.BLACK: # black is minimizing
                score: int = math.inf
                for g in self.moves_from(game):
                    score = min(score, self.minimax(g, depth + 1, alpha, beta))
                    if score < alpha:
                        return score
                    beta = min(beta, score)
                return score
