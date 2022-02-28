from definitions import *

filename = "files"

def get_raw(content):
    if content.type == DataType.INSTRUCTION:
        this_type = content.type << 30
        op = content.op << 24
        addr1mode = content.addr1mode << 22
        addr1 = content.addr1 << 12
        addr2mode = content.addr2mode << 10
        addr2 = content.addr2
        raw = this_type | op | addr1 | addr1mode | addr2 | addr2mode
        return raw
    else:
        data = (content.data & Masks.DATA) | (content.type << 30)
        return data

class Files:
    def __init__(self,filename = filename,size=250000):
        self.filename = filename
        self.data = []
        self.size = size
        self.read()

    def read(self):
        with open(self.filename, "rb") as f:
            for i in range(self.size):
                piece = f.read(4)
                temp = int.from_bytes(piece,'big')
                if temp == 0:
                    break
                self.data.append(temp)

    def save(self):
        with open(self.filename, "wb") as f:
            for i in self.data:
                bytes = i.to_bytes(4,'big')
                f.write(bytes)

    def add(self,t):
        self.data.append(t)

#print(get_bytes(ram_content(DataType.UNSIGNED,0,0,0,0,0,0,10)))
