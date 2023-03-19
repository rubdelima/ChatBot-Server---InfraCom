import socket
import datetime

def get_time() -> str:
    now = datetime.datetime.now()
    time = now.strftime("%H:%M")
    return time

# cria o socket UDP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# define o IP e a porta do servidor
server_address = ('localhost', 5000)

# solicita ao usuário o nome e o número da mesa
user_name = input('Digite seu nome: ')
table_number = input('Digite o número da mesa: ')

# envia o comando de conexão e os argumentos para o servidor
message = f'chefia:{user_name}:{table_number}'
client_socket.sendto(message.encode(), server_address)
data, address = client_socket.recvfrom(1024)
print(f'{get_time()} Server: {data.decode()}')

while True:
    
    command = input(f'{get_time()} {user_name}> ')
    if command == 'sair':
        client_socket.sendto('sair'.encode(), server_address)
        data, address = client_socket.recvfrom(1024)
        print(f'{get_time()} Server: {data.decode()}')
        if data.decode() == 'Ok, você pode sair.':
            print('Desconectado com sucesso')
            client_socket.close()
            break
    elif command == 'pedido':
        client_socket.sendto(command.encode(), server_address)
        data, address = client_socket.recvfrom(1024)
        print(f'{get_time()} Server: {data.decode()}')

        num_pedidos = input(f'{get_time()} {user_name}> ')
        client_socket.sendto(num_pedidos.encode(), server_address)
        data, address = client_socket.recvfrom(1024)
        print(f'{get_time()} Server: {data.decode()}')

    else:
        client_socket.sendto(command.encode(), server_address)
        data, address = client_socket.recvfrom(1024)
        print(f'{get_time()} Server: {data.decode()}')

