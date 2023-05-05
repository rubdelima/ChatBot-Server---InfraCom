import socket
import struct
from threading import Thread
import time

class RDT():
    def __init__(self, sock):
        self.sock = sock
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

    def wait_for_response(self, endereco)->dict:
        while True:
            data, rcv_address = self.sock.recvfrom(1024) # recebo um pacote
            data = self.unpack_pkt(data) # desempacoto o pacote
            #print(f"Pacote recebido de {rcv_address}: ACK: {data['ack']} SEQ: {data['seq']}")
            # variáveis de confirmação
            v1 = (rcv_address == endereco) # se for uma mensagem do destino que eu espero
            v2 = (self.checksum(data['mensagem']) == data['checksum']) # se o checksum estiver correto (não está corrompido)
            v3 = self.conections[endereco]['next_seq'] == data['ack'] # se o ack for para a sequência que eu espero
            if v1 and v2 and v3:
                return data
            
    def enviar(self, msg, destino):
        msg = str(msg)
        if destino not in self.conections.keys(): # Se o destino não está nas conexões
            self.conections[destino] = {
                'snd_base' : 0, 'next_seq' : 0, 'rcv_base' : 0
                } # ponto na minha lista de conexões
        
        # Bloco 1 - Enviar ACK
        
        ack_pck = self.create_pkt(
            ack = self.conections[destino]['rcv_base'],
            seq = self.conections[destino]['snd_base'],
            msg= "ACK"
        )
        
        self.sock.sendto(ack_pck,destino) # envio o pacote
        
        self.conections[destino]['next_seq'] += 1
        
        # Bloco 2 - Esperar Confirmaçao
        data = self.wait_for_response(destino)
        self.conections[destino]['snd_base'] = data['ack']
        self.conections[destino]['rcv_base'] += 1
        
        # Bloco 3 - Enviar Mensagem
        msg_pck  = self.create_pkt(
            ack = self.conections[destino]['rcv_base'],
            seq = self.conections[destino]['snd_base'],
            msg= msg
        )
        self.sock.sendto(msg_pck, destino)
        self.conections[destino]['next_seq'] += len(msg)
        
        # Bloco 4 - Aguardar Confirmação e Encerrar
        data = self.wait_for_response(destino)
        self.conections[destino]['snd_base'] = data['ack']
        self.conections[destino]['rcv_base'] += 1
        
        last_pck  = self.create_pkt(
            ack = self.conections[destino]['rcv_base'],
            seq = self.conections[destino]['snd_base'],
            msg= msg
        )
    
        self.sock.sendto(last_pck, destino)
        '''
        print('send_base: {}, next_seq: {}, rcv_base: {}'.format(
                *self.conections[destino].values()))
        '''
    
    def receber(self):
        # Bloco 1 - Receber o ACK e enviar confirmação
        while True:
            data, rcv_address = self.sock.recvfrom(1024) # recebo um pacote
            data = self.unpack_pkt(data) # desempacoto o pacote
            if data['mensagem'] == 'ACK':
                break
        
        if rcv_address not in self.conections.keys():
            self.conections[rcv_address] = {
                'snd_base': 0, 'next_seq': 0, 'rcv_base' : 0
            }
        
        self.conections[rcv_address]['rcv_base'] += 1

        ack_resp_pck = self.create_pkt(
            ack = self.conections[rcv_address]['rcv_base'],
            seq = self.conections[rcv_address]['next_seq'],
            msg = '1'
        )
        
        self.sock.sendto(ack_resp_pck, rcv_address)
        self.conections[rcv_address]['next_seq'] += 1
        
        # Bloco 2 - Receber Pacote e Enviar Confirmação
        
        data = self.wait_for_response(rcv_address)
                
        self.conections[rcv_address]['snd_base'] = data['ack']
        self.conections[rcv_address]['rcv_base'] += len(data['mensagem'])
        
        mensagem = data['mensagem']
        
        msg_conf_pck = self.create_pkt(
            ack = self.conections[rcv_address]['rcv_base'],
            seq = self.conections[rcv_address]['snd_base'],
            msg= '2'
        )
        self.sock.sendto(msg_conf_pck, rcv_address)
        self.conections[rcv_address]['next_seq'] +=  1
        
        # Bloco 3 - Confirmar Recibo
        data = self.wait_for_response(rcv_address)
        
        self.conections[rcv_address]['snd_base'] = data['ack']
        '''
        print('send_base: {}, next_seq: {}, rcv_base: {}'.format(
                *self.conections[rcv_address].values()))
        '''
        return mensagem, rcv_address
