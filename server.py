import socket
import datetime
from user import User
from rdt import Server
import json

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
serv = Server(server_socket)

# cria um dicionário para armazenar os clientes conectados
cardapio = {'Pastel-de-Frango': 5, 'Pastel-de-Queijo': 5,'Pastel-de-Catupiry': 5,
            'Pizza-Mussarela-P': 7, 'Pizza-Mussarela-M' : 15 ,'Pizza-Mussarela-G' : 30,
            'Pizza-Portugusa-P': 7, 'Pizza-Portuguesa-M' : 15 ,'Pizza-Portuguesa-G' : 30,
            'Pizza-Calabresa-P': 8, 'Pizza-Calabresa-M' : 18 ,'Pizza-Calabresa-G' : 35,
            'Batata-Simples' : 5, 'Batata-Media': 7, 'Ultimate-Batata' : 15,
            'Hamburguer-Simples' : 10, 'Hamburguer-Orion': 12, 'Ultimate-Hamburguer': 15,
            'Coca-Cola-Lata' : 5, 'Coca-Cola-1L' : 10, 'Fanta-Lata' : 5, 'Fanta-1L' : 10,
            'Heineken' : 5, 'Budweiser' : 5, 'Stela' : 5, 'Smirnoff' : 5
        }
lista_opcoes = ['sair', 'cardapio', 'pedido', 'pagar', 'conta individual', 'conta da mesa']
clients = {}
mesas = {}
lista_pedidos = []
clients_relatorio = []

def get_relatorio()->None:
    with open('relatorio.txt', 'w') as f:
        print(70*"-", file=f)
        a = 'Relatório de Vendas'
        b = ' '*(34-(len(a)//2))
        print('|'+b+a+b+'|', file=f)
        print(70*"-", file=f)
        print("| {:<3}| {:<25} | {:<5} | {:<18} | {:<4} |".format(
            'Nº', 'Item', 'Valor', 'Cliente', 'Mesa'), file = f)
        total = 0
        for i,j in enumerate(lista_pedidos):
            print("| {:<3}| {:<25} | {:<5} | {:<18} | {:<4} |".format(i+1, *j.values()), file=f)
            total += j['valor']
        print('-'*70, file=f)
        a = f'Total: {total}'
        b = ' '*(34-(len(a)//2))
        print('|'+b+a+b+'|', file=f)
        print('-'*70, file=f)
        
    with open('relatorio.json', 'w') as saida:
        json.dump(clients_relatorio, saida)
        
        
def run_command(command, args, client_address, data)->bool:
    match(command):
            case 'fechar_server':
                serv.enviar('Todos pagando suas contas, o restaurante fechou', client_address)
                for client_s in clients.keys():
                    clients[client_s].pay()
                    client = clients[client_s]
                    clients_relatorio.append(
                        {'nome': client.nome, 'mesa': client.mesa, 'conta individual': client.valor_gasto,
                         'socket': client.address, 'pedidos' : client.pedidos})
                    print(f'{get_time()} Cliente desconectado: {client.nome} (mesa {client.mesa})')
                return False
            
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
                        clients_relatorio.append(
                            {'nome': client.nome, 'mesa': client.mesa, 'conta individual': client.valor_gasto,
                             'socket': client.address, 'pedidos' : client.pedidos})
                        print(f'{get_time()} Cliente desconectado: {client.nome} (mesa {client.mesa})')
                        serv.enviar('Ok, você pode sair.', client_address)
                    else:
                        serv.enviar('Você não pode sair, ainda tem uma fatura pendente.', client_address)

            case 'cardapio':
                # envia ao cliente o cardápio
                serv.enviar(str(cardapio), client_address)

            case 'conta individual':
                # envia ao cliente a lista de pedidos e o valor total da fatura
                if client_address in clients:
                    serv.enviar((clients[client_address].get_fatura()), client_address)

            case 'pagar':
                # atualiza o valor pago pelo cliente
                if client_address in clients:
                    clients[client_address].fase = 'pagamento'
                    serv.enviar('Quanto deseja pagar?', client_address)

            case 'pedido':
                # recebe a mensagem perguntando quantos pedidos o cliente deseja fazer
                serv.enviar('Quantos pedidos deseja fazer?', client_address)
                clients[client_address].fase = 'pedido1'
                
            case 'conta da mesa':
                message = [(i.nome, i.valor_gasto, i.valor_pago) for i in mesas[clients[client_address].mesa]]
                serv.enviar(str(message), client_address)

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
                        print(nome_pedido)
                        if nome_pedido in cardapio:
                            lista_pedidos.append(
                                {   'pedido' : nome_pedido, 'valor' : cardapio[nome_pedido],
                                    'nome' :  clients[client_address].nome, 'mesa' : clients[client_address].mesa 
                                }
                            )
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
                        
                    case 'pagamento':
                        if client_address in clients.keys():
                            clients[client_address].fase = None
                            try:
                                valor = int(data)
                                resto = clients[client_address].pay(valor)
                                r_1 = resto
                                for i in mesas.keys():
                                    if clients[client_address] in mesas[i]:
                                        mesa_len = len(mesas[i])
                                        mesa = i
                                        break
                                
                                ja_pagos = 1
                                #enquanto tiver troco pra distribuir e gente na mesa para receber e tiver mais troco que pessoa
                                while (resto > 0 and mesa_len>0 and resto>=mesa_len and (mesa_len-ja_pagos)>0):
                                    print(f'{resto // (mesa_len-ja_pagos)} = {resto} // ({mesa_len-ja_pagos})')
                                    dist = resto // (mesa_len-ja_pagos)
                                    print(f'{dist}')
                                    resto = resto % mesa_len-ja_pagos
                                    mesa_len = 0
                                    r = 0
                                    for colega in mesas[mesa]:
                                        if colega.valor_pago < colega.valor_gasto:
                                            r += colega.pay(dist)
                                            mesa_len += 1
                                    resto += r
                                            
                                
                                if r_1 == 0:
                                    serv.enviar('Obrigado pelo pagamento, falta {} para concluir'.format(
                                        clients[client_address].valor_gasto - clients[client_address].valor_pago), client_address)
                                else:
                                    serv.enviar(f'Obrigado pelo pagamento, o troco do seu pagamento foi distrbuido entre seus amigos e sobrou {resto} ainda', client_address)
                                
                            except ValueError:
                                serv.enviar('Valor inválido', client_address)
                        
                    # operação inválida
                    case _:
                        serv.enviar('Código inválido', client_address)
    return True


if __name__ == '__main__':
    while True:
        data, client_address = serv.receber()
        message = data
        parts = message.split(':')
        command = parts[0]
        args = parts[1:]
        
        if not run_command(command, args, client_address, data):
            break
        
        for i in clients.keys():
            print(clients[i])
    
    get_relatorio()
    serv.sock.close()


