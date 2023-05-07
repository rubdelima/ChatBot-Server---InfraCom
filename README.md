# Informação da Equipe
## Membros:
* Felipe Neiva
* Frederick Almeida
* Hugo Felix
* Rubens Lima

# Informações dos Arquivos
## Globais
* rdt.py (Arquivo com a class RDT que implemeta a tranferência confiável o UDP)

## Arquivos de Teste
Foram feitos 2 arquivos para testar se o RDT está conseguindo enviar e receber a mensagem, é bom para testes rápidos
* test_client.py (progama do cliente)
* test_server.py (progama do server)
* rdt_prova.py (Implementação de transferência confiável como o da prova)

### Como rodar:
* Passo 1: execute em uma janela do terminal o comando `python3 test_server.py`
* Passo 2: execute em outra janela do teminal com o server já em funcionamento o comando `python3 test_client.py`

## Arquivos do Projeto
* user.py (Arquivo com a classe User utilizada no server para identificar o cliente)
* client.py (arquivo do cliente)
* server.py (arquivo do server)

### Como rodar:
* Passo 1: execute em uma janela do terminal o comando `python3 server.py`
* Passo 2: execute em outra janela do teminal com o server já em funcionamento o comando `python3 client.py`

### Funcionamento dos comandos
#### **server.py**
Nesse não é preciso executar algum comando, ele apenas deve ser executado primeiramente para servir de servidor, após o fim de sua execuçõ são gerados 2 arquivos de relatório, o primeiro `.json` é como está na especificação do projeto, e o `.txt` é um relatório de todos os itens vendidos

#### **client.py**
Nesse código será necessário executar os comando, inicie inserindo os itens solicitados, e após se conectar com o servidor, recomenda-se que seja pedido o cardapio com o comando `cardapio` para que assim ao fazer um pedido, o auto-compliter possa lhe ajudar, e ajudará a evitar erros.