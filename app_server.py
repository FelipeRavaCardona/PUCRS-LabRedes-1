import json
import threading
from udp import udp_server as server

#Lista de usuários comunicando com o servidor
users = []

def find_user_by_address(ip, port):
    # Procura na lista de usuários por um usuário com um ip e porta específicos
    # retorna None caso não encontre
    global users
    for user in users:
        if user['ip'] == ip and user['port'] == port:
            return user
    return None

def find_user_by_nickname(nickname):
    # Procura na lista de usuários por um usuário com um nickname específico,
    # Retorna None caso não encontre
    for user in users:
        if user['nickname'] == nickname:
            return user
    return None

def handle_registration(nickname, sender_ip, sender_port):
    # Cadastra um usuário na aplicação
    # Retorna code 1 caso ja exista um usuário com o nickname escolhido
    # Retorna code 0 caso o cadastro seja feito com sucesso
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
    # Recebe a mensagem de um usuário e envia para outro
    # Retorna code 1 para o usuário que enviou a mensagem caso a mensagem não possa ser entregue ao remetente
    # Envia com code 0 para o remetente caso tudo dê certo 
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
    # Recebe a mensagem e um arquivo de um usuário e envia para outro
    # Retorna code 1 para o usuário que enviou a mensagem caso a mensagem e o arquivo não possam ser entregues ao remetente
    # Envia com code 0 para o remetente caso tudo dê certo
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
    # Lida com a mensagem avisando do encerramento da conexão
    # Retorna code 0 caso o usuário seja desconectado com sucesso
    # Retorna code 1 caso o usuário não exista(não esteja mais conectado) na aplicação
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
    # Lida com todas mensagens que chegam
    while True:
        data, address = server.message_queue.get()
        message = json.loads(data.decode('utf-8'))
        sender_ip, sender_port = address
        match message['OPCODE']:
            case 1:
                # OPCODE 1, registrar usuário
                server.send_data(handle_registration(message['nickname'], sender_ip, sender_port), address)
            case 2:
                # OPCODE 2, enviar mensagem de um usuário para outro
                server.send_data(handle_message(sender_ip, sender_port, message), address)
            case 3:
                # OPCODE 3, enviar mensagem e arquivo de um usuário para outro
                server.send_data(handle_file(sender_ip, sender_port, message), address)
            case 4:
                # OPCODE 4, encerramento de comunicação
                server.send_data(handle_disconnect(sender_ip, sender_port), address)
            case _:
                # OPCODE desconhecido
                server.send_data(f"OPCODE '{message.OPCODE} is not known.", address)

# Inicia thread the receber mensagens do UDP
receiving_thread = threading.Thread(target=server.receive_data)
receiving_thread.daemon = True
receiving_thread.start()

handle_received()
