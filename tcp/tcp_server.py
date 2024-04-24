import json
import socket
import threading

server_socket = None
users = []


# Função que, dado o ip e porta, encontra o usuário na lista de usuários conectados
def find_user_by_address(ip, port):
    global users
    for user in users:
        if user['ip'] == ip and user['port'] == port:
            return user
    return None

# Função que, dado o nickname, encontra o usuário na lista de usuários conectados no servidor
def find_user_by_nickname(nickname):
    for user in users:
        if user['nickname'] == nickname:
            return user
    return None


# Função que trata o registro de um usuário no servidor.
def handle_registration_tcp(nickname, conn,sender_ip, sender_port):

    # Se encontrar um usuário com o mesmo nickname, retorna code 1.
    if find_user_by_nickname(nickname):
        return {
            'OPCODE': 1,
            'code': 1,
            'message': 'Nickname already used.'
        }

    # Adiciona o usuário na lista de usuários conectados no servidor
    users.append({
        'nickname': nickname,
        'ip': sender_ip,
        'port': sender_port,
        "connection" : conn
    })
    print()
    print()
    print(f"{nickname}({sender_ip}:{sender_port}) connected.")

    # Retorna uma mensagem com code 0 de sucesso no registro.
    return {
        'OPCODE': 1,
        'code': 0,
        'message': 'User registered successfully.'
    }

# Trata da funcionalidade de enviar mensagens para outro usuário conectado ao servidor.
def handle_message_tcp(sender_ip, sender_port, message_data):
   
    # Verifica se existe um usuário com o nickname do destinatário no atributo "recipient" da mensagem
    # Caso não, envia uma mensagem de erro com code 1.
    recipient = find_user_by_nickname(message_data['recipient'])
    if not recipient:
        return {
            'OPCODE': 2,
            'code': 1,
            'message': f"{recipient} is not online."
        }

    # Acha o nome do usuário que enviou a mensagem e envia como 'sender' em um atributo
    # da mensagem queserá enviada para o destinatário
    sender = find_user_by_address(sender_ip, sender_port)
    message = json.dumps({
        'OPCODE': 2,
        'sender': sender['nickname'],
        'message': message_data['message']
    })

    # Utiliza o objeto de conexão guardado junto ao objeto do usuário na lista de usuário conectados 
    # para enviar a mensagem ao destinatário.
    recipient['connection'].sendall(message.encode())
  
    # Retorna uma confirmação para quem enviou a mensagem.
    return {
        'OPCODE': 2,
        'code': 0,
        'message': f"Message sent to {recipient['nickname']}."
    }


# Função que trata o envio de arquivos para um outro usuário conectado ao servidor
def handle_file_tcp(sender_ip, sender_port, message_data):
    # Verifica se todos os campos estão presentes na mensagem
    recipient = message_data.get('recipient')
    file = message_data.get('file')
    msg = message_data.get('message')
    if None in (recipient, file, msg):
        return "Recipient, file, and message are required for OPCODE 3"

    # Encontra o recipiente e, caso este não esteja na lista de usuários conectados,
    # retorna ao usuário que enviou um code 1.
    recipient = find_user_by_nickname(message_data['recipient'])
    if not recipient:
        return {
            'OPCODE': 3,
            'code': 1,
            'message': f"{message_data['recipient']} is not online."
        }
    
    # Encontra o nickname do usuário que enviou o arquivo e adiciona a um atributo da 
    # mensagem
    sender = find_user_by_address(sender_ip, sender_port)

    # Cria o objeto da mensagem e utiliza o objeto de conexão do usuário destinatário
    # para enviar a mensagem.
    message = json.dumps({
        'OPCODE': 3,
        'sender': sender['nickname'],
        'message': message_data['message'],
        'file' : message_data['file'],
        'file_name': message_data['file_name']
    })
    recipient['connection'].sendall(message.encode())

    print()
    print()
    print("File sent from: "  + message_data['recipient'] + " To user: " + sender['nickname'])

    # Retorna uma mensagem de confirmação para o usuário que enviou o arquivo com code 0.
    return {
        'OPCODE': 3,
        'code': 0,
        'message': f"File sent to {recipient['nickname']}."
    }

# Trata a desconexão de um usuário com o servidor.
def handle_disconnect_tcp(sender_ip, sender_port):

    # Encontra o usuário que está tentando se desconectar do servidor 
    # na lista de usuários conectados.
    sender = find_user_by_address(sender_ip, sender_port)
    if sender:
        try:
            # Remove da lista de usuários
            users.remove(sender)

            # Monta a mensagem de confirmação de desconexão para o usuário.
            response = {
                'OPCODE': 4,
                'code': 2,
                'message': f"{sender['nickname']} successfully disconnected."
            }
            
            # Envia a mensagem de desconexão utilizando o objeto de conexão do usuário
            # e fecha esta conexão.
            sender['connection'].sendall(json.dumps(response).encode())
            sender['connection'].close()
            return response

        # Caso ocorra um erro na desconexão, envia uma mensagem para o usuário com code 0.
        except Exception as e:

            return {
                'OPCODE': 4,
                'code': 0,
                'message': f"An error occured when disconecting user {sender['nickname']}."
            }
    # Se o usuário não for encontrado na lista, retorna uma mensagem com code 1
    return {
        'OPCODE': 4,
        'code': 1,
        'message': 'User does not exist.'
    }

# Trata o recebimento de dados por um cliente no servidor.
def handle_received_tcp(data, conn, sender_ip, sender_port):
    # Tenta decodificar a mensagem com JSON, caso não tenha sucesso retorna um
    # erro para o cliente.
    try:
        message = json.loads(data.decode('utf-8'))
    except json.JSONDecodeError as e:
        return f"Error decoding JSON: {str(e)}"
    except UnicodeDecodeError as e:
        return f"Error decoding UTF-8 data: {str(e)}"

    # Captura o OPCODE do JSON enviado e trata conforme a ocasião.
    opcode = message.get('OPCODE')

    # OPCODE 1 Trata o caso de registro do usuário
    if opcode == 1:
        # Pega o nickname da mensagem e chama a função que trata do registro de usuários
        nickname = message.get('nickname')
        if nickname is None:
            return "Nickname is required for OPCODE 1"
        return json.dumps(handle_registration_tcp(nickname, conn, sender_ip, sender_port))

    # OPCODE 2 Trata o caso onde o usuário envia uma mensagem para outro usuário
    elif opcode == 2:
        # Chama a função que trata o envio de mensagens para outro usuário
        return json.dumps(handle_message_tcp(sender_ip, sender_port, message))

    # OPCODE 3 Trata o caso do envio de arquivos entre usuários conectados.
    elif opcode == 3:
        
        return json.dumps(handle_file_tcp(sender_ip, sender_port, message))

    # OPCODE 4 trata da desconexão de um usuário do servidor.
    elif opcode == 4:
        # Chama a função que trata da desconexão do usuário com o servidor
        response = handle_disconnect_tcp(sender_ip, sender_port)

        # Trata o caso onde a conexão foi fechada com sucesso, logo nada mais pode ser enviado 
        # para o cliente.
        if response['OPCODE'] == 4 and response['code'] == 2:
            print(f"Message from server:{response['message']}")
            return None
        
        # Retorna a resposta em formato JSON.
        return json.dumps(response)

    # Trata o caso onde o OPCODE é desconhecido pelo servidor.
    else:
        return f"OPCODE '{opcode}' is not known."

#Inicializa o tratamento da conexão do servidor com o cliente 
def handle_client(conn, addr):
    print()
    print()
    print(f"Conectado por {addr}")
    try:
        while True:
            #Recebe 2048 bytes de dados
            data = conn.recv(2048)

            if not data:
                break

            # Chama a função de tratamento dos dados recebidos, a conexão utilizada
            # e o ip e a porta do cliente que enviou os dados
            response = handle_received_tcp(data, conn, addr[0], addr[1])

            # A resposta None corresponde a uma resposta de desconexão do servidor com o cliente.
            if response == None:
                break

            # Transforma a resposta recebida pelo handler em bytes e envia para o cliente que enviou 
            # a requisição. Geralmente utilizada para confirmar ou não que a operação foi realizada com
            # sucesso pelo servidor.
            conn.sendall(response.encode())

    finally:
        conn.close()


# Inicia o servidor TCP dado o host e a porta.
def start_server_tcp(host, port):
    # Inicializa o servidor no 'host' e 'port'.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"TCP Server listening on {host}:{port}.")

        # Aceita conexão de diversos clientes que desejam se comunicar e a cada conexão
        # inicia uma nova thread que tratará das requisições e envios desse cliente.
        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()

# Chama função que inicia o servidor TCP
start_server_tcp('localhost', 3000)
