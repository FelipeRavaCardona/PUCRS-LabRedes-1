import json
import socket

server_socket = None
users = []

def find_user_by_address(ip, port):
    global users
    for user in users:
        if user['ip'] == ip and user['port'] == port:
            return user
    return None

def find_user_by_nickname(nickname):
    for user in users:
        if user['nickname'] == nickname:
            return user
    return None

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
    print(f"{nickname}({sender_ip}:{sender_port}) connected.")
    return json.dumps({
        'OPCODE': 1,
        'code': 0,
        'message': 'User registered successfully.',
        'nickname': nickname
    })

def handle_message(sender_ip, sender_port, message_data):
    recipient = find_user_by_nickname(message_data['recipient'])
    if not recipient:
        return json.dumps({
            'OPCODE': 2,
            'code': 1,
            'message': f"{message_data['recipient']} is not online."
        })
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sender = find_user_by_address(sender_ip, sender_port)
        print(f"Message sent from {sender['nickname']} to {recipient['nickname']}")
        message = json.dumps({
            'OPCODE': 5,
            'sender': sender['nickname'],
            'message': message_data['message']
        })
        sock.sendto(message.encode(), (recipient['ip'], recipient['port']))
    return json.dumps({
        'OPCODE': 2,
        'code': 0,
        'message': f"Message sent to {recipient['nickname']}."
    })

def handle_file(sender_ip, sender_port, message_data):
    recipient = find_user_by_nickname(message_data['recipient'])
    if not recipient:
        return json.dumps({
            'OPCODE': 2,
            'code': 1,
            'message': f"{message_data['recipient']} is not online."
        })
    # TODO: Send file and message to recipient
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sender = find_user_by_address(sender_ip, sender_port)
        print(f"File sent from {sender['nickname']} to {recipient['nickname']}")
        message = json.dumps({
            'OPCODE': 6,
            'sender': sender['nickname'],
            'file': message_data['file'],
            'message': message_data['message']
        })
        sock.sendto(message.encode(), (recipient['ip'], recipient['port']))
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
    message = json.loads(data.decode('utf-8'))
    match message['OPCODE']:
        case 1:
            return handle_registration(message['nickname'], sender_ip, sender_port)
        case 2:
            return handle_message(sender_ip, sender_port, message)
        case 3:
            return handle_file(sender_ip, sender_port, message)
        case 4:
            return handle_disconnect(sender_ip, sender_port)
        case _:
            return f"OPCODE '{message.OPCODE} is not known."

def start_server_udp(host, port):
    # TODO: follow commented code?
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))
    print(f"UDP server listening on {host}:{port}")

    while True:
        data, address = server_socket.recvfrom(2000)
        response = handle_received(data, address[0], address[1])
        server_socket.sendto(response.encode(), address)

start_server_udp('localhost', 3000)
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