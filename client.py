import socket
import datetime
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

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

#lista de comandos e cardápio para autocompletion
cardapio = WordCompleter([])
comandos = WordCompleter(['chefia', 'levantar da mesa', 'pagar', 'pedido',
                          'conta da mesa', 'conta individual', 'cardapio'])

while True:
    
    command = prompt(f'{get_time()} {user_name}> ', completer=comandos)
    client_socket.sendto(command.encode(), server_address)
    data, address = client_socket.recvfrom(1024)
    
    if command == 'sair':
        print(f'{get_time()} Server: {data.decode()}')
        if data.decode() == 'Ok, você pode sair.':
            print('Desconectado com sucesso')
            client_socket.close()
            break
    elif command == 'cardapio':
        cardapio_data = data.decode().split(',')
        cardapio = WordCompleter(cardapio_data)
        print(f'{get_time()} Server: o nosso cardápio tem:')
        [print(i) for i in cardapio_data]
    
    elif command == 'fatura mesa':
        print(f'{get_time()} Server: os valores da cada um da mesa é')
        fatura_mesa = data.decode().split(',')
        [print(i) for i in fatura_mesa]
        
    elif command == 'pedido':
        print(f'{get_time()} Server: {data.decode()}')
        while True:
            try:
                command = int(input(f'{get_time()} {user_name}> '))
                client_socket.sendto(str(command).encode(), server_address)
                break
            except ValueError:
                print("Por favor digite um valor inteiro")
                
        counter = 0
        while True: # "do - while de python"
            data, address = client_socket.recvfrom(1024)
            resposta = data.decode()
            print(f'{get_time()} Server: {resposta}')
            if 'registrado' in resposta: counter += 1
            if not (counter < command): break
            pedido = prompt(f'{get_time()} {user_name}> ', completer=cardapio).split()[0]
            client_socket.sendto(str(pedido).encode(), server_address)
        
            
    else:
        print(f'{get_time()} Server: {data.decode()}')

