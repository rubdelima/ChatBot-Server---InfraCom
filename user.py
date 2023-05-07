#from server import cardapio
cardapio = {'Pastel-de-Frango': 5, 'Pastel-de-Queijo': 5,'Pastel-de-Catupiry': 5,
            'Pizza-Mussarela-P': 7, 'Pizza-Mussarela-M' : 15 ,'Pizza-Mussarela-G' : 30,
            'Pizza-Portugusa-P': 7, 'Pizza-Portuguesa-M' : 15 ,'Pizza-Portuguesa-G' : 30,
            'Pizza-Calabresa-P': 8, 'Pizza-Calabresa-M' : 18 ,'Pizza-Calabresa-G' : 35,
            'Batata-Simples' : 5, 'Batata-Media': 7, 'Ultimate-Batata' : 15,
            'Hamburguer-Simples' : 10, 'Hamburguer-Orion': 12, 'Ultimate-Hamburguer': 15,
            'Coca-Cola-Lata' : 5, 'Coca-Cola-1L' : 10, 'Fanta-Lata' : 5, 'Fanta-1L' : 10,
            'Heineken' : 5, 'Budweiser' : 5, 'Stela' : 5, 'Smirnoff' : 5
        }
class User():
    def __init__(self, adress, args):
        self.ip = adress[0]
        self.port = adress[1]
        self.address = adress
        self.nome = args[0]
        self.mesa = args[1]
        self.pedidos = []
        self.valor_gasto = 0
        self.valor_pago = 0
        self.fase = None
        self.novo_pedido = []
        self.novo_pedido_qnt =0
        
    def __str__(self):
        return "Nome:{}, mesa: {}, ip/porta = {} pedidos = {}, valor gasto: {}, valor pago: {}".format(
            self.nome, self.mesa, self.address, self.pedidos, self.valor_gasto, self.valor_pago
        )
    
    def pay(self, valor:int=None)->int:
        valor_inicial = valor
        if valor == None:
            self.valor_pago = self.valor_gasto
            for i in range(len(self.pedidos)):
                self.pedidos[i][1] = 'Pago'
        else:
            for i in self.pedidos:
                if i[2] > i[3]:
                    if valor+i[3] >= i[2]:
                        valor -= abs(i[3] - i[2])
                        i[3] = i[2] ; i[1] = 'Pago'
                    else:
                        i[3] += valor
                        valor = 0
                        break
                if valor == 0:
                    break
            self.valor_pago = valor_inicial - valor
            return valor
                

    def get_fatura(self) -> str:
        return str(self.pedidos)
    
    def atualizar_pedidos(self):
        #self.pedidos.extend(self.novo_pedido)
        for i in self.novo_pedido:
            a = [i, 'Pendente', cardapio[i], 0]
            self.pedidos.append(a)
        self.novo_pedido = []
        self.novo_pedido_qnt =0
        self.fase = None
