import socket
import os
from tkinter.filedialog import askopenfilename
from tqdm import tqdm
import time
from common import *


BUFFER_SIZE = 1024

server_address = ('localhost', 5000)
client_address = ('localhost', 0)

def send_file(sock, filename):
    # Obtém o tamanho do arquivo
    filesize = os.path.getsize(filename)
    data = f"{os.path.basename(filename)}|{filesize}"

    # Codifica os dados e envia para o servidor
    sock.sendto(data.encode('utf-8'), server_address)

    # Recebe uma mensagem de confirmação (ack) do servidor
    ack, _ = sock.recvfrom(BUFFER_SIZE)

    # Número de sequência inicial
    sequence_number = 0

    with open(filename, 'rb') as f:
        with tqdm(total=filesize, desc=f'Sending {filename}', unit='B', unit_scale=True) as pbar:
            while True:
                # Lê 1024 bytes por vez
                data = f.read(BUFFER_SIZE)
                if not data:
                    break
                
                data = create_header(data.decode(), sequence_number);

                # Envia os bytes para o servidor
                print("Enviando para o servidor")
                sock.sendto(data, server_address)

                # Atualiza a barra de progresso com o número de bytes enviados
                pbar.update(len(data))

                # Inicia o temporizador
                start_time = time.time()

                # Tempo limite para retransmissão (em segundos)
                timeout = 1

                while True:
                    # Verifica se o temporizador expirou
                    if time.time() - start_time > timeout:
                        # Retransmite os dados
                        print("ACK nao recebido ou NACK recebido. Reenviando para o servidor")
                        sock.sendto(data, server_address)

                        # Reinicia o temporizador
                        start_time = time.time()

                    # Tenta receber a confirmação do servidor
                    try:
                        # Configura o socket para não bloquear a espera de dados
                        sock.settimeout(0.1)

                        # Recebe dados do servidor
                        ack_data, server = sock.recvfrom(BUFFER_SIZE)
                        ack = rcv_ack(ack_data,~ sequence_number)

                        # Verifica se a confirmação é para o pacote enviado
                        if ack:
                            print(f'ack {sequence_number} recebido')
                            sequence_number = 1 - sequence_number
                            break
                    except socket.timeout:
                        # Continua o loop interno se não receber dados do servidor
                        continue

        print(f"{filename} sent")
        f.close()

    return filesize


def receive_file(sock, filename, filesize):
    client_directory = f"client_files/received"
    
    # Caso o diretório não exista, será criado
    if not os.path.exists(client_directory):
        os.makedirs(client_directory)

    with open(f"{client_directory}/{filename}", 'wb') as f:
        # variável para comparar a quantidade de bytes recebidos
        received = 0
        while received < filesize:
            # Recebe os dados do servidor
            data, _ = sock.recvfrom(BUFFER_SIZE)
            # Escreve os dados no arquivo
            f.write(data)
            # Incrementa o número de bytes recebidos
            received += len(data)
        print(f"{filename} received from server")
        f.close()


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        # Vincula o socket com o endereço de destino
        sock.bind(client_address)
        print(f"Client started on {sock.getsockname()}")

        # abre uma janela de para selecionar o arquivo a ser enviado
        filename = askopenfilename()

        # envia o arquivo para o servidor e obtém o tamanho do arquivo
        filesize = send_file(sock, filename)
        
        # recebe o arquivo do servidor
        receive_file(sock, os.path.basename(filename), filesize)


if __name__ == '__main__':
    main()
