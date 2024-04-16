import json
import socket

SERVER_ADDRESS = ('localhost', 3000)
BUFF_SIZE = 1200

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def register(nickname):
    message = json.dumps({
        'OPCODE': 1,
        'nickname': nickname
    })

    client_socket.sendto(message.encode(), SERVER_ADDRESS)
    # response, _ = client_socket.recvfrom(BUFF_SIZE)
    # return json.loads(response.decode('utf-8'))

def send_msg(recipient, message):
    message = json.dumps({
        'OPCODE': 2,
        'recipient': recipient,
        'message': message
    })
    client_socket.sendto(message.encode(), SERVER_ADDRESS)
    # response, _ = client_socket.recvfrom(BUFF_SIZE)
    # return json.loads(response.decode('utf-8'))


def receive_data():
    while True:
        print('receiving in thread')
        response, _ = client_socket.recvfrom(BUFF_SIZE)
        print(response)
        