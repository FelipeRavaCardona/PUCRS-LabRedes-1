import json
import socket

SERVER_ADDRESS = ('localhost', 3000)

def register(nickname):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        message = json.dumps({
            'OPCODE': 1,
            'nickname': nickname
        })

        sock.sendto(message.encode(), SERVER_ADDRESS)
        response, _ = sock.recvfrom(1024)
        print(response.decode())