import socket
import datetime
from threading import Thread

# função para obter a hora atual
def get_time() -> str:
    now = datetime.datetime.now()
    time = now.strftime("%H:%M")
    return time

# cria o socket UDP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# define o IP e a porta do servidor
server_address = ('localhost', 5000)

# faz o bind do socket com o IP e a porta do servidor
server_socket.bind(server_address)

print(get_time() + ' Servidor UDP iniciado.')

# cria um dicionário para armazenar os clientes conectados
cardapio = {'Sushi': 10,'Carne de Sol': 20}
lista_opcoes = ['sair', 'cardapio', 'pedido', 'pagar', 'fatura']
clients = {}

thread_run = True

def mainloop():
    while thread_run:
        data, client_address = server_socket.recvfrom(1024)
        message = data.decode()
        parts = message.split(':')
        command = parts[0]
        args = parts[1:]
        match(command):
            case 'chefia':
                args.append([]) # lista de pedidos 
                args.append(0) #valor gasto
                args.append(0) #valor pago
                clients[client_address] = args
                print(f'{get_time()} Cliente conectado: {args[0]} (mesa {args[1]})')
                server_socket.sendto(f'O que deseja fazer?{lista_opcoes}'.encode(), client_address)

            case 'sair':
                # remove o cliente do dicionário de clientes se o valor gasto for igual ao valor pago
                if client_address in clients:
                    args = clients[client_address]
                    if args[4] == args[3]:
                        clients.pop(client_address)
                        print(f'{get_time()} Cliente desconectado: {args[0]} (mesa {args[1]})')
                        server_socket.sendto('Ok, você pode sair.'.encode(), client_address)
                    else:
                        server_socket.sendto('Você não pode sair, ainda tem uma fatura pendente.'.encode(), client_address)

            case 'cardapio':
                # envia ao cliente o cardápio
                cardapio_str = ', '.join([f'{k} ({v} reais)' for k,v in cardapio.items()])
                server_socket.sendto(cardapio_str.encode(), client_address)

            case 'fatura':
                # envia ao cliente a lista de pedidos e o valor total da fatura
                if client_address in clients:
                    args = clients[client_address]
                    pedido_str = ', '.join(args[2])
                    fatura_str = f'Valor gasto: {args[2]} reais\nPedidos: {pedido_str}'
                    server_socket.sendto(fatura_str.encode(), client_address)

            case 'pagar':
                # atualiza o valor pago pelo cliente
                if client_address in clients:
                    args = clients[client_address]
                    args[4] = args[3]
                    server_socket.sendto('Obrigado pelo pagamento.'.encode(), client_address)

            case 'pedido':
                # recebe a mensagem perguntando quantos pedidos o cliente deseja fazer
                server_socket.sendto('Quantos pedidos deseja fazer?'.encode(), client_address)
                data, client_address = server_socket.recvfrom(1024)
                num_pedidos = int(data.decode())

                # recebe os nomes dos pedidos e registra no banco
                pedidos = []
                total_pedido = 0
                for i in range(num_pedidos):
                    server_socket.sendto('Digite o nome do pedido:'.encode(), client_address)
                    data, client_address = server_socket.recvfrom(1024)
                    nome_pedido = data.decode()
                    if nome_pedido in cardapio:
                        pedidos.append(nome_pedido)
                        total_pedido += cardapio[nome_pedido]
                    else:
                        server_socket.sendto('Pedido inválido.'.encode(), client_address)

                # atualiza o valor gasto pelo cliente e a lista de pedidos
                if client_address in clients:
                    args = clients[client_address]
                    args[3] += total_pedido
                    args[2].extend(pedidos)
                    server_socket.sendto(f'Pedido registrado. Total a pagar: {args[3]} reais'.encode(), client_address)

            case _:
                server_socket.sendto('Código inválido'.encode(), client_address)
                # operação inválida

        for i in clients.keys():
            print(f'{i} : {clients[i]}')

if __name__ == '__main__':
    
    thr = Thread(target=mainloop)
    thr.run()
    
    while True:
        command_server = input()
        if command_server == 'exit':
            thread_run = False
            break
        elif command_server == 'show':
            for i in clients.keys():
                print(f'{i} : {clients[i]}')

