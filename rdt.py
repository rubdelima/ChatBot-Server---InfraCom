import socket
import struct
from threading import Thread
import time

class RDT():
    def __init__(self, tipo=None):
        # cria o socket UDP
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print(self.sock)
        # define o IP e a porta do servidor
        self.server_address = ('localhost', 5000)
        if tipo == 'server':
            # faz o bind do socket com o IP e a porta do servidor
            self.sock.bind(self.server_address)
        self.conections = {}
        self.estado = None
    
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
    
    def create_pkt(self, ack:int, seq:int, msg:str)->bytes:
        tamanho_mensagem = len(msg.encode())
        # Empacotar a estrutura com o tamanho da mensagem no início
        chcs = self.checksum(msg)
        pacote = struct.pack('>i3i1008s', tamanho_mensagem, ack, seq, chcs, msg.encode())
        return pacote
    
    def unpack_pkt(self, packet)->dict:
        # Desempacotar o pacote
        tamanho_mensagem, num1, num2, num3, mensagem = struct.unpack('>i3i1008s', packet)
        # Decodificar a string de volta para o formato de string original
        mensagem = mensagem[:tamanho_mensagem].decode()
        dicionario = {'ack' : num1, 'seq' : num2, 'checksum' : num3, 'mensagem' : mensagem, 'mensagem_size' : tamanho_mensagem}
        return dicionario
    
    def enviar_pacote(self, pacote, destino):
        while  True: # do while loop
            self.sock.sendto(pacote, destino) # envia o pacote
            time.sleep(5) #aguarda 5 segundos
            if ("waiting" not in self.estado): # se o estado nao for mais de esperar
                break #encerra
            
    
    def emitir(self, mensagem, destino=('127.0.0.1', 5000)):
        # Bloco 1 - Enviar ACK
        if destino not in self.conections.values(): # Se o destino não está nas conexões
            self.conections[destino] = {'ack' : 0, 'seq' : 0, 'expec_seq' : 0} # ponto na minha lista de conexões
        
        self.conections[destino]['expec_seq'] += 1 # Espero receber +1 na sequência
        
        ack_pck = self.create_pkt(
            ack = self.conections[destino]['ack'],
            seq = self.conections[destino]['seq'],
            msg= "ACK"
        )
        
        self.estado = "waiting for ack confirmation"
        
        enviar = Thread(target=self.enviar_pacote, args = (ack_pck, destino))
        enviar.start()
        
        # Bloco 2 - Esperar confirmação do ACK
        
        while True:
            data, rcv_address = self.sock.recvfrom(1024) # recebo um pacote
            data = self.unpack_pkt(data) # desempacoto o pacote
            # variáveis de confirmação
            v1 = (rcv_address == destino) # se for uma mensagem do destino que eu espero
            v2 = (self.checksum(data['mensagem']) == data['checksum']) # se o checksum estiver correto (não está corrompido)
            v3 = self.conections[destino]['expec_seq'] == data['ack'] # se o ack for para a sequência que eu espero
            if v1 and v2 and v3:
                self.estado = 'sending message'
                #enviar.join()
                break
        
        # Bloco 3 - Atualizar os dados e enviar a mensagem
         
        self.conections[destino]['seq'] = data['ack']
        self.conections[destino]['ack'] = data['seq']
        self.conections[destino]['expec_seq'] += len(mensagem)
        
        msg_pck  = self.create_pkt(
            ack = self.conections[destino]['ack'],
            seq = self.conections[destino]['seq'],
            msg= mensagem
        )
        
        self.estado = "waiting for message confirmation"
        
        enviar = Thread(target=self.enviar_pacote, args = (msg_pck, destino))
        enviar.start()
        
        # Bloco 4 - Esperar confirmaçao do recebimento da Mensagem
        
        while True:
            data, rcv_address = self.sock.recvfrom(1024) # recebo um pacote
            data = self.unpack_pkt(data) # desempacoto o pacote
            # variáveis de confirmação
            v1 = (rcv_address == destino) # se for uma mensagem do destino que eu espero
            v2 = (self.checksum(data['mensagem']) == data['checksum']) # se o checksum estiver correto (não está corrompido)
            v3 = self.conections[destino]['expec_seq'] == data['ack'] # se o ack for para a sequência que eu espero
            if v1 and v2 and v3:
                self.estado = 'finished'
                #enviar.join()
                break
        
        self.conections[destino]['seq'] = data['ack']
        self.conections[destino]['ack'] = data['seq']
                
    
    def receber(self):
        # Bloco 1 - Receber ACK e reenviar
        data, rcv_address = self.sock.recvfrom(1024) # recebo um pacote
        if rcv_address not in self.conections.keys(): # se não tiver na tabela de conexões
            data = self.unpack_pkt(data)
            self.conections[rcv_address] = {'ack' : data['seq'], 'seq' : data['ack'], 'expec_seq' : data['ack']}
        
        self.conections[rcv_address]['ack'] += 1
        
        ack_resp_pck = self.create_pkt(
            ack = self.conections[rcv_address]['ack'],
            seq = self.conections[rcv_address]['seq'],
            msg= "1"
        )
        
        self.estado = "waiting for message"
        
        enviar = Thread(target=self.enviar_pacote, args = (ack_resp_pck, rcv_address))
        enviar.start()
        
        # Bloco 2 - Receber mensagem e confirmar
        
        while True:
            data, rcv_address_n = self.sock.recvfrom(1024) # recebo um pacote
            data = self.unpack_pkt(data) # desempacoto o pacote
            # variáveis de confirmação
            v1 = (rcv_address == rcv_address_n) # se for uma mensagem do destino que eu espero
            v2 = (self.checksum(data['mensagem']) == data['checksum']) # se o checksum estiver correto (não está corrompido)
            v3 = self.conections[rcv_address]['expec_seq'] == data['ack'] # se o ack for para a sequência que eu espero
            if v1 and v2 and v3:
                self.estado = 'finished'
                #enviar.join()
                break
        
        self.conections[rcv_address]['seq'] = data['ack']
        self.conections[rcv_address]['ack'] = data['seq'] +  len(data['mensagem'])
        self.conections[rcv_address]['expec_seq'] += len(data['mensagem'])
        
        msg_resp_pck = self.create_pkt(
            ack = self.conections[rcv_address]['ack'],
            seq = self.conections[rcv_address]['seq'],
            msg= "2"
        )
        self.enviar_pacote(msg_resp_pck, rcv_address)      
        
        return data['mensagem'], rcv_address