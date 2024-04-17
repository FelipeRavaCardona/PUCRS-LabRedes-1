import json
import threading
from udp import udp_server as server

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
    sender = find_user_by_address(sender_ip, sender_port)
    print(f"Message sent from {sender['nickname']} to {recipient['nickname']}")
    message = json.dumps({
        'OPCODE': 5,
        'sender': sender['nickname'],
        'message': message_data['message']
    })
    server.send_data(message, (recipient['ip'], recipient['port']))
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
    sender = find_user_by_address(sender_ip, sender_port)
    print(f"File sent from {sender['nickname']} to {recipient['nickname']}")
    message = json.dumps({
        'OPCODE': 6,
        'sender': sender['nickname'],
        'file': message_data['file'],
        'message': message_data['message']
    })
    server.send_data(message, (recipient['ip'], recipient['port']))
    return json.dumps({
        'OPCODE': 2,
        'code': 0,
        'message': f"File sent to {message_data['recipient']}."
    })

def handle_disconnect(sender_ip, sender_port):
    sender = find_user_by_address(sender_ip, sender_port)
    if sender:
        users.remove(sender)
        print(f"{sender['nickname']} disconnected.")
        return json.dumps({
            'OPCODE': 4,
            'code': 0,
            'message': f"{sender['nickname']} disconnected."
        })
    return json.dumps({
        'OPCODE': 4,
        'code': 1,
        'message': 'User does not exist.'
    })

def handle_received():
    while True:
        data, address = server.message_queue.get()
        message = json.loads(data.decode('utf-8'))
        sender_ip, sender_port = address
        match message['OPCODE']:
            case 1:
                server.send_data(handle_registration(message['nickname'], sender_ip, sender_port), address)
            case 2:
                server.send_data(handle_message(sender_ip, sender_port, message), address)
            case 3:
                server.send_data(handle_file(sender_ip, sender_port, message), address)
            case 4:
                server.send_data(handle_disconnect(sender_ip, sender_port), address)
            case _:
                server.send_data(f"OPCODE '{message.OPCODE} is not known.", address)

receiving_thread = threading.Thread(target=server.receive_data)
receiving_thread.daemon = True
receiving_thread.start()

handle_received()
