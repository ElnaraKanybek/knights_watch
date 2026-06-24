import re

from move import BaseDecideMove
from game import Game, GameException

def print_help():
    input("""Knight's Watch commands:
  > Pa2a3  - Performs any valid move.
  > PASS   - Skip a turn.
  > RESIGN - Give up and quit the game.
""")

class DecideMove(BaseDecideMove):
    def __init__(self):
        super().__init__(-1)

    def decide_best_move(self, game: Game):
        while True:
            move_str = input(f"{game.turn}> ")
            move_str = re.sub(r'#.*', "", move_str)
            move_str = move_str.strip()
            if not move_str or move_str.lower() in ("help", "?"):
                print_help()
                continue
            try:
                game.move(move_str)
                self.best_move = move_str
                break
            except GameException as e:
                input(e)
