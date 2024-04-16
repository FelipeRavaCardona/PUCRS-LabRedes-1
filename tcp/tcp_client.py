import socket
import threading

def send_messages(sock):
    while True:
        message = input("Digite sua mensagem: ")
        sock.sendall(message.encode())

def receive_messages(sock):
    while True:
        data = sock.recv(1024)
        if not data:
            print("Servidor encerrou a conexão.")
            break
        print(f"Recebido do servidor: {data.decode()}")

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

if __name__ == "__main__":
    start_client('localhost', 3000)
