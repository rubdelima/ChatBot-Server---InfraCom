import socket
from rdt_prova import RDT
from rdt import Server

# cria o socket UDP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('127.0.0.1', 5000)
server_socket.bind(server_address)

sv = Server(server_socket)

while True:
    mensagem, cliente = sv.receber()
    print(f' O cliente {cliente} disse {mensagem}')
    sv.enviar(f'Você disse: {mensagem}', cliente)
    