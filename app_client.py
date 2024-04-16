import base64
import threading
from udp import udp_client as client

nickname = None

def register(new_nickname):
    client.register(new_nickname)

def send_message(recipient, message):
    client.send_msg(recipient, message)

def send_file(recipient, file_name, message):
    # TODO: send file and message to recipient
    with open(f"./files/{file_name}", 'rb') as file:
        file_data = file.read()
    
    client.send_file(recipient, base64.b64encode(file_data).decode('utf-8'), message)

def end_connection():
    # TODO: send message finishing connection with server
    print('Ending connection...')

def handle_received_data():
    # TODO: receive messages from server and handle them
    while True:
        global nickname
        message = client.message_queue.get()
        match message['OPCODE']:
            case 1:
                if message['code'] == 0:
                    nickname = message['nickname']
                    print('User registered successfully.')
                else:
                    print('Nickname already used.')
            case 2:
                print(message['message'])
            case 3:
                print(message)
            case 4:
                print(message)
            case 5:
                print(f"{message['sender']}: {message['message']}")
            case 6:
                print('received file')
                print(message)

def parse_input(input):
    first_quote_index = input.find('"')
    last_quote_index = input.rfind('"')
    
    action_parts = None
    # If both quotes are found and the first quote comes before the last one
    if first_quote_index != -1 and last_quote_index != -1 and first_quote_index < last_quote_index:
        # Split the string into three parts: before message, message, after message
        before_message = input[:first_quote_index].split()
        message = input[first_quote_index + 1:last_quote_index]
        after_message = input[last_quote_index + 1:].split()
        
        # Combine parts before message, message, and after message
        action_parts = before_message + [message] + after_message
    else:
        # If quotes are not found or not properly placed, split normally
        action_parts = action.split()
    return action_parts

receiving_thread = threading.Thread(target=client.receive_data)
receiving_thread.daemon = True
receiving_thread.start()

handling_thread = threading.Thread(target=handle_received_data)
handling_thread.daemon = True
handling_thread.start()

while True:
    action = input()
    action_parts = parse_input(action)
    match action_parts[0]:
        case '/REG':
            if len(action_parts) != 2:
                print('Missing nickname.')
            if nickname:
                print('User already registered.')
                continue
            register(action_parts[1])
        case '/MSG':
            if not nickname:
                print('User not registered.')
                continue
            if len(action_parts) != 3:
                print('Command is malformed.')
                continue
            send_message(action_parts[1], action_parts[2])
        case '/FILE':
            if not nickname:
                print('User not registered.')
                continue
            if len(action_parts) != 4:
                print('Command is malformed.')
                continue
            send_file(action_parts[1], action_parts[2], action_parts[3])
        case '/OFF':
            if not nickname:
                print('User not registered.')
                continue
            end_connection()
            break
        case _:
            print(f"'{action_parts[0]}' is not a known command.")