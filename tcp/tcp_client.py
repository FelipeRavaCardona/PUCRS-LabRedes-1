import base64
import json
import random
import socket
import string
import threading
import os

user_nickname = None
BUFF_SIZE = 2048

# Função que desconecta um cliente do servidor.
def register(sock, nickname):
    global user_nickname

    # Cria mensagem com OPCODE 1 e envia o nickname do usuário.
    message = json.dumps({
        'OPCODE': 1,
        'nickname': nickname
    })

    #Envia a mensagem para o servidor
    sock.sendall(message.encode())

    #Guarda o nome do usuário registrado.
    user_nickname = nickname

# Função que envia uma mensagem para o servidor destinada a
# um outro usuário.
def send_message(sock, recipient, message):
 
    # Cria o objeto da mensagem
    message_json = json.dumps({
        'OPCODE': 2,
        'recipient': recipient,
        'message': message
    })

    #Envia para o servidor
    sock.sendall(message_json.encode())

    print("Mensagem enviada para o servidor!")
    print(message)



# Função que envia uma mensagem com um arquivo para o servidor 
# destinada a um outro usuário.
def send_file(sock, recipient, file_name, message):
    #Checa se o nome do arquivo está bem formatado no comando.
    if '"' in file_name or "'" in file_name:
        print("Erro nome do arquivo inválido")
        return
    
    # Lê o arquivo em modo binário e armazena em uma variável
    file_path = f"repo/{file_name}"
    try:
        with open(file_path, 'rb') as file:
            file_data = file.read()
    except FileNotFoundError:
        print("Erro: Arquivo não encontrado.")
        return

    # Codifica os dados do arquivo em base64 para enviar como string JSON
    file_data_encoded = base64.b64encode(file_data).decode('utf-8')

    # Cria a mensagem com o o arquivo, o destinatário, uma mensagem e o nome do arquivo
    data_to_send = {
        'OPCODE': 3,  
        'recipient': recipient,
        'file': file_data_encoded,
        'message': message,
        'file_name': file_name
    }

    # Converte o dicionário para JSON e envia para o servidor.
    message_json = json.dumps(data_to_send)
    sock.sendall(message_json.encode())

    print("Arquivo e mensagem enviados!")
    print(f"Destinatário: {recipient}")
    print(f"Arquivo: {file_name}")
    print(f"Mensagem: {message}")
    print()
    print()


# Função que desconecta um cliente do servidor.
def end_connection(sock):
    # Cria uma mensagem com o OPCODE 4
    message = json.dumps({
        'OPCODE': 4
    })

    # Envia a mensagem para o servidor.
    sock.sendall(message.encode())
    print()
    print()
    print("Pedido de desconexão enviado! ")
    

# Função que recebe inputs do usuário e envia mensagens para
# o servidor.
def send_messages(sock):
    while True:
        # Recebe o input e quebra em pedaços
        action = input()
        action_parts = action.split()

        # Decodifica os pedaços do comando.
        command = action_parts[0]
        
        # Trata o comando de registro
        if command == '/REG':
            # Verifica se o comando tem todos os atributos necessários.
            if len(action_parts) != 2:
                print('Missing nickname.')
                continue
            # Verifica se o usuário já não está registrado.
            if user_nickname:
                print(f'User already registered as{user_nickname}')
                continue
            # Chama a função que regitra o usuário
            register(sock, action_parts[1])
        
        # Trata o comando de enviar mensagem para outro usuario
        elif command == '/MSG':
            # Verifica se o usuário está registrado.
            if not user_nickname:
                print('User not registered.')
                continue

            # Verifica se o comando tem todos os atributos necessários.
            if len(action_parts) != 3:
                print('Command is missing parts.')
                continue

            # Chama a função de enviar mensagem para outro usuário.
            send_message(sock, action_parts[1], action_parts[2])
        
        # Trata o comando de enviar um arquivo para outro usuario
        elif command == '/FILE':
            # Verifica se o usuário está registrado.
            if not user_nickname:
                print('User not registered.')
                continue
            # Verifica se o comando tem todos os atributos necessários.
            if len(action_parts) != 4:
                print('Command is missing parts.')
                continue

            recipient = action_parts[1]
            file_name = action_parts[2]
            message = action_parts[3]

            # Chama a função de enviar arquivo com os atributos.
            send_file(sock, recipient, file_name, message)
        
        # Trata o comando de desconectar com o servidor.
        elif command == '/OFF':
            # Verifica se o usuário está registrado.
            if not user_nickname:
                print('User not registered.')
                continue

            # Chama a função para desconectar com o servidor.
            end_connection(sock)
            break
        
        # Trata comandos inválidos.
        else:
            print(f"'{command}' is not a known command.")


# Função que fica recebendo pacotes da rede e trata conforme
# o OPCODE da aplicação, assim chamando a função necessária.
def receive_messages(sock):
    while True:
        data = sock.recv(BUFF_SIZE)
        if not data:
            print("Servidor encerrou a conexão.")
            break
        message = json.loads(data.decode('utf-8'))
        # OPCODE 2 trata de recebimento e envio de mensagens.
        if message['OPCODE'] == 2:
            code = message.get('code')
            print()
            print()
            # Tratamento do code 0, onde o servidor confirma que a mensagem foi enviada.
            if code == 0:
                print(f"Mensagem do servidor: {message['message']}")
            elif code == 1:
            # Tratamento do code 1, onde o servidor não conseguiu enviar a mensagem para o destino.
                print(f"Mensagem do servidor: {message['message']}")
            else:
            # Tratamento do recebimento de uma mensagem de outro usuário
                print(f"Usuario: {message['sender']} enviou: {message['message']}")
        # OPCODE 3 trata de recebimento e envio de arquivos
        elif message['OPCODE'] == 3:
            code = message.get('code')
            # Tratamento do code 0, onde o servidor confirma que a mensagem foi enviada e do 
            # code 1, onde o servidor não conseguiu enviar a mensagem para o destino.
            if code == 0 or code == 1:
                print(f"Mensagem do servidor: {message['message']}")
            # Tratamento do recebimento de um arquivo de outro usuário.
            else:
                # Decodifica os dados do arquivo
                file_data = base64.b64decode(message['file'])
                file_name = message['file_name']
                user_message = message['message']
                sender = message['sender']
                # Cria o diretório 'recebidas' se não existir
                os.makedirs('recebidas', exist_ok=True)
                
                # Salva o arquivo na pasta 'recebidas'
                file_path = os.path.join('recebidas', file_name)
                with open(file_path, 'wb') as file:
                    file.write(file_data)
                print()
                print()
                print(f"Arquivo {file_name} recebido e salvo em 'recebidas'.")
                print(f"Usuario: {sender} enviou: {user_message}")
        # OPCODE 4 trata da operação de desconexão do cliente.
        elif message['OPCODE'] == 4:
            code = message.get('code')
            # Tratamento do code 0, onde o servidor informa que ocorreu um erro ao desconectar e
            # do code 1, onde o servidor não conseguiu encontrar o usuário tentando desconectar.
            if code == 0 or code == 1:
                print(f"Mensagem do servidor: {message['message']}")
            # Tratamento do caso onde a desconexão foi efetuada com sucesso.
            else:
                user_nickname = None
                print("Disconected from the server.")
                break
        else:
            print(f"Recebido do servidor: {message}")

# Função que inicia o cliente TCP. Esta função é responsável por iniciar a thread que recebe
# e envia mensagens utilizando o mesmo socket de maneira simultânea.
def start_client(server_host, server_port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((server_host, server_port))

        # Criando e iniciando thread de envio
        send_thread = threading.Thread(target=send_messages, args=(s,))
        send_thread.start()
        
        # Criando e iniciando thread de recebimento
        receive_thread = threading.Thread(target=receive_messages, args=(s,))
        receive_thread.start()
        
        # Aguardar as threads terminarem
        send_thread.join()
        receive_thread.join()

# Chama a função de inicializar o cliente TCP
if __name__ == "__main__":
    start_client('localhost', 3000)