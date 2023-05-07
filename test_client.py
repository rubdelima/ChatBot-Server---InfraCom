import socket
from rdt_prova import RDT
from rdt import Client

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('127.0.0.1', 5000)
cl = Client(client_socket)

while True:
    mensagem = input('Insira uma mensagem: ')
    cl.enviar(mensagem, server_address)
    mensagem, _ = cl.receber()
    print(f'Servidor: {mensagem}')