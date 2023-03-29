class User():
    def __init__(self, adress, args):
        self.ip = adress[0]
        self.port = adress[1]
        self.address = adress
        self.nome = args[0]
        self.mesa = args[1]
        self.pedidos =[]
        self.valor_gasto = 0
        self.valor_pago = 0
        self.fase = None
        self.novo_pedido =[]
        self.novo_pedido_qnt =0
        
    def __str__(self):
        return f"Nome:{self.nome}, mesa: {self.mesa}, ip/porta = {self.address} pedidos = {self.pedidos}, valor gasto: {self.valor_gasto}, valor pago: {self.valor_pago}"
    
    def pay(self):
        self.valor_pago = self.valor_gasto

    def get_fatura(self) -> str:
        return f'Pedidos realizados = {",".join(self.pedidos)} Total: {self.valor_gasto} Valor que falta pagar: {self.valor_gasto - self.valor_pago}'
    
    def atualizar_pedidos(self):
        self.pedidos.extend(self.novo_pedido)
        self.novo_pedido = []
        self.novo_pedido_qnt =0
        self.fase = None