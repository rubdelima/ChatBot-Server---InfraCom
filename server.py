import socket
import datetime
from user import User
from rdt import RDT

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
# Criando a classe com RDT
serv = RDT(server_socket)

# cria um dicionário para armazenar os clientes conectados
cardapio = {'Refrigerante': 5, 'Sushi': 10,'Carne-de-Sol': 20}
lista_opcoes = ['sair', 'cardapio', 'pedido', 'pagar', 'conta individual', 'conta da mesa']
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
                
                serv.enviar(f'O que deseja fazer?{lista_opcoes}', client_address)
                
            case 'sair':
                # remove o cliente do dicionário de clientes se o valor gasto for igual ao valor pago
                if client_address in clients:
                    client = clients[client_address]
                    if client.valor_pago == client.valor_gasto:
                        mesas[client.mesa].remove(clients[client_address])
                        clients.pop(client_address)
                        print(f'{get_time()} Cliente desconectado: {client.nome} (mesa {client.mesa})')
                        serv.enviar('Ok, você pode sair.', client_address)
                    else:
                        serv.enviar('Você não pode sair, ainda tem uma fatura pendente.', client_address)

            case 'cardapio':
                # envia ao cliente o cardápio
                cardapio_str = ','.join([f'{k} ({v} reais)' for k,v in cardapio.items()])
                serv.enviar(cardapio_str, client_address)

            case 'conta individual':
                # envia ao cliente a lista de pedidos e o valor total da fatura
                if client_address in clients:
                    serv.enviar((clients[client_address].get_fatura()), client_address)

            case 'pagar':
                # atualiza o valor pago pelo cliente
                if client_address in clients:
                    clients[client_address].pay()
                    serv.enviar('Obrigado pelo pagamento.', client_address)

            case 'pedido':
                # recebe a mensagem perguntando quantos pedidos o cliente deseja fazer
                serv.enviar('Quantos pedidos deseja fazer?', client_address)
                clients[client_address].fase = 'pedido1'
                
            case 'conta da mesa':
                message = ','.join([f'{i.nome} ({i.valor_gasto-i.valor_pago} reais)' for i in mesas[clients[client_address].mesa]])
                serv.enviar(message, client_address)

            case _:
                match(clients[client_address].fase):
                    case 'pedido1':
                        try:
                            clients[client_address].novo_pedido_qnt = int(data)
                            serv.enviar('Digite o nome do pedido:', client_address)
                            clients[client_address].fase = 'pedido2'
                        except:
                            serv.enviar('Informe um valor válido', client_address)
                    
                    case 'pedido2':
                        nome_pedido = data
                        if nome_pedido in cardapio:
                            clients[client_address].novo_pedido.append(nome_pedido)
                            clients[client_address].valor_gasto += cardapio[nome_pedido]
                            pedidos_restantes = clients[client_address].novo_pedido_qnt - len(clients[client_address].novo_pedido)
                            if pedidos_restantes >0:
                                mensagem = f'Pedido de {nome_pedido} registrado, você têm {pedidos_restantes} pedidos.'
                            else:
                                mensagem = f'Pedido de {nome_pedido} registrado, o total é de {sum([cardapio[i] for i in clients[client_address].novo_pedido])}'
                                clients[client_address].atualizar_pedidos()
                            serv.enviar(mensagem, client_address)
                        else:
                            serv.enviar('Pedido inválido.', client_address)
                        
                    case _:
                        serv.enviar('Código inválido', client_address)
                # operação inválida


if __name__ == '__main__':
    while True:
        data, client_address = serv.receber()
        print(data)
        message = data
        parts = message.split(':')
        command = parts[0]
        args = parts[1:]
        
        run_command(command, args, client_address, data)
        
        for i in clients.keys():
            print(clients[i])


