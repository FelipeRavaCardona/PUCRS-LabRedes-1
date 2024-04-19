import json
import queue
import socket
import random

SERVER_ADDRESS = ('localhost', 3000)
BUFF_SIZE = 1200

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.bind(('localhost', random.randint(1, 9999)))

message_queue = queue.Queue()

def send_data(message):
    client_socket.sendto(message.encode(), SERVER_ADDRESS)

def receive_data():
    while True:
        response, _ = client_socket.recvfrom(BUFF_SIZE)
        message_queue.put(json.loads(response.decode('utf-8')))
        