import socket
import os
from threading import Thread
from tqdm import tqdm
BUFFER_SIZE = 1024

server_address = ('localhost', 5000)
clients = {}
thread_list = []

def receive_file(sock, address, filename, filesize):
    received = 0
    client_directory = f"server_files/{clients[address]}"
    if not os.path.exists(client_directory):
        os.makedirs(client_directory)
    with open(f"{client_directory}/{filename}", 'wb') as f:
        while received < filesize:
            data, _ = sock.recvfrom(BUFFER_SIZE)
            f.write(data)
            received += len(data)
        print(f"{filename} received from {address}")

    # reabrir o arquivo e enviar de volta para o cliente
    with open(f"{client_directory}/{filename}", 'rb') as f:
        with tqdm(total=filesize, desc=f'Sending {filename}', unit='B', unit_scale=True) as pbar:
            while True:
                data = f.read(BUFFER_SIZE)
                if not data:
                    break
                sock.sendto(data, address)
                pbar.update(len(data))
        print(f"{filename} sent")

if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(server_address)   # vincula com o endereço do servidor
        print(f"Server started on {server_address}")

        while True:
            data, address = sock.recvfrom(BUFFER_SIZE)
            if address not in clients:
                clients[address] = len(clients) + 1

            filename, filesize = data.decode('utf-8').split('|')
            filesize = int(filesize)

            sock.sendto('ack'.encode('utf-8'), address)
            thread_list.append(Thread(target=receive_file, args=(sock, address, filename, filesize)))
            
            receive_file(sock, address, filename, filesize)