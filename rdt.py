import socket
import struct

class RDT():
    def __init__(self,sock):
        self.sock = sock
    
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
    
    def wait_for_ack(self, destino, ack_value, sndpkt)->bool:
        # S1, S2, S3 / S6, S7, S8
        estado = f'wait for ack{ack_value}'
        while estado == f'wait for ack{ack_value}':
            try:
                data, endereco = self.sock.recvfrom(1024)
                data = self.unpack_pkt(data)
                v1 = endereco == destino
                v2 = self.checksum(data['mensagem']) == data['checksum']
                v3 = data['ack'] == ack_value^1
                # S3
                if v1 and v2 and v3:
                    self.sock.settimeout(None) # encerrando o timer
                    estado = f'wait for ack{ack_value^1}'
                    return True
                else: # S2
                    continue
            
            except socket.timeout: # S3
                self.sock.sendto(sndpkt, destino) # Reenvio o pacote
                self.sock.settimeout(2) # Reinicio o timer
   
    def enviar(self, msg, destino):
        # S0 - Criar o pacote e enviar e iniciar o timer
        sndpkt = self.create_pkt(ack = 1, seq=0, msg='ACK')
        # S1, S2, S3, S4 (S4 - Receber, restante na função)
        self.sock.sendto(sndpkt, destino)
        self.sock.settimeout(2)
        rcvpkt = self.wait_for_ack(destino, 0, sndpkt)
        
        # S5
        sndpkt = self.create_pkt(ack=0, seq=1, msg=msg)
        # S6, S7, S8, S9 (S9 - Receber, restante na função)
        self.sock.sendto(sndpkt, destino)
        self.sock.settimeout(2)
        rcvpkt = self.wait_for_ack(destino, 1, sndpkt)

    def wait_for_seq(self, seq:int, endereco_s=None)->tuple:
            estado = f'wait for {seq} from below'
            while (estado == f'wait for {seq} from below'):
                data, endereco = self.sock.recvfrom(1024)
                data = self.unpack_pkt(data)
                v1 = self.checksum(data['mensagem']) == data['checksum']
                v2 = data['seq'] == seq
                v3 = (endereco_s == endereco) or (endereco_s == None)
                if v1 and v2 and v3:
                    sndpkt = self.create_pkt(ack=seq^1, seq=seq^1, msg='OK')
                    estado = f'wait for {seq^1} from below'
                else:
                    sndpkt = self.create_pkt(ack=seq, seq=seq, msg='NO')

                self.sock.sendto(sndpkt, endereco)
            
            return data['mensagem'], endereco
        
    def receber(self):
        # R0 e R1
        data, endereco = self.wait_for_seq(0)
        data, endereco = self.wait_for_seq(1, endereco)
        return data, endereco
                
class Server(RDT):
    def __init__(self,sock):
        super().__init__(sock)

class Client(RDT):
    def __init__(self,sock):
        super().__init__(sock)