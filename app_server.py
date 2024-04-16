import json
import socket

server_socket = None
users = []

def find_user_by_address(ip, port):
    global users
    print(users)
    for user in users:
        print(user)
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
        'message': 'User registered successfully.'
    })

def handle_message(sender_ip, sender_port, message_data):
    recipient = find_user_by_nickname(message_data['recipient'])
    if not recipient:
        return json.dumps({
            'OPCODE': 2,
            'code': 1,
            'message': f"{recipient} is not online."
        })
    # TODO: Send message to recipient
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        print(f"ip {sender_ip}, port {sender_port}")
        sender = find_user_by_address(sender_ip, sender_port)
        print(sender)
        message = json.dumps({
            'OPCODE': 2,
            'sender': sender['nickname'],
            'message': message_data['message']
        })
        sock.sendto(message.encode(), (recipient['ip'], recipient['port']))
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
    message = json.loads(data.decode('utf-8'))
    match message['OPCODE']:
        case 1:
            return handle_registration(message['nickname'], sender_ip, sender_port)
        case 2:
            return handle_message(sender_ip, sender_port, message)
        case 3:
            return handle_file(sender_ip, sender_port, message['recipient'], message['file'], message['message'])
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
        data, address = server_socket.recvfrom(1024)
        response = handle_received(data, address[0], address[1])
        server_socket.sendto(response.encode(), address)

# start_server_udp('localhost', 3000)
################################################ TCP ##########################################################

def start_server_tcp(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"TCP Server listening on {host}:{port}.")
        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            


def handle_client(conn, addr):
    print(f"Conectado por {addr}")
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            data, address = server_socket.recvfrom(1024)
            response = handle_received_tcp(data, conn, address[0], address[1])
            conn.sendall(response.encode())

    finally:
        conn.close()


def handle_received_tcp(data,conn,sender_ip, sender_port):
    message = json.loads(data.decode('utf-8'))
    match message['OPCODE']:
        case 1:
            return handle_registration_tcp(message['nickname'], conn,sender_ip, sender_port)
        case 2:
            return handle_message_tcp(sender_ip, sender_port, message)
        case 3:
            return handle_file_tcp(sender_ip, sender_port, message['recipient'], message['file'], message['message'])
        case 4:
            return handle_disconnect_tcp(sender_ip, sender_port)
        case _:
            return f"OPCODE '{message.OPCODE} is not known."


def handle_registration_tcp(nickname, conn,sender_ip, sender_port):
    if find_user_by_nickname(nickname):
        return json.dumps({
            'OPCODE': 1,
            'code': 1,
            'message': 'Nickname already used.'
        })
    users.append({
        'nickname': nickname,
        'ip': sender_ip,
        'port': sender_port,
        "connection" : conn
    })
    print(f"{nickname}({sender_ip}:{sender_port}) connected.")
    return json.dumps({
        'OPCODE': 1,
        'code': 0,
        'message': 'User registered successfully.'
    })


def handle_message_tcp(sender_ip, sender_port, message_data):
    recipient = find_user_by_nickname(message_data['recipient'])
    if not recipient:
        return json.dumps({
            'OPCODE': 2,
            'code': 1,
            'message': f"{recipient} is not online."
        })
    
    # TODO: Send message to recipient
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        print(f"ip {sender_ip}, port {sender_port}")
        sender = find_user_by_address(sender_ip, sender_port)
        print(sender)
        message = json.dumps({
            'OPCODE': 2,
            'sender': sender['nickname'],
            'message': message_data['message']
        })
        sock.sendto(message.encode(), (recipient['ip'], recipient['port']))
    return json.dumps({
        'OPCODE': 2,
        'code': 0,
        'message': f"Message sent to {recipient}."
    })

def handle_file_tcp(sender_ip, sender_port, recipient, file, message):
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

def handle_disconnect_tcp(sender_ip, sender_port):
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

