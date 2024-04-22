import json
import socket
import threading

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
            response = handle_received_tcp(data, conn, addr[0], addr[1])
            conn.sendall(response.encode())

    finally:
        conn.close()




def handle_received_tcp(data, conn, sender_ip, sender_port):
    try:
        message = json.loads(data.decode('utf-8'))
    except json.JSONDecodeError as e:
        return f"Error decoding JSON: {str(e)}"
    except UnicodeDecodeError as e:
        return f"Error decoding UTF-8 data: {str(e)}"

    opcode = message.get('OPCODE')
    if opcode == 1:
        nickname = message.get('nickname')
        if nickname is None:
            return "Nickname is required for OPCODE 1"
        return handle_registration_tcp(nickname, conn, sender_ip, sender_port)
    elif opcode == 2:
        print("oba---------")
        return handle_message_tcp(sender_ip, sender_port, message)
    elif opcode == 3:
        recipient = message.get('recipient')
        file = message.get('file')
        msg = message.get('message')
        if None in (recipient, file, msg):
            return "Recipient, file, and message are required for OPCODE 3"
        return handle_file_tcp(sender_ip, sender_port, message)
    elif opcode == 4:
        return handle_disconnect_tcp(sender_ip, sender_port)
    else:
        return f"OPCODE '{opcode}' is not known."



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
    sender = find_user_by_address(sender_ip, sender_port)
    message = json.dumps({
        'OPCODE': 2,
        'sender': sender['nickname'],
        'message': message_data['message']
    })

    recipient['connection'].sendall(message.encode())
  
    return json.dumps({
        'OPCODE': 2,
        'code': 0,
        'message': f"Message sent to {recipient['nickname']}."
    })

def handle_file_tcp(sender_ip, sender_port, message_data):
    print("recipient: "  + message_data['recipient'])
    print("message:" + message_data['message'])
    recipient = find_user_by_nickname(message_data['recipient'])
    if not recipient:
        return json.dumps({
            'OPCODE': 3,
            'code': 1,
            'message': f"{message_data['recipient']} is not online."
        })
    
    sender = find_user_by_address(sender_ip, sender_port)
    message = json.dumps({
        'OPCODE': 3,
        'sender': sender['nickname'],
        'message': message_data['message'],
        'file' : "file"
    })
    recipient['connection'].sendall(message.encode())

    return json.dumps({
        'OPCODE': 3,
        'code': 0,
        'message': f"File sent to {recipient['nickname']}."
    })

def handle_disconnect_tcp(sender_ip, sender_port):
    sender = find_user_by_address(sender_ip, sender_port)
    if sender:
        sender['connection'].close()
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

start_server_tcp('localhost', 3000)