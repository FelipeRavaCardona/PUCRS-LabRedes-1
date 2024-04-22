import base64
import json
import random
import socket
import string
import threading

user_nickname = None


def register(sock, nickname):
    global user_nickname
    message = json.dumps({
        'OPCODE': 1,
        'nickname': nickname
    })
    sock.sendall(message.encode())
    user_nickname = nickname

def send_message(sock, recipient, message):
    # TODO: send message to recipient
    # response = client.send_msg(recipient, message)
    # print(response)
    message_json = json.dumps({
        'OPCODE': 2,
        'recipient': recipient,
        'message': message
    })
    sock.sendall(message_json.encode())
    print("Mensagem enviada!")
    print(message)

import json
import os

def send_file(sock, recipient, file_name, message):
    # Lê o arquivo em modo binário e armazena em uma variável
    if '"' in file_name or "'" in file_name:
        print("Erro nome do arquivo inválido")
        return
    
    file_path = f"repo/{file_name}"
    try:
        with open(file_path, 'rb') as file:
            file_data = file.read()
    except FileNotFoundError:
        print("Erro: Arquivo não encontrado.")
        return

    # Codifica os dados do arquivo em base64 para enviar como string JSON
    file_data_encoded = base64.b64encode(file_data).decode('utf-8')

    # Cria um dicionário com os dados a serem enviados
    data_to_send = {
        'OPCODE': 3,  # OPCODE diferente para diferenciar o tipo de operação
        'recipient': recipient,
        'file': file_data_encoded,
        'message': message,
        'file_name': file_name
    }

    # Converte o dicionário para JSON e codifica em bytes
    message_json = json.dumps(data_to_send)
    sock.sendall(message_json.encode())

    print("Arquivo e mensagem enviados!")
    print(f"Destinatário: {recipient}")
    print(f"Arquivo: {file_name}")
    print(f"Mensagem: {message}")


def end_connection(sock):
    message = json.dumps({
        'OPCODE': 4
    })
    sock.sendall(message.encode())
    print()
    print()
    print("Pedido de desconexão enviado! ")
    


def send_messages(sock):
    while True:
        action = input()
        action_parts = action.split()
        command = action_parts[0]
        
        if command == '/REG':
            if len(action_parts) != 2:
                print('Missing nickname.')
                continue
            if user_nickname:
                print(f'User already registered as{user_nickname}')
                continue
            register(sock, action_parts[1])
        
        elif command == '/MSG':
            if not user_nickname:
                print('User not registered.')
                continue
            if len(action_parts) != 3:
                print('Command is missing parts.')
                continue
            send_message(sock, action_parts[1], action_parts[2])
        
        elif command == '/FILE':
            if not user_nickname:
                print('User not registered.')
                continue
            if len(action_parts) != 4:
                print('Command is missing parts.')
            
                continue
            recipient = action_parts[1]
            file_name = action_parts[2]
            message = action_parts[3]
            send_file(sock, recipient, file_name, message)
        
        elif command == '/OFF':
            if not user_nickname:
                print('User not registered.')
                continue
            end_connection(sock)
            break
        
        else:
            print(f"'{command}' is not a known command.")


def receive_messages(sock):
    while True:
        data = sock.recv(3072)
        if not data:
            print("Servidor encerrou a conexão.")
            break
        message = json.loads(data.decode('utf-8'))
        if message['OPCODE'] == 2:
            code = message.get('code')
            print()
            print()
            if code == 0:
                print(f"Mensagem do servidor: {message['message']}")
            elif code == 1:
                print(f"Mensagem do servidor: {message['message']}")
            else:
                print(f"Usuario: {message['sender']} enviou: {message['message']}")
        elif message['OPCODE'] == 3:
            code = message.get('code')
            if code == 0 or code == 1:
                print(f"Mensagem do servidor: {message['message']}")
            else:
                # Decodifica os dados do arquivo
                file_data = base64.b64decode(message['file'])
                file_name = message['file_name']
                user_message = message['message']
                sender = message['sender']
                # Cria o diretório 'recebidas' se não existir
                os.makedirs('recebidas', exist_ok=True)
                
                # Salva o arquivo
                file_path = os.path.join('recebidas', file_name)
                with open(file_path, 'wb') as file:
                    file.write(file_data)
                print()
                print()
                print(f"Arquivo {file_name} recebido e salvo em 'recebidas'.")
                print(f"Usuario: {sender} enviou: {user_message}")
        elif message['OPCODE'] == 4:
            code = message.get('code')
            if code == 0 or code == 1:
                print(f"Mensagem do servidor: {message['message']}")
            else:
                user_nickname = None
                print("Disconected from the server.")
                break
        else:
            print(f"Recebido do servidor: {message}")

def start_client(server_host, server_port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((server_host, server_port))
        # Criando e iniciando thread de envio
        send_thread = threading.Thread(target=send_messages, args=(s,))
        send_thread.start()
        
        # Criando e iniciando thread de recebimento
        receive_thread = threading.Thread(target=receive_messages, args=(s,))
        receive_thread.start()
        
        # Aguardar as threads terminarem
        send_thread.join()
        receive_thread.join()

if __name__ == "__main__":
    start_client('localhost', 3000)
