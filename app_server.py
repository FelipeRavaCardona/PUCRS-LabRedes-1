import json

users = []

def find_user_by_address(ip, port):
    for user in users:
        if user['ip'] == ip and user['port'] == port:
            return user
    return None

def find_user_by_nickname(nickname):
    for user in users:
        if user['nickname'] == nickname:
            return True
    return False

def handle_registration(nickname, sender_ip, sender_port):
    if find_user_by_nickname(nickname):
        return json.dumps({
            'OPCODE': 1,
            'code': 1,
            'message': 'Nickname already used.'
        })
    users.append({
        'nickname': nickname,
        'ip': sender_ip,
        'port': sender_port
    })
    return json.dumps({
        'OPCODE': 1,
        'code': 0,
        'message': 'User registered successfully.'
    })

def handle_message(sender_ip, sender_port, recipient, message):
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

def handle_file(sender_ip, sender_port, recipient, file, message):
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

def handle_disconnect(sender_ip, sender_port):
    sender = find_user_by_address(sender_ip, sender_port)
    if sender:
        users.remove(sender)
        return json.dumps({
            'OPCODE': 4,
            'code': 0,
            'message': f"{sender.nickname} disconnected."
        })
    return json.dumps({
        'OPCODE': 4,
        'code': 1,
        'message': 'User does not exist.'
    })

def handle_received(data, sender_ip, sender_port):
    message = data.decode()
    match message.OPCODE:
        case 1:
            return handle_registration(data.nickname, sender_ip, sender_port)
        case 2:
            return handle_message(sender_ip, sender_port, data.recipient, data.message)
        case 3:
            return handle_file(sender_ip, sender_port, data.recipient, data.file, data.message)
        case 4:
            return handle_disconnect(sender_ip, sender_port)
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