from move import BaseDecideMove
import math
import random

from knights_watch import KWGame, Piece, format_pos
from game import Player, State

MAX_DEPTH = 2

class DecideMove(BaseDecideMove):
    def __init__(self):
        # scores go from -100 to 100
        super().__init__(max_depth=MAX_DEPTH, max_white_score=100, min_black_score=-100)

    # generate all possibilities of next game state from the present one
    def moves_from(self, game: KWGame) -> list[KWGame]:
        if game.is_over():
            return []

        results = []
        player = game.turn

        for i in range(36):
            piece_at = game.pieces[i]
            if piece_at is None:
                continue
            if piece_at[0] != player:
                continue

            piece_type = piece_at[1]
            from_x = i % 6
            from_y = i // 6

            if piece_type == Piece.PAWN:
                if player == Player.WHITE:
                    step_y = 1
                else:
                    step_y = -1

                to_y = from_y + step_y

                if to_y < 0 or to_y > 5:
                    continue

                # straight forward
                to_pos_forward = to_y * 6 + from_x
                if game.pieces[to_pos_forward] is None:
                    move_str = self._make_move_string("P", from_x, from_y, from_x, to_y)
                    new_game = self._apply_move(game, move_str)
                    if new_game is not None:
                        results.append(new_game)

                # diagonal captures
                for step_x in [-1, 1]:
                    to_x = from_x + step_x
                    if to_x < 0 or to_x > 5:
                        continue
                    to_pos_diag = to_y * 6 + to_x
                    if game.pieces[to_pos_diag] is not None and game.pieces[to_pos_diag][0] != player:
                        move_str = self._make_move_string("P", from_x, from_y, to_x, to_y)
                        new_game = self._apply_move(game, move_str)
                        if new_game is not None:
                            results.append(new_game)

            elif piece_type == Piece.KNIGHT:
                # all 8 knight moves
                knight_jumps = [
                    (2, 1), (2, -1), (-2, 1), (-2, -1),
                    (1, 2), (1, -2), (-1, 2), (-1, -2)
                ]
                for step_x, step_y in knight_jumps:
                    to_x = from_x + step_x
                    to_y = from_y + step_y
                    if to_x < 0 or to_x > 5 or to_y < 0 or to_y > 5:
                        continue
                    to_pos = to_y * 6 + to_x
                    if game.pieces[to_pos] is not None and game.pieces[to_pos][0] == player:
                        continue
                    move_str = self._make_move_string("K", from_x, from_y, to_x, to_y)
                    new_game = self._apply_move(game, move_str)
                    if new_game is not None:
                        results.append(new_game)

        if len(results) == 0:
            new_game = game.copy()
            new_game.lose_turn()
            results.append(new_game)
        return results

    # convert internal coords back to a move string
    def _make_move_string(self, piece: str, fx: int, fy: int, tx: int, ty: int) -> str:
        from_str = format_pos(fx, fy)
        to_str = format_pos(tx, ty)
        return piece + from_str + to_str

    # try to apply a move and return the resulting game, or None if invalid
    def _apply_move(self, game: KWGame, move_str: str):
        try:
            g = game.copy()
            g.move(move_str)
            return g

        except Exception:
            return None

    # evaluate the board : positive = good for WHITE, negative = good for BLACK
    # weighting advancement more because getting a pawn across wins
    def evaluate(self, game: KWGame) -> int:
        if game.state == State.WHITE_WIN:
            return 100
        if game.state == State.BLACK_WIN:
            return -100
        if game.state == State.DRAW:
            return 0

        score = 0
        white_pawns = 0
        black_pawns = 0
        white_knights = 0
        black_knights = 0

        for index in range(36):
            p = game.pieces[index]
            if p is None:
                continue

            player, piece_type = p
            col = index % 6
            row = index // 6

            if player == Player.WHITE:
                if piece_type == Piece.PAWN:
                    white_pawns += 1

                    # advancement
                    advancement = row  # 0-5
                    score += 2 + advancement * 3

                    # bonus for  columns
                    if 1 <= col <= 4:
                        score += 1

                elif piece_type == Piece.KNIGHT:
                    white_knights += 1
                    score += 8
                    # knight in center controls more squares
                    distance_from_center = abs(col - 2) + abs(row - 2)
                    score += max(0, 4 - distance_from_center)
            else:  # BLACK
                if piece_type == Piece.PAWN:
                    black_pawns += 1
                    # for black, lower row = more advanced (toward row 0)
                    advancement = 5 - row
                    score -= 2 + advancement * 3

                    if 1 <= col <= 4:
                        score -= 1

                elif piece_type == Piece.KNIGHT:
                    black_knights += 1
                    score -= 8
                    distance_from_center = abs(col - 2) + abs(row - 2)
                    score -= max(0, 4 - distance_from_center)

        # reward having more knights/pawns than the opponent
        if white_knights > black_knights:
            score += 5 * (white_knights - black_knights)
        elif black_knights > white_knights:
            score -= 5 * (black_knights - white_knights)

        if white_pawns > black_pawns:
            score += 3 * (white_pawns - black_pawns)
        elif black_pawns > white_pawns:
            score -= 3 * (black_pawns - white_pawns)

        return score

    # decide the best move using minimax following same pattern as the tic tac toe ex
    def decide_best_move(self, game: KWGame):
        if game.turn == Player.WHITE:
            best_score = -math.inf
            best_move = None

            for g in self.moves_from(game):
                if len(g.history) == 0:
                    continue
                move_string = g.history[-1]

                score = self.minimax(g)
                # tiebreaker so it doesn't loop on equal moves
                score += random.uniform(0, 0.5)

                if score > best_score:
                    best_score = score
                    best_move = move_string

            if best_move is not None:
                self.best_move = best_move

        else:   # BLACK is minimizing
            best_score = math.inf
            best_move = None

            for g in self.moves_from(game):
                if len(g.history) == 0:
                    continue
                move_string = g.history[-1]

                score = self.minimax(g)
                # tiebreaker
                score -= random.uniform(0, 0.5)

                if score < best_score:
                    best_score = score
                    best_move = move_string

            if best_move is not None:
                self.best_move = best_move