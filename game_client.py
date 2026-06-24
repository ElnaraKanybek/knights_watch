import argparse
import socket
from time import sleep
from threading import Thread
from random import randint
import sys

from knights_watch import KWGame, GameException
from game import Game, Player
from protocol import DEFAULT_HOST, DEFAULT_PORT, OK, ERROR, WHITE, BLACK, send, receive
from move import BaseDecideMove, Interrupted

# defaults
MAX_MOVE_TIME = 2

# ================================================================================
# Program Arguments
# --------------------------------------------------------------------------------

parser = argparse.ArgumentParser(
    prog = "game_client.py",
    description = "Play the game either locally or join a client.",
    epilog = "")

parser.add_argument("-n", "--name", metavar="NAME", help="""Player's name.""")

parser.add_argument("-m", "--module", metavar="MODULE", help="""The first python module to get moves from. In the case of a networked game, this will be the player, in the case of a local game this will be the opponent.""")

parser.add_argument("-m2", "--module2", metavar="MODULE", help="""The second python module to get moves from. Only for local game.""")

parser.add_argument("--host", help="""The name or IP of the host to connect to. Defaults to localhost if a port is specified, otherwise assumes a local game.""")

parser.add_argument("-p", "--port", help="""The port of the host to connect to.""")

parser.add_argument("-t", "--timeout", metavar="SECONDS", help="""The time limit for automated move selection.""")

args = parser.parse_args()

# ================================================================================

class CollectMove(Thread):
    """A tread that runs the move decider but can be interrupted."""
    def __init__(self, decider: BaseDecideMove, game: Game):
        super().__init__()
        self.chosen_move: str = ""
        self.move_decider: BaseDecideMove = decider
        self.game = game
        
    def interrupt(self):
        if self.move_decider:
            self.move_decider.interrupt()

    def run(self):
        try:
            self.move_decider.decide_best_move(self.game.copy())
        except Interrupted:
            print("Warning: decision took too long, using current best move.")

        self.chosen_move = self.move_decider.best_move

        
def collect(decider, game, timeout: int = MAX_MOVE_TIME) -> str:
    """Run the decider on a thread and interrupt after the time expires."""
    thread = CollectMove(decider.DecideMove(), game)
    thread.start()
    sleep(timeout)
    thread.interrupt()
    thread.join()
    return thread.chosen_move

# ================================================================================

def play_local_game(name1: str, decider1, name2: str, decider2, timeout: int):

    game = KWGame(do_log=True)

    if randint(1, 2) == 1:
        name1, name2 = name2, name1
        decider1, decider2 = decider2, decider1

    print(f"{name1} is WHITE")
    print(f"{name2} is BLACK")
    input("<press enter to start>")

    while not game.is_over():
        game.print()

        match game.turn:
            case Player.WHITE:
                move_str = collect(decider1, game, timeout)
            case Player.BLACK:
                move_str = collect(decider2, game, timeout)
        print()

        try:
            game.move(move_str)
        except GameException as e:
            print(e)

    game.print()
    print(f"{game.state}")

# ================================================================================

        
def play_network_game(host: str, port: int, name: str, decider, timeout: int):
        
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        s.connect((host, port))
        s.sendall(name.encode())

        player = receive(s, 30)
        print(player)

        game: KWGame = KWGame(do_log=True)

        while True:
            command = receive(s, 30)
            match command:
                case command if command in ("WHITE", "BLACK"):
                    move_str: str = ""
                    if player == command:
                        move_str = collect(decider, game, timeout)
                        send(s, move_str)
                    else:
                        move_str = receive(s, 6)
                        print(move_str)
                        send(s, OK)
                    game.move(move_str)
                    game.print()

                case "OK":
                    print("Move accepted")
                    send(s, OK)

                case "ERROR":
                    print("Problem with move")
                    send(s, OK)

                case "GAME_OVER":
                    send(s, OK)
                    winner = receive(s, 5)
                    print(winner)
                    send(s, OK)
                    break


# ================================================================================

timeout = int(args.timeout) if args.timeout else MAX_MOVE_TIME

# setting the port or the host will cause a networked game
if args.port or args.host:
    if not args.name:
        print("Name required when connecting to server.")
        sys.exit(1)
    name = args.name
    port = int(args.port) if args.port else DEFAULT_PORT
    host = args.host if args.host else DEFAULT_HOST
    mod = __import__(args.module if args.module else "ui_player")
    play_network_game(host, port, name, mod, timeout)
else:
    mod1 = __import__(args.module if args.module else "ui_player")
    name1 = args.module if args.module else "human"
    mod2 = __import__(args.module2 if args.module2 else "ui_player")
    name2 = args.module2 if args.module2 else "human"
    play_local_game(name1, mod1, name2, mod2, timeout)
