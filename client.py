import socket
import datetime
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from rdt import RDT

def get_time() -> str:
    now = datetime.datetime.now()
    time = now.strftime("%H:%M")
    return time

# cria o socket UDP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# define o IP e a porta do servidor
server_address = ('127.0.0.1', 5000)

# Criar a classe RDT

cl = RDT(client_socket)

# solicita ao usuário o nome e o número da mesa
user_name = input('Digite seu nome: ')
table_number = input('Digite o número da mesa: ')

# envia o comando de conexão e os argumentos para o servidor
message = f'chefia:{user_name}:{table_number}'
cl.enviar(message, server_address)
data, address = cl.receber()
print(f'{get_time()} Server: {data}')

#lista de comandos e cardápio para autocompletion
cardapio = WordCompleter([])
comandos = WordCompleter(['chefia', 'levantar da mesa', 'pagar', 'pedido',
                          'conta da mesa', 'conta individual', 'cardapio'])

while True:
    
    command = prompt(f'{get_time()} {user_name}> ', completer=comandos)
    cl.enviar(command, server_address)
    data, address = cl.receber()
    
    if command == 'sair':
        print(f'{get_time()} Server: {data}')
        if data == 'Ok, você pode sair.':
            print('Desconectado com sucesso')
            client_socket.close()
            break
    elif command == 'cardapio':
        cardapio_data = data.split(',')
        cardapio = WordCompleter(cardapio_data)
        print(f'{get_time()} Server: o nosso cardápio tem:')
        [print(i) for i in cardapio_data]
    
    elif command == 'fatura mesa':
        print(f'{get_time()} Server: os valores da cada um da mesa é')
        fatura_mesa = data.split(',')
        [print(i) for i in fatura_mesa]
        
    elif command == 'pedido':
        print(f'{get_time()} Server: {data}')
        while True:
            try:
                command = int(input(f'{get_time()} {user_name}> '))
                cl.enviar(str(command), server_address)
                break
            except ValueError:
                print("Por favor digite um valor inteiro")
                
        counter = 0
        while True: # "do - while de python"
            data, address = cl.receber()
            resposta = data
            print(f'{get_time()} Server: {resposta}')
            if 'registrado' in resposta: counter += 1
            if not (counter < command): break
            pedido = prompt(f'{get_time()} {user_name}> ', completer=cardapio).split()[0]
            cl.enviar(str(pedido), server_address)
        
            
    else:
        print(f'{get_time()} Server: {data}')

