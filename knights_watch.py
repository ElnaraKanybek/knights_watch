#  Copyright (c) 2026 Ian Clement.
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
#  License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any
#  later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
#  warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with this program. If not,
#  see <https://www.gnu.org/licenses/>.

from __future__ import annotations

from typing import Optional
from enum import Enum
from random import choice
import re
import datetime as dt

from game import Game, Player, State, GameException


# Change to False if you use a light terminal
TERMINAL_DARK = True

class Piece(Enum):
    """Represent the two playable pieces"""
    PAWN, KNIGHT = range(2)

    
def parse_pos(pos: str) -> tuple[int, int]:
    """Convert from a string representation to (x, y)"""
    x = ord(pos[0]) - ord("a")
    y = ord(pos[1]) - ord("1")
    if x < 0 or x > 5 or y < 0 or y > 5:
        raise GameException(f"Invalid position {pos}.")
    return (5 - x), y


def format_pos(pos_x: int, pos_y: int) -> str:
    """Convert from (x, y) to the chess coordinate system."""
    x = chr(5 - pos_x + ord("a"))
    y = chr(pos_y + ord("1"))
    return f"{x}{y}"


def piece_str(player_piece: Optional[tuple[Player, Piece]]) -> str:
    """Get the unicode chess piece"""
    match player_piece:
        case (Player.WHITE, Piece.KNIGHT):
            return "♞" if TERMINAL_DARK else "♘"
        case (Player.WHITE, Piece.PAWN):
            return "♟" if TERMINAL_DARK else "♙"
        case (Player.BLACK, Piece.KNIGHT):
            return "♘" if TERMINAL_DARK else "♞"
        case (Player.BLACK, Piece.PAWN):
            return "♙" if TERMINAL_DARK else "♟"
        case None:
            return " "


HEX_DIGITS = "0123456789abcdef"
ID_LENGTH = 6

GAME_LOG_DIR = "logs/"
        
class KWGame(Game):
    """Knight's Watch game"""
    
    def __init__(self, do_log: bool = False):
        self.id: str = "".join(choice(HEX_DIGITS) for i in range(ID_LENGTH))

        if do_log:
            self.game_log = open(f"{GAME_LOG_DIR}/kw_game_{self.id}.log", "w")

            print("# Knight's Watch", file=self.game_log)
            now = dt.datetime.now()
            print(f"# Played at {now.isoformat()}", file=self.game_log)
        else:
            self.game_log = None
            
        self.pieces: list[Optional[tuple[Player,Piece]]] = [None] * 36
        self.pieces[1] = (Player.WHITE, Piece.KNIGHT)
        self.pieces[4] = (Player.WHITE, Piece.KNIGHT)
        self.pieces[6] = (Player.WHITE, Piece.PAWN)
        self.pieces[7] = (Player.WHITE, Piece.PAWN)
        self.pieces[8] = (Player.WHITE, Piece.PAWN)
        self.pieces[9] = (Player.WHITE, Piece.PAWN)
        self.pieces[10] = (Player.WHITE, Piece.PAWN)
        self.pieces[11] = (Player.WHITE, Piece.PAWN)
        self.pieces[24] = (Player.BLACK, Piece.PAWN)
        self.pieces[25] = (Player.BLACK, Piece.PAWN)
        self.pieces[26] = (Player.BLACK, Piece.PAWN)
        self.pieces[27] = (Player.BLACK, Piece.PAWN)
        self.pieces[28] = (Player.BLACK, Piece.PAWN)
        self.pieces[29] = (Player.BLACK, Piece.PAWN)
        self.pieces[31] = (Player.BLACK, Piece.KNIGHT)
        self.pieces[34] = (Player.BLACK, Piece.KNIGHT)

        self.turn = Player.WHITE
        self.state: State = State.IN_PROGRESS
        self.history: list[str] = []

    def __del__(self):
        if self.game_log:
            self.game_log.close()


    def __str__(self) -> str:
        return f"turn={self.turn} board={','.join(map(piece_str, self.pieces))}"
        
    def is_over(self):
        return not self.state

    
    def print(self):

        if self.turn == Player.BLACK: 
            black_token = "○" if TERMINAL_DARK else "●"
            white_token = " "
        else:
            white_token = "●" if TERMINAL_DARK else "○"
            black_token = " "

        game_history: list[str] = ["", "", "", "", "", "", "", "", "", "", ""]
        for i, m in enumerate(self.history):
            game_history[i % 11] += f"{m:<8}"
        
        print(f"  ╔═══╤═══╤═══╤═══╤═══╤═══╗ {black_token}")
        print(f"6 ║ {piece_str(self.pieces[35])} │ {piece_str(self.pieces[34])} │ {piece_str(self.pieces[33])} │ {piece_str(self.pieces[32])} │ {piece_str(self.pieces[31])} │ {piece_str(self.pieces[30])} ║    {game_history[0]}")
        print(f"  ╟───┼───┼───┼───┼───┼───╢    {game_history[1]}")
        print(f"5 ║ {piece_str(self.pieces[29])} │ {piece_str(self.pieces[28])} │ {piece_str(self.pieces[27])} │ {piece_str(self.pieces[26])} │ {piece_str(self.pieces[25])} │ {piece_str(self.pieces[24])} ║    {game_history[2]}")
        print(f"  ╟───┼───┼───┼───┼───┼───╢    {game_history[3]}")
        print(f"4 ║ {piece_str(self.pieces[23])} │ {piece_str(self.pieces[22])} │ {piece_str(self.pieces[21])} │ {piece_str(self.pieces[20])} │ {piece_str(self.pieces[19])} │ {piece_str(self.pieces[18])} ║    {game_history[4]}")
        print(f"  ╟───┼───┼───┼───┼───┼───╢    {game_history[5]}")
        print(f"3 ║ {piece_str(self.pieces[17])} │ {piece_str(self.pieces[16])} │ {piece_str(self.pieces[15])} │ {piece_str(self.pieces[14])} │ {piece_str(self.pieces[13])} │ {piece_str(self.pieces[12])} ║    {game_history[6]}")
        print(f"  ╟───┼───┼───┼───┼───┼───╢    {game_history[7]}")
        print(f"2 ║ {piece_str(self.pieces[11])} │ {piece_str(self.pieces[10])} │ {piece_str(self.pieces[9])} │ {piece_str(self.pieces[8])} │ {piece_str(self.pieces[7])} │ {piece_str(self.pieces[6])} ║    {game_history[8]}")
        print(f"  ╟───┼───┼───┼───┼───┼───╢    {game_history[9]}")
        print(f"1 ║ {piece_str(self.pieces[5])} │ {piece_str(self.pieces[4])} │ {piece_str(self.pieces[3])} │ {piece_str(self.pieces[2])} │ {piece_str(self.pieces[1])} │ {piece_str(self.pieces[0])} ║    {game_history[10]}")
        print(f"  ╚═══╧═══╧═══╧═══╧═══╧═══╝ {white_token}")
        print(f"    a   b   c   d   e   f")


    def move(self, move_str: str):

        if not self.state:
            raise GameException("The game is over.")

        if move_str == "PASS":
            self.history.append("PASS")
            if self.game_log:
                print("PASS", file=self.game_log)
            if self.state:
                self.turn = Player.BLACK if self.turn == Player.WHITE else Player.WHITE
            return

        if move_str == "RESIGN":
            self.history.append("RESIGN")
            if self.game_log:
                print("RESIGN", file=self.game_log)

            if self.turn == Player.BLACK:
                self.state = State.WHITE_WIN
            else:
                self.state = State.BLACK_WIN
            return

        if len(move_str) != 5 or move_str[0] not in ("K", "P"):
            raise GameException(f"Invalid move string {move_str}. The format is 'piece-from-to' where 'piece' is 'P' or 'K', and from/to are coordinates on the board. For example 'Pa2a3' or 'Kb1a3'.")

        piece_str: str = move_str[0]

        # convert to the 
        from_x, from_y = parse_pos(move_str[1:3])
        from_pos: int = 6 * from_y + from_x
        to_x, to_y = parse_pos(move_str[3:5])
        to_pos: int = 6 * to_y + to_x

        # Validate the chosen piece
        if not self.pieces[from_pos]:
            raise GameException(f"There is no piece at position {move_str[1:3]}.")

        if self.turn != self.pieces[from_pos][0]:
            raise GameException(f"The piece at {move_str[1:3]} does not belong to {self.turn} player.")

        if piece_str == "K" and self.pieces[from_pos][1] != Piece.KNIGHT:
            raise GameException(f"The piece at {move_str[1:3]} is not a KNIGHT.")

        if piece_str == "P" and self.pieces[from_pos][1] != Piece.PAWN:
            raise GameException(f"The piece at {move_str[1:3]} is not a PAWN.")

        # Validate move

        if self.pieces[to_pos] and self.pieces[to_pos][0] == self.turn:
            raise GameException("Cannot move to a position occupied by your own piece.")

        # Validate a PAWN move
        if piece_str == "P":
            if self.turn == Player.BLACK:
                if from_y - to_y < 1:
                    raise GameException("A BLACK PAWN can only move down.")
                if from_y - to_y > 1:
                    raise GameException("A PAWN can only move one space.")
            if self.turn == Player.WHITE:
                if to_y - from_y < 1:
                    raise GameException("A WHITE PAWN can only move up.")
                if to_y - from_y > 1:
                    raise GameException("A PAWN can only move one space.")
                
            if from_x == to_x:
                if self.pieces[to_pos]:
                    raise GameException("A PAWN can only move forward to an empty space.")
            elif to_x == from_x - 1 or to_x == from_x + 1:
                if not self.pieces[to_pos]: # it must be an enemy since we checked that to is not them
                    raise GameException("A PAWN can only move diagonally when capturing.")
                
            else:
                raise GameException("Invalid PAWN move.")

            # Update the win condition
            if self.turn == Player.WHITE and to_y == 5:
                self.state = State.WHITE_WIN
            elif self.turn == Player.BLACK and to_y == 0:
                self.state = State.BLACK_WIN

        # Validate a KNIGHT move
        elif piece_str == "K":
            dx = abs(from_x - to_x)
            dy = abs(from_y - to_y)
            if (dx != 2 or dy != 1) and (dx != 1 or dy != 2):
                raise GameException("Invalid KNIGHT move. Can only move in an 'L' shape.")

        else:
            raise GameException("Not implemented")

        # Move is now valid
        
        # track the move history
        self.history.append(move_str)
        if self.game_log:
            print(move_str, file=self.game_log)
        
        # perform the board updates
        self.pieces[to_pos] = self.pieces[from_pos]
        self.pieces[from_pos] = None
                    
        # check for loss by no pieces
        white_has_pieces: bool = False
        for p in self.pieces:
            if p is not None: 
                if p[0] == Player.WHITE:
                    white_has_pieces = True
                    break
        if not white_has_pieces:
            self.state = State.BLACK_WIN
                
        black_has_pieces: bool = False
        for p in self.pieces:
            if p is not None:
                if p[0] == Player.BLACK:
                    black_has_pieces = True
                    break
        if not black_has_pieces:
            self.state = State.WHITE_WIN

        # check for draw with no pawns
        has_pawns: bool = False
        for p in self.pieces:
            if p is not None:
                if p[1] == Piece.PAWN:
                    has_pawns = True

        if not has_pawns:
            self.state = State.DRAW

        # game in progress > 100 is a draw
        if len(self.history) > 100 and self.state:
            self.state = State.DRAW

        # progress to next player's turn
        if self.state:
            self.turn = Player.BLACK if self.turn == Player.WHITE else Player.WHITE

            
    def lose_turn(self):
        """Lose a turn. Equivalent to calling move('PASS')."""
        self.move("PASS")

    def resign(self):
        """Resign the game. Equivalent to calling move('RESIGN')."""
        self.move("RESIGN")

    def copy(self) -> KWGame:
        """Create a copy (clone) of the KW game board"""
        tmp: KWGame = KWGame()
        tmp.pieces = self.pieces.copy()
        tmp.turn = self.turn
        tmp.state = self.state
        return tmp


def setup(black_pieces: dict[str, Piece],  white_pieces: dict[str, Piece], turn: Player) -> KWGame:
    """Create a game with pieces setup accordingly"""
    game: KWGame = KWGame()
    game.turn = turn
    game.state = State.IN_PROGRESS
    game.pieces =  [None] * 36
    for loc, p in black_pieces.items():
        x, y = parse_pos(loc)
        game.pieces[y * 6 + x] = (Player.BLACK, p)
    for loc, p in white_pieces.items():
        x, y = parse_pos(loc)
        game.pieces[y * 6 + x] = (Player.WHITE, p)
    return game


def print_help():
    input("""Knight's Watch commands:
  > Pa2a3  - Performs any valid move.
  > PASS   - Skip a turn.
  > RESIGN - Give up and quit the game.
""")
    
def main():
    game = KWGame()
    while not game.is_over():
        game.print_fancy()
        move_str = input(f"{game.turn}> ")
        print()

        move_str = re.sub(r'#.*', "", move_str)
        move_str = move_str.strip()
        if not move_str or move_str.lower() in ("help", "?"):
            print_help()
            continue
            
        try:
            game.move(move_str)
        except GameException as e:
            input(e)
    game.print_fancy()
    print(f"{game.state}")

    
if __name__ == "__main__":
    main()
