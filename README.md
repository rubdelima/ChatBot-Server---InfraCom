# Informações dos Arquivos

## Globais
* rdt.py (Arquivo com a class RDT que implemeta a tranferência confiável o UDP)

## Arquivos de Teste
Foram feitos 2 arquivos para testar se o RDT está conseguindo enviar e receber a mensagem, é bom para testes rápidos
* test_client.py (progama do cliente)
* test_server.py (progama do server)
### Como rodar:
* Passo 1: execute em uma janela do terminal o comando `python3 test_server.py`
* Passo 2: execute em outra janela do teminal com o server já em funcionamento o comando `python3 test_client.py`

## Arquivos do 
* user.py (Arquivo com a classe User utilizada no server para identificar o cliente)
* client.py (arquivo do cliente)
* server.py (arquivo do server)
### Como rodar:
* Passo 1: execute em uma janela do terminal o comando `python3 server.py`
* Passo 2: execute em outra janela do teminal com o server já em funcionamento o comando `python3 client.py`