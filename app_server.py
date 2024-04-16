import json

users = {}

def handle_registration(nickname, address):
    if nickname in users:
        return json.dumps({
            'OPCODE': 1,
            'code': 1,
            'message': 'Nickname already used.'
        })
    users[nickname] = address
    return json.dumps({
        'OPCODE': 1,
        'code': 0,
        'message': 'User registered successfully.'
    })

def handle_message(sender, recipient, message):
    if recipient not in users:
        return json.dumps({
            'OPCODE': 2,
            'code': 1,
            'message': f"{recipient} is not online."
        })
    # TODO: Send message to recipient
    return json.dumps({
        'OPCODE': 2,
        'code': 0,
        'message': f"Message sent to {recipient}."
    })

def handle_file(sender, recipient, file, message):
    if recipient not in users:
        return json.dumps({
            'OPCODE': 3,
            'code': 1,
            'message': f"{recipient} is not online."
        })
    # TODO: Send file and message to recipient
    return json.dumps({
        'OPCODE': 2,
        'code': 0,
        'message': f"File sent to {recipient}."
    })

def handle_disconnect(sender):
    if sender in users:
        del users[sender]
        return json.dumps({
            'OPCODE': 4,
            'code': 0,
            'message': f"{sender} disconnected."
        })
    return json.dumps({
        'OPCODE': 4,
        'code': 1,
        'message': 'User does not exist.'
    })

def handle_received(data, address):
    message = data.decode()
    match message.OPCODE:
        case 1:
            return handle_registration(data.nickname, address)
        case 2:
            return handle_message(address, data.recipient, data.message)
        case 3:
            return handle_file(address, data.recipient, data.file, data.message)
        case 4:
            return handle_disconnect(address)
        case _:
            return f"OPCODE '{message.OPCODE} is not known."

def start_server(host, port):
    # TODO: follow commented code?
    print('starting server...')

# import socket

# def start_server(host, port):
#     server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     server_socket.bind((host, port))
#     print(f"UDP server listening on {host}:{port}")

#     while True:
#         data, address = server_socket.recvfrom(1024)
#         response = handle_message(data, address)
#         server_socket.sendto(response.encode(), address)

# # Example usage:
# if __name__ == "__main__":
#     HOST = 'localhost'  # Change this to your server's IP address
#     PORT = 3000        # Choose a port for your server
#     start_server(HOST, PORT)