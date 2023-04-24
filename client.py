import os
from tkinter.filedialog import askopenfilename
from rdt import RDT


if __name__ == '__main__':
    r = RDT(tipo='client')
    filename = askopenfilename()
    filesize = r.send_file(filename)
    r.receive_file(os.path.basename(filename), filesize)
    r.close()
    