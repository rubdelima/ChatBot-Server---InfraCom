from rdt import RDT

cl = RDT()
while True:
    mensagem = input('Digite a mensagem: ')
    cl.emitir(mensagem)
    retorno, _ = cl.receber()
    print(f'Server: {retorno}')
    if mensagem == 'sair':
        cl.sock.close()
        break