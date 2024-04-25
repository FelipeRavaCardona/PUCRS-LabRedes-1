import json
import base64
import threading
from udp import udp_client as client

#Nome escolhido pelo usuário e reconhecido pelo servidor
nickname = None

def register(new_nickname):
    # Monta a mensagem com os dados necessários para registrar um novo usuário
    message = json.dumps({
        'OPCODE': 1,
        'nickname': new_nickname
    })
    client.send_data(message)

def send_message(recipient, message):
    # Monta a mensagem com os dados necessários para enviar uma mensagem para outro usuário
    message = json.dumps({
        'OPCODE': 2,
        'recipient': recipient,
        'message': message
    })
    client.send_data(message)

def send_file(recipient, file_name, message):
    # Monta a mensagem com os dados necessários para enviar um arquivo e uma mensagem para outro usuário
    with open(f"./files/{file_name}", 'rb') as file:
        file_data = file.read()
    
    message = json.dumps({
        'OPCODE': 3,
        'recipient': recipient,
        'file': base64.b64encode(file_data).decode('utf-8'),
        'message': message
    })
    client.send_data(message)

def end_connection():
    # Monta a mensagem para finalizar a comunicação com o servidor
    message = json.dumps({
        'OPCODE': 4
    })
    client.send_data(message)
    
def handle_received_data():
    # Lida com as mensagens vindas do servidor
    while True:
        global nickname
        message = client.message_queue.get()
        match message['OPCODE']:
            case 1:
                # OPCODE 1, resposta do registro do usuário
                if message['code'] == 0:
                    nickname = message['nickname']
                    print('User registered successfully.')
                else:
                    print('Nickname already used.')
                print(message['message'])
                nickname = None
            case 5:
                # OPCODE 5, recebeu uma mensagem de outro usuário
                print(f"{message['sender']}: {message['message']}")
            case 6:
                # OPCODE 6, recebeu uma mensagem e arquivo de outro usuário
                print(f"{message['sender']} sent you a file with message: {message['message']}")
                with open(f"./received/{message['sender']}.txt", 'wb') as file:
                    file.write(base64.b64decode(message['file']))

def parse_input(input):
    # Faz a divisão do input do usuário em partes diferentes
    first_quote_index = input.find('"')
    last_quote_index = input.rfind('"')
    
    action_parts = None
    if first_quote_index != -1 and last_quote_index != -1 and first_quote_index < last_quote_index:
        before_message = input[:first_quote_index].split()
        message = input[first_quote_index + 1:last_quote_index]
        after_message = input[last_quote_index + 1:].split()
        
        action_parts = before_message + [message] + after_message
    else:
        action_parts = action.split()
    return action_parts

# Inicia o thread UDP para receber mensagens do servidor
receiving_thread = threading.Thread(target=client.receive_data)
receiving_thread.daemon = True
receiving_thread.start()

# Inicia o thread para lidar com as mensagens recebidas que entram na fila de mensagens
handling_thread = threading.Thread(target=handle_received_data)
handling_thread.daemon = True
handling_thread.start()

while True:
    #Recolhe o input do usuário
    action = input()
    action_parts = parse_input(action)
    match action_parts[0]:
        case '/REG':
            #Caso de registro
            if len(action_parts) != 2:
                print('Missing nickname.')
            if nickname:
                print('User already registered.')
                continue
            register(action_parts[1])
        case '/MSG':
            #Caso de enviar mensagem
            if not nickname:
                print('User not registered.')
                continue
            if len(action_parts) != 3:
                print('Command is malformed.')
                continue
            send_message(action_parts[1], action_parts[2])
        case '/FILE':
            #Caso de enviar mensagem e arquivo
            if not nickname:
                print('User not registered.')
                continue
            if len(action_parts) != 4:
                print('Command is malformed.')
                continue
            send_file(action_parts[1], action_parts[2], action_parts[3])
        case '/OFF':
            #Caso de encerrar comunicação
            if not nickname:
                print('User not registered.')
                continue
            end_connection()
        case _:
            #Caso default para lidar com comandos desconhecidos
            print(f"'{action_parts[0]}' is not a known command.")