import socket
from rdt import RDT

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('127.0.0.1', 5000)
cl = RDT(client_socket)

while True:
    mensagem = input('Insira uma mensagem: ')
    cl.enviar2(mensagem, server_address)
    mensagem, _ = cl.receber2()
    print(f'Servidor: {mensagem}')