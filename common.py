from socket import *

def create_header(data, seq_num):
    sum = checksum(data)

    return str({
        'seq': seq_num,
        'checksum': sum,
        'payload': data
    }).encode()

def checksum(data):
    sum = 0
    for i in range(0, len(data), 2):
        if i + 1 >= len(data):
            sum += ord(data[i]) & 0xFF

        else:
            sum += ((ord(data[i]) << 8) & 0xFF00) + (ord(data[i+1]) & 0xFF)
    
    while (sum >> 16) > 0:
        sum = (sum & 0xFFFF) + (sum >> 16)
    
    sum = ~sum

    return sum & 0xFFFF

def checksum_(sum, payload):
    if checksum(payload) == sum:
        return True
    else:
        return False

def send_ack(ack, seq_n):
    if ack:
        data = create_header("ACK", seq_n)
    else:
        data = create_header("NACK", seq_n)
    
    return data

def rcv_ack(data, seq_num):
    data = eval(data.decode())
    seq_num_recv = data['seq']
    checksum = data['checksum']
    payload = data['payload']

    if checksum_(checksum, payload) and seq_num_recv == seq_num and payload == "ACK":
        return True
    else:
        return False