import threading
from udp import udp_client as client

nickname = None

def register(new_nickname):
    global nickname
    # TODO: send nickname to server and handle return
    response = client.register(new_nickname)
    nickname = new_nickname
    # print(response)
    # if response['code'] == 0:
    #     nickname = new_nickname
    # print(nickname)

def send_message(recipient, message):
    # TODO: send message to recipient
    response = client.send_msg(recipient, message)
    print(response)

def send_file(recipient, file_name, message):
    # TODO: send file and message to recipient
    print(file_name)

def end_connection():
    # TODO: send message finishing connection with server
    print('Ending connection...')

def handle_received_data():
    # TODO: receive messages from server and handle them
    print('handling messages...')

receiving_thread = threading.Thread(target=client.receive_data)
receiving_thread.daemon = True
receiving_thread.start()

while True:
    action = input()
    action_parts = action.split()
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
                print('Command is missing parts.')
                continue
            send_message(action_parts[1], action_parts[2])
        case '/FILE':
            if not nickname:
                print('User not registered.')
                continue
            if len(action_parts) != 4:
                print('Command is missing parts.')
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