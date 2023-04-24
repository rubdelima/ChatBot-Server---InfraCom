import socket
import os
from tqdm import tqdm
from threading import Thread
from time import time

class RDT():
    def __init__(self, tipo):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = ('localhost', 5000)
        self.client_address = ('localhost', 0) 
        self.BUFFER_SIZE = 1024
        self.tipo = tipo
        if tipo == 'client':
            self.sock.bind(self.client_address)
        else:
            self.clients ={}
            self.sock.bind(self.server_address)
            print(f"Server started on {self.server_address}")
        self.state = 0

            
    def receive_file(self, filename, filesize, address=None) ->str:
        if self.tipo == 'client':
            client_directory = f"client_files/received"
        else:
            client_directory = f"server_files/received"

        # Caso o diretório não exista, será criado
        if not os.path.exists(client_directory):
            os.makedirs(client_directory)

        with open(f"{client_directory}/{filename}", 'wb') as f:
            # variável para comparar a quantidade de bytes recebidos
            received = 0
            while received < filesize:
                # Recebe os dados do servidor
                data, env = self.sock.recvfrom(self.BUFFER_SIZE)
                # Escreve os dados no arquivo
                data = self.unpack(data)
                if data['checksum'] == self.checksum(data['payload']):
                    f.write(data['payload'])
                    received += len(data['payload'])
                    data['seq'] = 1- data['seq']
                    data = str(data)
                    self.sock.sendto(data.encode(), env)
                # Incrementa o número de bytes recebidos
                
            print(f"{filename} received from server")
            f.close()
        return client_directory
            
    
    def send_file(self, filename, address=None) -> int:
        # Obtém o tamanho do arquivo
        filesize = os.path.getsize(filename)
        if self.tipo == "client":
            data = f"{os.path.basename(filename)}|{filesize}"
            # Codifica os dados e envia para o servidor
            self.sock.sendto(data.encode('utf-8'), self.server_address)
            # Recebe uma mensagem de confirmação (ack) do servidor
            ack, _ = self.sock.recvfrom(self.BUFFER_SIZE)

        if address == None: address =self.server_address
        with open(filename, 'rb') as f:
            with tqdm(total=filesize, desc=f'Sending {filename}', unit='B', unit_scale=True) as pbar:
                while True:
                    # Lê 1024 bytes por vez
                    data = f.read(self.BUFFER_SIZE-800)
                    if not data:
                        break
                    # Envia os bytes para o servidor
                    n_data = self.pack(data)
                    print(f'{len(data)}=original,  cabecalho={len(n_data)}')
                    self.sock.sendto(n_data, address)
                    self.wait_for_ack()
                    # Atualiza a barra de progresso com o número de bytes enviados
                    pbar.update(len(data))
                    
            print(f"{filename} sent")
            f.close()

        return filesize
    
    def wait_for_ack(self):
        while True:
            data, _ = self.sock.recvfrom(self.BUFFER_SIZE)
            data = self.unpack(data)
            if data['seq'] != self.state:
                self.state = 1-self.state
                break
        
    
    def checksum(self, data):
        sum = 0
        data = str(data)
        for i in range(0,len(data),2):
            if i + 1 >= len(data):
                sum += ord(data[i]) & 0xFF
            else:
                w = ((ord(data[i]) << 8) & 0xFF00) + (ord(data[i+1]) & 0xFF)
                sum += w

        while (sum >> 16) > 0:
            sum = (sum & 0xFFFF) + (sum >> 16)

        sum = ~sum

        return sum & 0xFFFF


    def pack(self, data):
        chcksum = self.checksum(data)
        return str({
            'seq': self.state,
            'checksum': chcksum,
            'payload' : data
        }).encode()
    
    def unpack(self, data) -> dict:
        data = eval(data.decode())
        seq_num = data['seq']
        checksum = data['checksum']
        print(checksum)
        payload = data['payload']
        return data
    
        
    def close(self):
        self.sock.close()


