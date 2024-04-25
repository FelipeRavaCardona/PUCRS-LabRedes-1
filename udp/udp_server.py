import queue
import socket

#Definição da configuração UDP
SERVER_ADDRESS = ('localhost', 3000)
BUFF_SIZE = 2048

#Inicialização do socket UDP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(SERVER_ADDRESS)

#Criação da fila de mensagens recebidas
message_queue = queue.Queue()

print(f"UDP server listening on {SERVER_ADDRESS[0]}:{SERVER_ADDRESS[1]}")

def send_data(message, address):
    #Envia mensagens aos usuários
    server_socket.sendto(message.encode(), address)

def receive_data():
    #Recebe mensagens dos usuários
    while True:
        data, address = server_socket.recvfrom(BUFF_SIZE)
        message_queue.put((data, address))