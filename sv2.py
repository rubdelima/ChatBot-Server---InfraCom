from rdt import RDT

sr = RDT('server')
while True:
    mensagem, client = sr.receber()
    print(mensagem)
    sr.emitir(mensagem, client)

