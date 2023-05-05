import socket
from rdt import RDT

# cria o socket UDP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('127.0.0.1', 5000)
server_socket.bind(server_address)

sv = RDT(server_socket)

while True:
    mensagem, cliente = sv.receber2()
    print(f' O cliente {cliente} disse {mensagem}')
    sv.enviar2(f'Você disse: {mensagem}', cliente)
    