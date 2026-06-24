import socket
from threading import Thread
import random
from typing import Optional

from knights_watch import KWGame, Player, GameException, State
import sys
from protocol import DEFAULT_HOST, DEFAULT_PORT, OK, ERROR, WHITE, BLACK, GAME_OVER, send, receive

def receive_move(conn, game: KWGame) -> Optional[str]:
    try:
        move_str = receive(conn, 5)
    except Exception:
        return None
    
    print(f"Received move {move_str}")
    try:
        if move_str == "PASS":
            game.lose_turn()
        else:
            game.move(move_str)
        return move_str
    except GameException as e:
        print(f"Error: {e}")

    return None


def play_game(conn1, name1, conn2, name2):

    print(f"Starting game between {name1} and {name2}")

    order: tuple
    name_order: tuple[str]
    if random.randint(1, 2) == 1:
        order = (conn1, conn2)
        name_order = (name1, name2)
    else:
        order = (conn2, conn1)
        name_order = (name2, name1)

    try:
        send(order[0], WHITE)
        send(order[1], BLACK)
        game: KWGame = KWGame(do_log=True)
        current: int = 0
        while not game.is_over():

            current_player = game.turn

            game.print()

            # prompt the player for their mov
            match current_player:
                case Player.WHITE:
                    send(order[0], WHITE)
                case Player.BLACK:
                    send(order[1], BLACK)

            move_str = receive_move(order[current], game)
            if move_str is None:
                send(order[current], ERROR)
                receive(order[current], 2)  # consume confirmation
                continue

            send(order[current], OK)
            receive(order[current], 2)  # consume confirmation

            current = 1 if current == 0 else 0

            print(f"Sending {move_str} to {name_order[current]}")
            match current_player:
                case Player.WHITE:
                    send(order[1], WHITE)
                case Player.BLACK:
                    send(order[0], BLACK)

            send(order[current], move_str)
            receive(order[current], 2)   # consume confirmation

        game.print_fancy()
        match game.state:
            case State.DRAW:
                print("Draw")
            case State.WHITE_WIN:
                print(f"WHITE ({name_order[0]}) wins!")
            case State.BLACK_WIN:
                print(f"BLACK ({name_order[1]}) wins!")

        send(order[0], GAME_OVER)
        receive(order[0], 2)  # consume confirmation
        send(order[0], str(game.state))
        receive(order[0], 2)  # consume confirmation

        send(order[1], GAME_OVER)
        receive(order[1], 2)  # consume confirmation
        send(order[1], str(game.state))
        receive(order[1], 2)  # consume confirmation

    except InterruptedError as e:
       pass

    conn1.close()
    conn2.close()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    host = DEFAULT_HOST
    port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
    s.bind((host, port))

    players = []

    while True:
        s.listen()

        print(f"Waiting for Player 1")
        conn1, addr1 = s.accept()
        print(f"Connection from {addr1}")

        name1_b = conn1.recv(30)
        if not name1_b:
            print(f"No name sent. Closing...")
            conn1.close()
            continue
        name1 = name1_b.decode()

        print(f"Waiting for Player 2")
        conn2, addr2 = s.accept()
        print(f"Connection from {addr2}")
        name2_b = conn2.recv(30)
        if not name2_b:
            print(f"No name sent. Closing...")
            conn1.close()
            conn2.close()
            continue
        name2 = name2_b.decode()
        
        Thread(target=play_game, args=(conn1, name1, conn2, name2)).start()

