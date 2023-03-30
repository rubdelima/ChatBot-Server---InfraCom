import socket
import os
from tkinter.filedialog import askopenfilename
from tqdm import tqdm

BUFFER_SIZE = 1024

server_address = ('localhost', 5000)
client_address = ('localhost', 0)

def send_file(sock, filename):
    filesize = os.path.getsize(filename)
    data = f"{os.path.basename(filename)}|{filesize}"
    sock.sendto(data.encode('utf-8'), server_address)
    ack, _ = sock.recvfrom(BUFFER_SIZE)

    with open(filename, 'rb') as f:
        with tqdm(total=filesize, desc=f'Sending {filename}', unit='B', unit_scale=True) as pbar:
            while True:
                data = f.read(BUFFER_SIZE)
                if not data:
                    break
                sock.sendto(data, server_address)
                pbar.update(len(data))
        print(f"{filename} sent")

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(client_address)
        print(f"Client started on {sock.getsockname()}")

        filename = askopenfilename()

        send_file(sock, filename)

if __name__ == '__main__':
    main()
