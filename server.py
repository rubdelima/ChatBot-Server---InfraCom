import socket

from rdt import RDT

if __name__ == '__main__':
    r=RDT(tipo='server')
    while True:
        data, address = r.sock.recvfrom(r.BUFFER_SIZE)
        # Verifica se o cliente que enviou os dados já está registrado no dicionário clients
        if address not in r.clients:
            r.clients[address] = len(r.clients) + 1
        # Extrai o nome do arquivo e o tamanho do arquivo dos dados recebidos
        filename, filesize = data.decode('utf-8').split('|')
        filesize = int(filesize)
        # Envia uma mensagem de confirmação ('ack') para o cliente
        r.sock.sendto('ack'.encode('utf-8'), address)
        directory = r.receive_file(address=address, filename=filename, filesize=filesize)
        filename = f"{directory}/{filename}"
        # Envia o arquivo de volta para o cliente
        r.send_file(filename, address)
    r.close()