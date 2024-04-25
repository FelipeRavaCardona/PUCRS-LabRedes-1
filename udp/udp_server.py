import json
import queue
import socket

SERVER_ADDRESS = ('localhost', 3000)
BUFF_SIZE = 2048

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(SERVER_ADDRESS)

message_queue = queue.Queue()

print(f"UDP server listening on {SERVER_ADDRESS[0]}:{SERVER_ADDRESS[1]}")

def send_data(message, address):
    server_socket.sendto(message.encode(), address)

def receive_data():
    while True:
        data, address = server_socket.recvfrom(BUFF_SIZE)
        message_queue.put((data, address))