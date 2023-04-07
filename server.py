import socket
import os
from threading import Thread
from tqdm import tqdm

# Define o tamanho do buffer utilizado na transferência de dados
BUFFER_SIZE = 1024

# Define o endereço do servidor
server_address = ('localhost', 5000)

# Cria um dicionário para armazenar a identificação de cada cliente conectado
clients = {}

# Cria uma lista para armazenar as threads criada (não utilizado na primeira entrega)
thread_list = []

# Função que recebe um arquivo enviado por um cliente e o salva no diretório do cliente correspondente
def receive_file(sock, address, filename, filesize):
    # variavel para comparar a quantidade de bits recebidos
    received = 0
    
    client_directory = f"server_files/{clients[address]}"
    
    # Cria o diretório caso ainda não exista
    if not os.path.exists(client_directory):
        os.makedirs(client_directory)
    with open(f"{client_directory}/{filename}", 'wb') as f:
        while received < filesize:
            data, _ = sock.recvfrom(BUFFER_SIZE)
            f.write(data)
            received += len(data)
        print(f"{filename} received from {address}")
        f.close()

    return client_directory


# Função que envia o arquivo de volta para o cliente
def send_file(sock, filename, address):
    filesize = os.path.getsize(filename)

    with open(filename, 'rb') as f:
        with tqdm(total=filesize, desc=f'Sending {os.path.basename(filename)}', unit='B', unit_scale=True) as pbar:
            while True:
                data = f.read(BUFFER_SIZE)
                if not data:
                    break

                sock.sendto(data, address)
                pbar.update(len(data))

        print(f"{os.path.basename(filename)} sent")
        f.close()


if __name__ == '__main__':
    # Cria um socket UDP
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        # Vincula o socket com o endereço do servidor
        sock.bind(server_address)
        print(f"Server started on {server_address}")

        # Entra em um loop para receber arquivos de clientes
        while True:
            # Recebe dados enviados por um cliente e o endereço do cliente que enviou os dados
            data, address = sock.recvfrom(BUFFER_SIZE)

            # Verifica se o cliente que enviou os dados já está registrado no dicionário clients
            if address not in clients:
                clients[address] = len(clients) + 1

            # Extrai o nome do arquivo e o tamanho do arquivo dos dados recebidos
            filename, filesize = data.decode('utf-8').split('|')
            filesize = int(filesize)
            print(f"o tamanho do arquivo que o client vai enviar e {filesize}")

            # Envia uma mensagem de confirmação ('ack') para o cliente
            sock.sendto('ack'.encode('utf-8'), address)

            # Cria uma nova thread para receber o arquivo do cliente e adiciona a thread na lista (não usado nessa entrega)
            thread_list.append(Thread(target=receive_file, args=(sock, address, filename, filesize)))

            # Recebe o arquivo enviado pelo cliente e armazena o caminho do arquivo no diretório do cliente
            directory = receive_file(sock, address, filename, filesize)
            filename = f"{directory}/{filename}"

            # Envia o arquivo de volta para o cliente
            send_file(sock, filename, address)
