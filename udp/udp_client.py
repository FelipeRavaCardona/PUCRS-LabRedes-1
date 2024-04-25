import json
import queue
import socket
import random

#Definição da configuração do UDP
SERVER_ADDRESS = ('localhost', 3000)
BUFF_SIZE = 2048

#Inicialização do socket UDP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.bind(('localhost', random.randint(1, 9999)))

#Criação da fila de mensagens recebidas
message_queue = queue.Queue()

def send_data(message):
    #Envia mensagens ao servidor
    client_socket.sendto(message.encode(), SERVER_ADDRESS)

def receive_data():
    #Recebe mensagens do servidor
    while True:
        response, _ = client_socket.recvfrom(BUFF_SIZE)
        message_queue.put(json.loads(response.decode('utf-8')))
        