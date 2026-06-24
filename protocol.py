from socket import socket

DEFAULT_HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
DEFAULT_PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

OK = "OK"
ERROR = "ERROR"
WHITE = "WHITE"
BLACK = "BLACK"
GAME_OVER = "GAME_OVER"

VERBOSE = True

def send(conn: socket, data):
    if VERBOSE:
        print(f"SENDING to {conn.getpeername()}: {data}")
    conn.sendall(data.encode())
    

def receive(conn, size=5) -> str:
    tmp = conn.recv(size)
    if not tmp:
        print(f"ERROR RECEIVING from {conn.getpeername()}")
        raise Exception()

    tmp = tmp.decode()
    if VERBOSE:
        print(f"RECEIVING from {conn.getpeername()}: {tmp}")
    return tmp
