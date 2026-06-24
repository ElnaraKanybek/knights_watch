# Knight's Watch — Minimax Game
 
A computer opponent for **Knight's Watch**, a 6×6 chess variant played with pawns and knights, implemented using the **minimax algorithm**.
 
##  About the Game
 
Knight's Watch is played on a reduced 6×6 chessboard with only two piece types:
 
- **Pawns (♙ / ♟)** — move forward one square, capture diagonally forward (no en passant)
- **Knights (♘ / ♞)** — move in a standard chess "L" shape, no restrictions
```
6 0m0ZnZ
5 opopop
4 0Z0Z0Z
3 Z0Z0Z0
2 POPOPO
1 ZNZ0M0
  a b c d e f
```
 
**Win conditions:**
- Get a pawn to the opponent's back wall (row 6 for Black, row 1 for White)
- Capture every opposing piece (pawns + knights), without triggering a draw
- **Draw:** all pawns on the board are captured
- A player with no legal moves must **pass** their turn (no stalemates)
- Games are capped at 100 moves (50 rounds) to avoid infinite play
##  The Opponent — `DecideMove`
 
The AI opponent is a subclass of `BaseDecideMove` that implements three core methods:
 
| Method | Purpose |
|---|---|
| `moves_from(game)` | Generates every legal resulting game state for the player to move |
| `evaluate(game)` | Scores a board position — positive favors White (maximizer), negative favors Black (minimizer) |
| `decide_best_move(game)` | Runs `minimax` and sets `self.best_move` to the chosen move string |
 
**Key design considerations:**
- `evaluate()` weighs both material (pawns vs. knights) and positional factors (e.g. pawn advancement toward the opponent's wall)
- Search respects a configurable timeout (default 2s), so minimax must be interruptible mid-search
- Built and tested against random-move, beginner, and more skilled opponents using the provided `game_client.py` test harness
##  Running the Game
 
```bash
# Human vs Human
python3 game_client.py
 
# Human vs Computer
python3 game_client.py -m opponent
 
# Computer vs Computer
python3 game_client.py -m opponent_v1 -m2 opponent_v2
 
# Custom timeout (seconds)
python3 game_client.py -m opponent -t 5
```
 
Games are logged to `logs/` and can be replayed with:
 
```bash
python3 game_client.py < logs/kw_game_4aa221.log
```
 
##  Tech Stack
 
- **Language:** Python
- **Core algorithm:** Minimax (game tree search)
- **Architecture:** Subclassing an abstract base player (`BaseDecideMove`) provided by the game engine
