import socket
import os
from tkinter.filedialog import askopenfilename
from tqdm import tqdm

BUFFER_SIZE = 1024

server_address = ('localhost', 5000)
client_address = ('localhost', 0)

def send_file(sock, filename):
    filesize = os.path.getsize(filename)    # tamanho do arquivo
    print(f"o tamanho do arquivo enviado para o servidor e {filesize}")
    data = f"{os.path.basename(filename)}|{filesize}"
    sock.sendto(data.encode('utf-8'), server_address)   # codifica em bytes e envia para o servidor
    ack, _ = sock.recvfrom(BUFFER_SIZE)

    with open(filename, 'rb') as f:
        with tqdm(total=filesize, desc=f'Sending {filename}', unit='B', unit_scale=True) as pbar:
            while True:
                data = f.read(BUFFER_SIZE)  # lê 1024 bytes por vez
                if not data:
                    break
                sock.sendto(data, server_address)   # envia os bytes
                pbar.update(len(data))
        print(f"{filename} sent")
        f.close()
    
    return filesize

def receive_file(sock, filename, filesize):
    client_directory = f"client_files/received"

    if not os.path.exists(client_directory):
        os.makedirs(client_directory)
    
    with open(f"{client_directory}/{filename}", 'wb') as f:
        received = 0
        while received < filesize:
            data, _ = sock.recvfrom(BUFFER_SIZE)
            f.write(data)
            received += len(data)
        print(f"{filename} received from server")
        f.close()


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(client_address)   # vincula com o endereço de destino
        print(f"Client started on {sock.getsockname()}")

        filename = askopenfilename()    # seleciona o arquivo a ser enviado

        filesize = send_file(sock, filename)   # envia o arquivo
        # TODO: devemos pedir para o servidor o novo filesize, ou usar o mesmo?
        print(f"o tamanho do arquivo que o client espera receber e {filesize}")
        receive_file(sock, os.path.basename(filename), filesize)

if __name__ == '__main__':
    main()
