import socket
import datetime
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from rdt import Client


def get_time() -> str:
    now = datetime.datetime.now()
    time = now.strftime("%H:%M")
    return time

# cria o socket UDP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# define o IP e a porta do servidor
server_address = ('127.0.0.1', 5000)

# Criar a classe RDT

cl = Client(client_socket)

# solicita ao usuário o nome e o número da mesa
user_name = input('Digite seu nome: ')
table_number = input('Digite o número da mesa: ')

# envia o comando de conexão e os argumentos para o servidor
comando = ''
while comando != 'chefia':
    comando = input('Insira chefia para iniciar o chat: ')

message = f'{comando}:{user_name}:{table_number}'
cl.enviar(message, server_address)
data, address = cl.receber()
print(f'{get_time()} Server: {data}')

#lista de comandos e cardápio para autocompletion
cardapio = WordCompleter([])
comandos = WordCompleter(['chefia', 'levantar da mesa', 'pagar', 'pedido',
                          'conta da mesa', 'conta individual', 'cardapio'])

while True:
    try:
        command = prompt(f'{get_time()} {user_name}> ', completer=comandos)
        cl.enviar(command, server_address)
        data, address = cl.receber()
    except:
        print('O Server já fechou até mais')
        break
    
    if command == 'sair':
        print(f'{get_time()} Server: {data}')
        if data == 'Ok, você pode sair.':
            print('Desconectado com sucesso')
            client_socket.close()
            break
    
    if command == 'fechar_server':
        print(f'{get_time()} Server: {data}')
        client_socket.close()
    
    elif command == 'cardapio':
        #cardapio_data = data.split(',')
        cardapio_data = eval(data)
        cardapio = WordCompleter(cardapio_data.keys())
        print(f'{get_time()} Server: o nosso cardápio tem:')
        print(f"|{'Prato':<25} |{'Valor':<7}|")
        [print(f"|{i:<25} |{cardapio_data[i]:<7}|") for i in cardapio_data.keys()]
    
    elif command == 'conta individual' or command == 'fatura':
        minha_conta = eval(data)
        try:
            valor_total = 0
            valor_pendente = 0
            print(f"|{'Nº':<2}| {'Item':<25} | {'Valor':<5} |{'Status':<8}|{'V Pend':<6}|")
            for b, i in enumerate(minha_conta):
                print(f"|{b:<2}| {i[0]:<25} | {i[2]:<5} |{i[2]-i[3]:<8}|")
                valor_pendente += (i[2]-i[3])
                valor_total += i[2]
            print(f'Total gasto: {valor_total}\nValor pendente: {valor_pendente}')
        except:
            print(f'Aconteceu algum erro, por favor, se garanta que voê já fez um pedido ou pediu o cardápio')
    
    elif command == 'conta da mesa':
        print(f'{get_time()} Server: os valores da cada um da mesa é')
        fatura_mesa = eval(data)
        print("|{:<2}|{:<15}|{:<6}|{:<6}|{:<6}|".format(
            'N', 'Nome', 'V Gast', 'V Pago', 'V Pend'
        ))
        for i, j in enumerate(fatura_mesa):
            print("|{:<2}|{:<15}|{:<6}|{:<6}|{:<6}|".format(
            i, j[0], j[1], j[2], j[1]-j[2]
        ))
            
        
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

