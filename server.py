import socket
import datetime
from user import User

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
cardapio = {'Sushi': 10,'Carne-de-Sol': 20}
lista_opcoes = ['sair', 'cardapio', 'pedido', 'pagar', 'fatura']
clients = {}
mesas = {}

thread_run = True

def run_command(command, args, client_address, data):
    match(command):
            case 'chefia':
                if client_address not in clients.keys():
                    clients[client_address] = User(client_address, args)
                    print(f'{get_time()} Cliente conectado: {args[0]} (mesa {args[1]})')
                    if args[1] not in mesas.keys():
                        mesas[args[1]] = [clients[client_address]]
                    else:
                        mesas[args[1]].append(clients[client_address])
                
                server_socket.sendto(f'O que deseja fazer?{lista_opcoes}'.encode(), client_address)
                
            case 'sair':
                # remove o cliente do dicionário de clientes se o valor gasto for igual ao valor pago
                if client_address in clients:
                    client = clients[client_address]
                    if client.valor_pago == client.valor_gasto:
                        clients.pop(client_address)
                        print(f'{get_time()} Cliente desconectado: {client.nome} (mesa {client.mesa})')
                        server_socket.sendto('Ok, você pode sair.'.encode(), client_address)
                    else:
                        server_socket.sendto('Você não pode sair, ainda tem uma fatura pendente.'.encode(), client_address)

            case 'cardapio':
                # envia ao cliente o cardápio
                cardapio_str = ','.join([f'{k} ({v} reais)' for k,v in cardapio.items()])
                server_socket.sendto(cardapio_str.encode(), client_address)

            case 'conta individual':
                # envia ao cliente a lista de pedidos e o valor total da fatura
                if client_address in clients:
                    server_socket.sendto((clients[client_address].get_fatura()).encode(), client_address)

            case 'pagar':
                # atualiza o valor pago pelo cliente
                if client_address in clients:
                    clients[client_address].pay()
                    server_socket.sendto('Obrigado pelo pagamento.'.encode(), client_address)

            case 'pedido':
                # recebe a mensagem perguntando quantos pedidos o cliente deseja fazer
                server_socket.sendto('Quantos pedidos deseja fazer?'.encode(), client_address)
                clients[client_address].fase = 'pedido1'
                
            case 'conta da mesa':
                message = ','.join([f'{i.nome} ({i.valor_gasto} reais)' for i in mesas[clients[client_address].mesa]])
                server_socket.sendto(message.encode(), client_address)

            case _:
                match(clients[client_address].fase):
                    case 'pedido1':
                        try:
                            clients[client_address].novo_pedido_qnt = int(data.decode())
                            server_socket.sendto('Digite o nome do pedido:'.encode(), client_address)
                            clients[client_address].fase = 'pedido2'
                        except:
                            server_socket.sendto('Informe um valor válido'.encode(), client_address)
                    
                    case 'pedido2':
                        nome_pedido = data.decode()
                        if nome_pedido in cardapio:
                            clients[client_address].novo_pedido.append(nome_pedido)
                            clients[client_address].valor_gasto += cardapio[nome_pedido]
                            pedidos_restantes = clients[client_address].novo_pedido_qnt - len(clients[client_address].novo_pedido)
                            if pedidos_restantes >0:
                                mensagem = f'Pedido de {nome_pedido} registrado, você têm {pedidos_restantes} pedidos.'
                            else:
                                mensagem = f'Pedido de {nome_pedido} registrado, o total é de {sum([cardapio[i] for i in clients[client_address].novo_pedido])}'
                                clients[client_address].atualizar_pedidos()
                            server_socket.sendto(mensagem.encode(), client_address)
                        else:
                            server_socket.sendto('Pedido inválido.'.encode(), client_address)
                        
                    case _:
                        server_socket.sendto('Código inválido'.encode(), client_address)
                # operação inválida


if __name__ == '__main__':
    while True:
        data, client_address = server_socket.recvfrom(1024)
        message = data.decode()
        parts = message.split(':')
        command = parts[0]
        args = parts[1:]
        
        run_command(command, args, client_address, data)
        
        for i in clients.keys():
            print(clients[i])


